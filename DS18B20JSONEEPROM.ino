#include <ESP8266WiFi.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <EEPROM.h>
#include <ArduinoJson.h>

//wifi-set-channel
extern "C" {
#include "user_interface.h"
}


//pro teploměr
#define ONE_WIRE_BUS D1
#define TEMPERATURE_PRECISION 12

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
DeviceAddress dsAddress;

const char* ssid = "ApartmanBenesov";
const char* password = "VtXPni3ChzPq";

// Time to sleep (in seconds):
const int sleepTimeS = 10;
const int serverSendCount = 5;
const char* host = "192.168.2.200";
const char* addr = "/~beda/JSONServer/store.php";
const int httpPort = 80;

//cold start? yes = clear EEPROM
bool coldStart;

//Error? yes = set counter to 255 => reset device after deep sleep
bool error;

void setup(void) {

  Serial.begin(115200);

  coldStart = false;
  error = false;
  Serial.println(" ");
  Serial.print("Boot reason: ");
  const rst_info * resetInfo = system_get_rst_info();
  Serial.println(resetInfo->reason);

  if (resetInfo->reason != 5)
  {
    prepare();
    coldStart = true;
  }
  byte counter = readCounter();
  if (counter == 255)
  {
    Serial.println("ERROR before deep sleep -> RESET.");
    ESP.restart();
  }
  else if (counter >= serverSendCount)
  {
    Serial.println("Data sent to server before deep sleep -> clearing data.");
    clearData();
    counter = 0;
  }
  Serial.print("Counter = ");
  Serial.println(counter);

  if (coldStart)
  {
    oneWire.reset_search();
    Serial.println("Cold start -> looking for Temperature sensors.");

    if (!oneWire.search(dsAddress) || (dsAddress[0] == 0 && dsAddress[1] == 0 && dsAddress[2] == 0 && dsAddress[3] == 0 && dsAddress[4] == 0 && dsAddress[5] == 0 && dsAddress[6] == 0 && dsAddress[7] == 0))
    {
      Serial.println("Temperature sensor not found!");
      error = true;
    }

    Serial.print("Temperature sensor 1 address: ");
    for (uint8_t i = 0; i < 8; i++)
    {
      // zero pad the address if necessary
      if (dsAddress[i] < 16) Serial.print("0");
      Serial.print(dsAddress[i], HEX);
    }
    Serial.println();

    writeTempAddr();
  }
  else
  {
    readTempAddr();
  }

  //Set resolution
  sensors.setResolution(dsAddress, TEMPERATURE_PRECISION);

  sensors.requestTemperatures();
  float temperature = sensors.getTempC(dsAddress);
  if (temperature == -127.0)
  {
    error = true;
    Serial.println("ERROR while reading temperature -> restart after deep sleep.");
  }

  writeTemperature(counter, temperature);

  //Read all temperatures
  for (int i = 0; i <= counter; i++)
  {
    Serial.print("Temperature[");
    Serial.print(i);
    Serial.print("] = ");
    Serial.print(readTemperature(i));
    Serial.print(" | ");
    Serial.println(readTime(i));
  }

  if (error)
  {
    writeCounter(255);
  }
  else
  {
    counter++;
    writeCounter(counter);
    
    if (counter >= serverSendCount)
    {
      //Send to Server// Connect to WiFi
      //WiFi.mode(WIFI_STA); //Co tohle dela???
      WiFi.begin(ssid, password);
      wifi_set_channel(6);

      //Hardcocded IP
      //WiFi.config(IPAddress(192, 168, 2, 99), IPAddress(192, 168, 2, 1), IPAddress(255, 255, 255, 0));
      for (int i = 0; WiFi.status() != WL_CONNECTED && i < 200; i++) {
        delay(100);
        Serial.print(".");
      }
      Serial.println(" ");
      Serial.println("Sending data to server...");
      WiFiClient client;

      StaticJsonBuffer<300> JSONbuffer;
      JsonObject& JSONencoder = JSONbuffer.createObject();
      JSONencoder["sensorType"] = "Temperature";
      JSONencoder["timeSleep"] = sleepTimeS;
      JsonArray& values = JSONencoder.createNestedArray("temperatures");
      JsonArray& times = JSONencoder.createNestedArray("times");


      for (int i = 0; i <= counter-1; i++)
      {
        values.add(readTemperature(i));
        if(i == counter-1)
          times.add(millis());
        else
          times.add(readTime(i));
      }

      String output;
      JSONencoder.printTo(output);

      if (client.connect(host, httpPort)) {
        client.print("POST ");
        client.print(addr);
        client.println(" HTTP/1.1");
        client.print("Host: ");
        client.println(host);
        client.println("Cache-Control: no-cache");
        client.println("Content-Type: application/json");
        client.print("Content-Length: ");
        client.println(output.length());
        client.println();
        client.println(output);


        Serial.println("closing connection");
      }
      else {
        Serial.println("connection failed");
      }
    }
  }
  
  unsigned long t = millis();
  writeTime(counter-1, t);
  Serial.print("Time: ");
  Serial.println(t);
  ESP.deepSleep(sleepTimeS * 1000000);
}

