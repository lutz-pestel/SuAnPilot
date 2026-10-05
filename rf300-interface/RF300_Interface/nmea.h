int nmea0183_checksum(char *nmea_data)
{
    int crc = 0;
    int i;

    // ignore the first $ sign,  no checksum in sentence
    for (i = 1; i < strlen(nmea_data); i ++) { // removed the - 3 because no cksum is present
        crc ^= nmea_data[i];
    }

    return crc;
}

/******************************************************************************
 Funktion zum Aussenden des NMEA-RSA-Datensatzes 
 Es läuft ein Timer, der den RSA-Datensatz nicht bei jedem Aufruf der Funktion
 sendet, sondern immer nur dann, wenn der Teimer abgelaufen ist.
 Die Pause zwischen dem Aussenden der Datensätze ist 2 x period.
 
 RSA - Rudder Sensor Angle
        1   2 3   4 5
        |   | |   | |
 $--RSA,x.x,A,x.x,A*hh<CR><LF>

Field Number:
    Starboard (or single) rudder sensor, "-" means Turn To Port
    Status, A = valid, V = Invalid
    Port rudder sensor
    Status, A = valid, V = Invalid
    Checksum
*******************************************************************************/
void send_RSA_sentence()
{  
  char sentence[40];
  char valid;
  static unsigned long start=millis();
  unsigned long period=100; //Achtung: Periode läuft zweimal ab, um einmal zu senden
  static boolean send=false;
  if (start+period<millis())
  {
    //Periode ist um, Daten senden
    start=millis();
    send=!send;
    if (send)
    { 
      //$--RSA,x.x,A,x.x,A*hh<CR><LF>
      if (RF300_is_valid) valid='A';
      else valid='V';
      sprintf(sentence, "$GPRSA,%d.0,%c,,V", rudder_angle,valid);
      int checksum=nmea0183_checksum(sentence);
      sprintf(sentence, "%s*%02X",sentence,checksum);
      Serial.println(sentence);
    }
  }
}
