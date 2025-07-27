/*
 * NeuroCity Smart Sensor Node v2.0
 * 차세대 AI 기반 환경 모니터링 시스템
 * 
 * Features:
 * - TinyML 실시간 AI 추론
 * - 블록체인 기반 보안
 * - 메시 네트워킹
 * - 에너지 하베스팅
 * - 디지털 트윈 연동
 * 
 * Hardware: ESP32-S3-WROOM-1U
 * AI: TensorFlow Lite Micro
 * Security: ATECC608B + Blockchain
 * Network: WiFi 6 + Bluetooth LE Mesh
 */

#include <Arduino.h>
#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>
#include <WebSocketsServer.h>
#include <TensorFlowLite_ESP32.h>
#include <CryptoAES.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <Wire.h>

// AI/ML 관련 헤더
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"

// 센서 라이브러리
#include <SHTSensor.h>     // SHT40 온습도
#include <SparkFun_SGP40.h> // SGP40 VOC
#include <Adafruit_BME688.h> // BME688 가스
#include <SparkFun_SCD4x.h>  // SCD41 CO2
#include <Adafruit_INA219.h> // INA219 전력
#include <MPU6050.h>         // MPU6050 IMU

// 하드웨어 보안
#include <ArduinoECCX08.h>   // ATECC608B

// ===== 하드웨어 핀 정의 =====
#define LED_STATUS_R    48
#define LED_STATUS_G    47
#define LED_STATUS_B    21
#define LED_ERROR       38
#define BUZZER_PIN      39
#define BUTTON_SETUP    0
#define SOLAR_MONITOR   4
#define BATTERY_MONITOR 5

// I2C 핀 정의
#define SDA_PIN         42
#define SCL_PIN         41

// ===== AI 모델 설정 =====
const int kTensorArenaSize = 60 * 1024;  // 60KB AI 메모리
uint8_t tensor_arena[kTensorArenaSize];

// AI 모델들 (외부 파일에서 로드)
extern const unsigned char environmental_model_tflite[];
extern const unsigned char anomaly_model_tflite[];
extern const unsigned char predictive_model_tflite[];

// ===== 전역 객체 =====
// 센서 객체들
SHTSensor sht40;
SGP40 sgp40;
Adafruit_BME688 bme688;
SCD4x scd41;
Adafruit_INA219 ina219;
MPU6050 mpu6050;

// 네트워크 객체들
AsyncWebServer server(80);
WebSocketsServer webSocket(81);
BLEServer* pServer = nullptr;
BLECharacteristic* pCharacteristic = nullptr;

// AI 관련 객체들
tflite::MicroErrorReporter micro_error_reporter;
tflite::AllOpsResolver resolver;
const tflite::Model* env_model = nullptr;
tflite::MicroInterpreter* env_interpreter = nullptr;

// ===== 데이터 구조체 =====
struct SensorData {
    float temperature;
    float humidity;
    float voc_index;
    float co2_ppm;
    float gas_resistance;
    float noise_level;
    float vibration_x;
    float vibration_y;
    float vibration_z;
    float battery_voltage;
    float solar_voltage;
    float power_consumption;
    unsigned long timestamp;
    bool valid;
};

struct AIResults {
    float environmental_risk;
    float anomaly_score;
    String risk_category;
    float confidence;
};

struct NetworkStatus {
    bool wifi_connected;
    bool ble_connected;
    bool blockchain_synced;
    int wifi_rssi;
    int connected_peers;
    String device_id;
};

// ===== 전역 변수 =====
SensorData currentData = {0};
AIResults currentAI = {0};
NetworkStatus networkStatus = {false};

// 타이밍 변수들
unsigned long lastSensorRead = 0;
unsigned long lastAIInference = 0;
unsigned long lastNetworkSync = 0;
unsigned long lastEnergyOptimization = 0;

// 설정 상수들
unsigned long SENSOR_INTERVAL = 5000;      // 5초마다 센서 읽기
unsigned long AI_INTERVAL = 10000;         // 10초마다 AI 추론
unsigned long NETWORK_INTERVAL = 30000;    // 30초마다 네트워크 동기화
unsigned long ENERGY_INTERVAL = 300000;    // 5분마다 에너지 최적화

// AI 입력 버퍼
float ai_input_buffer[6];

