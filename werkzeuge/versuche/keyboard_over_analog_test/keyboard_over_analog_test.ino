
#include <Arduino.h>
#include <U8g2lib.h>
// Einfügen der Mittelwert-Klasse für das glätten der Frequenz-Werte
#include "average.cpp"  
Average av; 

#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif

#define RF300_PIN         2          
#define RudderAngle_PWM   3
#define PortLED           4
#define StbLED            5
#define Status            6
#define Buzzer            7
#define HallSensor_PIN    A0
#define KeyPad_PIN        A1

//Nokia 5110 - Display spezifizieren
U8G2_PCD8544_84X48_F_4W_SW_SPI u8g2(U8G2_R0, /* clock=*/ 13, /* data=*/ 11, /* cs=*/ 10, /* dc=*/ 9, /* reset=*/ 8);  // Nokia 5110 Display
//U8G2_PCD8544_84X48_F_4W_HW_SPI u8g2(U8G2_R0, /* cs=*/ 10, /* dc=*/ 9, /* reset=*/ 8); 		// Nokia 5110 Display

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
  u8g2.setFont(u8g2_font_helvR08_tf);
  u8g2.drawStr(5,10,"Keyboard Test"); 
  u8g2.sendBuffer();          
  LCDshow(5,20,"Line 2:",false,2,false); 
  LCDshow(5,30,"Line 3:",false,3,false); 
  LCDshow(5,40,"Line 4:",false,4,false); 
  delay(1000);
  //u8g2.clear();
  LCDshow(0,10,"Press a Key:",false,1,true); 
}

void loop(void) 
{  
   key=check_keys();
   if (key>0)Serial.println(key);
   
}

/******************************************************************************
 Funktion zum Erfassen von Tastenbetätigungen
 --------------------------------------------

 Es werden sowohl lange, als auch kurze Tastenbetätigungen registriert
 Übergabeparameter: keine
 Rückgabeparameter: Tasten-Code
 Tastenanordnung: rot=key2, yellow=key1, white=key4, blue=key3
 Tasten-Code:
 rot    kurz=2, lang=20
 yellow kurz=1, lang=10
 white  kurz=4, lang=40
 blue   kurz=3, lang=30

 Für den Tastenklick wird ein Buzzer verwendet. Dieser sollte an einem Pin 
 mit dem Namen Buzzer angeschlossen sein.

 Der Zustand des Buzzers wird gepuffert.

******************************************************************************/

unsigned int check_keys(void)
{
  unsigned int key_value=0;                     //Analoger Wert von KeyPad_PIN
  static unsigned long pressed_time  = 0;       //Zeitpunkt des Tastendrucks
  static unsigned long pressed_duration  = 0;   //Dauer des Tastendrucks
  static unsigned int key = 0;                  //Code für gedrückte Taste
  const unsigned int long_press=1000;           //Indicator für langen Tastendruck
  static boolean key_pressed_before = false;    //Merker für Tastendruck
  static boolean long_pressed_before = false;   //Merker für langen Tastendruck
  boolean Buzzer_Merker;                        //Merker fürk Zustand des Buzzers

  Buzzer_Merker = digitalRead(Buzzer);  //Zustand des Buzzers vor dem Aufruf merken
  key_value=analogRead(KeyPad_PIN);     //Analoge Tastaturschnittstelle abfragen
  if (key_value>200) 
  {
    if (!key_pressed_before) //wenn vorher noch keine Taste gedrückt wurde
    {
      //key wurde gerade gedrückt
      pressed_time=millis(); //Zeitpunkt des Tastendrucks merken
      key_pressed_before = true;  //Merken, dass Taste gedrückt ist
      //Tasten Click
      digitalWrite(Buzzer,HIGH);
      delay(10);
      digitalWrite(Buzzer,LOW);
    }else 
    {
      //key war vorher auch schon gedrückt : Zeit wird länger
      pressed_duration = millis()-pressed_time;
      LCDshow(0,20,"Duration:",false,pressed_duration,false);  
    }
    //no key      : key_value=0
    //key 2 red   : key_value=846
    //key 1 yellow: key_value=699
    //key 4 white : key_value=513
    //key 3 blue  : key_value=372
    
    if (key_value>200 and key_value<442) key=3;
    if (key_value>442 and key_value<606) key=4;
    if (key_value>606 and key_value<772) key=1;
    if (key_value>772)                   key=2;
    
    if (pressed_duration>long_press )
    {
      key*=10; //Key-Code für langen Tastendruck ist 10*kurzer Tastendruck
      if (!long_pressed_before)
      {
        digitalWrite(Buzzer,HIGH);
        delay(100);
        digitalWrite(Buzzer,LOW);
        delay(50);
        digitalWrite(Buzzer,HIGH);
        delay(100);
        digitalWrite(Buzzer,LOW);
        long_pressed_before = true;
      } 
    }
    LCDshow(0,10,"Value:",false,key_value,true); //Ausgabe kev_value auf LCD ohne NL, aber mit Clear Screen
    LCDshow(0,30,"Key:",false,key,false); //Ausgabe kev_value auf LCD ohne NL, aber mit Clear Screen
  }
  else // key_value<200 ==> keine Taste gedrückt
  {
    if (key_pressed_before) //wenn vorher noch keine Taste gedrückt wurde
    {
      key_pressed_before = false;
      long_pressed_before = false;
      pressed_duration = 0;
      digitalWrite(Buzzer,Buzzer_Merker); //alten Buzzer Zustand wieder herstellen
      return key;
    }
  }
  digitalWrite(Buzzer,Buzzer_Merker); //alten Buzzer Zustand wieder herstellen
  return 0;
}


void LCDshow(byte x, byte y, String lable, boolean nl, int value, boolean cl)
{
  if (cl) u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_helvR08_tf);         
  u8g2.setCursor(x,y);
  u8g2.print(lable);
  if (nl) u8g2.setCursor(x,y+10);
  u8g2.print(value);
  //u8g2.setFont(u8g2_font_5x7_tf);
  //u8g2.setFont(u8g2_font_chikita_tf);
  u8g2.setFont(u8g2_font_trixel_square_tf);
  //u8g2.setFont(u8g2_font_p01type_tf);
  u8g2.setCursor(0,46);
  u8g2.print(" + | - | i |...");
  u8g2.sendBuffer(); 
}
