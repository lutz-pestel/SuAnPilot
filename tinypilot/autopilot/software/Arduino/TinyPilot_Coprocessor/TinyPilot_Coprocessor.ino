/***********************************************************************************************
 *       Test für Serielle Eingabe vom Ruderwinkel                                          ****
 *       Mixed-Mode Darstellung im LCD Displa                                               ****
 *       Es wird sowohl mit u8g2.print(), als auch mit u8g2log.print() gearbeitet           ****                     
 *       Wenn u8g2log.print()verwendet wird, dann scrolled der Bildschirm nach unten        ****
 *       Die Ausgabe erfolt in der u8g2.firstPage()-u8g2.nextPage()-Schleife.               ****
 *       Vor der Ausgabe in dieser Schleife, wird u8g2log.print vorbereitet                 ****
 *       und dann schließlich mit u8g2.drawLog(0, 23, u8g2log) ausgegeben.                  ****
 *       Der Bereich für .drawLog() beginnt erst unterhalb der Y-Position 23.               ****
 *       Die Anzahl der Zeilen in diesem Bereich errechnet sich aus der Höhe des LCD (128)  ****
 *       minus des Begins auf y=23 geteilt durch die Höhe des Fonts (u8g2_font_5x7_tr)      ****
 *       (128-23)/7+1=15. Es lassen sich damit 15 Zeilen scrollen.                          ****
 *       Die +1 ergibt sich daraus, dass der Text oberhalb der y-Pos. gezeichnet wird.      ****
 *       Die Anzahl der Zeichen/Zeile errechnet sich aus der Breite des LCD (64) geteilt    ****
 *       durch die Breite eines Zeichens im Font (5) 64/5=12.8 Zeichen / Zeile.             ****
 *                                                                                          ****
 *       Die Lesbarkeit des LCD verbessert sich wenn .setContrast(160) im setup() erfolt.   ****
 ***********************************************************************************************/

/***********************************************************************************************
 ******  Begin der Deklerationen für ST7565_JLX12864 LCD                       *****************
 ***********************************************************************************************/
#include <Arduino.h>
#include <U8g2lib.h>

#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif

//Use U8G2_R3 für gedrehtes Display
U8G2_ST7565_JLX12864_1_4W_HW_SPI u8g2(U8G2_R3, /* cs=*/ 10, /* dc=*/ 9, /* reset=*/ 8);

/***********************************************************************************************
 ******   Ende der Deklerationen für ST7565_JLX12864 LCD                       *****************
 ***********************************************************************************************/

/***********************************************************************************************
 ******   Begin Einfügen der INCLUDES                                          *****************
 ***********************************************************************************************/
//Einfügen der Routine zum lesen der seriellen Schnittstelle
#include "dienst.h"
#include "NMEA_parsing.h"
#include "serial_read.h"
//Definition für Modul check_keys.h
#define Buzzer 7
#define KeyPad_PIN A7
#include "check_keys.h"
//Definition für Modul send_key_to_RPi.h
#define KB_Auto       2
#define KB_Select     3
#define KB_Menu       4
#define KB_Port_1     5
#define KB_Tack       A0
#define KB_Stb_10     A1
#define KB_Port_10    A2
#define KB_Stb_1      A3
#define AUX           6
#include "send_key_to_RPI.h"
//More Modul-Includes
#include "key_context.h"
#include "states.h"
#include "state_machine.h"
int state; 
/***********************************************************************************************
 ******    Ende Einfügen der INCLUDES                                          *****************
 ***********************************************************************************************/


void setup(void) {
  //Setting Up ST7565_JLX12864 LCD 
  u8g2.begin(); //
  u8g2.setContrast(160); 
  Serial.begin(9600); 
  //Setup für Modul check_keys.h
  pinMode(Buzzer, OUTPUT);
  //Setup für Modul send_key_to_RPi.h
  pinMode(KB_Auto, OUTPUT);
  pinMode(KB_Select, OUTPUT);
  pinMode(KB_Menu, OUTPUT);
  pinMode(KB_Port_1, OUTPUT);
  pinMode(KB_Tack, OUTPUT);
  pinMode(KB_Stb_10, OUTPUT);
  pinMode(KB_Port_10, OUTPUT);
  pinMode(KB_Stb_1, OUTPUT);
  pinMode(AUX, OUTPUT);
  //Anueige der Start-Page
  show_StartPage();
  state=rsa;  //Status zur Anzeige des Ruderwinkels
  delay(5000);
}

unsigned long t = 0;

// print the output of millis() to the terminal every second
void loop(void) {
  
  if (!serial_read(100)) RSA=180;
  state=state_machine(state);
  //Serial.print(F("State:"));Serial.println(state);
  sprungverteiler(state);
 
}
