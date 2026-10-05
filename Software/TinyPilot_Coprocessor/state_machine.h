
#define rsa             10
#define menu1           20
#define menu2           30



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
  if (key>0)
  {
    //Bestimmte Keys ändern den Zustand (state)
    switch (state) 
    {
    //Anzeige im Arbeitszustand - normales Arbeiten
    case rsa: 
      //Serial.print("Menu RSA, state="); Serial.print(state); Serial.print(" key=");Serial.println(key);
      if (key==3) state=menu1; 
      if (key==30) send_puls_to_RPi(KB_Tack); 
      if (key==1) send_puls_to_RPi(KB_Port_1); 
      if (key==10) send_puls_to_RPi(KB_Port_10); 
      if (key==4) send_puls_to_RPi(KB_Stb_1); 
      if (key==40) send_puls_to_RPi(KB_Stb_10); 
      if (key==2) send_puls_to_RPi(KB_Auto);  
      key=0;
      break;
    //Anzeige des Menu1: Hauptmenues
    case menu1:
      //Serial.print("Menu Menu1, state="); Serial.print(state); Serial.print(" key=");Serial.println(key);
      if (key==40) state=rsa; //zurück zum Hauptmode 
      if (key==1) send_puls_to_RPi(KB_Menu); 
      if (key==2) send_puls_to_RPi(KB_Select); 
      if (key==3) send_puls_to_RPi(KB_Auto); 
      if (key==4) send_puls_to_RPi(KB_Tack);
      if (key==10) send_puls_to_RPi(KB_Port_1); 
      if (key==20) send_puls_to_RPi(KB_Stb_1); 
      if (key==30) state=100;//send_puls_to_RPi(KB_Port_1);  
      key=0;
      break;
    //Anzeige des Menu2: Hauptmenues
    case menu2:
      if (key==40) state=rsa; //zurück zum Hauptmode 
     
      key=0;
      break;
    //unerwarteter Zustand
    default:
      // Error state
      show_unknown("state_machine",state);
      if (key==4) state=rsa; //zurück zum Hauptmode 
      break;
    }
  }//if key>0
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
 //Serial.print(F("State:"));Serial.println(state);
 switch (state) 
  {
  case rsa:
    show_RSA();
    break;
  case menu1:
    show_Menu1();
    break;
  case menu2:
    show_Menu2();
    break;
  default:
    // Error state
    show_unknown("Sprungverteiler",state);
    break;
  }
}
