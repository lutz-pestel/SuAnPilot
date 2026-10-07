/**************************************************************************************************
 Funktion zum Zeichnen einer Fußzeile für 4-Tasten-Kontext-Menü
 Am unteren Rand des LCD-Displays wird eine Fußzeile in vier Spalten unterteilt. Dadurch entstehen
 4 Boxen. In jede der Boxen kann ein Symbol gezeichnet werden. Die Codes der Symbole (Icons) werden
 als Parameter übergeben. Die einzelnen Symbole und ihre Codes können hier gefunden werden:
 D:\Users\SuAn\Cloud\My Computer\Hardware\Displays\fntgrpiconic · olikraus-u8g2 Wiki · GitHub.pdf
 Die ganze Fußzeile kann mit dem letzten Parameter invertiert werden.
 Vor dem Aufruf muss ein Icon-Zeichensatz aufgerufen werden: z.B.:
        u8g2.setFont(u8g2_font_open_iconic_all_1x_t);
 Übergabeparameter: vier Integer und ein Boolean, Beispiel:0x0040,0,0x0042,0x005E,false
 Rückgabeparameter: keine

 Achtung:
 Die Funktion verwendet setFontMode(1) und u8g2.setDrawColor(2) (XOR) außerdem wir ein spezieller
 Zeichensatz aktiviert (8g2.setFont(u8g2_font_open_iconic_all_1x_t))

 Diese Einstellungen müssen bei Bedarf nach dem Aufruf der Funktion wieder rückgängig gemacht werden.

***************************************************************************************************/
void draw_key_context(int icon_0, int icon_1, int icon_2, int icon_3,boolean invert){
  //u8g2.setFontMode(1);        /* activate transparent font mode */
  //u8g2.setDrawColor(2);       //Pixel werden negiert
  //Breite und Höhe des Displays rücklesen
  int disp_width=u8g2.getDisplayWidth();
  int disp_height=u8g2.getDisplayHeight();
  //Höhe der Fußzeile festlegen
  int line_height=10;
  //großen Rahmen um alles zeichnen
  if (invert) u8g2.drawBox(0, disp_height-line_height, disp_width, line_height);
  else u8g2.drawFrame(0, disp_height-line_height, disp_width, line_height);
  //Spaltenbreite bestimmen
  int column_width=disp_width / 4;
  //Vertikale Trennstriche zeichen
  for (int i=1;i<4;i++) u8g2.drawVLine(i*column_width,disp_height-line_height,line_height);
  //offset zur unteren Line
  int bottom_offset=1;
  //Wenn der Code des Icons vorhanden ist, wird Icon in die Box gezeichnet
  if (icon_0>0) u8g2.drawGlyph(0*column_width+6, disp_height-bottom_offset, icon_0); 
  if (icon_1>0) u8g2.drawGlyph(1*column_width+6, disp_height-bottom_offset, icon_1); 
  if (icon_2>0) u8g2.drawGlyph(2*column_width+6, disp_height-bottom_offset, icon_2); 
  if (icon_3>0) u8g2.drawGlyph(3*column_width+6, disp_height-bottom_offset, icon_3); 
}    
