//using u8g2_font_open_iconic_all_1x_t
#define menu          199
#define arrow_down    72
#define arrow_left    80
#define arrow_right   81
#define engage        136

/*
//using u8g2_font_open_iconic_arrow_1x_t
#define settings      91
#define arrow_down    64
#define arrow_up      67
#define arrow_left    65
#define arrow_right   66
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
*/


//Start Page
/********************************************************************
 * Wird am Ende der setup()-Routine aufgerufen
 * und für einige Sekunden angezeigt
 * Danach wir in den RSA-Mode geschaltet
 *******************************************************************/
void show_StartPage()
{
  u8g2.firstPage();
  do {
    u8g2.setFont(u8g2_font_helvB14_tr);
    u8g2.setCursor(6, 30);
    u8g2.print("SuAn");
    u8g2.setCursor(8, 44);
    u8g2.setFont(u8g2_font_helvB08_tr);
    u8g2.print("electronic");
    u8g2.setFont(u8g2_font_helvB08_tr);
    u8g2.setCursor(5, 70);
    u8g2.print("Lutz Pestel"); 
    u8g2.setCursor(20, 85);
    u8g2.print("2021");  
  } while ( u8g2.nextPage() ); 
}

//Normaler Betriebsmodus: Anzeige des Ruderwinkels
/********************************************************************
 * Funktion zur Ausgabe des Ruderwinkels auf das LCD
 * mit Richtungs /Engage / und Menu Tastenfunktion
 * Wichtig: int RSA muß als globale Variable verfügbar sein
 *******************************************************************/
void show_RSA()
{
  byte r=32;         //Radius des Bogens in der Anzeige
  byte xc=64;        //x-Center: X-Wert des Mittelpunktes des Ruderlagers
  byte yc=15;        //y-Center: Y-Wert des Mittelpunktes des Ruderlagers
  int i;             //Laufvariable
  float rad;         //Ruderwinkel im Bogenmaß
  float x;
  float y;           //für Ruderlagen-Graphic
  byte width;        //Breite des LCD in Pixeln
  byte hight;        //Höhe des LCD in Pixeln

  width=u8g2.getWidth();
  hight=u8g2.getHeight();
  xc=width/2;           //Halbe Breite
  yc=hight/2-14;        //Etwas über der halben Höhe
  
  u8g2.firstPage();
  do {
    //u8g2.setFont(u8g2_font_5x7_tr);     // set the font for the terminal window
    u8g2.setFont(u8g2_font_profont10_tr);
    u8g2.setCursor(0, 10);
    u8g2.print(F("Rudder: ")); 
    if(RSA>-90 && RSA<90) //Ist der Ruderwinkel im normalen Bereich?
    {
      u8g2.setCursor(width/2-14, 40); 
      u8g2.setFont(u8g2_font_helvB18_tn);
      u8g2.print(RSA); 
    } else //Der Ruderwinkel ist außerhalb des normalen Bereichs
    {
      u8g2.print(RSA);
      u8g2.setCursor(5, 30); 
      u8g2.setFont(u8g2_font_helvB08_tr);
      u8g2.print("invalid data"); 
    }
    //Bogen zeichnen
    for (i=90; i<270; i++)
    {
        rad=i*PI/180;
        y=-cos(rad)*r*1.5;      //y ist um 50% verlängert
        x=sin(rad)*r;
        u8g2.drawPixel(x+xc,y+yc);
    }
    //Bogenenden mit Gerade verbinden
    u8g2.drawLine(xc-r,yc,xc+r,yc);
    //30 Grad Begrenzungslinien zeichen
    rad=45*PI/180;
    y=cos(rad)*r*1.5+yc;      //y ist um 50% verlängert
    x=sin(rad)*r+xc;
    u8g2.drawLine(xc,yc,x,y);
    rad=-45*PI/180;   
    y=cos(rad)*r*1.5+yc;      //y ist um 50% verlängert
    x=sin(rad)*r+xc;
    u8g2.drawLine(xc,yc,x,y);
    //Ruderschaft zeichnen
    u8g2.drawCircle(xc,yc,3);
    if(RSA>-90 && RSA<90) //Ist der Ruderwinkel im normalen Bereich?
    {
      //Ruderblatt zeichnen
      rad=RSA*PI/180.0;
      y=cos(rad)*(r+5)*1.5+yc;    //y ist um 50% verlängert
      x=sin(rad)*(r+5)+xc;
      u8g2.drawLine(xc+1,yc,x+1,y);
      u8g2.drawLine(xc,yc,x,y);
      u8g2.drawLine(xc-1,yc,x-1,y);
    }
    //D:\Users\SuAn\Cloud\My Computer\Hardware\Displays\fntgrpiconic · olikraus-u8g2 Wiki · GitHub.pdf
    //u8g2.setFont(u8g2_font_profont10_tn);
    u8g2.setFont(u8g2_font_open_iconic_all_1x_t);
    draw_key_context(arrow_left,engage,menu,arrow_right,false);
  } while ( u8g2.nextPage() );
}

