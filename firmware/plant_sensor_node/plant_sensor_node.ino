#include <Arduino.h>
#include <Wire.h>
#include <BH1750.h>
#include <Adafruit_AHTX0.h>
#include <U8x8lib.h>

// -------------------- Pins --------------------
const int moisturePin_1 = A0;
const int moisturePin_2 = A1;

// -------------------- Moisture Calibration --------------------
// Replace these with values measured from your own sensors.
const int moisture1DryValue = 850;
const int moisture1WetValue = 350;

const int moisture2DryValue = 850;
const int moisture2WetValue = 350;

// -------------------- Sensors --------------------
BH1750 lightMeter;
Adafruit_AHTX0 aht20;

// SSD1306 128x64 OLED using hardware I2C
U8X8_SSD1306_128X64_NONAME_HW_I2C u8x8(U8X8_PIN_NONE);

// -------------------- Data Structures --------------------
struct ClimateData {
  float temperature;
  float humidity;
};

// -------------------- Sensor Status --------------------
bool lightSensorAvailable = false;
bool climateSensorAvailable = false;

// -------------------- Function Prototypes --------------------
int readMoistureSensor(int pin);

int moisturePercent(
  int rawValue,
  int dryValue,
  int wetValue
);

const char* getMoistureCondition(int percent);

float readLightSensor();
const char* getLightCondition(float lux);

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

// ------------------------------------------------------------

void loop() {
  int rawMoisture1 = readMoistureSensor(moisturePin_1);
  int rawMoisture2 = readMoistureSensor(moisturePin_2);

  int moisture1 = moisturePercent(
    rawMoisture1,
    moisture1DryValue,
    moisture1WetValue
  );

  int moisture2 = moisturePercent(
    rawMoisture2,
    moisture2DryValue,
    moisture2WetValue
  );

  float lux = readLightSensor();
  ClimateData climate = readClimate();

  // -------------------- Serial Output --------------------

  Serial.println("------------------------");

  Serial.print("Moisture 1: ");
  Serial.print(moisture1);
  Serial.print("% (");
  Serial.print(getMoistureCondition(moisture1));
  Serial.print("), Raw: ");
  Serial.println(rawMoisture1);

  Serial.print("Moisture 2: ");
  Serial.print(moisture2);
  Serial.print("% (");
  Serial.print(getMoistureCondition(moisture2));
  Serial.print("), Raw: ");
  Serial.println(rawMoisture2);

  if (lightSensorAvailable && lux >= 0) {
    Serial.print("Light: ");
    Serial.print(lux, 1);
    Serial.print(" lux (");
    Serial.print(getLightCondition(lux));
    Serial.println(")");
  } else {
    Serial.println("Light sensor unavailable");
  }

  if (climateSensorAvailable) {
    Serial.print("Temperature: ");
    Serial.print(climate.temperature, 1);
    Serial.println(" F");

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

  delay(1000);
}

// -------------------- Moisture Functions --------------------

int readMoistureSensor(int pin) {
  return analogRead(pin);
}

int moisturePercent(
  int rawValue,
  int dryValue,
  int wetValue
) {
  int percent = map(
    rawValue,
    dryValue,
    wetValue,
    0,
    100
  );

  return constrain(percent, 0, 100);
}

const char* getMoistureCondition(int percent) {
  // Short words are used so they fit on the OLED.
  if (percent >= 80) {
    return "V.Wet";
  } else if (percent >= 60) {
    return "Wet";
  } else if (percent >= 40) {
    return "Moist";
  } else if (percent >= 20) {
    return "Dry";
  } else {
    return "V.Dry";
  }
}

// -------------------- Light Functions --------------------

float readLightSensor() {
  if (!lightSensorAvailable) {
    return -1.0;
  }

  return lightMeter.readLightLevel();
}

const char* getLightCondition(float lux) {
  if (lux < 0) {
    return "ERROR";
  } else if (lux < 10) {
    return "Dark";
  } else if (lux < 100) {
    return "Dim";
  } else if (lux < 1000) {
    return "Indoor";
  } else if (lux < 10000) {
    return "Bright";
  } else {
    return "Sunlight";
  }
}

// -------------------- Climate Function --------------------

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

  // Convert Celsius to Fahrenheit
  data.temperature =
    (temperatureEvent.temperature * 9.0 / 5.0) + 32.0;

  data.humidity =
    humidityEvent.relative_humidity;

  return data;
}

// -------------------- OLED Display --------------------

void displaySensorData(
  int moisture1,
  int moisture2,
  float lux,
  ClimateData climate
) {
  // A 128x64 U8X8 display has 16 columns and 8 rows.

  // Row 0: title
  u8x8.clearLine(0);
  u8x8.setCursor(0, 0);
  u8x8.print("Sensor Readings");

  // Row 1: moisture sensor 1
  u8x8.clearLine(1);
  u8x8.setCursor(0, 1);
  u8x8.print("M1:");
  u8x8.print(moisture1);
  u8x8.print("% ");
  u8x8.print(getMoistureCondition(moisture1));

  // Row 2: moisture sensor 2
  u8x8.clearLine(2);
  u8x8.setCursor(0, 2);
  u8x8.print("M2:");
  u8x8.print(moisture2);
  u8x8.print("% ");
  u8x8.print(getMoistureCondition(moisture2));

  // Row 3: light value
  u8x8.clearLine(3);
  u8x8.setCursor(0, 3);
  u8x8.print("Light:");

  if (lightSensorAvailable && lux >= 0) {
    u8x8.print(lux, 0);
    u8x8.print("lx");
  } else {
    u8x8.print("ERROR");
  }

  // Row 4: light condition
  u8x8.clearLine(4);
  u8x8.setCursor(0, 4);
  u8x8.print("Level:");

  if (lightSensorAvailable && lux >= 0) {
    u8x8.print(getLightCondition(lux));
  } else {
    u8x8.print("ERROR");
  }

  // Row 5: temperature
  u8x8.clearLine(5);
  u8x8.setCursor(0, 5);
  u8x8.print("Temp:");

  if (climateSensorAvailable) {
    u8x8.print(climate.temperature, 1);
    u8x8.print(" F");
  } else {
    u8x8.print("ERROR");
  }

  // Row 6: humidity
  u8x8.clearLine(6);
  u8x8.setCursor(0, 6);
  u8x8.print("Hum:");

  if (climateSensorAvailable) {
    u8x8.print(climate.humidity, 1);
    u8x8.print("%");
  } else {
    u8x8.print("ERROR");
  }

  // Row 7: update indicator
  // u8x8.clearLine(7);
  // u8x8.setCursor(0, 7);
  // u8x8.print("Update: 1 sec");
}