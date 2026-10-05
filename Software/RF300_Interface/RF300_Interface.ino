//Check Port
//Make sure that you have removed the jumper on RX


#include <Arduino.h>
#include <U8g2lib.h>

#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif

//Nokia 5110 - Display spezifizieren
U8G2_PCD8544_84X48_F_4W_SW_SPI u8g2(U8G2_R0, /* clock=*/ 13, /* data=*/ 11, /* cs=*/ 10, /* dc=*/ 9, /* reset=*/ 8);  // Nokia 5110 Display
//U8G2_PCD8544_84X48_F_4W_HW_SPI u8g2(U8G2_R0, /* cs=*/ 10, /* dc=*/ 9, /* reset=*/ 8); 		// Nokia 5110 Display

//Definition der Arduino-Pins
#define RF300_PIN         2          
#define RudderAngle_PWM   3
#define PortLED           4
#define StbLED            5
#define Status            6
#define Buzzer            7
#define HallSensor_PIN    A0
#define KeyPad_PIN        A1

//Definition der Tasten nach Farben und Betätigungszeit
#define red               2
#define yellow            1
#define white             4
#define blue              3
#define red_long          20
#define yellow_long       10
#define white_long        40
#define blue_long         30

//Definition der Zustände der State-Machine
#define main              0
#define set_angle_max     11
#define set_angle_min     12
#define set_f_max         21
#define set_f_mid         22
#define set_f_min         23
#define show_para         30

//global vars
int ontime;           //Time in RF300-Signal when Pegel is up
int offtime;          //Tine in RF300-Signal when Pegel is down
int period;           //Periodenlänge einer Schwingung im RF300-Signal (up+down)
float freq;           //calculated frequency of the RF300-Signal
float freq_av;        //frequeny nach glätten durch gleitenden Mittelwert
unsigned int pwm_val;          //Wert für PWM ausgabe zur Erzeugung einer ruderlagen-proportionalen Spannung
int rudder_angle;     //berechneter Ruderlagenwinkel
boolean RF300_is_valid=false; //zeigt an, ob der RF300 angeschlossen ist und eine Frequenz sendet
int contrast=160;     //Voreinstellung für LCD-Kontrast
int key=0;            //Nummer der betätigten Tasete - 0 = keine Taste
int state=main;       //aktueller State des Systems

//Defaultwerte für Ruder-Parameter 
#define def_angle_max   40   //maximaler Ruderausschlag eine Steuerbord
#define def_angle_min   -40  //maximaler Ruderausschlag andere Backbord
#define def_f_max       3153 //f bei maximalen Ruderausschlag Backbord
#define def_f_mid       2450 //f bei Null Ruderausschlag
#define def_f_min       2157 //f bei maximalen Ruderausschlag Steuerbord

//Ruderparameter werden aus dem EEPROM gelesen
int angle_max=0;      //maximaler Ruderausschlag eine Richtung
int angle_min=0;      //maximaler Ruderausschlag andere Richtung
int f_max=0;          //f bei maximalen Ruderausschlag eine Richtung
int f_mid=0;          //f bei Null Ruderausschlag
int f_min=0;          //f bei maximalen Ruderausschlag andere Richtung

//Definition der EEPROM-Speicherplätze
#define addr_angle_max  10    //EEPROM Addr für maximaler Ruderausschlag eine Richtung
#define addr_angle_min  12    //EEPROM Addr für maximaler Ruderausschlag andere Richtung
#define addr_f_max      14    //EEPROM Addr für f bei maximalen Ruderausschlag eine Richtung
#define addr_f_mid      16    //EEPROM Addr für f bei Null Ruderausschlag
#define addr_f_min      18    //EEPROM Addr für f bei maximalen Ruderausschlag andere Richtung

// Einfügen der Funktionen für Lesen und Schreiben von Integer Werten in den EEPROM
#include "eeprom_int.h"
// Einfügen des Fußzeilen Kontextmenues
#include "key_context.h"
// Einfügen der Tastenbafrage
#include "check_keys.h"
//Routinen für RF300 f-U-Umwandlung
#include "RF300.h"
// Einfügen der State-Funktionen
#include "states.h"
// Einfügen der State Maschine und des Sprungverteilers
#include "state_machine.h"
// Einfügen der NMEA-Datenaufbereitung für Ruderwinkelausgabe
#include "nmea.h"

void setup(void) {
  //Average-Klasse initialisieren
  av.init(); //30-Elemente gleitender Mittelwert
  // Input Pins
  pinMode(RF300_PIN, INPUT);
  pinMode(HallSensor_PIN, INPUT);
  pinMode(KeyPad_PIN, INPUT);
  // Output Pins
  pinMode(RudderAngle_PWM, OUTPUT);
  pinMode(PortLED, OUTPUT);
  pinMode(StbLED, OUTPUT);
  pinMode(Status, OUTPUT);
  pinMode(Buzzer, OUTPUT);
  
  
  // Serielle Schnittstelle starten
  Serial.begin(4800);
  u8g2.begin();
  u8g2.setContrast(contrast);
  //Fonts: https://arduino-projekte.info/schriftarten-fuer-oled-display/
  u8g2.setFont(u8g2_font_helvB12_tr);
  //u8g2.setFont(u8g2_font_profont10_tr);
  u8g2.drawStr(5,20,"RF300"); 
  u8g2.drawStr(5,35,"Interface");  
  u8g2.sendBuffer();          

  //Default-Werte der Ruder Parameter in den EEPROM laden
  //>>>Nur für Testzwecke<<<
  //write_defaul_rudder_parameter_to_EEPROM();
  //Ruderparameter aus dem EEPROM in die Variablen laden
  read_rudder_parameter_from_EEPROM();
  delay(500); 
}

//Hauptschleife
void loop(void) 
{  
   RF300_is_valid=read_RF300();   //Frequenz von RF300 in Spannung und Winkel wandeln
   test_max_rudder();             //Blinkt Status LED, wenn der Ruderwinkel>max
   send_RSA_sentence();           //Ruderlagen NMEA-RSA-Datensatz über serielle Schnittstelle senden
   state=state_machine(state);    //State in Abängigkeit von Tasteneingaben ändern
   sprungverteiler(state);        //Funktionen in Abhängigkeit von State aufrufen 
}
