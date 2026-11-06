// Robnet-Analyse: Messschleife des Oszilloskops. Version 00.01, Stand 06.11.2026.
// Liest den oberen Wandler (U2, MCP3208, CE0) ueber direkten Registerzugriff so schnell wie moeglich.
// Nur lesen: Das Programm sendet nichts auf den Robnet-Bus. Laeuft als root (Zugriff auf /dev/mem).
// Bauen: gcc -O2 -pthread -o messkern messkern_v00.01.c
//
// Befehle auf stdin, je eine Zeile:
//   K <teiler> <n> <code1> .. <coden>   Kanalliste; code = Kanal 0..7, +8 = Differenz im Chip
//   F <vor> <nach> <art> <quelle> <pegel> <steigend> <wartezeit_ms> <breite>
//       art 0 Auto, 1 Normal/Einmal; quelle -1 keine, 0..n-1 Listenplatz, 100 Bus, 101 Alarm
//   R <pfad> <dauer_s>                  Rohdaten in Datei schreiben
//   X                                   Frame oder Aufzeichnung abbrechen
//   E                                   Beenden
// Antworten auf stdout: Kopf_t, danach bei Frames n*breite*2 uint16 (min, max je Spalte).
// Unterbefehl zum Lesen: messkern A <datei> <n> <von_scan> <bis_scan> <breite>
#define _GNU_SOURCE
#include <fcntl.h>
#include <pthread.h>
#include <sched.h>
#include <signal.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>

#define PERI 0x3F000000u
#define ST_CLO (0x3004 / 4)
#define G_SET0 (0x200000 / 4 + 7)
#define G_CLR0 (0x200000 / 4 + 10)
#define G_LEV0 (0x200000 / 4 + 13)
#define SPI_CS (0x204000 / 4)
#define SPI_FIFO (0x204004 / 4)
#define SPI_CLK (0x204008 / 4)
#define CS_TA (1u << 7)
#define CS_CLEAR (3u << 4)
#define CS_DONE (1u << 16)
#define CE0 (1u << 8)
#define GPIO_BUS 23
#define GPIO_ALARM 27
#define RING (1u << 23)         // 8 Mio. Werte, 16 MB
#define MASKE (RING - 1)
#define KALIB_TEILER 800u       // 0,5 MHz gilt als Referenz
#define KALIB_KANAL 5           // Bordspannung
#define MAXK 8

typedef struct {
    char kennung[4];
    uint32_t art;               // 1 Frame, 2 Aufzeichnung fertig, 3 Konfiguration
    uint32_t n, breite;
    uint32_t ausgeloest, teiler;
    uint64_t scans;             // Scans im Frame oder in der Datei
    uint64_t trigger_scan;      // Lage des Triggers im Frame
    uint32_t tick_start;        // Systemzeit (us) des ersten Scans, wie bei pigpio
    float rate;                 // gemessene Scans pro Sekunde
    float abstand_min, abstand_max; // kleinster und groesster Scanabstand in us
    float kalib;                // Referenzwert / Messwert der Bordspannung bei diesem Teiler
    float kalib_ref;            // Referenzwert der Bordspannung (Rohwert bei 0,5 MHz)
} Kopf_t;

static volatile uint32_t *p;
static uint16_t *ring;
static _Atomic uint64_t schreib;       // Werte insgesamt
static _Atomic int laufen = 1;
static _Atomic int neu_konfig;
static uint32_t k_teiler = 56;
static int k_n = 1;
static uint32_t k_code[MAXK];
static _Atomic int aktiv_n = 1;
static float kalib = 1.0f, kalib_ref;

// Trigger, von der Messschleife ausgewertet
static _Atomic int t_scharf;           // 0 aus, 1 scharf
static _Atomic int t_quelle = -1;
static _Atomic int t_pegel, t_steigend = 1;
static _Atomic uint64_t t_treffer;     // Scan des Treffers + 1, 0 = keiner
static _Atomic uint32_t t_tick;
// Statistik
static _Atomic uint32_t s_tick_a, s_tick_b;
static _Atomic uint64_t s_scan_a, s_scan_b;
static _Atomic uint32_t s_min = 1000000, s_max;
static _Atomic int s_ruecksetzen;
// Zeit und Scanzahl, zusammen veroeffentlicht
typedef struct { uint32_t t; uint64_t s; } Paar;
static Paar paar[2];
static _Atomic int paar_i;

static inline uint32_t tick(void) { return p[ST_CLO]; }