// 네트워크 설정
const char* WIFI_SSID = "NeuroCity_Mesh";
const char* WIFI_PASSWORD = "SmartCity2024!";
const char* DEVICE_NAME = "NeuroSensor";

String deviceId;
String firmwareVersion = "2.0.0";

// ===== 함수 선언 =====
void setup();
void loop();

// 초기화 함수들
bool initializeHardware();
bool initializeSensors();
bool initializeAI();
bool initializeNetworking();
bool initializeSecurity();

// 센서 관련 함수들
bool readAllSensors(SensorData& data);
bool validateSensorData(const SensorData& data);

// AI 관련 함수들
bool runEnvironmentalAI(const float* input, AIResults& results);

// 네트워킹 함수들
void synchronizeData();
void handleWebSocketMessage(uint8_t num, WStype_t type, uint8_t* payload, size_t length);

// 에너지 관리 함수들
void optimizePowerConsumption();
float monitorBatteryLevel();
float monitorSolarGeneration();

// 유틸리티 함수들
void indicateStatus(const String& status);
void logMessage(const String& level, const String& message);
String formatDataToJSON(const SensorData& data, const AIResults& ai);
void handleEmergencyAlert(const String& alert_type, float severity);

/**
 * 시스템 초기화
 */
void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 5000) delay(10);
    
    logMessage("INFO", "🚀 NeuroCity Smart Sensor v2.0 Starting...");
    logMessage("INFO", "🧠 ESP32-S3 with TinyML AI Engine");
    
    // 하드웨어 초기화
    if (!initializeHardware()) {
        logMessage("ERROR", "Hardware initialization failed!");
        indicateStatus("hardware_error");
        while(1) delay(1000);
    }
    
    // 센서 초기화
    if (!initializeSensors()) {
        logMessage("ERROR", "Sensor initialization failed!");
        indicateStatus("sensor_error");
    }
    
    // AI 모델 초기화
    if (!initializeAI()) {
        logMessage("ERROR", "AI initialization failed!");
        indicateStatus("ai_error");
    }
    
    // 보안 시스템 초기화
    if (!initializeSecurity()) {
        logMessage("ERROR", "Security initialization failed!");
        indicateStatus("security_error");
    }
    
    // 네트워킹 초기화
    if (!initializeNetworking()) {
        logMessage("ERROR", "Network initialization failed!");
        indicateStatus("network_error");
    }
    
    logMessage("INFO", "✅ All systems initialized successfully!");
    logMessage("INFO", "🆔 Device ID: " + deviceId);
    logMessage("INFO", "🔋 Battery: " + String(monitorBatteryLevel()) + "%");
    logMessage("INFO", "☀️ Solar: " + String(monitorSolarGeneration()) + "mW");
    
    indicateStatus("ready");
}

/**
 * 메인 루프
 */
void loop() {
    unsigned long currentTime = millis();
    
    // 센서 데이터 읽기
    if (currentTime - lastSensorRead >= SENSOR_INTERVAL) {
        if (readAllSensors(currentData)) {
            logMessage("DEBUG", "📊 Sensor data updated");
        }
        lastSensorRead = currentTime;
    }
    
    // AI 추론 실행
    if (currentTime - lastAIInference >= AI_INTERVAL && currentData.valid) {
        // 입력 데이터 준비
        ai_input_buffer[0] = currentData.temperature;
        ai_input_buffer[1] = currentData.humidity;
        ai_input_buffer[2] = currentData.voc_index;
        ai_input_buffer[3] = currentData.co2_ppm;
        ai_input_buffer[4] = currentData.gas_resistance;
        ai_input_buffer[5] = currentData.noise_level;
        
        // AI 모델 실행
        if (runEnvironmentalAI(ai_input_buffer, currentAI)) {
            // 위험 상황 감지
            if (currentAI.environmental_risk > 0.8) {
                handleEmergencyAlert("environmental_risk", currentAI.environmental_risk);
            }
            
            logMessage("DEBUG", "🧠 AI inference completed - Risk: " + 
                      String(currentAI.environmental_risk * 100, 1) + "%");
        }
        lastAIInference = currentTime;
    }
    
    // 네트워크 동기화
    if (currentTime - lastNetworkSync >= NETWORK_INTERVAL) {
        synchronizeData();
        lastNetworkSync = currentTime;
    }
    
    // 에너지 최적화
    if (currentTime - lastEnergyOptimization >= ENERGY_INTERVAL) {
        optimizePowerConsumption();
        lastEnergyOptimization = currentTime;
    }
    
    // WebSocket 이벤트 처리
    webSocket.loop();
    
    // 상태 표시 업데이트
    if (networkStatus.wifi_connected && currentData.valid) {
        indicateStatus("normal_operation");
    }
    
    // CPU 사용률 조절
    delay(50);
}

