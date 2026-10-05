//using u8g2_font_open_iconic_arrow_1x_t
#define settings      91
#define arrow_down    64
#define arrow_up      67
#define arrow_left    65
#define arrow_right   67
#define up            79
#define down          76
#define angle_down    80
#define angle_up      83
#define down_to       84
#define up_to         85
#define back          91
#define details       88

//using u8g2_font_profont10_tn
#define one           49
#define two           50
#define three         51
#define four          52
#define plus          42
#define minus         44

//Normaler Betriebsmodus: Anzeige des Ruderwinkels
void state_main_fuction(void)
{
  if (RF300_is_valid) //Nur wenn vorher eine gültige Frequenz gemessen wurde
  {
    //grüne LED ansteuern wenn Kurs nach Steuerbord
    if (rudder_angle>3) digitalWrite(StbLED,HIGH);
    else digitalWrite(StbLED,LOW);
    //rote LED ansteuern wenn Kurs nach Backbord
    if (rudder_angle<-3) digitalWrite(PortLED,HIGH);
    else digitalWrite(PortLED,LOW);
    //Informationen auf Nokia 5110 Display ausgeben
    u8g2.clearBuffer(); 
    //Ausgabe Überschrift - Ruder Winkel        
    //u8g2.setFont(u8g2_font_helvR08_tr);
    u8g2.setFont(u8g2_font_profont10_tr);
    u8g2.setCursor(5, 10);
    u8g2.print(F("Rudder Angle"));
    u8g2.setCursor(70, 10);
    //Ausgabe des Ruder-Winkels als Zahl
    u8g2.setFont(u8g2_font_helvB14_tn);
    u8g2.setCursor(10, 26);
    u8g2.print(rudder_angle);
    //°-Symbol ausgeben
    //u8g2.print(F("\xb0"));
    //Ausgabe der RF300-Frequenz
    //u8g2.setFont(u8g2_font_trixel_square_tf);
    u8g2.setFont(u8g2_font_profont10_tr);
    u8g2.setCursor(0, 36);
    u8g2.print(F("f="));
    int f=round(freq_av);
    u8g2.print(round(f));
    u8g2.setCursor(40, 36);
    if (f>f_max)
    {
      u8g2.print(F("f>f_max!"));
    }
    if (f<f_min)
    {
      u8g2.print(F("f<f_min!"));
    }
    //u8g2.sendBuffer(); 
  }else //RF300 liefert kein gültiges Sinal
  {
    u8g2.clearBuffer();         
    u8g2.setFont(u8g2_font_helvB10_tr);
    u8g2.setCursor(0, 20);
    u8g2.print(F("RF300 Error"));
    u8g2.setFont(u8g2_font_profont10_tr);
    u8g2.setCursor(0, 35);
    u8g2.print(F("Missing Frequency"));
    //u8g2.sendBuffer(); 
  }
  //file:///D:/Users/SuAn/Desktop/fntgrpiconic%20%C2%B7%20olikraus-u8g2%20Wiki%20%C2%B7%20GitHub.pdf
  u8g2.setFont(u8g2_font_open_iconic_arrow_1x_t);
  draw_key_context(0,0,down_to,arrow_down,false);
  u8g2.sendBuffer();
}


  
//Setzen des Winkels für den maximalen Ruderausschlag
void state_set_angle_max_function(void)
{
  u8g2.clearBuffer();         
  u8g2.setFont(u8g2_font_profont10_tr);
  u8g2.setCursor(0, 6);
  u8g2.print(F("Edit max rudder"));
  u8g2.setCursor(0, 14);
  u8g2.print(F("angle:"));
  u8g2.drawBox(5,16,40,16);
  u8g2.setFont(u8g2_font_helvB14_tn);
  u8g2.setCursor(10, 30);
  u8g2.print(angle_max);
  //file:///D:/Users/SuAn/Desktop/fntgrpiconic%20%C2%B7%20olikraus-u8g2%20Wiki%20%C2%B7%20GitHub.pdf
  u8g2.setFont(u8g2_font_open_iconic_arrow_1x_t);
  draw_key_context(up,down,arrow_up,arrow_down,false);
  u8g2.sendBuffer();
}

//Setzen des Winkels für den minimalen Ruderausschlag
void state_set_angle_min_function(void)
{
  u8g2.clearBuffer();         
  u8g2.setFont(u8g2_font_profont10_tr);
  u8g2.setCursor(0, 6);
  u8g2.print(F("Edit min rudder"));
  u8g2.setCursor(0, 14);
  u8g2.print(F("angle:"));
  u8g2.drawBox(5,16,40,16);
  u8g2.setFont(u8g2_font_helvB14_tn);
  u8g2.setCursor(10, 30);
  u8g2.print(angle_min);
  //file:///D:/Users/SuAn/Desktop/fntgrpiconic%20%C2%B7%20olikraus-u8g2%20Wiki%20%C2%B7%20GitHub.pdf
  u8g2.setFont(u8g2_font_open_iconic_arrow_1x_t);
  draw_key_context(up,down,arrow_up,arrow_down,false);
  u8g2.sendBuffer();
}    

