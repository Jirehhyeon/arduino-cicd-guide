/*
 * Arduino IoT Temperature Monitoring System
 * 
 * 설명: DHT22 센서를 사용한 온도/습도 모니터링 시스템
 * 작성자: Arduino CI/CD Team
 * 생성일: 2024-01-01
 * 버전: 1.0.0
 * 
 * 기능:
 * - DHT22 센서를 통한 온도/습도 측정
 * - WiFi를 통한 데이터 전송
 * - MQTT를 통한 실시간 데이터 스트리밍
 * - 웹 API를 통한 상태 모니터링
 * - 자동 재연결 및 오류 복구
 */

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <WebServer.h>
#include <time.h>

// ===== 하드웨어 설정 =====
#define DHT_PIN 2
#define DHT_TYPE DHT22
#define LED_STATUS 13
#define LED_ERROR 12
#define BUTTON_RESET 0

// ===== 네트워크 설정 =====
const char* WIFI_SSID = "YourWiFiSSID";
const char* WIFI_PASSWORD = "YourWiFiPassword";
const char* MQTT_SERVER = "your-mqtt-broker.com";
const int MQTT_PORT = 1883;
const char* MQTT_USER = "arduino_device";
const char* MQTT_PASSWORD = "device_password";

// ===== MQTT 토픽 설정 =====
const char* TOPIC_TEMPERATURE = "sensors/temperature";
const char* TOPIC_HUMIDITY = "sensors/humidity";
const char* TOPIC_STATUS = "sensors/status";
const char* TOPIC_COMMANDS = "sensors/commands";

// ===== 타이밍 설정 =====
const unsigned long SENSOR_INTERVAL = 10000;  // 10초마다 센서 읽기
const unsigned long MQTT_INTERVAL = 30000;    // 30초마다 MQTT 전송
const unsigned long STATUS_INTERVAL = 60000;  // 1분마다 상태 보고
const unsigned long WIFI_TIMEOUT = 30000;     // WiFi 연결 타임아웃
const unsigned long MQTT_TIMEOUT = 10000;     // MQTT 연결 타임아웃

// ===== 전역 객체 =====
DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
WebServer webServer(80);

// ===== 전역 변수 =====
struct SensorData {
    float temperature;
    float humidity;
    float heatIndex;
    unsigned long timestamp;
    bool valid;
};

struct SystemStatus {
    bool wifiConnected;
    bool mqttConnected;
    bool sensorOnline;
    unsigned long uptime;
    unsigned long lastSensorRead;
    unsigned long lastMqttSend;
    int wifiRssi;
    String lastError;
};

SensorData currentReading = {0};
SystemStatus systemStatus = {false, false, false, 0, 0, 0, 0, ""};

unsigned long lastSensorRead = 0;
unsigned long lastMqttSend = 0;
unsigned long lastStatusUpdate = 0;
unsigned long lastReconnectAttempt = 0;

String deviceId;
String firmwareVersion = "1.0.0";

// ===== 함수 선언 =====
void setup();
void loop();
void initializeSystem();
void initializeHardware();
void initializeWiFi();
void initializeMQTT();
void initializeWebServer();
void generateDeviceId();

void handleSensorReading();
void handleMqttCommunication();
void handleWebRequests();
void handleSystemStatus();
void handleReconnection();

bool readSensorData(SensorData& data);
void publishSensorData(const SensorData& data);
void publishSystemStatus();
void updateSystemStatus();

void onMqttMessage(char* topic, byte* payload, unsigned int length);
void setupWebRoutes();
void handleWebRoot();
void handleWebStatus();
void handleWebData();
void handleWebConfig();

void connectWiFi();
void connectMQTT();
bool isWiFiConnected();
bool isMqttConnected();

void indicateStatus();
void indicateError(const String& error);
void logMessage(const String& message);
void logError(const String& error);

String formatSensorDataJson(const SensorData& data);
String formatStatusJson();
float calculateHeatIndex(float temperature, float humidity);

/**
 * 시스템 초기화
 */