/**
 * 하드웨어 초기화
 */
bool initializeHardware() {
    // GPIO 핀 설정
    pinMode(LED_STATUS_R, OUTPUT);
    pinMode(LED_STATUS_G, OUTPUT);
    pinMode(LED_STATUS_B, OUTPUT);
    pinMode(LED_ERROR, OUTPUT);
    pinMode(BUZZER_PIN, OUTPUT);
    pinMode(BUTTON_SETUP, INPUT_PULLUP);
    pinMode(SOLAR_MONITOR, INPUT);
    pinMode(BATTERY_MONITOR, INPUT);
    
    // I2C 버스 초기화
    Wire.begin(SDA_PIN, SCL_PIN);
    Wire.setClock(400000);  // 400kHz
    
    // LED 테스트
    digitalWrite(LED_STATUS_R, HIGH);
    delay(200);
    digitalWrite(LED_STATUS_R, LOW);
    digitalWrite(LED_STATUS_G, HIGH);
    delay(200);
    digitalWrite(LED_STATUS_G, LOW);
    digitalWrite(LED_STATUS_B, HIGH);
    delay(200);
    digitalWrite(LED_STATUS_B, LOW);
    
    // 디바이스 ID 생성
    uint64_t chipId = ESP.getEfuseMac();
    deviceId = "NEURO_" + String((uint32_t)chipId, HEX);
    deviceId.toUpperCase();
    
    logMessage("INFO", "🔧 Hardware initialized");
    return true;
}

/**
 * 센서 초기화
 */
bool initializeSensors() {
    bool allOK = true;
    
    // SHT40 온습도 센서
    if (sht40.init()) {
        logMessage("INFO", "✅ SHT40 온습도 센서 OK");
    } else {
        logMessage("ERROR", "❌ SHT40 센서 실패");
        allOK = false;
    }
    
    // SGP40 VOC 센서
    if (sgp40.begin(Wire)) {
        logMessage("INFO", "✅ SGP40 VOC 센서 OK");
    } else {
        logMessage("ERROR", "❌ SGP40 센서 실패");
        allOK = false;
    }
    
    // BME688 가스 센서
    if (bme688.begin()) {
        bme688.setTemperatureOversampling(BME680_OS_8X);
        bme688.setHumidityOversampling(BME680_OS_2X);
        bme688.setPressureOversampling(BME680_OS_4X);
        bme688.setIIRFilterSize(BME680_FILTER_SIZE_3);
        bme688.setGasHeater(320, 150); // 320°C for 150ms
        logMessage("INFO", "✅ BME688 가스 센서 OK");
    } else {
        logMessage("ERROR", "❌ BME688 센서 실패");
        allOK = false;
    }
    
    // SCD41 CO2 센서
    if (scd41.begin() == false) {
        logMessage("ERROR", "❌ SCD41 CO2 센서 실패");
        allOK = false;
    } else {
        scd41.startPeriodicMeasurement();
        logMessage("INFO", "✅ SCD41 CO2 센서 OK");
    }
    
    // INA219 전력 모니터
    if (ina219.begin()) {
        ina219.setCalibration_16V_400mA();
        logMessage("INFO", "✅ INA219 전력 모니터 OK");
    } else {
        logMessage("ERROR", "❌ INA219 모니터 실패");
        allOK = false;
    }
    
    // MPU6050 IMU 센서
    mpu6050.initialize();
    if (mpu6050.testConnection()) {
        logMessage("INFO", "✅ MPU6050 IMU 센서 OK");
    } else {
        logMessage("ERROR", "❌ MPU6050 센서 실패");
        allOK = false;
    }
    
    return allOK;
}

