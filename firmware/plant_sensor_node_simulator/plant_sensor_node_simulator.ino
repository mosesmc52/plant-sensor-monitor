#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <math.h>
#include "wifi_config.h"

// -------------------- Wi-Fi Configuration --------------------

// Replace with the Raspberry Pi's IP address or hostname.
// const char* serverUrl =
//   "http://192.168.1.157:8000/api/v1/readings";
const char* serverUrl =
   "http://greenhouse.local:8000/api/v1/readings";

// -------------------- Device Configuration --------------------

const char* deviceId = "Pesto";

// Send one reading every 5 seconds.
const unsigned long postIntervalMs = 10000;

// Built-in LED used as the transmission indicator.
#ifndef LED_BUILTIN
#define LED_BUILTIN 2
#endif

const int statusLedPin = LED_BUILTIN;

unsigned long lastPostTime = 0;
unsigned long readingNumber = 0;
unsigned long simulationStartTime = 0;

const float twoPi = 6.28318530718;
const unsigned long moistureCycleDurationMs = 60UL * 60UL * 1000UL;
const unsigned long temperatureCycleDurationMs = 30UL * 60UL * 1000UL;
const unsigned long humidityCycleDurationMs = 45UL * 60UL * 1000UL;
const unsigned long lightCycleDurationMs = 20UL * 60UL * 1000UL;

// -------------------- Simulated Data --------------------

struct SensorData {
  float temperatureF;
  float humidityPercent;
  float lightLux;
  int moisture1Percent;
};

// -------------------- Function Prototypes --------------------

void connectToWiFi();
void blinkStatusLed(
  int blinkCount = 2,
  unsigned long onTimeMs = 100,
  unsigned long offTimeMs = 100
);

SensorData generateSimulatedData();
bool sendSensorData(const SensorData& data);
void printSensorData(const SensorData& data);


// ------------------------------------------------------------

void setup() {
  Serial.begin(115200);


  pinMode(statusLedPin, OUTPUT);
  digitalWrite(statusLedPin, HIGH);  // LED off

  delay(1000);

  Serial.println();
  Serial.println("Plant sensor simulator starting...");

  simulationStartTime = millis();

  connectToWiFi();
}

// ------------------------------------------------------------

void loop() {
  // Reconnect if Wi-Fi becomes unavailable.
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
  }

  unsigned long currentTime = millis();

  if (
    lastPostTime == 0 ||
    currentTime - lastPostTime >= postIntervalMs
  ) {
    lastPostTime = currentTime;

    SensorData data = generateSimulatedData();

    printSensorData(data);

    bool sentSuccessfully = sendSensorData(data);

    if (sentSuccessfully) {
      Serial.println("Reading posted successfully.");
    } else {
      Serial.println("Failed to post reading.");
    }

    Serial.println("--------------------------------");
  }

  delay(100);
}

// -------------------- Status LED --------------------

void blinkStatusLed(
  int blinkCount,
  unsigned long onTimeMs,
  unsigned long offTimeMs
) {
  for (int blink = 0; blink < blinkCount; blink++) {
    digitalWrite(statusLedPin, LOW);   // LED on
    delay(onTimeMs);

    digitalWrite(statusLedPin, HIGH);  // LED off

    if (blink < blinkCount - 1) {
      delay(offTimeMs);
    }
  }
}

// -------------------- Wi-Fi --------------------

void connectToWiFi() {
  if (WiFi.status() == WL_CONNECTED) {
    return;
  }

  Serial.print("Connecting to Wi-Fi: ");
  Serial.println(wifiSsid);

  digitalWrite(statusLedPin, HIGH);  // Keep LED off

  WiFi.mode(WIFI_STA);
  WiFi.begin(wifiSsid, wifiPassword);

  const unsigned long timeoutMs = 20000;
  unsigned long connectionStart = millis();

  while (
    WiFi.status() != WL_CONNECTED &&
    millis() - connectionStart < timeoutMs
  ) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Wi-Fi connected.");

    Serial.print("Device IP address: ");
    Serial.println(WiFi.localIP());

    Serial.print("Signal strength: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("Wi-Fi connection timed out.");
  }
}

// -------------------- Simulated Sensor Data --------------------

