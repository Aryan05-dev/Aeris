#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <TinyGPS++.h>
#include <HardwareSerial.h>

#define DHTPIN 4
#define DHTTYPE DHT22

#define MQ7_PIN 34
#define NO2_PIN 35

#define PMS_RX 26
#define PMS_TX 27

#define GPS_RX 16
#define GPS_TX 17

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASSWORD";

String server = "http://YOUR_SERVER_IP:8000/data";

DHT dht(DHTPIN, DHTTYPE);

TinyGPSPlus gps;
HardwareSerial gpsSerial(1);
HardwareSerial pmsSerial(2);

float pm25 = 0;
float pm10 = 0;

void connectWiFi()
{
  if (WiFi.status() == WL_CONNECTED) return;

  Serial.println("Connecting WiFi...");

  WiFi.begin(ssid, password);

  int retry = 0;

  while (WiFi.status() != WL_CONNECTED && retry < 20)
  {
    delay(500);
    Serial.print(".");
    retry++;
  }

  if (WiFi.status() == WL_CONNECTED)
    Serial.println("WiFi Connected");
  else
    Serial.println("WiFi Failed");
}

void readPM()
{
  if (pmsSerial.available())
  {
    uint8_t buffer[32];

    pmsSerial.readBytes(buffer, 32);

    pm25 = (buffer[12] << 8) | buffer[13];
    pm10 = (buffer[14] << 8) | buffer[15];
  }
}

float readCO()
{
  int raw = analogRead(MQ7_PIN);
  return raw * (3.3 / 4095.0);
}

float readNO2()
{
  int raw = analogRead(NO2_PIN);
  return raw * (3.3 / 4095.0);
}

void readGPS()
{
  while (gpsSerial.available())
  {
    gps.encode(gpsSerial.read());
  }
}

void sendData(float temp, float hum, float co, float no2)
{
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;

  http.begin(server);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<300> doc;

  doc["device"] = "AERIS_NODE_1";
  doc["pm25"] = pm25;
  doc["pm10"] = pm10;
  doc["co"] = co;
  doc["no2"] = no2;
  doc["temperature"] = temp;
  doc["humidity"] = hum;

  if (gps.location.isValid())
  {
    doc["lat"] = gps.location.lat();
    doc["lon"] = gps.location.lng();
  }

  String payload;
  serializeJson(doc, payload);

  int response = http.POST(payload);

  Serial.print("Server Response: ");
  Serial.println(response);

  http.end();
}

void setup()
{
  Serial.begin(115200);

  dht.begin();

  gpsSerial.begin(9600, SERIAL_8N1, GPS_RX, GPS_TX);
  pmsSerial.begin(9600, SERIAL_8N1, PMS_RX, PMS_TX);

  pinMode(MQ7_PIN, INPUT);
  pinMode(NO2_PIN, INPUT);

  connectWiFi();
}

void loop()
{
  connectWiFi();

  readPM();
  readGPS();

  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  float co = readCO();
  float no2 = readNO2();

  Serial.println("Sending Data...");

  sendData(temp, hum, co, no2);

  delay(30000);
}