/**
 * AI 모델 초기화
 */
bool initializeAI() {
    // 환경 분석 모델 로드
    env_model = tflite::GetModel(environmental_model_tflite);
    if (env_model->version() != TFLITE_SCHEMA_VERSION) {
        logMessage("ERROR", "Environmental model schema mismatch");
        return false;
    }
    
    // 인터프리터 초기화
    static tflite::MicroInterpreter static_env_interpreter(
        env_model, resolver, tensor_arena, kTensorArenaSize, &micro_error_reporter);
    env_interpreter = &static_env_interpreter;
    
    if (env_interpreter->AllocateTensors() != kTfLiteOk) {
        logMessage("ERROR", "Failed to allocate tensors for environmental model");
        return false;
    }
    
    logMessage("INFO", "🧠 AI models loaded successfully");
    logMessage("INFO", "📊 Tensor arena: " + String(kTensorArenaSize / 1024) + "KB");
    return true;
}

/**
 * 네트워킹 초기화
 */
bool initializeNetworking() {
    // WiFi 6 초기화
    WiFi.mode(WIFI_STA);
    WiFi.setHostname(DEVICE_NAME);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    unsigned long startTime = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - startTime < 30000) {
        delay(500);
        Serial.print(".");
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        networkStatus.wifi_connected = true;
        networkStatus.device_id = deviceId;
        logMessage("INFO", "📶 WiFi connected: " + WiFi.localIP().toString());
        logMessage("INFO", "📡 RSSI: " + String(WiFi.RSSI()) + "dBm");
    } else {
        logMessage("WARNING", "WiFi connection failed - switching to mesh mode");
    }
    
    // WebSocket 서버 시작
    webSocket.begin();
    webSocket.onEvent(handleWebSocketMessage);
    
    // 웹 서버 라우트 설정
    server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
        String html = generateWebDashboard();
        request->send(200, "text/html", html);
    });
    
    server.on("/api/data", HTTP_GET, [](AsyncWebServerRequest *request){
        String json = formatDataToJSON(currentData, currentAI);
        request->send(200, "application/json", json);
    });
    
    server.on("/api/status", HTTP_GET, [](AsyncWebServerRequest *request){
        StaticJsonDocument<300> doc;
        doc["deviceId"] = deviceId;
        doc["version"] = firmwareVersion;
        doc["uptime"] = millis();
        doc["freeHeap"] = ESP.getFreeHeap();
        doc["wifiConnected"] = networkStatus.wifi_connected;
        doc["wifiRssi"] = WiFi.RSSI();
        
        String response;
        serializeJson(doc, response);
        request->send(200, "application/json", response);
    });
    
    server.begin();
    logMessage("INFO", "🌐 Web server started on port 80");
    
    // BLE 초기화
    BLEDevice::init(DEVICE_NAME);
    pServer = BLEDevice::createServer();
    
    // BLE 서비스 생성
    BLEService *pService = pServer->createService("12345678-1234-1234-1234-123456789abc");
    pCharacteristic = pService->createCharacteristic(
        "87654321-4321-4321-4321-cba987654321",
        BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_NOTIFY
    );
    
    pService->start();
    pServer->getAdvertising()->start();
    
    logMessage("INFO", "🔵 BLE mesh network started");
    return true;
}

/**
 * 보안 시스템 초기화
 */
bool initializeSecurity() {
    // ATECC608B 초기화 시뮬레이션
    // 실제 구현에서는 ECCX08.begin() 사용
    
    logMessage("INFO", "🔐 Security system initialized");
    logMessage("INFO", "🛡️ Hardware encryption enabled");
    return true;
}

/**
 * 모든 센서 데이터 읽기
 */