static inline uint32_t lese(uint32_t code) {
    uint32_t single = (code & 8) ? 0x04 : 0x06;
    uint32_t ch = code & 7;
    p[G_CLR0] = CE0;
    p[SPI_CS] = CS_CLEAR | CS_TA;
    p[SPI_FIFO] = single | (ch >> 2);
    p[SPI_FIFO] = (ch & 3) << 6;
    p[SPI_FIFO] = 0;
    while (!(p[SPI_CS] & CS_DONE)) {}
    (void)p[SPI_FIFO];
    uint32_t a = p[SPI_FIFO], b = p[SPI_FIFO];
    p[SPI_CS] = 0;
    p[G_SET0] = CE0;
    return ((a & 0x0F) << 8) | b;
}

static float kalibrieren(uint32_t teiler) {
    long a = 0, b = 0;
    p[SPI_CLK] = KALIB_TEILER;
    for (int i = 0; i < 2000; i++) a += lese(KALIB_KANAL);
    p[SPI_CLK] = teiler;
    for (int i = 0; i < 2000; i++) lese(KALIB_KANAL);   // einschwingen
    for (int i = 0; i < 2000; i++) b += lese(KALIB_KANAL);
    if (b < 2000 * 100 || a < 2000 * 100) return 1.0f;  // keine brauchbare Bordspannung
    kalib_ref = (float)a / 2000.0f;
    return (float)a / (float)b;
}

static void *messen(void *arg) {
    (void)arg;
    cpu_set_t c;
    CPU_ZERO(&c);
    CPU_SET(3, &c);
    sched_setaffinity(0, sizeof c, &c);
    uint64_t w = 0, scan = 0;
    uint32_t code[MAXK];
    int n = 0;
    int alt[MAXK + 2] = {0};
    uint32_t letzt = tick();
    uint32_t tmin = 1000000, tmax = 0;
    uint32_t block = 0;
    while (atomic_load(&laufen)) {
        if (atomic_load(&neu_konfig)) {
            kalib = kalibrieren(k_teiler);
            p[SPI_CLK] = k_teiler;
            n = k_n;
            for (int i = 0; i < n; i++) code[i] = k_code[i];
            atomic_store(&aktiv_n, n);
            w = 0;
            scan = 0;
            atomic_store(&schreib, 0);
            atomic_store(&t_treffer, 0);
            atomic_store(&s_scan_a, 0);
            atomic_store(&s_tick_a, tick());
            tmin = 1000000;
            tmax = 0;
            atomic_store(&s_min, 0);
            atomic_store(&s_max, 0);
            letzt = tick();
            paar[0].t = paar[1].t = letzt;
            paar[0].s = paar[1].s = 0;
            atomic_store(&neu_konfig, 0);
        }
        if (n == 0) { usleep(1000); continue; }
        for (int j = 0; j < n; j++) ring[(w + j) & MASKE] = (uint16_t)lese(code[j]);
        w += n;
        scan++;
        atomic_store_explicit(&schreib, w, memory_order_release);

        uint32_t jetzt = tick();
        uint32_t d = jetzt - letzt;
        letzt = jetzt;
        if (d < tmin) tmin = d;
        if (d > tmax) tmax = d;

        if (atomic_load_explicit(&t_scharf, memory_order_relaxed)) {
            int q = atomic_load_explicit(&t_quelle, memory_order_relaxed);
            int wert, schwelle = 1;
            if (q >= 100) {
                wert = (p[G_LEV0] >> (q == 100 ? GPIO_BUS : GPIO_ALARM)) & 1;
            } else {
                wert = ring[(w - n + q) & MASKE];
                schwelle = atomic_load_explicit(&t_pegel, memory_order_relaxed);
            }
            int oben = wert >= schwelle;
            int stg = atomic_load_explicit(&t_steigend, memory_order_relaxed);
            if (alt[0] != 2 && oben != alt[0] && oben == stg) {
                atomic_store(&t_tick, jetzt);
                atomic_store(&t_treffer, scan);
                atomic_store(&t_scharf, 0);
            }
            alt[0] = oben;
        } else {
            alt[0] = 2;
        }
        if ((scan & 63) == 0) {
            int i = !atomic_load(&paar_i);
            paar[i].t = jetzt;
            paar[i].s = scan;
            atomic_store(&paar_i, i);
            if (atomic_exchange(&s_ruecksetzen, 0)) {
                tmin = d;
                tmax = d;
            }
            atomic_store(&s_min, tmin);
            atomic_store(&s_max, tmax);
        }
        if (++block >= 4096) {
            block = 0;
            atomic_store(&s_tick_b, atomic_load(&s_tick_a));
            atomic_store(&s_scan_b, atomic_load(&s_scan_a));
            atomic_store(&s_tick_a, jetzt);
            atomic_store(&s_scan_a, scan);
        }
    }
    return NULL;
}