void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 5000) {
        delay(10);
    }
    
    logMessage("=== Arduino IoT Temperature Monitor Starting ===");
    logMessage("Firmware Version: " + firmwareVersion);
    
    initializeSystem();
    
    logMessage("System initialized successfully!");
    logMessage("Device ID: " + deviceId);
    logMessage("Free heap: " + String(ESP.getFreeHeap()) + " bytes");
}

/**
 * 메인 루프
 */
void loop() {
    // 시스템 상태 업데이트
    updateSystemStatus();
    
    // 주요 작업들
    handleSensorReading();
    handleMqttCommunication();
    handleWebRequests();
    handleSystemStatus();
    handleReconnection();
    
    // 상태 표시
    indicateStatus();
    
    // CPU 사용률 조절
    delay(100);
}

/**
 * 시스템 전체 초기화
 */
void initializeSystem() {
    generateDeviceId();
    initializeHardware();
    initializeWiFi();
    initializeMQTT();
    initializeWebServer();
    
    logMessage("All subsystems initialized");
}

/**
 * 하드웨어 초기화
 */
void initializeHardware() {
    // LED 핀 설정
    pinMode(LED_STATUS, OUTPUT);
    pinMode(LED_ERROR, OUTPUT);
    pinMode(BUTTON_RESET, INPUT_PULLUP);
    
    // 초기 LED 상태
    digitalWrite(LED_STATUS, LOW);
    digitalWrite(LED_ERROR, LOW);
    
    // DHT 센서 초기화
    dht.begin();
    delay(2000); // DHT 센서 안정화 대기
    
    // 시간 동기화 설정
    configTime(9 * 3600, 0, "pool.ntp.org"); // KST (UTC+9)
    
    logMessage("Hardware initialized");
}

/**
 * WiFi 초기화
 */
void initializeWiFi() {
    WiFi.mode(WIFI_STA);
    WiFi.setHostname(deviceId.c_str());
    connectWiFi();
}

/**
 * MQTT 초기화
 */
void initializeMQTT() {
    mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
    mqttClient.setCallback(onMqttMessage);
    mqttClient.setKeepAlive(60);
    connectMQTT();
}

/**
 * 웹 서버 초기화
 */
void initializeWebServer() {
    setupWebRoutes();
    webServer.begin();
    logMessage("Web server started on port 80");
}

/**
 * 디바이스 ID 생성
 */
void generateDeviceId() {
    uint64_t chipId = ESP.getEfuseMac();
    deviceId = "ARDUINO_" + String((uint32_t)chipId, HEX);
    deviceId.toUpperCase();
}

/**
 * 센서 데이터 읽기 처리
 */
void handleSensorReading() {
    if (millis() - lastSensorRead >= SENSOR_INTERVAL) {
        SensorData newReading;
        
        if (readSensorData(newReading)) {
            currentReading = newReading;
            systemStatus.sensorOnline = true;
            systemStatus.lastSensorRead = millis();
            
            logMessage("Sensor read: T=" + String(currentReading.temperature, 1) + 
                      "°C, H=" + String(currentReading.humidity, 1) + "%");
        } else {
            systemStatus.sensorOnline = false;
            indicateError("Sensor read failed");
        }
        
        lastSensorRead = millis();
    }
}

/**
 * MQTT 통신 처리
 */
void handleMqttCommunication() {
    // MQTT 클라이언트 루프 처리
    if (mqttClient.connected()) {
        mqttClient.loop();
        systemStatus.mqttConnected = true;
        
        // 주기적 데이터 전송
        if (millis() - lastMqttSend >= MQTT_INTERVAL && currentReading.valid) {
            publishSensorData(currentReading);
            lastMqttSend = millis();
            systemStatus.lastMqttSend = millis();
        }
    } else {
        systemStatus.mqttConnected = false;
    }
}

/**
 * 웹 요청 처리
 */
void handleWebRequests() {
    webServer.handleClient();
}

/**
 * 시스템 상태 처리
 */
void handleSystemStatus() {
    if (millis() - lastStatusUpdate >= STATUS_INTERVAL) {
        publishSystemStatus();
        lastStatusUpdate = millis();
        
        // 메모리 사용량 체크
        if (ESP.getFreeHeap() < 10000) {
            indicateError("Low memory warning: " + String(ESP.getFreeHeap()));
        }
    }
}