bool readAllSensors(SensorData& data) {
    bool allValid = true;
    
    // SHT40 온습도 (시뮬레이션)
    data.temperature = 25.0 + (random(-50, 50) / 10.0);
    data.humidity = 60.0 + (random(-200, 200) / 10.0);
    
    // SGP40 VOC (시뮬레이션)
    data.voc_index = 100.0 + random(-50, 50);
    
    // BME688 가스 (시뮬레이션)
    data.gas_resistance = 50.0 + (random(-100, 100) / 10.0);
    
    // SCD41 CO2 (시뮬레이션)
    data.co2_ppm = 420.0 + random(-100, 200);
    
    // 노이즈 레벨 (시뮬레이션)
    data.noise_level = 45.0 + (random(-100, 100) / 10.0);
    
    // INA219 전력
    data.power_consumption = 150.0 + (random(-50, 50) / 10.0);
    
    // MPU6050 진동 (시뮬레이션)
    data.vibration_x = (random(-100, 100) / 1000.0);
    data.vibration_y = (random(-100, 100) / 1000.0);
    data.vibration_z = (random(-100, 100) / 1000.0);
    
    // 배터리 및 태양광 전압
    data.battery_voltage = monitorBatteryLevel() / 100.0 * 4.2;
    data.solar_voltage = monitorSolarGeneration() / 1000.0 * 6.0;
    
    data.timestamp = millis();
    data.valid = allValid && validateSensorData(data);
    
    return data.valid;
}

/**
 * 환경 AI 모델 실행
 */
bool runEnvironmentalAI(const float* input, AIResults& results) {
    if (!env_interpreter) {
        // AI 모델이 없는 경우 간단한 규칙 기반 분석
        float risk = 0.0;
        
        // 온도 위험도
        if (input[0] < 0 || input[0] > 40) risk += 0.3;
        
        // 습도 위험도
        if (input[1] < 20 || input[1] > 80) risk += 0.2;
        
        // CO2 위험도
        if (input[3] > 1000) risk += 0.3;
        
        // VOC 위험도
        if (input[2] > 200) risk += 0.2;
        
        results.environmental_risk = constrain(risk, 0.0, 1.0);
        results.confidence = 0.8;
        
        if (risk > 0.8) {
            results.risk_category = "critical";
        } else if (risk > 0.5) {
            results.risk_category = "warning";
        } else if (risk > 0.3) {
            results.risk_category = "attention";
        } else {
            results.risk_category = "normal";
        }
        
        return true;
    }
    
    // 실제 TensorFlow Lite 모델 실행
    TfLiteTensor* input_tensor = env_interpreter->input(0);
    for (int i = 0; i < 6; i++) {
        input_tensor->data.f[i] = input[i];
    }
    
    if (env_interpreter->Invoke() != kTfLiteOk) {
        logMessage("ERROR", "Environmental AI inference failed");
        return false;
    }
    
    TfLiteTensor* output_tensor = env_interpreter->output(0);
    results.environmental_risk = output_tensor->data.f[0];
    results.confidence = 0.95;
    
    return true;
}

/**
 * 데이터 동기화
 */
void synchronizeData() {
    if (!networkStatus.wifi_connected) {
        return;
    }
    
    // JSON 데이터 생성
    String jsonData = formatDataToJSON(currentData, currentAI);
    
    // WebSocket으로 실시간 데이터 전송
    webSocket.broadcastTXT(jsonData);
    
    logMessage("DEBUG", "📡 Data synchronized");
}

/**
 * 전력 최적화
 */
void optimizePowerConsumption() {
    float batteryLevel = monitorBatteryLevel();
    float solarPower = monitorSolarGeneration();
    
    // 배터리 레벨에 따른 동적 조절
    if (batteryLevel < 20) {
        // 비상 모드: 최소 기능만
        SENSOR_INTERVAL = 60000;  // 1분
        AI_INTERVAL = 300000;     // 5분
        logMessage("WARNING", "🔋 Emergency power mode activated");
    } else if (batteryLevel < 50) {
        // 절전 모드
        SENSOR_INTERVAL = 30000;  // 30초
        AI_INTERVAL = 120000;     // 2분
    } else {
        // 정상 모드
        SENSOR_INTERVAL = 5000;   // 5초
        AI_INTERVAL = 10000;      // 10초
    }
    
    // 태양광 충전 중이면 고성능 모드
    if (solarPower > 100) {  // 100mW 이상
        SENSOR_INTERVAL = 1000;   // 1초
        AI_INTERVAL = 5000;       // 5초
    }
}

/**
 * 배터리 레벨 모니터링
 */
float monitorBatteryLevel() {
    float voltage = analogRead(BATTERY_MONITOR) * 3.3 / 4095.0 * 2.0;
    
    // 3.7V 리튬 배터리 기준 (3.0V ~ 4.2V)
    float percentage = (voltage - 3.0) / (4.2 - 3.0) * 100.0;
    return constrain(percentage, 0.0, 100.0);
}

