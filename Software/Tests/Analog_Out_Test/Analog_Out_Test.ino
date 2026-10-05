
//Pins
const int pwm_out = 5;
String inString = "";    // string to hold input
int value;
int pwm_val;



// the setup function runs once when you press reset or power the board
void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  pinMode(pwm_out, OUTPUT);
  Serial.println("Start");
}

void loop()  
{
  waitforinput();
  inString=Serial.readString();
  value=inString.toInt();
  Serial.println(value);
  analogWrite(pwm_out, value);
}


void waitforinput(){
  Serial.println("waiting for input ...");
  while (Serial.available() == 0) {
    ;
  }
}