/**
 * 재연결 처리
 */
void handleReconnection() {
    // WiFi 재연결
    if (!isWiFiConnected() && millis() - lastReconnectAttempt >= 30000) {
        logMessage("Attempting WiFi reconnection...");
        connectWiFi();
        lastReconnectAttempt = millis();
    }
    
    // MQTT 재연결
    if (isWiFiConnected() && !isMqttConnected() && millis() - lastReconnectAttempt >= 10000) {
        logMessage("Attempting MQTT reconnection...");
        connectMQTT();
        lastReconnectAttempt = millis();
    }
}

/**
 * 센서 데이터 읽기
 */
bool readSensorData(SensorData& data) {
    float temp = dht.readTemperature();
    float hum = dht.readHumidity();
    
    // 유효성 검사
    if (isnan(temp) || isnan(hum)) {
        data.valid = false;
        return false;
    }
    
    // 범위 검사
    if (temp < -40 || temp > 85 || hum < 0 || hum > 100) {
        data.valid = false;
        return false;
    }
    
    // 데이터 저장
    data.temperature = temp;
    data.humidity = hum;
    data.heatIndex = calculateHeatIndex(temp, hum);
    data.timestamp = millis();
    data.valid = true;
    
    return true;
}

/**
 * 센서 데이터 MQTT 전송
 */
void publishSensorData(const SensorData& data) {
    if (!mqttClient.connected()) return;
    
    String jsonData = formatSensorDataJson(data);
    
    // 개별 토픽으로 전송
    mqttClient.publish(TOPIC_TEMPERATURE, String(data.temperature, 2).c_str());
    mqttClient.publish(TOPIC_HUMIDITY, String(data.humidity, 2).c_str());
    
    // 통합 JSON 데이터 전송
    String deviceTopic = "sensors/" + deviceId + "/data";
    mqttClient.publish(deviceTopic.c_str(), jsonData.c_str());
    
    logMessage("Data published to MQTT");
}

/**
 * 시스템 상태 MQTT 전송
 */
void publishSystemStatus() {
    if (!mqttClient.connected()) return;
    
    String statusJson = formatStatusJson();
    String statusTopic = "sensors/" + deviceId + "/status";
    
    mqttClient.publish(statusTopic.c_str(), statusJson.c_str());
    mqttClient.publish(TOPIC_STATUS, statusJson.c_str());
}

/**
 * 시스템 상태 업데이트
 */
void updateSystemStatus() {
    systemStatus.wifiConnected = isWiFiConnected();
    systemStatus.mqttConnected = isMqttConnected();
    systemStatus.uptime = millis();
    systemStatus.wifiRssi = WiFi.RSSI();
}

/**
 * MQTT 메시지 수신 콜백
 */
