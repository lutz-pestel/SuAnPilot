/***********************************************************
 * Funktion zum Auslesen der seriellen Schnittstelle
 * Nur im Abstand von invterval
 * Ist inerval noch nicht um, passiert nichts und die 
 * Funktion kehrt zurück.
 * Wenn interval um ist, aber noch keine Daten eingegangen sind
 * wird der no_data_counter hochgezählt. Dieser bestimmt, ob die 
 * Funkton true oder false zurückgibt.
 * Solange Daten eingehen, ist no_data_counter < 10 und die
 * Funktion gibt true zurück.
 * Gehen keine Daten ein und der no_data_counter ist > 10 gibt die
 * Funktion false zurück (missing Data)
 * 
 * Übergabeparameter: unsigned long inteval: Der Abstand der Abfragen
 * Rückgabewerte:     boolean: true => Daten empfangen, sonst false
 */

boolean serial_read(unsigned long interval)
{
  static String Sentence="";
  static int no_data_counter=0;
  unsigned long currentMillis = millis();
  static unsigned long previousMillis = 0; 
  boolean result=false;
  if (currentMillis - previousMillis >= interval) 
  {
    // save the last time you blinked the LED
    previousMillis = currentMillis;
    
    if (Serial.available())
    {
      no_data_counter=0; //reset no_data_counter
      while(Serial.available())
      {
        char c = Serial.read(); // Receive a single character
        Sentence.concat(c); // Add rhe character to the receive buffer
        if (c=='\n') //Sentence vollständig?
        {
          if ((Sentence.lastIndexOf('$')==0)&&(Sentence.lastIndexOf('*')>5))       //Muss mit $ beginnen und midestens 5 Zeichen lang sein
          {
            //Parsen der NMEA-Daten
            parce(Sentence);
          } //Begin mit $
          Sentence="";  // Clear the Buffer
          result=true;
        } //if (c=='\n') //Sentence vollständig?
      }//while(Serial.available())
    }else//if (Serial.available())
    {
      //keine Daten im seriallen Eingangspuffer
      no_data_counter++;
      if (no_data_counter>10) result=false;
      else result=true;
    }  
  }//if (currentMillis - previousMillis >= interval) 
  return result;
}