SensorData generateSimulatedData() {
  unsigned long elapsedMs = millis() - simulationStartTime;

  // Temperature, humidity, and light smoothly oscillate within their
  // configured ranges instead of changing randomly between readings.
  float temperaturePhase = twoPi * (
    static_cast<float>(elapsedMs % temperatureCycleDurationMs) /
    temperatureCycleDurationMs
  );
  float humidityPhase = twoPi * (
    static_cast<float>(elapsedMs % humidityCycleDurationMs) /
    humidityCycleDurationMs
  );
  float lightPhase = twoPi * (
    static_cast<float>(elapsedMs % lightCycleDurationMs) /
    lightCycleDurationMs
  );

  float temperatureF = 75.0 + 10.0 * sin(temperaturePhase);
  float humidityPercent = 55.0 + 25.0 * sin(humidityPhase);
  float lightLux = 1000.0 + 1000.0 * sin(lightPhase);

  // Moisture drains steadily from maximum to the low threshold over one
  // hour. At the end of the cycle it jumps back to maximum, simulating
  // watering after the plant needs water.
  unsigned long moistureElapsedMs = elapsedMs % moistureCycleDurationMs;
  float moistureProgress = static_cast<float>(moistureElapsedMs) /
    moistureCycleDurationMs;
  int moisture1Percent = static_cast<int>(
    90.0 - (65.0 * moistureProgress)
  );

  if (moistureElapsedMs < postIntervalMs) {
    Serial.println("Simulation: plant was watered; moisture reset to maximum.");
  }

  SensorData data;

  data.temperatureF = temperatureF;
  data.humidityPercent = humidityPercent;
  data.lightLux = lightLux;
  data.moisture1Percent = moisture1Percent;

  return data;
}

// -------------------- HTTP POST --------------------

bool sendSensorData(const SensorData& data) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Cannot send data: Wi-Fi unavailable.");
    return false;
  }

  WiFiClient wifiClient;
  HTTPClient http;

  if (!http.begin(wifiClient, serverUrl)) {
    Serial.println("Unable to initialize HTTP client.");
    return false;
  }

  http.addHeader("Content-Type", "application/json");

  String jsonPayload = "{";

  jsonPayload += "\"device_id\":\"";
  jsonPayload += deviceId;
  jsonPayload += "\",";

  jsonPayload += "\"reading_number\":";
  jsonPayload += String(readingNumber++);
  jsonPayload += ",";

  jsonPayload += "\"temperature_f\":";
  jsonPayload += String(data.temperatureF, 1);
  jsonPayload += ",";

  jsonPayload += "\"humidity_percent\":";
  jsonPayload += String(data.humidityPercent, 1);
  jsonPayload += ",";

  jsonPayload += "\"light_lux\":";
  jsonPayload += String(data.lightLux, 1);
  jsonPayload += ",";

  jsonPayload += "\"moisture_1_percent\":";
  jsonPayload += String(data.moisture1Percent);
  jsonPayload += ",";

  jsonPayload += "\"uptime_seconds\":";
  jsonPayload += String(millis() / 1000);

  jsonPayload += "}";

  Serial.println("POST payload:");
  Serial.println(jsonPayload);

  int responseCode = http.POST(jsonPayload);

  if (responseCode <= 0) {
    Serial.print("HTTP request error: ");
    Serial.println(http.errorToString(responseCode));

    http.end();
    return false;
  }

  // Blink after the server receives the message successfully.
  if (responseCode >= 200 && responseCode < 300) {
    blinkStatusLed(2, 100, 100);
  }

  Serial.print("HTTP response code: ");
  Serial.println(responseCode);

  String responseBody = http.getString();

  if (responseBody.length() > 0) {
    Serial.println("Server response:");
    Serial.println(responseBody);
  }

  http.end();

  return responseCode >= 200 && responseCode < 300;
}

// -------------------- Serial Output --------------------

void printSensorData(const SensorData& data) {
  Serial.println();
  Serial.println("Simulated sensor reading");

  Serial.print("Temperature: ");
  Serial.print(data.temperatureF, 1);
  Serial.println(" F");

  Serial.print("Humidity: ");
  Serial.print(data.humidityPercent, 1);
  Serial.println(" %");

  Serial.print("Light: ");
  Serial.print(data.lightLux, 1);
  Serial.println(" lux");

  Serial.print("Moisture 1: ");
  Serial.print(data.moisture1Percent);
  Serial.println(" %");

}
