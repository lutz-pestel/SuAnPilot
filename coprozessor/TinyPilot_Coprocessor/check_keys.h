/******************************************************************************
 Funktion zum Erfassen von Tastenbetätigungen
 --------------------------------------------
  Vorbereitung im Hauptprogramm:
 - Im Deklarationsteil: #define Buzzer 2
                        #define KeyPad_PIN A0
                        #include "check_keys.h"
 
 Es werden sowohl lange, als auch kurze Tastenbetätigungen registriert
 Übergabeparameter: KeyPad_PIN: Der Anschluss-Pin des Buzzers
                    Buzzer: Der Anschluss-Pin des Buzzers     
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

 Aufruf:
 

******************************************************************************/

unsigned int check_keys()
{
  unsigned int key_value=0;                     //Analoger Wert von KeyPad_PIN
  static unsigned long pressed_time  = 0;       //Zeitpunkt des Tastendrucks
  static unsigned long pressed_duration  = 0;   //Dauer des Tastendrucks
  static unsigned int key = 0;                  //Code für gedrückte Taste
  const unsigned int long_press=1000;           //Indicator für langen Tastendruck
  static boolean key_pressed_before = false;       //Merker für Tastendruck
  static boolean long_pressed_before = false;      //Merker für langen Tastendruck
  static boolean Buzzer_Merker;                           //Merker fürk Zustand des Buzzers

  Buzzer_Merker = digitalRead(Buzzer);          //Zustand des Buzzers vor dem Aufruf merken
  key_value=analogRead(KeyPad_PIN);             //Analoge Tastaturschnittstelle abfragen
  //Serial.print(F("analogRdead:"));Serial.println(key_value);
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
    }
    //no key      : key_value=0
    //key 2 red   : key_value=846
    //key 1 yellow: key_value=699
    //key 4 white : key_value=513
    //key 3 blue  : key_value=372
    
    if (key_value>200 and key_value<442) key=2;
    if (key_value>442 and key_value<606) key=1;
    if (key_value>606 and key_value<772) key=4;
    if (key_value>772)                   key=3;
    
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
