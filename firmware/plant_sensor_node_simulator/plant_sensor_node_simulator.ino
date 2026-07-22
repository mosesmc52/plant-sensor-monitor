#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>

// -------------------- Wi-Fi Configuration --------------------
// ssh basil@greenhouse.local // password

const char* wifiSsid = "Verizon_F3JP4G";
const char* wifiPassword = "then7detain2cod";

// Replace with the Raspberry Pi's IP address or hostname.
// const char* serverUrl =
//   "http://192.168.1.157:8000/api/v1/readings";
const char* serverUrl =
   "http://greenhouse.local:8000/api/v1/readings";

// -------------------- Device Configuration --------------------

const char* deviceId = "plant-sensor-01";

// Send one reading every 5 seconds.
const unsigned long postIntervalMs = 5000;

// Built-in LED used as the transmission indicator.
#ifndef LED_BUILTIN
#define LED_BUILTIN 2
#endif

const int statusLedPin = LED_BUILTIN;

unsigned long lastPostTime = 0;
unsigned long readingNumber = 0;

// -------------------- Simulated Data --------------------

struct SensorData {
  float temperatureF;
  float humidityPercent;
  float lightLux;
  int moisture1Percent;
  int moisture2Percent;
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

float randomFloat(float minimum, float maximum);
float clampFloat(float value, float minimum, float maximum);
int clampInt(int value, int minimum, int maximum);

// ------------------------------------------------------------

void setup() {
  Serial.begin(115200);


  pinMode(statusLedPin, OUTPUT);
  digitalWrite(statusLedPin, HIGH);  // LED off

  delay(1000);

  Serial.println();
  Serial.println("Plant sensor simulator starting...");

  randomSeed(micros());

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
  static float temperatureF = 72.0;
  static float humidityPercent = 52.0;
  static float lightLux = 450.0;
  static int moisture1Percent = 64;
  static int moisture2Percent = 58;

  temperatureF += randomFloat(-0.4, 0.4);
  humidityPercent += randomFloat(-1.0, 1.0);
  lightLux += randomFloat(-40.0, 40.0);

  moisture1Percent -= random(0, 2);
  moisture2Percent -= random(0, 2);

  if (moisture1Percent < 25) {
    moisture1Percent = random(70, 91);
    Serial.println("Simulation: plant 1 was watered.");
  }

  if (moisture2Percent < 25) {
    moisture2Percent = random(70, 91);
    Serial.println("Simulation: plant 2 was watered.");
  }

  temperatureF = clampFloat(
    temperatureF,
    65.0,
    85.0
  );

  humidityPercent = clampFloat(
    humidityPercent,
    30.0,
    80.0
  );

  lightLux = clampFloat(
    lightLux,
    0.0,
    2000.0
  );

  moisture1Percent = clampInt(
    moisture1Percent,
    0,
    100
  );

  moisture2Percent = clampInt(
    moisture2Percent,
    0,
    100
  );

  SensorData data;

  data.temperatureF = temperatureF;
  data.humidityPercent = humidityPercent;
  data.lightLux = lightLux;
  data.moisture1Percent = moisture1Percent;
  data.moisture2Percent = moisture2Percent;

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

  jsonPayload += "\"moisture_2_percent\":";
  jsonPayload += String(data.moisture2Percent);
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

  Serial.print("Moisture 2: ");
  Serial.print(data.moisture2Percent);
  Serial.println(" %");
}

// -------------------- Utilities --------------------

float randomFloat(float minimum, float maximum) {
  long randomValue = random(0, 10001);

  float normalizedValue =
    static_cast<float>(randomValue) / 10000.0;

  return minimum +
    normalizedValue * (maximum - minimum);
}

float clampFloat(
  float value,
  float minimum,
  float maximum
) {
  if (value < minimum) {
    return minimum;
  }

  if (value > maximum) {
    return maximum;
  }

  return value;
}

int clampInt(
  int value,
  int minimum,
  int maximum
) {
  if (value < minimum) {
    return minimum;
  }

  if (value > maximum) {
    return maximum;
  }

  return value;
}