//Setzen der Frequenz für den maximalen Ruderausschlag
void state_set_f_max_function(void)
{
  u8g2.clearBuffer();         
  u8g2.setFont(u8g2_font_profont10_tr);
  u8g2.setCursor(0, 6);
  u8g2.print(F("Max frequency"));
  u8g2.setCursor(0, 16);
  u8g2.print(F("RF300 f:"));
  u8g2.print(round(freq_av));
  u8g2.setCursor(0, 24);
  u8g2.print(F("  max f:"));
  u8g2.print(f_max);
  u8g2.setCursor(0, 35);
  u8g2.print(F("Set RF300 to max"));
  //file:///D:/Users/SuAn/Desktop/fntgrpiconic%20%C2%B7%20olikraus-u8g2%20Wiki%20%C2%B7%20GitHub.pdf
  //u8g2.setFont(u8g2_font_profont10_tn);
  u8g2.setFont(u8g2_font_open_iconic_arrow_1x_t);
  draw_key_context(angle_down,0,arrow_up,arrow_down,false);
  u8g2.sendBuffer();
}

//Setzen der Frequenz für Ruder Mittschiffs
void state_set_f_mid_function(void)
{
  u8g2.clearBuffer();         
  u8g2.setFont(u8g2_font_profont10_tr);
  u8g2.setCursor(0, 6);
  u8g2.print(F("Mid frequency"));
  u8g2.setCursor(0, 16);
  u8g2.print(F("RF300 f:"));
  u8g2.print(round(freq_av));
  u8g2.setCursor(0, 24);
  u8g2.print(F("  mid f:"));
  u8g2.print(f_mid);
  u8g2.setCursor(0, 35);
  u8g2.print(F("Set RF300 to mid"));
  //file:///D:/Users/SuAn/Desktop/fntgrpiconic%20%C2%B7%20olikraus-u8g2%20Wiki%20%C2%B7%20GitHub.pdf
  //u8g2.setFont(u8g2_font_profont10_tn);
  u8g2.setFont(u8g2_font_open_iconic_arrow_1x_t);
  draw_key_context(angle_down,0,arrow_up,arrow_down,false);
  u8g2.sendBuffer();
}

//Setzen der Frequenz für den minimalen Ruderausschlag
void state_set_f_min_function(void)
{
  u8g2.clearBuffer();         
  u8g2.setFont(u8g2_font_profont10_tr);
  u8g2.setCursor(0, 6);
  u8g2.print(F("Min frequency"));
  u8g2.setCursor(0, 16);
  u8g2.print(F("RF300 f:"));
  u8g2.print(round(freq_av));
  u8g2.setCursor(0, 24);
  u8g2.print(F("  min f:"));
  u8g2.print(f_min);
  u8g2.setCursor(0, 35);
  u8g2.print(F("Set RF300 to min"));
  //file:///D:/Users/SuAn/Desktop/fntgrpiconic%20%C2%B7%20olikraus-u8g2%20Wiki%20%C2%B7%20GitHub.pdf
  //u8g2.setFont(u8g2_font_profont10_tn);
  u8g2.setFont(u8g2_font_open_iconic_arrow_1x_t);
  draw_key_context(angle_down,0,arrow_up,arrow_down,false);
  u8g2.sendBuffer();
}

//Anzeige der Eingestellten Parameter
void state_show_para_function(void)
{
  //Informationen auf Nokia 5110 Display ausgeben
  u8g2.clearBuffer();     
  u8g2.setFont(u8g2_font_profont10_tr);
  u8g2.setCursor(0, 7);
  u8g2.print(F("RF300 Details:"));
  u8g2.setCursor(0, 15);
  u8g2.print(F("t:"));u8g2.print(ontime);
  u8g2.print(F("/"));u8g2.print(offtime);
   u8g2.setCursor(0, 23);
  u8g2.print(F("f:"));
  int f=round(freq_av);
  u8g2.print(round(f));
  u8g2.print(F("("));
  u8g2.print(f_min);
  u8g2.print(F("-"));
  u8g2.print(f_max);
  u8g2.print(F(")"));
  u8g2.setCursor(0, 30);
  u8g2.print(F("angle:"));
  u8g2.print(rudder_angle);
  u8g2.print(F("("));
  u8g2.print(angle_min);
  u8g2.print(F("-"));
  u8g2.print(angle_max);
  u8g2.print(F(")"));
  u8g2.setCursor(0, 37);
  u8g2.print(F("pwm:"));
  u8g2.print(pwm_val);
  //file:///D:/Users/SuAn/Desktop/fntgrpiconic%20%C2%B7%20olikraus-u8g2%20Wiki%20%C2%B7%20GitHub.pdf
  u8g2.setFont(u8g2_font_open_iconic_arrow_1x_t);
  draw_key_context(0,0,arrow_up,arrow_down,false);
  u8g2.sendBuffer();
}

void state_error_function(String source)
{ 
  u8g2.clearBuffer();         
  u8g2.setFont(u8g2_font_profont10_tr);
  u8g2.setCursor(10, 6);
  u8g2.print(F("State-Error: "));
  u8g2.setCursor(0, 20);
  u8g2.print(state);
  u8g2.print(F(": not found in "));
  u8g2.setCursor(0, 30);
  u8g2.print(source);
  //file:///D:/Users/SuAn/Desktop/fntgrpiconic%20%C2%B7%20olikraus-u8g2%20Wiki%20%C2%B7%20GitHub.pdf
  u8g2.setFont(u8g2_font_open_iconic_arrow_1x_t);
  draw_key_context(0,0,0,257,false);
  u8g2.sendBuffer();
}  

    