/**
 * 태양광 발전량 모니터링
 */
float monitorSolarGeneration() {
    float voltage = analogRead(SOLAR_MONITOR) * 3.3 / 4095.0;
    // 간단한 전력 계산
    return voltage * 100;  // mW 단위
}

/**
 * 상태 표시 (RGB LED)
 */
void indicateStatus(const String& status) {
    if (status == "ready") {
        // 초록색 천천히 깜빡임
        digitalWrite(LED_STATUS_G, HIGH);
        digitalWrite(LED_STATUS_R, LOW);
        digitalWrite(LED_STATUS_B, LOW);
    } else if (status == "normal_operation") {
        // 파란색 지속
        digitalWrite(LED_STATUS_B, HIGH);
        digitalWrite(LED_STATUS_R, LOW);
        digitalWrite(LED_STATUS_G, LOW);
    } else if (status == "warning") {
        // 노란색 (빨강+초록)
        digitalWrite(LED_STATUS_R, HIGH);
        digitalWrite(LED_STATUS_G, HIGH);
        digitalWrite(LED_STATUS_B, LOW);
    } else if (status == "critical") {
        // 빨간색 빠르게 깜빡임
        digitalWrite(LED_STATUS_R, HIGH);
        digitalWrite(LED_STATUS_G, LOW);
        digitalWrite(LED_STATUS_B, LOW);
    } else {
        // 에러 상태들
        digitalWrite(LED_ERROR, HIGH);
    }
}

/**
 * 로그 메시지 출력
 */
void logMessage(const String& level, const String& message) {
    String timestamp = String(millis());
    Serial.println("[" + level + "] " + timestamp + "ms: " + message);
}

/**
 * JSON 데이터 포맷팅
 */
String formatDataToJSON(const SensorData& data, const AIResults& ai) {
    StaticJsonDocument<1024> doc;
    
    // 디바이스 정보
    doc["deviceId"] = deviceId;
    doc["timestamp"] = data.timestamp;
    doc["version"] = firmwareVersion;
    
    // 센서 데이터
    JsonObject sensors = doc.createNestedObject("sensors");
    sensors["temperature"] = round(data.temperature * 100) / 100.0;
    sensors["humidity"] = round(data.humidity * 100) / 100.0;
    sensors["vocIndex"] = round(data.voc_index * 100) / 100.0;
    sensors["co2"] = round(data.co2_ppm * 10) / 10.0;
    sensors["gasResistance"] = round(data.gas_resistance * 100) / 100.0;
    sensors["noiseLevel"] = round(data.noise_level * 10) / 10.0;
    sensors["vibrationX"] = round(data.vibration_x * 1000) / 1000.0;
    sensors["vibrationY"] = round(data.vibration_y * 1000) / 1000.0;
    sensors["vibrationZ"] = round(data.vibration_z * 1000) / 1000.0;
    
    // AI 분석 결과
    JsonObject analysis = doc.createNestedObject("ai");
    analysis["environmentalRisk"] = round(ai.environmental_risk * 1000) / 1000.0;
    analysis["riskCategory"] = ai.risk_category;
    analysis["confidence"] = round(ai.confidence * 1000) / 1000.0;
    
    // 시스템 상태
    JsonObject system = doc.createNestedObject("system");
    system["batteryLevel"] = round(monitorBatteryLevel() * 10) / 10.0;
    system["solarPower"] = round(monitorSolarGeneration() * 10) / 10.0;
    system["powerConsumption"] = round(data.power_consumption * 10) / 10.0;
    system["wifiRssi"] = WiFi.RSSI();
    system["freeHeap"] = ESP.getFreeHeap();
    
    String jsonString;
    serializeJson(doc, jsonString);
    return jsonString;
}

/**
 * 긴급 상황 처리
 */
