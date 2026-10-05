// Einfügen der Mittelwert-Klasse für das glätten der Frequenz-Werte
#include "average.cpp"  
Average av; 

boolean read_RF300(void)
{
   ontime = pulseIn(RF300_PIN,HIGH);
   offtime = pulseIn(RF300_PIN,LOW);
   if ((ontime>0) and (offtime>0))
   {
     period = ontime+offtime;
     freq = 1000000.0/period;
     freq_av=av.glaetten(freq);
     rudder_angle = map(freq_av, f_min, f_max, angle_max, angle_min);
     
     pwm_val = map(freq_av, f_min-200, f_max+200, 255, 0);
     //Frequenzproportionale Spannung ausgeben
     analogWrite(RudderAngle_PWM, pwm_val);
     return true;
   }//if
   else
   {
      freq=0;
      freq_av=0;
      rudder_angle=0;
      return false;
   }
}

//Funktion testet, ob der Ruderwinkel
//den maximalen oder minimalen Winkel übersteigt
//und blinkt dann die gelbe Status-LED
void test_max_rudder()
{
  static unsigned long start=millis();
  unsigned long period=100;
  static boolean blink=false;
  if (start+period<millis())
  {
    //Periode ist um
    start=millis();
    blink=!blink;
  }
  
  int f=round(freq_av);
  if (f>f_max)
    {
      digitalWrite(Status,blink);
      return false;
    }
    if (f<f_min)
    {
      digitalWrite(Status,blink);
      return false;
    }
  return true;  
}
