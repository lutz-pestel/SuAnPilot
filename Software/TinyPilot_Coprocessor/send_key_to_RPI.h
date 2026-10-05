/*
#define KB_Auto       2
#define KB_Select     3
#define KB_Menu       4
#define KB_Port_1     5
#define KB_Tack       A0
#define KB_Stb_10     A1
#define KB_Port_10    A2
#define KB_Stb_1     A3
#define AUX           6
*/

void send_puls_to_RPi(int RPi_key)
{
   Serial.print(F("Sending Impuls to RPi Key:"));Serial.println(RPi_key);
   digitalWrite(Buzzer, HIGH);
   digitalWrite(RPi_key, HIGH);
   delay(500);
   digitalWrite(RPi_key, LOW); 
   digitalWrite(Buzzer, LOW); 
}