//Menu: Auswahl der Kommandos / Tasten für den RPi
/********************************************************************
 * Mit der 4 Tasten Folientastatur können alle 8 Eingaben 
 * Für PyPilot auf dem Raspberry Pi erzeugt werden
 * 
 *******************************************************************/
void show_Menu1()
{
  u8g2.firstPage();
  do {
    u8g2.setFont(u8g2_font_helvB14_tr);
    u8g2.setCursor(0, 15);
    u8g2.print("Menu");   
    u8g2.setFont(u8g2_font_profont10_tr);  
    u8g2.setCursor(10, 25);
    u8g2.print("1: Menu"); 
    u8g2.setCursor(10, 35);
    u8g2.print("2: Select");   
    u8g2.setCursor(10, 45);
    u8g2.print("3: Auto"); 
    u8g2.setCursor(10, 55);
    u8g2.print("4: Tack");
    u8g2.setCursor(10, 65);   
    u8g2.print("10: Port"); 
    u8g2.setCursor(10, 75);
    u8g2.print("20: Stb");   
    u8g2.setCursor(10, 85);
    u8g2.print("30: Reserve"); 
    u8g2.setCursor(10, 95);
    u8g2.print("40: Return");       
   
    //D:\Users\SuAn\Cloud\My Computer\Hardware\Displays\fntgrpiconic · olikraus-u8g2 Wiki · GitHub.pdf
    //u8g2.setFont(u8g2_font_profont10_tn);
    u8g2.setFont(u8g2_font_open_iconic_arrow_1x_t);
    draw_key_context(0,0,0,0,false);
  } while ( u8g2.nextPage() );
}

//Menu2: Noch nicht implementiert
/********************************************************************
 * Mit der 4 Tasten Folientastatur können alle 8 Eingaben 
 * Für PyPilot auf dem Raspberry Pi erzeugt werden
 * 
 *******************************************************************/
void show_Menu2()
{
  u8g2.firstPage();
  do {
    u8g2.setFont(u8g2_font_helvB14_tr);
    u8g2.setCursor(0, 15);
    u8g2.print("Menu 2");       
   
    //D:\Users\SuAn\Cloud\My Computer\Hardware\Displays\fntgrpiconic · olikraus-u8g2 Wiki · GitHub.pdf
    //u8g2.setFont(u8g2_font_profont10_tn);
    u8g2.setFont(u8g2_font_open_iconic_arrow_1x_t);
    draw_key_context(0,0,0,arrow_down,false);
  } while ( u8g2.nextPage() );
}

//Anzeige wenn ein Fehler aufgetreten ist. 
/********************************************************************
 * - unerlaubter Zustand
 * 
 * 
 *******************************************************************/
void show_unknown(String problem, int state)
{
   u8g2.firstPage();
  do {
    u8g2.setFont(u8g2_font_profont10_tr);
    u8g2.setCursor(10, 20);
    u8g2.print(F("ERROR: ")); 
    u8g2.setCursor(0,40); 
    u8g2.print(problem);  
    u8g2.setCursor(0,60); 
    u8g2.print("State: ");
    u8g2.print(state);  
    //D:\Users\SuAn\Cloud\My Computer\Hardware\Displays\fntgrpiconic · olikraus-u8g2 Wiki · GitHub.pdf
    //u8g2.setFont(u8g2_font_profont10_tn);
    u8g2.setFont(u8g2_font_open_iconic_arrow_1x_t);
    draw_key_context(0,0,0,arrow_down,false);
  } while ( u8g2.nextPage() );
}

    