void onMqttMessage(char* topic, byte* payload, unsigned int length) {
    String message = "";
    for (unsigned int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    logMessage("MQTT received: " + String(topic) + " = " + message);
    
    // 명령 처리
    if (String(topic) == TOPIC_COMMANDS + "/" + deviceId) {
        if (message == "restart") {
            logMessage("Restart command received");
            ESP.restart();
        } else if (message == "status") {
            publishSystemStatus();
        } else if (message == "read_sensor") {
            handleSensorReading();
        }
    }
}

/**
 * 웹 라우트 설정
 */
void setupWebRoutes() {
    webServer.on("/", handleWebRoot);
    webServer.on("/status", handleWebStatus);
    webServer.on("/data", handleWebData);
    webServer.on("/config", handleWebConfig);
    
    webServer.onNotFound([]() {
        webServer.send(404, "text/plain", "Not found");
    });
}

/**
 * 웹 루트 페이지
 */
void handleWebRoot() {
    String html = R"(
<!DOCTYPE html>
<html>
<head>
    <title>Arduino Temperature Monitor</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; margin: 40px; background-color: #f0f0f0; }
        .container { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
        .status { display: flex; justify-content: space-between; margin: 20px 0; }
        .card { background: #f9f9f9; padding: 15px; border-radius: 5px; text-align: center; min-width: 120px; }
        .value { font-size: 24px; font-weight: bold; color: #4CAF50; }
        .unit { font-size: 14px; color: #666; }
        .refresh { margin-top: 20px; }
        button { background: #4CAF50; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
        button:hover { background: #45a049; }
    </style>
    <script>
        function refreshData() {
            fetch('/data')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('temperature').textContent = data.temperature.toFixed(1);
                    document.getElementById('humidity').textContent = data.humidity.toFixed(1);
                    document.getElementById('heat-index').textContent = data.heatIndex.toFixed(1);
                    document.getElementById('last-update').textContent = new Date(data.timestamp).toLocaleString();
                })
                .catch(error => console.error('Error:', error));
        }
        
        setInterval(refreshData, 10000); // 10초마다 자동 갱신
    </script>
</head>
<body>
    <div class="container">
        <h1 class="header">🌡️ Arduino Temperature Monitor</h1>
        
        <div class="status">
            <div class="card">
                <div class="value" id="temperature">)" + String(currentReading.temperature, 1) + R"(</div>
                <div class="unit">°C</div>
                <div>Temperature</div>
            </div>
            
            <div class="card">
                <div class="value" id="humidity">)" + String(currentReading.humidity, 1) + R"(</div>
                <div class="unit">%</div>
                <div>Humidity</div>
            </div>
            
            <div class="card">
                <div class="value" id="heat-index">)" + String(currentReading.heatIndex, 1) + R"(</div>
                <div class="unit">°C</div>
                <div>Heat Index</div>
            </div>
        </div>
        
        <div class="refresh">
            <button onclick="refreshData()">🔄 Refresh Data</button>
            <button onclick="window.location.href='/status'">📊 System Status</button>
        </div>
        
        <p><small>Last update: <span id="last-update">)" + String(millis()) + R"(</span></small></p>
        <p><small>Device ID: )" + deviceId + R"(</small></p>
        <p><small>Firmware: v)" + firmwareVersion + R"(</small></p>
    </div>
</body>
</html>
)";
    
    webServer.send(200, "text/html", html);
}

/**
 * 웹 상태 페이지
 */
void handleWebStatus() {
    String json = formatStatusJson();
    webServer.send(200, "application/json", json);
}

/**
 * 웹 데이터 API
 */
void handleWebData() {
    String json = formatSensorDataJson(currentReading);
    webServer.send(200, "application/json", json);
}

/**
 * 웹 설정 페이지
 */
void handleWebConfig() {
    webServer.send(200, "text/plain", "Configuration interface - TODO");
}

/**
 * WiFi 연결
 */
void connectWiFi() {
    logMessage("Connecting to WiFi: " + String(WIFI_SSID));
    
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    unsigned long startTime = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - startTime < WIFI_TIMEOUT) {
        delay(500);
        Serial.print(".");
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        systemStatus.wifiConnected = true;
        logMessage("WiFi connected!");
        logMessage("IP address: " + WiFi.localIP().toString());
        logMessage("RSSI: " + String(WiFi.RSSI()) + " dBm");
    } else {
        systemStatus.wifiConnected = false;
        indicateError("WiFi connection failed");
    }
}

/**
 * MQTT 연결
 */
void connectMQTT() {
    if (!isWiFiConnected()) return;
    
    logMessage("Connecting to MQTT: " + String(MQTT_SERVER));
    
    String clientId = deviceId + "_" + String(millis());
    
    if (mqttClient.connect(clientId.c_str(), MQTT_USER, MQTT_PASSWORD)) {
        systemStatus.mqttConnected = true;
        logMessage("MQTT connected!");
        
        // 명령 토픽 구독
        String commandTopic = String(TOPIC_COMMANDS) + "/" + deviceId;
        mqttClient.subscribe(commandTopic.c_str());
        
        // 온라인 상태 발행
        publishSystemStatus();
    } else {
        systemStatus.mqttConnected = false;
        indicateError("MQTT connection failed, state: " + String(mqttClient.state()));
    }
}

/**
 * WiFi 연결 상태 확인
 */
bool isWiFiConnected() {
    return WiFi.status() == WL_CONNECTED;
}

/**
 * MQTT 연결 상태 확인
 */
bool isMqttConnected() {
    return mqttClient.connected();
}

/**
 * 상태 표시 (LED)
 */
void indicateStatus() {
    static unsigned long lastBlink = 0;
    static bool ledState = false;
    
    if (millis() - lastBlink >= 1000) {
        if (systemStatus.wifiConnected && systemStatus.mqttConnected && systemStatus.sensorOnline) {
            // 모든 시스템 정상 - 천천히 깜빡임
            ledState = !ledState;
            digitalWrite(LED_STATUS, ledState);
            digitalWrite(LED_ERROR, LOW);
        } else if (systemStatus.wifiConnected) {
            // WiFi만 연결됨 - 빠르게 깜빡임
            ledState = !ledState;
            digitalWrite(LED_STATUS, ledState);
            digitalWrite(LED_ERROR, LOW);
        } else {
            // WiFi 연결 안됨 - 오류 표시
            digitalWrite(LED_STATUS, LOW);
            digitalWrite(LED_ERROR, HIGH);
        }
        
        lastBlink = millis();
    }
}

/**
 * 오류 표시
 */
void indicateError(const String& error) {
    systemStatus.lastError = error;
    logError(error);
    
    // 오류 LED 점등
    digitalWrite(LED_ERROR, HIGH);
    digitalWrite(LED_STATUS, LOW);
}

/**
 * 로그 메시지 출력
 */
void logMessage(const String& message) {
    Serial.println("[INFO] " + String(millis()) + "ms: " + message);
}

/**
 * 로그 오류 출력
 */
void logError(const String& error) {
    Serial.println("[ERROR] " + String(millis()) + "ms: " + error);
}

/**
 * 센서 데이터 JSON 포맷
 */
String formatSensorDataJson(const SensorData& data) {
    StaticJsonDocument<200> doc;
    
    doc["deviceId"] = deviceId;
    doc["timestamp"] = data.timestamp;
    doc["temperature"] = round(data.temperature * 100) / 100.0;
    doc["humidity"] = round(data.humidity * 100) / 100.0;
    doc["heatIndex"] = round(data.heatIndex * 100) / 100.0;
    doc["valid"] = data.valid;
    
    String jsonString;
    serializeJson(doc, jsonString);
    return jsonString;
}

/**
 * 시스템 상태 JSON 포맷
 */
String formatStatusJson() {
    StaticJsonDocument<400> doc;
    
    doc["deviceId"] = deviceId;
    doc["firmware"] = firmwareVersion;
    doc["uptime"] = systemStatus.uptime;
    doc["freeHeap"] = ESP.getFreeHeap();
    doc["wifiConnected"] = systemStatus.wifiConnected;
    doc["wifiRssi"] = systemStatus.wifiRssi;
    doc["mqttConnected"] = systemStatus.mqttConnected;
    doc["sensorOnline"] = systemStatus.sensorOnline;
    doc["lastSensorRead"] = systemStatus.lastSensorRead;
    doc["lastMqttSend"] = systemStatus.lastMqttSend;
    doc["lastError"] = systemStatus.lastError;
    
    if (isWiFiConnected()) {
        doc["ipAddress"] = WiFi.localIP().toString();
        doc["macAddress"] = WiFi.macAddress();
    }
    
    String jsonString;
    serializeJson(doc, jsonString);
    return jsonString;
}

/**
 * 체감온도 계산 (Heat Index)
 */
float calculateHeatIndex(float temperature, float humidity) {
    if (temperature < 27) {
        return temperature; // 체감온도는 27°C 이상에서만 의미있음
    }
    
    float t = temperature;
    float h = humidity;
    
    float hi = -8.78469475556 +
               1.61139411 * t +
               2.33854883889 * h +
               -0.14611605 * t * h +
               -0.012308094 * t * t +
               -0.0164248277778 * h * h +
               0.002211732 * t * t * h +
               0.00072546 * t * h * h +
               -0.000003582 * t * t * h * h;
    
    return hi;
}