/**************************************************************/
/***********  float to string   *******************************/
/**************************************************************/
/*
*  floatToString.h
*
*  Usage: floatToString(buffer string, float value, precision, minimum text width)
*
*  Example:
*  char test[20];    // string buffer
*  float M;          // float variable to be converted
*                 // precision -> number of decimal places
*                 // min text width -> character output width, 0 = no right justify
*
*  Serial.print(floatToString(test, M, 3, 7)); // call for conversion function
*  
*/
char * floatToString(char * outstr, double val, byte precision, byte widthp)
{
 char temp[16]; //increase this if you need more digits than 15
 byte i;

 temp[0]='\0';
 outstr[0]='\0';

 if(val < 0.0){
   strcpy(outstr,"-\0");  //print "-" sign
   val *= -1;
 }

 if( precision == 0) {
   strcat(outstr, ltoa(round(val),temp,10));  //prints the int part
 }
 else {
   unsigned long frac, mult = 1;
   byte padding = precision-1;
   
   while (precision--)
     mult *= 10;

   val += 0.5/(float)mult;      // compute rounding factor
   
   strcat(outstr, ltoa(floor(val),temp,10));  //prints the integer part without rounding
   strcat(outstr, ".\0"); // print the decimal point

   frac = (val - floor(val)) * mult;

   unsigned long frac1 = frac;

   while(frac1 /= 10)
     padding--;

   while(padding--)
     strcat(outstr,"0\0");    // print padding zeros

   strcat(outstr,ltoa(frac,temp,10));  // print fraction part
 }

 // generate width space padding
 if ((widthp != 0)&&(widthp >= strlen(outstr))){
   byte J=0;
   J = widthp - strlen(outstr);

   for (i=0; i< J; i++) {
     temp[i] = ' ';
   }

   temp[i++] = '\0';
   strcat(temp,outstr);
   strcpy(outstr,temp);
 }

 return outstr;
}




/**************************************************************/
/***********  Display fre RAM   *******************************/
/**************************************************************/

    int freeRam() 
    {
      extern int __heap_start, *__brkval; 
      int v; 
      return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval); 
    }

    
    
/**************************************************************/
/***********  NMEA Parcing Functions  *************************/
/**************************************************************/

/* Function countParameter
   Bestimmt die Anzahl der durch Deli getrennten Parameter im String
   Übergabeparameter:
   String Sentence: Der zu untersuchende String
   char deli  : Das trennende Zeichen
   Rückgabewert:
   int : Die Anzahl der Parameter im String 
 */
/****************************************************/
int countParameter(String Sentence, char deli)
{
  int len=Sentence.length();
  int counter=0;

  for (int i=0; i<len; i++)
  {
    if (Sentence.charAt(i)==deli){counter++;}
  }
  return (counter-1);
}
/****************************************************/
/* Function getParameter
   Findet einen Teilstring (Parameter) in einem durch Delimeter
   unterteilten String. Damei wird vorgegeben nach dem wievielten
   Delimenter begonnen werden soll.
   Übergabeparameter:
   String Sentence: Der zu untersuchende String
   char deli  : Das Zeichen, welches den String unterteilt
   int index  : nach dem wievielten Auftreten des Delimeters
                der Teilstring (Parameter) beginnen soll.
   Rückgabewert:
   String : Der Parameter
   Fals index zu groß ist wird "Error" zurückgegeben.
 */
/****************************************************/
String getParameter(String Sentence, char separator, int index)
{
    int found = 0;
    int strIndex[] = { 0, -1 };
    int maxIndex = Sentence.length() - 1;

    //Serial.print("Free RAM in getParameter: ");
    //Serial.println(freeRam()); 
    for (int i = 0; i <= maxIndex && found <= index; i++) {
        if (Sentence.charAt(i) == separator || i == maxIndex) {
            found++;
            strIndex[0] = strIndex[1] + 1;
            strIndex[1] = (i == maxIndex) ? i+1 : i;
        }
    }
    return found > index ? Sentence.substring(strIndex[0], strIndex[1]) : "Error";
}

/****************************************************/
/* Function stripSentence
   Gibt den Teil von Sentence zurück, der sich zwischen 
   $ und * befindet
   Übergabeparameter:
   String Sentence: Der eingelesene Rohstring
   Rückgabewert:
   String : Der Parameter
   Fals ein Fehler auftrit wird "Error" zurückgegeben.
 */
/****************************************************/
String stripSentence(String Sentence)
{
    int start;
    int ende;
    String s="";
    
    start=Sentence.indexOf('$');
    ende=Sentence.indexOf('*');
    //Serial.print("Start=");
    //Serial.print(start);
    //Serial.print(" Ende=");
    //Serial.print(ende);
    if((start>=0)&&(ende>5))
    {
      s=Sentence.substring(start+1,ende);
      //Serial.print(" sentence=");
      //Serial.println(s);
      return (s);
    }else return("Error"); 
}

/****************************************************/
/* Function getChecksum
   Gibt den Teil von Sentence zurück, der sich hinter 
   dem * befindet
   Übergabeparameter:
   String Sentence: Der eingelesene Rohstring
   Rückgabewert:
   String : Checksum
   Fals ein Fehler auftrit wird "Error" zurückgegeben.
 */
/****************************************************/
String getChecksum(String Sentence)
{
    int start;
    String s="";
    
    start=Sentence.indexOf('*');
    
    if(start>=0)
    {
      s=Sentence.substring(start+1,start+3);
      return (s);
    }else return("Error"); 
}

/****************************************************/
/* Function CalcCheckSum
   Berechnet die Prüfsumme aus dem übergebenen String
   Übergabeparameter:
   String Sentence: Sentence (nach $ und vor *)
   Rückgabewert:
   String : Checksum
   Fals ein Fehler auftrit wird "Error" zurückgegeben.
 */
/****************************************************/
String CalcCheckSum(String s) {
int i, XOR, c;
String r="";

  for (XOR = 0, i = 0; i < s.length(); i++) {
    c = (unsigned char)s.charAt(i);
    if (c == '*') break;
    if ((c!='$') && (c!='!')) XOR ^= c;
  }
  r=String(XOR,HEX);
  if(r.length()<2){r='0'+r;}
  return r; 
}