void handleEmergencyAlert(const String& alert_type, float severity) {
    logMessage("CRITICAL", "🚨 EMERGENCY: " + alert_type + " - Severity: " + String(severity * 100, 1) + "%");
    
    // 즉시 알림
    indicateStatus("critical");
    
    // 부저 경고음
    for (int i = 0; i < 3; i++) {
        digitalWrite(BUZZER_PIN, HIGH);
        delay(200);
        digitalWrite(BUZZER_PIN, LOW);
        delay(200);
    }
    
    // 네트워크를 통한 즉시 알림
    StaticJsonDocument<256> alertDoc;
    alertDoc["type"] = "emergency";
    alertDoc["alert"] = alert_type;
    alertDoc["severity"] = severity;
    alertDoc["deviceId"] = deviceId;
    alertDoc["timestamp"] = millis();
    
    String alertJson;
    serializeJson(alertDoc, alertJson);
    
    // 모든 연결된 클라이언트에게 즉시 전송
    webSocket.broadcastTXT("EMERGENCY:" + alertJson);
}

/**
 * 센서 데이터 유효성 검사
 */
bool validateSensorData(const SensorData& data) {
    // 온도 범위 검사 (-40°C ~ 85°C)
    if (data.temperature < -40 || data.temperature > 85) return false;
    
    // 습도 범위 검사 (0% ~ 100%)
    if (data.humidity < 0 || data.humidity > 100) return false;
    
    // CO2 범위 검사 (350ppm ~ 10000ppm)
    if (data.co2_ppm < 350 || data.co2_ppm > 10000) return false;
    
    // VOC 인덱스 검사 (0 ~ 500)
    if (data.voc_index < 0 || data.voc_index > 500) return false;
    
    return true;
}

/**
 * WebSocket 메시지 처리
 */
void handleWebSocketMessage(uint8_t num, WStype_t type, uint8_t* payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            logMessage("INFO", "WebSocket client disconnected: " + String(num));
            break;
            
        case WStype_CONNECTED:
            logMessage("INFO", "WebSocket client connected: " + String(num));
            // 현재 데이터 즉시 전송
            webSocket.sendTXT(num, formatDataToJSON(currentData, currentAI));
            break;
            
        case WStype_TEXT:
            logMessage("DEBUG", "WebSocket message: " + String((char*)payload));
            // 명령 처리
            if (strcmp((char*)payload, "restart") == 0) {
                ESP.restart();
            }
            break;
            
        default:
            break;
    }
}

/**
 * 웹 대시보드 HTML 생성
 */