static float rate_jetzt(void) {
    uint32_t a = atomic_load(&s_tick_a), b = atomic_load(&s_tick_b);
    uint64_t sa = atomic_load(&s_scan_a), sb = atomic_load(&s_scan_b);
    uint32_t d = a - b;
    if (!d || sa <= sb) return 0;
    return (float)((sa - sb) * 1e6 / d);
}

static uint16_t *spalten;

static int zeile_lesen(char *z, size_t g, int warte_ms) {
    fd_set s;
    FD_ZERO(&s);
    FD_SET(0, &s);
    struct timeval t = {warte_ms / 1000, (warte_ms % 1000) * 1000};
    if (select(1, &s, NULL, NULL, &t) <= 0) return 0;
    size_t i = 0;
    while (i + 1 < g) {
        char c;
        if (read(0, &c, 1) != 1) { atomic_store(&laufen, 0); return -1; }
        if (c == '\n') break;
        z[i++] = c;
    }
    z[i] = 0;
    return 1;
}

static void schreibe(const void *d, size_t g) {
    const char *a = d;
    while (g) {
        ssize_t n = write(1, a, g);
        if (n <= 0) { atomic_store(&laufen, 0); return; }
        a += n;
        g -= (size_t)n;
    }
}

static void kopf_fuellen(Kopf_t *k, uint32_t art, uint32_t n, uint32_t breite) {
    memset(k, 0, sizeof *k);
    memcpy(k->kennung, "RNET", 4);
    k->art = art;
    k->n = n;
    k->breite = breite;
    k->teiler = k_teiler;
    k->rate = rate_jetzt();
    k->abstand_min = (float)atomic_load(&s_min);
    k->abstand_max = (float)atomic_load(&s_max);
    k->kalib = kalib;
    k->kalib_ref = kalib_ref;
}

// vor, nach in Scans. Antwortet immer mit genau einem Frame.
static void frame(long vor, long nach, int art, int quelle, int pegel, int steigend, int warte_ms, uint32_t breite) {
    int n = atomic_load(&aktiv_n);
    if (n < 1) n = 1;
    if (breite > 4000) breite = 4000;
    if (breite < 1) breite = 1;
    long maxscan = (long)(RING / (unsigned)n) - 1024;
    if (vor + nach > maxscan) { nach = maxscan - vor; if (nach < 1) { vor = maxscan / 2; nach = maxscan / 2; } }
    atomic_store(&s_ruecksetzen, 1);
    // Vorlauf abwarten
    uint64_t start = atomic_load(&schreib) / (unsigned)n;
    Paar mess_a = paar[atomic_load(&paar_i)];
    while (atomic_load(&laufen) && (long)(atomic_load(&schreib) / (unsigned)n - start) < vor) usleep(100);
    int ausgeloest = 0;
    uint64_t ziel;
    uint32_t tt = 0;
    if (quelle >= 0 || quelle == 100 || quelle == 101) {
        atomic_store(&t_quelle, quelle);
        atomic_store(&t_pegel, pegel);
        atomic_store(&t_steigend, steigend);
        atomic_store(&t_treffer, 0);
        atomic_store(&t_scharf, 1);
        struct timespec t0;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        while (atomic_load(&laufen)) {
            if (atomic_load(&t_treffer)) { ausgeloest = 1; break; }
            char z[64];
            if (zeile_lesen(z, sizeof z, 1) && z[0] == 'X') break;
            struct timespec t1;
            clock_gettime(CLOCK_MONOTONIC, &t1);
            long ms = (t1.tv_sec - t0.tv_sec) * 1000 + (t1.tv_nsec - t0.tv_nsec) / 1000000;
            if (art == 0 && ms >= warte_ms) break;
            if (art == 1 && warte_ms > 0 && ms >= warte_ms) break;
        }
        atomic_store(&t_scharf, 0);
    }
    if (ausgeloest) {
        ziel = atomic_load(&t_treffer) - 1;
        tt = atomic_load(&t_tick);
    } else {
        ziel = atomic_load(&schreib) / (unsigned)n;
        tt = tick();
    }
    while (atomic_load(&laufen) && (long)(atomic_load(&schreib) / (unsigned)n) < (long)ziel + nach + 1) usleep(100);
    long von = (long)ziel - vor;
    if (von < 0) von = 0;
    uint64_t scans = (uint64_t)(ziel + nach - (uint64_t)von);
    if (scans < 1) scans = 1;
    uint32_t b = scans < breite ? (uint32_t)scans : breite;
    for (int j = 0; j < n; j++) {
        for (uint32_t i = 0; i < b; i++) {
            uint64_t a = (uint64_t)von + scans * i / b, e = (uint64_t)von + scans * (i + 1) / b;
            uint16_t lo = 0xFFFF, hi = 0;
            for (uint64_t s = a; s < e; s++) {
                uint16_t v = ring[(s * (unsigned)n + (unsigned)j) & MASKE];
                if (v < lo) lo = v;
                if (v > hi) hi = v;
            }
            spalten[(j * b + i) * 2] = lo;
            spalten[(j * b + i) * 2 + 1] = hi;
        }
    }
    Kopf_t k;
    kopf_fuellen(&k, 1, (uint32_t)n, b);
    // Rate aus genau diesem Frame: Scans geteilt durch verstrichene Zeit
    Paar mess_e = paar[atomic_load(&paar_i)];
    uint32_t mess_d = mess_e.t - mess_a.t;
    if (mess_d >= 1000 && mess_e.s > mess_a.s) k.rate = (float)((double)(mess_e.s - mess_a.s) * 1e6 / mess_d);
    k.ausgeloest = (uint32_t)ausgeloest;
    k.scans = scans;
    k.trigger_scan = ziel - (uint64_t)von;
    k.tick_start = tt - (uint32_t)((double)(ziel - (uint64_t)von) * 1e6 / (k.rate > 0 ? k.rate : 1));
    schreibe(&k, sizeof k);
    schreibe(spalten, (size_t)n * b * 2 * sizeof(uint16_t));
}

