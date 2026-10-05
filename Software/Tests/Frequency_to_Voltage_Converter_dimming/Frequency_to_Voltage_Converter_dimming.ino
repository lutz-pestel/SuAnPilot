
//Pins
const int pwm_out = 6;
const int freq_in = 2;

// Constanten für Ruderendlagen
//const int f_min=2500;
//const int f_center=2700;
//const int f_max=3990;
const int f_min=2500;
const int f_center=3245;
const int f_max=3990;
const int offset_angle=0;

//global vars
const int sample_size=1;  //Anzahl der Messwerte zur Bestimmung der Frequentz
long ontime;
long offtime;
float period;
long freq;
int pwm_val;
int angle;
float volt;
//var für Blinken falls keine Eingangsfrequenz
unsigned long currentMillis = millis();
unsigned long previousMillis;


// the setup function runs once when you press reset or power the board
void setup() {
  Serial.begin(9600);
  pinMode(pwm_out, OUTPUT);
  pinMode(freq_in, INPUT);
  Serial.println("Start");
  delay(100);
}

void loop()  
{
   //Erste sample holen
   ontime = pulseIn(freq_in,HIGH);  //Lesen der Länge eines Pulses für HIGH
   //Serial.println(ontime);
   //RF300 sended pulsbreiten moduliertes Signal = ontime-Dauer ist annähernd konstant
   offtime = pulseIn(freq_in,LOW);  //Lesen der Länge eines Pulses für LOW
   //Wenn kein Frequentzinput=>Fehlermeldung
   if ((offtime>0))
   {
     //Weitere Sample holen
     for (int i=1;i<sample_size;i++)
     {
        //ontime += pulseIn(freq_in,HIGH);
        ontime += 122; //RF300 sended pulsbreiten moduliertes Signal = ontime-Dauer ist annähernd konstant
        offtime += pulseIn(freq_in,LOW);
     }
     ontime=ontime/sample_size*1.0;       //Mittelwert bestimmen
     offtime=offtime/sample_size*1.0;     //Mittelwert bestimmen
     period = ontime+offtime;
     freq = 1000000/period;
     if (freq<f_center)
     {
        pwm_val = map(freq, f_min, f_center, 0, 127);  
        angle = map(freq, f_min, f_center, -30, 0);
     }
     else //freq>=f_cenetr
     {
        pwm_val = map(freq, f_center, f_max, 128, 255);
        angle = map(freq, f_center, f_max, 0, 30);
     }
     volt = map(pwm_val, 0,255, 0, 500)/100.0;
     Serial.print(ontime);
     Serial.print(" : ");
     Serial.print(offtime);
     Serial.print(" > ");
     Serial.print(freq);
     Serial.print(" - ");
     Serial.print(" Frequency: ");
     Serial.print (freq);
     Serial.print("Hz, PWM out: ");
     Serial.print(pwm_val);
     Serial.print(", Votage: ");
     Serial.print(volt);
     Serial.print("V, Angle: ");
     Serial.println(angle);
     //Frequenzproportionale Spannung ausgeben
     analogWrite(pwm_out, pwm_val);
   }
   else //((ontime>0) and (offtime>0))
   {
      Serial.println("No frequency detected");
   }  
}
