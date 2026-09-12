/*
 * CropMind - ESP32 Sensor Firmware
 * Reads sensors and publishes data to MQTT broker
 *
 * Author: CropMind Team
 * Date: 2026
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// ============================================
// Pin Configuration
// ============================================

#define DHT_PIN        4
#define SOIL_PIN       34   // Analog input for soil moisture
#define PH_PIN         35   // Analog input for pH sensor
#define LED_PIN        2    // Built-in LED for status

// ============================================
// Sensor Configuration
// ============================================

#define DHT_TYPE       DHT22
#define SOIL_DRY       4095  // Analog value when soil is dry
#define SOIL_WET       1500  // Analog value when soil is wet
#define PH_OFFSET      0.0   // pH sensor calibration offset

// ============================================
// WiFi Configuration
// ============================================

const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// ============================================
// MQTT Configuration
// ============================================

const char* MQTT_SERVER = "192.168.1.100";
const int MQTT_PORT = 1883;
const char* MQTT_CLIENT_ID = "cropmind_esp32_A";

// ============================================
// Field Configuration
// ============================================

const char* FIELD_ID = "A";

// ============================================
// Timing Configuration
// ============================================

const unsigned long SEND_INTERVAL = 5000;  // 5 seconds

// ============================================
// Global Objects
// ============================================

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
DHT dht(DHT_PIN, DHT_TYPE);

unsigned long lastSendTime = 0;
bool ledState = false;

// ============================================
// Function Prototypes
// ============================================

void setupWiFi();
void setupMQTT();
void reconnectMQTT();
void publishSensorData();
float readTemperature();
float readHumidity();
float readSoilMoisture();
float readPH();
String getTimestamp();
void blinkLED(int count, int delayMs);

// ============================================
// Setup
// ============================================

void setup() {
  Serial.begin(115200);
  Serial.println("\n");
  Serial.println("========================================");
  Serial.println("🌾 CropMind - ESP32 Sensor Firmware");
  Serial.println("========================================");
  
  // Initialize pins
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  // Initialize sensors
  dht.begin();
  Serial.println("[ESP32] ✅ DHT22 initialized");
  
  // Connect to WiFi
  setupWiFi();
  
  // Setup MQTT
  setupMQTT();
  
  Serial.println("[ESP32] ✅ Setup complete");
  Serial.println("========================================");
}

// ============================================
// Main Loop
// ============================================

void loop() {
  // Ensure MQTT connection
  if (!mqttClient.connected()) {
    reconnectMQTT();
  }
  mqttClient.loop();
  
  // Send data at interval
  unsigned long now = millis();
  if (now - lastSendTime >= SEND_INTERVAL) {
    lastSendTime = now;
    publishSensorData();
    blinkLED(1, 50);
  }
}

// ============================================
// WiFi Setup
// ============================================

void setupWiFi() {
  Serial.print("[ESP32] 📶 Connecting to WiFi");
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println(" ✅");
    Serial.print("[ESP32] 📡 IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println(" ❌");
    Serial.println("[ESP32] ⚠️ WiFi connection failed");
  }
}

// ============================================
// MQTT Setup
// ============================================

void setupMQTT() {
  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  mqttClient.setCallback([](char* topic, byte* payload, unsigned int length) {
    // Handle incoming MQTT messages if needed
    // Not used in this firmware
  });
  
  Serial.print("[ESP32] 🔗 Connecting to MQTT broker");
  
  // Try to connect
  int attempts = 0;
  while (!mqttClient.connected() && attempts < 5) {
    if (mqttClient.connect(MQTT_CLIENT_ID)) {
      Serial.println(" ✅");
      Serial.println("[ESP32] ✅ Connected to MQTT broker");
    } else {
      Serial.print(".");
      delay(1000);
      attempts++;
    }
  }
}

// ============================================
// MQTT Reconnection
// ============================================

void reconnectMQTT() {
  Serial.println("[ESP32] 🔄 Reconnecting to MQTT...");
  
  if (mqttClient.connect(MQTT_CLIENT_ID)) {
    Serial.println("[ESP32] ✅ Reconnected to MQTT broker");
    blinkLED(2, 100);
  } else {
    Serial.print("[ESP32] ⚠️ MQTT reconnect failed, rc=");
    Serial.println(mqttClient.state());
    delay(1000);
  }
}

// ============================================
// Publish Sensor Data
// ============================================

void publishSensorData() {
  // Read sensors
  float temperature = readTemperature();
  float humidity = readHumidity();
  float soilMoisture = readSoilMoisture();
  float ph = readPH();
  String timestamp = getTimestamp();
  
  // Check if readings are valid
  bool hasError = false;
  
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("[ESP32] ⚠️ DHT22 read error");
    hasError = true;
  }
  
  if (isnan(soilMoisture)) {
    Serial.println("[ESP32] ⚠️ Soil moisture read error");
    hasError = true;
  }
  
  if (isnan(ph)) {
    Serial.println("[ESP32] ⚠️ pH sensor read error");
    hasError = true;
  }
  
  // Publish each sensor reading
  // Temperature
  if (!isnan(temperature)) {
    StaticJsonDocument<64> doc;
    doc["value"] = temperature;
    doc["timestamp"] = timestamp;
    
    String topic = "cropmind/field/" + String(FIELD_ID) + "/temperature";
    String payload;
    serializeJson(doc, payload);
    
    if (mqttClient.publish(topic.c_str(), payload.c_str())) {
      Serial.print("[ESP32] 📤 temperature: ");
      Serial.println(temperature);
    } else {
      Serial.println("[ESP32] ❌ Failed to publish temperature");
    }
  }
  
  // Humidity
  if (!isnan(humidity)) {
    StaticJsonDocument<64> doc;
    doc["value"] = humidity;
    doc["timestamp"] = timestamp;
    
    String topic = "cropmind/field/" + String(FIELD_ID) + "/humidity";
    String payload;
    serializeJson(doc, payload);
    
    if (mqttClient.publish(topic.c_str(), payload.c_str())) {
      Serial.print("[ESP32] 📤 humidity: ");
      Serial.println(humidity);
    } else {
      Serial.println("[ESP32] ❌ Failed to publish humidity");
    }
  }
  
  // Soil Moisture
  if (!isnan(soilMoisture)) {
    StaticJsonDocument<64> doc;
    doc["value"] = soilMoisture;
    doc["timestamp"] = timestamp;
    
    String topic = "cropmind/field/" + String(FIELD_ID) + "/soil_moisture";
    String payload;
    serializeJson(doc, payload);
    
    if (mqttClient.publish(topic.c_str(), payload.c_str())) {
      Serial.print("[ESP32] 📤 soil_moisture: ");
      Serial.println(soilMoisture);
    } else {
      Serial.println("[ESP32] ❌ Failed to publish soil_moisture");
    }
  }
  
  // pH
  if (!isnan(ph)) {
    StaticJsonDocument<64> doc;
    doc["value"] = ph;
    doc["timestamp"] = timestamp;
    
    String topic = "cropmind/field/" + String(FIELD_ID) + "/ph";
    String payload;
    serializeJson(doc, payload);
    
    if (mqttClient.publish(topic.c_str(), payload.c_str())) {
      Serial.print("[ESP32] 📤 ph: ");
      Serial.println(ph);
    } else {
      Serial.println("[ESP32] ❌ Failed to publish ph");
    }
  }
  
  Serial.println("[ESP32] ✅ Data published");
}

// ============================================
// Sensor Reading Functions
// ============================================

float readTemperature() {
  return dht.readTemperature();
}

float readHumidity() {
  return dht.readHumidity();
}

float readSoilMoisture() {
  int raw = analogRead(SOIL_PIN);
  
  // Map raw value (0-4095) to percentage (0-100%)
  // Higher analog value = drier soil
  float percentage = map(raw, SOIL_DRY, SOIL_WET, 0, 100);
  percentage = constrain(percentage, 0, 100);
  
  return percentage;
}

float readPH() {
  int raw = analogRead(PH_PIN);
  
  // Convert raw ADC value to pH (approximate)
  // pH = raw / 4095 * 14 + offset
  float ph = (raw / 4095.0) * 14.0 + PH_OFFSET;
  ph = constrain(ph, 0, 14);
  
  return ph;
}

// ============================================
// Utility Functions
// ============================================

String getTimestamp() {
  // Get current time from NTP or use elapsed time
  // For now, return a placeholder
  return "2026-01-01T00:00:00";
  
  // Note: For real time, uncomment the following code
  /*
  time_t now = time(nullptr);
  struct tm timeinfo;
  gmtime_r(&now, &timeinfo);
  
  char buffer[25];
  strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%S", &timeinfo);
  return String(buffer);
  */
}

void blinkLED(int count, int delayMs) {
  for (int i = 0; i < count; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(delayMs);
    digitalWrite(LED_PIN, LOW);
    if (i < count - 1) {
      delay(delayMs);
    }
  }
}