void loop(void) {
}


uint16_t read_u16_BE(int address)
{
  return (uint16_t)((EEPROM.read(address) << 8) | EEPROM.read(address + 1));
}
void write_u16_BE(int address, uint16_t data)
{
  EEPROM.write((uint8_t)((uint8_t)data >> 8), address);
  EEPROM.write((uint8_t)data, address + 1);
}

void writeTempAddr()
{
  EEPROM.begin(512);
  EEPROM.write(1, dsAddress[0]);
  EEPROM.write(2, dsAddress[1]);
  EEPROM.write(3, dsAddress[2]);
  EEPROM.write(4, dsAddress[3]);
  EEPROM.write(5, dsAddress[4]);
  EEPROM.write(6, dsAddress[5]);
  EEPROM.write(7, dsAddress[6]);
  EEPROM.write(8, dsAddress[7]);
  EEPROM.commit();
  EEPROM.end();
}
void readTempAddr()
{
  EEPROM.begin(512);
  dsAddress[0] = EEPROM.read(1);
  dsAddress[1] = EEPROM.read(2);
  dsAddress[2] = EEPROM.read(3);
  dsAddress[3] = EEPROM.read(4);
  dsAddress[4] = EEPROM.read(5);
  dsAddress[5] = EEPROM.read(6);
  dsAddress[6] = EEPROM.read(7);
  dsAddress[7] = EEPROM.read(8);
  EEPROM.end();
}
void writeCounter(byte counter)
{
  EEPROM.begin(512);
  Serial.println("Storing Counter to EEPROM");
  EEPROM.write(0, counter);
  EEPROM.commit();
  EEPROM.end();
}
byte readCounter()
{
  EEPROM.begin(512);
  byte counter = EEPROM.read(0);
  EEPROM.end();
  return counter;
}
float readTemperature(int counter)
{
  int offset = 9;
  int address = counter * 4 + offset;
  float val = 0;
  EEPROM.begin(512);
  uint32_t n = (uint32_t)((EEPROM.read(address) << 24) | (EEPROM.read(address + 1) << 16) | (EEPROM.read(address + 2) << 8) | EEPROM.read(address + 3));
  EEPROM.end();
  memcpy(&val, &n, 4);
  return val;
}
void writeTemperature(int counter, float data)
{
  int offset = 9;
  int address = counter * 4 + offset;
  uint32_t val = 0;
  memcpy(&val, &data, 4);
  EEPROM.begin(512);

  uint8_t tmpOut0 = (uint8_t)(val >> 24);
  uint8_t tmpOut1 = (uint8_t)(val >> 16);
  uint8_t tmpOut2 = (uint8_t)(val >> 8);
  uint8_t tmpOut3 = (uint8_t)val;
  EEPROM.write(address, tmpOut0);
  EEPROM.write(address + 1, tmpOut1);
  EEPROM.write(address + 2, tmpOut2);
  EEPROM.write(address + 3, tmpOut3);
  EEPROM.commit();
  EEPROM.end();
}
uint32_t readTime(int counter)
{
  int offset = 49;
  int address = counter * 4 + offset;
  EEPROM.begin(512);
  uint32_t n = (uint32_t)((EEPROM.read(address) << 24) | (EEPROM.read(address + 1) << 16) | (EEPROM.read(address + 2) << 8) | EEPROM.read(address + 3));
  EEPROM.end();
  return n;
}
void writeTime(int counter, uint32_t data)
{
  int offset = 49;
  int address = counter * 4 + offset;
  EEPROM.begin(512);

  uint8_t tmpOut0 = (uint8_t)(data >> 24);
  uint8_t tmpOut1 = (uint8_t)(data >> 16);
  uint8_t tmpOut2 = (uint8_t)(data >> 8);
  uint8_t tmpOut3 = (uint8_t)data;
  EEPROM.write(address, tmpOut0);
  EEPROM.write(address + 1, tmpOut1);
  EEPROM.write(address + 2, tmpOut2);
  EEPROM.write(address + 3, tmpOut3);
  EEPROM.commit();
  EEPROM.end();
}
void prepare()
{
  EEPROM.begin(512);
  //Clear memory
  Serial.println("Clearing Memory.");
  for (int i = 0; i < 512; i++)
    EEPROM.write(i, 0);

  EEPROM.commit();
  EEPROM.end();
}
void clearData()
{
  writeCounter(0);
  EEPROM.begin(512);
  //Clear memory
  Serial.println("Clearing Memory.");
  for (int i = 9; i < 512; i++)
    EEPROM.write(i, 0);

  EEPROM.commit();
  EEPROM.end();
}

