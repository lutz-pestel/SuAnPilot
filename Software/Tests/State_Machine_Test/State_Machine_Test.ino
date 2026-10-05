
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

// Einfügen der Mittelwert-Klasse für das glätten der Frequenz-Werte
#include "average.cpp"  
Average av; 
// Einfügen der Tastenbafrage
#include "check_keys.h"
// Einfügen des Fußzeilen Kontextmenues
#include "key_context.h"

#define RF300_PIN         2          
#define RudderAngle_PWM   3
#define PortLED           4
#define StbLED            5
#define Status            6
#define Buzzer            7
#define HallSensor_PIN    A0
#define KeyPad_PIN        A1

#define red               2
#define yellow            1
#define white             4
#define blue              3
#define red_long          20
#define yellow_long       10
#define white_long        40
#define blue_long         30

//Constanten für Frequenzanalyse des RF300-Ruderlagen-Signals
const int f_min=1700;
const int f_max=3200;
const int offset_angle=0;

//global vars
int ontime;
int offtime;
int period;
float freq;
float freq_av;
int pwm_val;
int rudder_angle;
int contrast=160;
int key=0;
int state=0; //Anfangszustand der State Maschin

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
  Serial.begin(9600);
  u8g2.begin();
  u8g2.setContrast(contrast);
  //Fonts: https://arduino-projekte.info/schriftarten-fuer-oled-display/
  u8g2.setFont(u8g2_font_helvB12_tr);
  //u8g2.setFont(u8g2_font_profont10_tr);
  u8g2.drawStr(5,20,"RF300"); 
  u8g2.drawStr(5,35,"Interface");  
  u8g2.sendBuffer();          
  delay(3000);  
}

void loop(void) 
{  
  
   state=state_machine(state);
   sprungverteiler(state);
}


int state_machine(int state)
{
  //Tastatur abfragen
  key=check_keys(KeyPad_PIN, Buzzer);  
  if (key>0)
  {
    Serial.print("old State:");Serial.println(state);
    Serial.print("Key:");Serial.println(key);
  }
  //Bestimmte Keys ändern den State
  switch (state) 
  {
  case 0:
    // Starting Point
    if (key==red) state=10;
    if (key==yellow) state=20; 
    if (key==white) state=30;
    Serial.print("New State:");Serial.println(state);
    break;
  case 10:
    // state 10
    //if (key==red) state=10;
    if (key==yellow) state=20; 
    if (key==white) state=30;
    if (key==blue) state=0;
    Serial.print("New State:");Serial.println(state);
    break;
  case 20:
    // state 20
    if (key==red) state=10;
    //if (key==yellow) state=20; 
    if (key==white) state=30;
    if (key==blue) state=0;
    Serial.print("New State:");Serial.println(state);
    break;
  case 30:
    // state 30
    if (key==red) state=10;
    if (key==yellow) state=20; 
    //if (key==white) state=30;
    if (key==blue) state=0;
    Serial.print("New State:");Serial.println(state);
    break;
  default:
    // Error state
    Serial.println("Error!");
    break;
  }
  return state;
}


void sprungverteiler(int state)
{
 switch (state) 
  {
  case 0:
    // Starting Point
    show_state(state);
    break;
  case 10:
    // state 10
    show_state(state);
    break;
  case 20:
    // state 20
    show_state(state);
    break;
  case 30:
    // state 30
    show_state(state);
    break;
  default:
    // Error state
    Serial.println("Error!");
    break;
  }
}

void show_state(int state)
{
  u8g2.clearBuffer();         
  u8g2.setFont(u8g2_font_helvR08_tf);
  u8g2.setCursor(10, 10);
  u8g2.print("State: ");
  u8g2.print(state);
  u8g2.sendBuffer(); 
}