static void aufzeichnen(const char *pfad, double dauer) {
    int n = atomic_load(&aktiv_n);
    FILE *f = fopen(pfad, "wb");
    uint64_t pos = atomic_load(&schreib);
    pos -= pos % (unsigned)n;
    uint32_t t_start = tick();
    uint64_t schreib_start = pos;
    Paar rec_a = paar[atomic_load(&paar_i)];
    int abbruch = 0;
    atomic_store(&s_ruecksetzen, 1);
    if (f) {
        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        double letzt = 0;
        for (;;) {
            uint64_t w = atomic_load(&schreib);
            w -= w % (unsigned)n;
            if (w - pos > RING - 4096) { pos = w - (RING / 2); pos -= pos % (unsigned)n; }  // zu langsam: alte Werte verwerfen
            while (pos < w) {
                uint64_t a = pos & MASKE;
                uint64_t g = w - pos;
                if (a + g > RING) g = RING - a;
                fwrite(ring + a, sizeof(uint16_t), g, f);
                pos += g;
            }
            clock_gettime(CLOCK_MONOTONIC, &t1);
            double t = (double)(t1.tv_sec - t0.tv_sec) + (double)(t1.tv_nsec - t0.tv_nsec) * 1e-9;
            if (t - letzt > 2.0) { fflush(f); fdatasync(fileno(f)); letzt = t; }
            if (t >= dauer) break;
            char z[64];
            if (zeile_lesen(z, sizeof z, 5) && z[0] == 'X') { abbruch = 1; break; }
        }
        fflush(f);
        fdatasync(fileno(f));
        fclose(f);
    }
    (void)abbruch;
    Kopf_t k;
    kopf_fuellen(&k, 2, (uint32_t)n, 0);
    k.scans = (pos - schreib_start) / (unsigned)n;
    k.tick_start = t_start;
    Paar rec_e = paar[atomic_load(&paar_i)];
    if (rec_e.t != rec_a.t && rec_e.s > rec_a.s) k.rate = (float)((double)(rec_e.s - rec_a.s) * 1e6 / (double)(rec_e.t - rec_a.t));
    schreibe(&k, sizeof k);
}

