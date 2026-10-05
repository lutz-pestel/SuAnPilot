/***************************************************************************
 ****     Definition globaler Variablen ************************************
 **************************************************************************/
 boolean Testmode=true; //Monitgor-Ausgaben auf Serielle Schnittstelle legen
/***************************************************************************
****     Definition globaler NMEA Parameter  *******************************
***************************************************************************/
int RSA=180; //Ruderwinkel mit sinnloser Vorgabe

//*************** Parcing GPRSA ***************
// Ruder Rückmeldung: Winkel der Ruderlage
void Sentence_GPRSA(String sentence)
{
  RSA=round(getParameter(sentence, ',', 1).toFloat());
  
  Serial.print (F("RSA="));
  Serial.print(RSA);
  Serial.println();

  //show_RSA(RSA); 
  //return RSA  
}

//*************** no Parsing ***************
void Sentence_unspecific(String sentence)
{       
   Serial.print(F("unknown sentences="));Serial.println(sentence);    
}//function

/*********************************************************/
/*********   Parcer              ***************/
/*********************************************************/
void parce(String sentence)
{
      String sentence_type=getParameter(sentence, ',', 0); //Nullten Parameter auslesen =>Sentence Type
      
      if(sentence_type.equals("$GPRSA")) //
      {
           Sentence_GPRSA(sentence); 
      }
      else 
      {
           Sentence_unspecific(sentence);  
      }
}      
