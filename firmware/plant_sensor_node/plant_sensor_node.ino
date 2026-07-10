#include <Arduino.h>
#include <Wire.h>
#include <BH1750.h>
#include <Adafruit_AHTX0.h>
#include <U8x8lib.h>

// -------------------- Pins --------------------
const int moisturePin_1 = A0;
const int moisturePin_2 = A1;

// -------------------- Sensors --------------------
BH1750 lightMeter;
Adafruit_AHTX0 aht20;

// SSD1306 128x64 OLED using hardware I2C
U8X8_SSD1306_128X64_NONAME_HW_I2C u8x8(U8X8_PIN_NONE);

// Structure to hold AHT20 readings
struct ClimateData {
  float temperature;
  float humidity;
};

// -------------------- Sensor Status --------------------
bool lightSensorAvailable = false;
bool climateSensorAvailable = false;

// -------------------- Function Prototypes --------------------
int readMoistureSensor(int pin);
float readLightSensor();
ClimateData readClimate();

void displaySensorData(
  int moisture1,
  int moisture2,
  float lux,
  ClimateData climate
);

// ------------------------------------------------------------

void setup() {
  Serial.begin(115200);

  // Start I2C bus
  Wire.begin();

  // Start OLED
  u8x8.begin();
  u8x8.setFlipMode(1);
  u8x8.setFont(u8x8_font_chroma48medium8_r);
  u8x8.clear();

  u8x8.setCursor(0, 0);
  u8x8.print("Starting...");

  // Start BH1750 light sensor
  lightSensorAvailable =
    lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE);

  if (!lightSensorAvailable) {
    Serial.println("Failed to initialize BH1750");
  }

  // Start AHT20 temperature and humidity sensor
  climateSensorAvailable = aht20.begin();

  if (!climateSensorAvailable) {
    Serial.println("Failed to initialize AHT20");
  }

  delay(1000);
  u8x8.clear();
}

void loop() {
  int moisture1 = readMoistureSensor(moisturePin_1);
  int moisture2 = readMoistureSensor(moisturePin_2);

  float lux = readLightSensor();
  ClimateData climate = readClimate();

  // -------------------- Serial Output --------------------

  Serial.println("------------------------");

  Serial.print("Moisture 1: ");
  Serial.println(moisture1);

  Serial.print("Moisture 2: ");
  Serial.println(moisture2);

  if (lightSensorAvailable) {
    Serial.print("Light: ");
    Serial.print(lux, 1);
    Serial.println(" lux");
  } else {
    Serial.println("Light sensor unavailable");
  }

  if (climateSensorAvailable) {
    Serial.print("Temperature: ");
    Serial.print(climate.temperature, 1);
    Serial.println(" C");

    Serial.print("Humidity: ");
    Serial.print(climate.humidity, 1);
    Serial.println(" %");
  } else {
    Serial.println("AHT20 unavailable");
  }

  // -------------------- OLED Output --------------------

  displaySensorData(
    moisture1,
    moisture2,
    lux,
    climate
  );

  delay(2000);
}

// -------------------- Sensor Functions --------------------

int readMoistureSensor(int pin) {
  return analogRead(pin);
}

float readLightSensor() {
  if (!lightSensorAvailable) {
    return -1.0;
  }

  return lightMeter.readLightLevel();
}

ClimateData readClimate() {
  ClimateData data;

  // Default error values
  data.temperature = -999.0;
  data.humidity = -999.0;

  if (!climateSensorAvailable) {
    return data;
  }

  sensors_event_t humidityEvent;
  sensors_event_t temperatureEvent;

  aht20.getEvent(
    &humidityEvent,
    &temperatureEvent
  );

  data.temperature = temperatureEvent.temperature;
  data.humidity = humidityEvent.relative_humidity;

  return data;
}

// -------------------- Display Function --------------------

void displaySensorData(
  int moisture1,
  int moisture2,
  float lux,
  ClimateData climate
) {
  // Each U8X8 row is cleared before printing so old
  // characters are removed when a value becomes shorter.

  u8x8.clearLine(0);
  u8x8.setCursor(0, 0);
  u8x8.print("Sensor Readings");

  u8x8.clearLine(1);
  u8x8.setCursor(0, 1);
  u8x8.print("Moist 1: ");
  u8x8.print(moisture1);

  u8x8.clearLine(2);
  u8x8.setCursor(0, 2);
  u8x8.print("Moist 2: ");
  u8x8.print(moisture2);

  u8x8.clearLine(3);
  u8x8.setCursor(0, 3);
  u8x8.print("Light: ");

  if (lightSensorAvailable && lux >= 0) {
    u8x8.print(lux, 0);
    u8x8.print(" lx");
  } else {
    u8x8.print("ERROR");
  }

  u8x8.clearLine(4);
  u8x8.setCursor(0, 4);
  u8x8.print("Temp: ");

  if (climateSensorAvailable) {
    u8x8.print(climate.temperature, 1);
    u8x8.print(" C");
  } else {
    u8x8.print("ERROR");
  }

  u8x8.clearLine(5);
  u8x8.setCursor(0, 5);
  u8x8.print("Hum: ");

  if (climateSensorAvailable) {
    u8x8.print(climate.humidity, 1);
    u8x8.print(" %");
  } else {
    u8x8.print("ERROR");
  }

  u8x8.clearLine(6);
  u8x8.setCursor(0, 6);
  u8x8.print("Update: 2 sec");
}