// Unterbefehl A: Ausschnitt aus einer Rohdatei als Spalten
static int ausschnitt(int argc, char **argv) {
    if (argc < 7) return 2;
    FILE *f = fopen(argv[2], "rb");
    if (!f) return 3;
    int n = atoi(argv[3]);
    long von = atol(argv[4]), bis = atol(argv[5]);
    long breite = atol(argv[6]);
    if (fseek(f, 0, SEEK_END)) return 3;
    long gesamt = ftell(f) / 2 / n;
    if (bis > gesamt) bis = gesamt;
    if (von < 0) von = 0;
    long scans = bis - von;
    if (scans < 1) { fclose(f); return 4; }
    if (breite > scans) breite = scans;
    uint16_t *aus = malloc((size_t)n * (size_t)breite * 4);
    uint16_t *puf = malloc(1 << 20);
    if (!aus || !puf) return 5;
    for (long j = 0; j < n * breite * 2; j += 2) { aus[j] = 0xFFFF; aus[j + 1] = 0; }
    fseek(f, von * 2 * n, SEEK_SET);
    long gel = 0;
    while (gel < scans) {
        long m = (1 << 19) / n;
        if (m > scans - gel) m = scans - gel;
        if (fread(puf, 2, (size_t)(m * n), f) != (size_t)(m * n)) break;
        for (long s = 0; s < m; s++) {
            long sp = (gel + s) * breite / scans;
            for (int j = 0; j < n; j++) {
                uint16_t v = puf[s * n + j];
                uint16_t *z = aus + (j * breite + sp) * 2;
                if (v < z[0]) z[0] = v;
                if (v > z[1]) z[1] = v;
            }
        }
        gel += m;
    }
    fclose(f);
    int32_t kopf[3] = {n, (int32_t)breite, (int32_t)gesamt};
    fwrite(kopf, 4, 3, stdout);
    fwrite(aus, 2, (size_t)n * (size_t)breite * 2, stdout);
    return 0;
}

int main(int argc, char **argv) {
    if (argc > 1 && argv[1][0] == 'A') return ausschnitt(argc, argv);
    signal(SIGPIPE, SIG_IGN);
    int fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (fd < 0) { perror("/dev/mem"); return 1; }
    p = mmap(NULL, 0x210000, PROT_READ | PROT_WRITE, MAP_SHARED, fd, PERI);
    if (p == MAP_FAILED) { perror("mmap"); return 1; }
    ring = calloc(RING, sizeof(uint16_t));
    spalten = malloc((size_t)MAXK * 4000 * 4);
    if (!ring || !spalten) return 1;
    uint32_t alt_clk = p[SPI_CLK], alt_cs = p[SPI_CS];
    k_code[0] = 1;
    atomic_store(&neu_konfig, 1);
    pthread_t th;
    pthread_create(&th, NULL, messen, NULL);
    char z[512];
    while (atomic_load(&laufen)) {
        int r = zeile_lesen(z, sizeof z, 200);
        if (r <= 0) continue;
        if (z[0] == 'E') break;
        if (z[0] == 'K') {
            unsigned t;
            int n, pos = 0, ge;
            if (sscanf(z + 1, "%u %d%n", &t, &n, &pos) == 2 && n >= 1 && n <= MAXK) {
                const char *q = z + 1 + pos;
                uint32_t neu[MAXK];
                int ok = 1;
                for (int i = 0; i < n; i++) {
                    if (sscanf(q, "%u%n", &neu[i], &ge) != 1) ok = 0;
                    q += ge;
                }
                if (ok) {
                    k_teiler = t & ~1u;
                    k_n = n;
                    for (int i = 0; i < n; i++) k_code[i] = neu[i];
                    atomic_store(&neu_konfig, 1);
                    while (atomic_load(&neu_konfig) && atomic_load(&laufen)) usleep(100);
                }
            }
            Kopf_t k;
            kopf_fuellen(&k, 3, (uint32_t)atomic_load(&aktiv_n), 0);
            schreibe(&k, sizeof k);
        } else if (z[0] == 'F') {
            long vor, nach;
            int art, quelle, pegel, stg, warte;
            unsigned b;
            if (sscanf(z + 1, "%ld %ld %d %d %d %d %d %u", &vor, &nach, &art, &quelle, &pegel, &stg, &warte, &b) == 8)
                frame(vor, nach, art, quelle, pegel, stg, warte, b);
        } else if (z[0] == 'R') {
            char pfad[400];
            double d;
            if (sscanf(z + 1, "%399s %lf", pfad, &d) == 2) aufzeichnen(pfad, d);
        }
    }
    atomic_store(&laufen, 0);
    pthread_join(th, NULL);
    p[SPI_CLK] = alt_clk;
    p[SPI_CS] = alt_cs;
    p[G_SET0] = CE0;
    return 0;
}
