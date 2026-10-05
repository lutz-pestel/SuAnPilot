#include <EEPROM.h>

/*
#define def_angle_max   30   //maximaler Ruderausschlag eine Richtung
#define def_angle_min   -30  //maximaler Ruderausschlag andere Richtung
#define def_f_max       3200 //f bei maximalen Ruderausschlag eine Richtung
#define def_f_mid       2450 //f bei Null Ruderausschlag
#define def_f_min       1700 //f bei maximalen Ruderausschlag andere Richtung

//Ruderparameter werden aus dem EEPROM gelesen
int angle_max=0;      //maximaler Ruderausschlag eine Richtung
int angle_min=0;      //maximaler Ruderausschlag andere Richtung
int f_max=0;          //f bei maximalen Ruderausschlag eine Richtung
int f_mid=0;          //f bei Null Ruderausschlag
int f_min=0;          //f bei maximalen Ruderausschlag andere Richtung

//Definition der EEPROM-Speicherplätze
#define addr_angle_max  10    //EEPROM Addr für maximaler Ruderausschlag eine Richtung
#define addr_angle_min  12    //EEPROM Addr für maximaler Ruderausschlag andere Richtung
#define addr_f_max      14    //EEPROM Addr für f bei maximalen Ruderausschlag eine Richtung
#define addr_f_mid      16    //EEPROM Addr für f bei Null Ruderausschlag
#define addr_f_min      18    //EEPROM Addr für f bei maximalen Ruderausschlag andere Richtung
*/



void writeIntIntoEEPROM(int address, int number)
{ 
  EEPROM.write(address, number >> 8);
  EEPROM.write(address + 1, number & 0xFF);
}

int readIntFromEEPROM(int address)
{
  return (EEPROM.read(address) << 8) + EEPROM.read(address + 1);
}

void writeUnsignedIntIntoEEPROM(int address, unsigned int number)
{ 
  EEPROM.write(address, number >> 8);
  EEPROM.write(address + 1, number & 0xFF);
}

unsigned int readUnsignedIntFromEEPROM(int address)
{
  return (EEPROM.read(address) << 8) + EEPROM.read(address + 1);
}

void writeLongIntoEEPROM(int address, long number)
{ 
  EEPROM.write(address, (number >> 24) & 0xFF);
  EEPROM.write(address + 1, (number >> 16) & 0xFF);
  EEPROM.write(address + 2, (number >> 8) & 0xFF);
  EEPROM.write(address + 3, number & 0xFF);
}
long readLongFromEEPROM(int address)
{
  return ((long)EEPROM.read(address) << 24) +
         ((long)EEPROM.read(address + 1) << 16) +
         ((long)EEPROM.read(address + 2) << 8) +
         (long)EEPROM.read(address + 3);
}

void writeIntArrayIntoEEPROM(int address, int numbers[], int arraySize)
{
  int addressIndex = address;
  for (int i = 0; i < arraySize; i++) 
  {
    EEPROM.write(addressIndex, numbers[i] >> 8);
    EEPROM.write(addressIndex + 1, numbers[i] & 0xFF);
    addressIndex += 2;
  }
}
void readIntArrayFromEEPROM(int address, int numbers[], int arraySize)
{
  int addressIndex = address;
  for (int i = 0; i < arraySize; i++)
  {
    numbers[i] = (EEPROM.read(addressIndex) << 8) + EEPROM.read(addressIndex + 1);
    addressIndex += 2;
  }
}

//Funktion schreibt Default-Werte in den EEPROM - Reset
void write_defaul_rudder_parameter_to_EEPROM()
{
  writeIntIntoEEPROM(addr_angle_max,def_angle_max);
  //Serial.print("angle_max:");Serial.println(def_angle_max);
  writeIntIntoEEPROM(addr_angle_min,def_angle_min);
  //Serial.print("angle_min:");Serial.println(def_angle_min);
  (addr_f_max,def_f_max);
  //Serial.print("f_max:");Serial.println(def_f_max);
  writeIntIntoEEPROM(addr_f_mid,def_f_mid);
  //Serial.print("f_mid:");Serial.println(def_f_mid);
  writeIntIntoEEPROM(addr_f_min,def_f_min);
  //Serial.print("f_min:");Serial.println(def_f_min);
}

//Funktion schreibt die Variablen Werte in den EEPROM
//Permanentes Speichern
void write_rudder_parameter_to_EEPROM()
{
  writeIntIntoEEPROM(addr_angle_max,def_angle_max);
  writeIntIntoEEPROM(addr_angle_min,def_angle_min);
  writeIntIntoEEPROM(addr_f_max,def_f_max);
  writeIntIntoEEPROM(addr_f_mid,def_f_mid);
  writeIntIntoEEPROM(addr_f_min,def_f_min);
}

//Funktion liest die im EEPROM gespeiherten
//Ruderparameter in die Variablen
void read_rudder_parameter_from_EEPROM()
{
  angle_max=readIntFromEEPROM(addr_angle_max);     //maximaler Ruderausschlag eine Richtung
  //Serial.print("angle_max:");Serial.println(angle_max);
  angle_min=readIntFromEEPROM(addr_angle_min);     //maximaler Ruderausschlag andere Richtung
  //Serial.print("angle_min:");Serial.println(angle_min);
  f_max=readIntFromEEPROM(addr_f_max);       //f bei maximalen Ruderausschlag eine Richtung
  //Serial.print("f_max:");Serial.println(f_max);
  f_mid=readIntFromEEPROM(addr_f_mid);       //f bei Null Ruderausschlag
  //Serial.print("f_mid:");Serial.println(f_mid);
  f_min=readIntFromEEPROM(addr_f_min);       //f bei maximalen Ruderausschlag andere Richtung
  //Serial.print("f_min:");Serial.println(f_min);
}
