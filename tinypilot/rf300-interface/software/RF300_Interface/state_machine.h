/*
#define main              0
#define set_angle_max     11
#define set_angle_min     12
#define set_f_max         21
#define set_f_mid         22
#define set_f_min         23
#define show_para         30
*/

/***********************************************************
 Funktion zum Steuern der Zustände (Anzeige, Settings usw.)

 Funktion fragt die Tasten ab und ändert den Zustand (State)
 je nach Kontext
 Zusätzlich werden in Abhängikeit vom Zustand noch bestimmte
 Tastenkommandos ausgeführt (z.B. Einstellen von Parametern)
 Übergabeparameter: int state
 Rückgabeparameter: int state
 ***********************************************************/
int state_machine(int state)
{
  //Tastatur abfragen
  int key=check_keys();  
  //Bestimmte Keys ändern den Zustand (state)
  switch (state) 
  {
  //Anzeige im Arbeitszustand - normales Arbeiten
  case main:  
    if (key==blue) state=set_angle_max;     //Vorwärts
    if (key==white) state=show_para ;       //Ende
    break;
  
  //Einstellen des maximalen Ruderwinkels
  case set_angle_max:
    if (key==blue) state=set_angle_min ; //Vorwärts
    if (key==white) state=main ;         //Rückwärts
    if (key==red) 
    {
      angle_max++;
      if (angle_max>60) angle_max=60;
      //Im EEPROM speichern
      writeIntIntoEEPROM(addr_angle_max,angle_max);
    }
    if (key==yellow) 
    {
      angle_max--;
      if (angle_max<10) angle_max=10;
      //Im EEPROM speichern
      writeIntIntoEEPROM(addr_angle_max,angle_max);
    }
    break;

  //Einstellen des minimalen Ruderwinkels
  case set_angle_min:
     if (key==blue) state=set_f_max ;       //Vorwärts
     if (key==white) state=set_angle_max;   //Rückwärts
     if (key==red) 
    {
      angle_min++;
      if (angle_min>-10) angle_min=-10;
      //Im EEPROM speichern
      writeIntIntoEEPROM(addr_angle_min,angle_min);
    }
    if (key==yellow) 
    {
      angle_min--;
      if (angle_min<-60) angle_min=-60;
      //Im EEPROM speichern
      writeIntIntoEEPROM(addr_angle_min,angle_min);
    }
    break;

  //Einstellung der maximalen RF300-Frequenz  
  case set_f_max:
     if (key==blue) state=set_f_mid ;       //Vorwärts
     if (key==white) state=set_angle_min;   //Rückwärts
     if (key==red) 
     {
      f_max=round(freq_av);    //Aktuelle Frequenz als maximale Frequenz speichern
      writeIntIntoEEPROM(addr_f_max,f_max);  //Im EEPROM speichern
     }
    break;

  //Einstellung der mittleren RF300-Frequenz  (Ruder Anschlag)
  case set_f_mid:
    if (key==blue) state=set_f_min;         //Vorwärts
    if (key==white) state=set_f_max;        //Rückwärts
    if (key==red) 
    {
      f_mid=round(freq_av);     //Aktuelle Frequenz als center Frequenz speichern
      writeIntIntoEEPROM(addr_f_mid,f_mid);  //Im EEPROM speichern
    }
    break;

  //Einstellung der minimalen RF300-Frequenz (Ruder Anschlag)
  case set_f_min:
    if (key==blue) state=show_para;         //Vorwärts
    if (key==white) state=set_f_mid;        //Rückwärts
    if (key==red) 
    {
      f_min=round(freq_av);     //Aktuelle Frequenz als minimale Frequenz speichern
      writeIntIntoEEPROM(addr_f_min,f_min);  //Im EEPROM speichern
    }
    break;
  
  case show_para:
    if (key==blue) state=main;              //Vorwärts  
    if (key==white) state=set_f_min;        //Rückwärts  
    break;
 
  default:
    // Error state
    state_error_function("state_machine()");
    break;
  }
  return state;
}

/***********************************************************
 Funktion zum Verzweigen des Programmablaufs in Abhängigkeit
 vom Zustand.
 Für jede Zustand wird die dazugehörige Funktion aufgerufen
 Übergabeparameter: int state
 Rückgabeparameter: int state
 ***********************************************************/
void sprungverteiler(int state)
{
 switch (state) 
  {
  case main:
    state_main_fuction();
    break;
  case set_angle_max:
    state_set_angle_max_function();
    break;
  case set_angle_min:
    state_set_angle_min_function();
    break;
  case set_f_max:
    state_set_f_max_function();
    break;
  case set_f_mid:
    state_set_f_mid_function();
    break;
  case set_f_min:
    state_set_f_min_function();
    break;
  case show_para:
    state_show_para_function();
    break;
  default:
    // Error state
    state_error_function("sprungverteiler()");
    break;
  }
}