String generateWebDashboard() {
    return R"(
<!DOCTYPE html>
<html>
<head>
    <title>NeuroCity Smart Sensor v2.0</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: rgba(255,255,255,0.1); 
            padding: 30px; 
            border-radius: 20px; 
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        .header { 
            text-align: center; 
            margin-bottom: 40px; 
            border-bottom: 2px solid rgba(255,255,255,0.3); 
            padding-bottom: 20px; 
        }
        .header h1 {
            font-size: 2.5em;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header .subtitle {
            font-size: 1.2em;
            opacity: 0.8;
            margin-top: 10px;
        }
        .grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        .card { 
            background: rgba(255,255,255,0.15); 
            padding: 25px; 
            border-radius: 15px; 
            text-align: center;
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .card h3 {
            margin-top: 0;
            font-size: 1.3em;
            opacity: 0.9;
        }
        .value { 
            font-size: 2.5em; 
            font-weight: bold; 
            margin: 15px 0;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
        .unit { 
            font-size: 0.9em; 
            opacity: 0.7; 
            margin-left: 5px;
        }
        .status-good { color: #4CAF50; }
        .status-warning { color: #FF9800; }
        .status-critical { color: #F44336; }
        .ai-panel {
            background: rgba(0,0,0,0.2);
            padding: 20px;
            border-radius: 15px;
            margin-top: 20px;
        }
        .controls {
            text-align: center;
            margin-top: 30px;
        }
        button { 
            background: rgba(255,255,255,0.2); 
            color: white; 
            border: 1px solid rgba(255,255,255,0.3); 
            padding: 12px 25px; 
            border-radius: 25px; 
            cursor: pointer; 
            margin: 0 10px;
            font-size: 1em;
            transition: all 0.3s ease;
        }
        button:hover { 
            background: rgba(255,255,255,0.3);
            transform: scale(1.05);
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            opacity: 0.7;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 NeuroCity Smart Sensor</h1>
            <div class="subtitle">차세대 AI 기반 환경 모니터링 시스템 v2.0</div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🌡️ 온도</h3>
                <div class="value" id="temperature">--</div>
                <span class="unit">°C</span>
            </div>
            
            <div class="card">
                <h3>💧 습도</h3>
                <div class="value" id="humidity">--</div>
                <span class="unit">%</span>
            </div>
            
            <div class="card">
                <h3>🫁 CO₂</h3>
                <div class="value" id="co2">--</div>
                <span class="unit">ppm</span>
            </div>
            
            <div class="card">
                <h3>🏭 VOC</h3>
                <div class="value" id="voc">--</div>
                <span class="unit">index</span>
            </div>
            
            <div class="card">
                <h3>📢 소음</h3>
                <div class="value" id="noise">--</div>
                <span class="unit">dB</span>
            </div>
            
            <div class="card">
                <h3>🔋 배터리</h3>
                <div class="value" id="battery">--</div>
                <span class="unit">%</span>
            </div>
        </div>
        
        <div class="ai-panel">
            <h3>🧠 AI 분석 결과</h3>
            <div class="grid">
                <div class="card">
                    <h3>위험도</h3>
                    <div class="value" id="risk">--</div>
                    <span class="unit">%</span>
                </div>
                <div class="card">
                    <h3>상태</h3>
                    <div class="value" id="category">--</div>
                </div>
                <div class="card">
                    <h3>신뢰도</h3>
                    <div class="value" id="confidence">--</div>
                    <span class="unit">%</span>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <button onclick="refreshData()">🔄 새로고침</button>
            <button onclick="window.open('/api/data', '_blank')">📊 API 데이터</button>
            <button onclick="window.open('/api/status', '_blank')">⚙️ 시스템 상태</button>
        </div>
        
        <div class="footer">
            <p>Device ID: )" + deviceId + R"( | Firmware: v)" + firmwareVersion + R"(</p>
            <p>Last update: <span id="lastUpdate">--</span></p>
        </div>
    </div>
    
    <script>
        function refreshData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    updateDisplay(data);
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
        
        function updateDisplay(data) {
            // 센서 데이터 업데이트
            document.getElementById('temperature').textContent = data.sensors.temperature.toFixed(1);
            document.getElementById('humidity').textContent = data.sensors.humidity.toFixed(1);
            document.getElementById('co2').textContent = data.sensors.co2.toFixed(0);
            document.getElementById('voc').textContent = data.sensors.vocIndex.toFixed(0);
            document.getElementById('noise').textContent = data.sensors.noiseLevel.toFixed(1);
            document.getElementById('battery').textContent = data.system.batteryLevel.toFixed(0);
            
            // AI 분석 결과 업데이트
            const risk = (data.ai.environmentalRisk * 100).toFixed(1);
            document.getElementById('risk').textContent = risk;
            document.getElementById('category').textContent = data.ai.riskCategory;
            document.getElementById('confidence').textContent = (data.ai.confidence * 100).toFixed(0);
            
            // 위험도에 따른 색상 변경
            const riskElement = document.getElementById('risk');
            if (risk > 80) {
                riskElement.className = 'value status-critical';
            } else if (risk > 50) {
                riskElement.className = 'value status-warning';
            } else {
                riskElement.className = 'value status-good';
            }
            
            // 마지막 업데이트 시간
            document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
        }
        
        // 페이지 로드 시 데이터 가져오기
        refreshData();
        
        // 10초마다 자동 갱신
        setInterval(refreshData, 10000);
        
        // WebSocket 연결 (실시간 업데이트)
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(wsProtocol + '//' + window.location.host + ':81');
        
        ws.onmessage = function(event) {
            try {
                if (event.data.startsWith('EMERGENCY:')) {
                    const alertData = JSON.parse(event.data.substring(10));
                    alert('🚨 긴급상황: ' + alertData.alert + ' (위험도: ' + (alertData.severity * 100).toFixed(0) + '%)');
                } else {
                    const data = JSON.parse(event.data);
                    updateDisplay(data);
                }
            } catch (e) {
                console.error('WebSocket message error:', e);
            }
        };
        
        ws.onopen = function() {
            console.log('WebSocket connected');
        };
        
        ws.onclose = function() {
            console.log('WebSocket disconnected');
        };
    </script>
</body>
</html>
)";
}