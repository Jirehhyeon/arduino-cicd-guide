# 🔧 Arduino CI/CD 실습용 하드웨어 가이드

## 📋 **완전 실습 키트 구성품**

### 🛠️ **기본 필수 부품 (총 비용: 약 50,000원)**

| 부품명 | 수량 | 가격 | 구매처 | 용도 |
|--------|------|------|--------|------|
| **ESP32 DevKit V1** | 1개 | 8,000원 | 디바이스마트, 엘레파츠 | 메인 컨트롤러 (WiFi 내장) |
| **DHT22 온습도 센서** | 1개 | 5,000원 | 아두이노몰, 디바이스마트 | 온도/습도 측정 |
| **토양 수분 센서** | 1개 | 3,000원 | 아두이노몰 | 토양 습도 측정 |
| **조도 센서 (CdS)** | 1개 | 1,000원 | 부품상 | 빛 감지 |
| **릴레이 모듈 (5V)** | 2개 | 4,000원 | 디바이스마트 | 워터펌프/팬 제어 |
| **WS2812B LED 스트립** | 1m | 8,000원 | 아두이노몰 | 조명 제어 |
| **미니 워터펌프** | 1개 | 5,000원 | 알리익스프레스 | 자동 급수 |
| **작은 팬 (5V)** | 1개 | 3,000원 | 부품상 | 환기 |
| **브레드보드** | 1개 | 2,000원 | 부품상 | 회로 연결 |
| **점퍼 와이어** | 1세트 | 3,000원 | 부품상 | 연결선 |
| **저항 (10kΩ, 330Ω)** | 각 5개 | 1,000원 | 부품상 | 풀업/LED 제한 |
| **미니 USB 케이블** | 1개 | 2,000원 | 다이소 | 프로그래밍/전원 |
| **5V 어댑터** | 1개 | 5,000원 | 부품상 | 외부 전원 |

---

## 🏗️ **1단계: 스마트 온실 기본 회로**

### 📐 **회로도 (ASCII Art)**

```
ESP32 DevKit V1 연결도:
                    ┌─────────────────┐
                    │      ESP32      │
                    │   DevKit V1     │
               ┌────┤                 ├────┐
               │    │  GPIO2    GPIO4 │    │
               │    │                 │    │
               │    │  GPIO5   GPIO18 │    │
               │    │                 │    │
               │    │ GPIO19   GPIO21 │    │
               │    │                 │    │
               │    │ GPIO22   GPIO23 │    │
               │    │                 │    │
               │    │  3.3V      GND  │    │
               │    │                 │    │
               │    │   5V       VIN  │    │
               │    └─────────────────┘    │
               │                           │
               │                           │
         ┌─────▼─────┐               ┌─────▼─────┐
         │   DHT22   │               │ 토양센서   │
         │  온습도   │               │           │
         │   센서    │               │           │
         └───────────┘               └───────────┘
         
    GPIO2 ◄─── DHT22 DATA
    3.3V  ◄─── DHT22 VCC
    GND   ◄─── DHT22 GND
    
    GPIO4 ◄─── 토양센서 A0
    3.3V  ◄─── 토양센서 VCC  
    GND   ◄─── 토양센서 GND

    GPIO5 ◄─── 조도센서 (CdS + 10kΩ 분압)
    
    GPIO18 ───► 릴레이1 (워터펌프)
    GPIO19 ───► 릴레이2 (팬)
    GPIO21 ───► WS2812B LED Strip
```

### 🔌 **상세 연결 방법**

#### **1. DHT22 온습도 센서 연결**
```
DHT22 핀배치:
 ┌─────┐
 │  1  │ ◄─── VCC (3.3V)
 │  2  │ ◄─── DATA (GPIO2)  
 │  3  │ ◄─── NC (연결안함)
 │  4  │ ◄─── GND
 └─────┘

연결:
- DHT22 핀1 (VCC) → ESP32 3.3V
- DHT22 핀2 (DATA) → ESP32 GPIO2
- DHT22 핀3 → 연결 안함
- DHT22 핀4 (GND) → ESP32 GND
- GPIO2와 3.3V 사이에 10kΩ 풀업 저항 연결
```

#### **2. 토양 수분 센서 연결**
```
토양센서 핀배치:
 ┌─────────┐
 │   VCC   │ ◄─── 3.3V
 │   GND   │ ◄─── GND
 │   A0    │ ◄─── GPIO4 (아날로그 입력)
 │   D0    │ ◄─── 사용안함
 └─────────┘

연결:
- VCC → ESP32 3.3V
- GND → ESP32 GND  
- A0 → ESP32 GPIO4
```

#### **3. 조도 센서 (CdS) 연결**
```
조도센서 분압회로:
                    3.3V
                      │
                   ┌──┴──┐
                   │CdS  │ (조도센서)
                   │     │
                   └──┬──┘
                      │ ←── GPIO5 (아날로그 입력)
                   ┌──┴──┐
                   │10kΩ │ (저항)
                   │     │
                   └──┬──┘
                      │
                     GND

연결:
- CdS 한쪽 → 3.3V
- CdS 다른쪽 → GPIO5 + 10kΩ저항
- 10kΩ저항 다른쪽 → GND
```

#### **4. 릴레이 모듈 연결**
```
릴레이 모듈 핀배치:
 ┌─────────────┐
 │     VCC     │ ◄─── 5V (외부전원)
 │     GND     │ ◄─── GND
 │     IN      │ ◄─── GPIO (제어신호)
 │             │
 │  NO  COM NC │ ◄─── 부하 연결부
 └─────────────┘

릴레이1 (워터펌프):
- VCC → 외부 5V
- GND → ESP32 GND  
- IN → ESP32 GPIO18
- COM → 워터펌프 +
- NO → 5V 전원

릴레이2 (팬):
- VCC → 외부 5V
- GND → ESP32 GND
- IN → ESP32 GPIO19  
- COM → 팬 +
- NO → 5V 전원
```

#### **5. LED 스트립 연결**
```
WS2812B LED 스트립:
 ┌─────────────┐
 │     5V      │ ◄─── 외부 5V 전원
 │     GND     │ ◄─── GND
 │     DIN     │ ◄─── GPIO21 (데이터)
 └─────────────┘

연결:
- 5V → 외부 5V 전원
- GND → ESP32 GND
- DIN → ESP32 GPIO21
- GPIO21과 DIN 사이에 330Ω 저항 연결 (보호용)
```

---

## 🔨 **2단계: 실제 제작 과정**

### **STEP 1: 브레드보드 레이아웃**

```
브레드보드 배치도 (위에서 본 모습):

    a b c d e   f g h i j
  ┌─────────────────────────┐
1 │ + + + + +   + + + + + │ ← 전원 레일 (+)
2 │ - - - - -   - - - - - │ ← 그라운드 레일 (-)
3 │                       │
4 │   ESP32               │
5 │   DevKit              │  
6 │   여기에              │
7 │   장착                │
8 │                       │
9 │ DHT22   토양센서       │
10│                       │
11│ 조도센서  릴레이모듈   │
12│                       │
  └─────────────────────────┘
```

### **STEP 2: 단계별 조립**

#### **1차: 전원 연결**
```bash
1. ESP32를 브레드보드 중앙에 꽂기
2. 전원 레일 연결:
   - ESP32 3.3V → 브레드보드 + 레일
   - ESP32 GND → 브레드보드 - 레일
3. 외부 5V 어댑터 준비
```

#### **2차: 센서 연결**
```bash
1. DHT22 연결:
   - 빨간선(VCC): ESP32 3.3V
   - 검은선(GND): ESP32 GND  
   - 흰선(DATA): ESP32 GPIO2
   - 10kΩ 풀업저항: GPIO2 ↔ 3.3V

2. 토양센서 연결:
   - 빨간선: ESP32 3.3V
   - 검은선: ESP32 GND
   - 노란선: ESP32 GPIO4

3. 조도센서 연결:
   - CdS 한쪽: ESP32 3.3V
   - CdS 다른쪽: ESP32 GPIO5 + 10kΩ저항 → GND
```

#### **3차: 액츄에이터 연결**
```bash
1. 릴레이 모듈 연결:
   릴레이1 (워터펌프):
   - VCC: 외부 5V
   - GND: ESP32 GND
   - IN: ESP32 GPIO18
   
   릴레이2 (팬):  
   - VCC: 외부 5V
   - GND: ESP32 GND
   - IN: ESP32 GPIO19

2. LED 스트립 연결:
   - 5V: 외부 5V
   - GND: ESP32 GND
   - DIN: ESP32 GPIO21 (330Ω 저항 통해서)
```

### **STEP 3: 연결 검증 체크리스트**

```bash
□ ESP32 전원 LED 켜짐 확인
□ DHT22 센서 전원 확인 (만지면 따뜻함)
□ 토양센서 LED 켜짐 확인
□ 릴레이 모듈 전원 LED 켜짐 확인  
□ LED 스트립 전원 확인
□ 모든 GND 연결 확인
□ 쇼트 없는지 확인 (멀티미터로 측정)
```

---

## 💻 **3단계: 테스트 코드 업로드**

### **기본 센서 테스트 코드**

```cpp
/*
🔧 Arduino CI/CD 실습용 스마트 온실 시스템
센서 테스트 및 기본 제어 코드
*/

#include <WiFi.h>
#include <DHT.h>
#include <Adafruit_NeoPixel.h>

// 핀 정의
#define DHT_PIN 2
#define SOIL_PIN 4  
#define LIGHT_PIN 5
#define PUMP_RELAY_PIN 18
#define FAN_RELAY_PIN 19
#define LED_STRIP_PIN 21
#define LED_COUNT 10

// 센서 초기화
DHT dht(DHT_PIN, DHT22);
Adafruit_NeoPixel strip(LED_COUNT, LED_STRIP_PIN, NEO_GRB + NEO_KHZ800);

// WiFi 설정
const char* ssid = "당신의_WiFi_이름";
const char* password = "WiFi_비밀번호";

void setup() {
  Serial.begin(115200);
  Serial.println("🌱 스마트 온실 시스템 시작");
  
  // 센서 초기화
  dht.begin();
  strip.begin();
  strip.show();
  
  // 릴레이 핀 설정
  pinMode(PUMP_RELAY_PIN, OUTPUT);
  pinMode(FAN_RELAY_PIN, OUTPUT);
  digitalWrite(PUMP_RELAY_PIN, LOW);  // 릴레이 끄기
  digitalWrite(FAN_RELAY_PIN, LOW);
  
  // WiFi 연결
  WiFi.begin(ssid, password);
  Serial.print("WiFi 연결중");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("✅ WiFi 연결 완료!");
  Serial.print("IP 주소: ");
  Serial.println(WiFi.localIP());
  
  // 시작 효과
  startupEffect();
}

void loop() {
  // 센서 데이터 읽기
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  int soilMoisture = analogRead(SOIL_PIN);
  int lightLevel = analogRead(LIGHT_PIN);
  
  // 센서 데이터 출력
  Serial.println("=== 센서 데이터 ===");
  Serial.printf("🌡️  온도: %.1f°C\n", temperature);
  Serial.printf("💧 습도: %.1f%%\n", humidity);
  Serial.printf("🌱 토양수분: %d (0-4095)\n", soilMoisture);
  Serial.printf("☀️  조도: %d (0-4095)\n", lightLevel);
  
  // 자동 제어 로직
  autoControl(temperature, humidity, soilMoisture, lightLevel);
  
  // LED 효과
  updateLEDEffect(temperature, humidity);
  
  delay(5000);  // 5초마다 측정
}

void autoControl(float temp, float humid, int soil, int light) {
  Serial.println("=== 자동 제어 ===");
  
  // 워터펌프 제어 (토양이 건조하면 급수)
  if (soil > 3000) {  // 토양이 건조함 (값이 클수록 건조)
    Serial.println("💧 토양이 건조함 - 워터펌프 ON");
    digitalWrite(PUMP_RELAY_PIN, HIGH);
    delay(3000);  // 3초간 급수
    digitalWrite(PUMP_RELAY_PIN, LOW);
  } else {
    Serial.println("✅ 토양 수분 적정");
  }
  
  // 팬 제어 (온도가 높으면 환기)
  if (temp > 28.0) {
    Serial.println("🌪️  온도가 높음 - 팬 ON");
    digitalWrite(FAN_RELAY_PIN, HIGH);
  } else if (temp < 24.0) {
    Serial.println("❄️  온도가 낮음 - 팬 OFF");
    digitalWrite(FAN_RELAY_PIN, LOW);
  }
}

void updateLEDEffect(float temp, float humid) {
  // 온도에 따른 색상 변화
  uint32_t color;
  
  if (temp < 20) {
    color = strip.Color(0, 0, 255);    // 파란색 (차가움)
  } else if (temp < 25) {
    color = strip.Color(0, 255, 0);    // 초록색 (적정)
  } else if (temp < 30) {
    color = strip.Color(255, 255, 0);  // 노란색 (따뜻함)
  } else {
    color = strip.Color(255, 0, 0);    // 빨간색 (뜨거움)
  }
  
  // LED 스트립 전체를 같은 색으로
  for (int i = 0; i < LED_COUNT; i++) {
    strip.setPixelColor(i, color);
  }
  strip.show();
}

void startupEffect() {
  Serial.println("🌈 시작 효과 실행");
  
  // 무지개 효과
  for (int i = 0; i < LED_COUNT; i++) {
    strip.setPixelColor(i, strip.Color(255, 0, 0));  // 빨강
    strip.show();
    delay(100);
  }
  delay(500);
  
  for (int i = 0; i < LED_COUNT; i++) {
    strip.setPixelColor(i, strip.Color(0, 255, 0));  // 초록
    strip.show();
    delay(100);
  }
  delay(500);
  
  for (int i = 0; i < LED_COUNT; i++) {
    strip.setPixelColor(i, strip.Color(0, 0, 255));  // 파랑
    strip.show();
    delay(100);
  }
  delay(500);
  
  // 모든 LED 끄기
  strip.clear();
  strip.show();
}
```

---

## 🧪 **4단계: 단계별 테스트 방법**

### **Test 1: 센서 개별 테스트**

```cpp
// DHT22 테스트
void testDHT22() {
  float temp = dht.readTemperature();
  float humid = dht.readHumidity();
  
  if (isnan(temp) || isnan(humid)) {
    Serial.println("❌ DHT22 센서 오류!");
  } else {
    Serial.printf("✅ DHT22 정상: %.1f°C, %.1f%%\n", temp, humid);
  }
}

// 토양센서 테스트  
void testSoilSensor() {
  int soil = analogRead(SOIL_PIN);
  Serial.printf("✅ 토양센서: %d ", soil);
  
  if (soil > 3500) Serial.println("(매우 건조)");
  else if (soil > 2500) Serial.println("(건조)");
  else if (soil > 1500) Serial.println("(적당)");
  else Serial.println("(습함)");
}

// 조도센서 테스트
void testLightSensor() {
  int light = analogRead(LIGHT_PIN);
  Serial.printf("✅ 조도센서: %d ", light);
  
  if (light > 3000) Serial.println("(밝음)");
  else if (light > 1500) Serial.println("(보통)");
  else Serial.println("(어두움)");
}
```

### **Test 2: 액츄에이터 테스트**

```cpp
// 릴레이 테스트
void testRelays() {
  Serial.println("🔧 릴레이 테스트 시작");
  
  // 워터펌프 테스트
  Serial.println("💧 워터펌프 ON");
  digitalWrite(PUMP_RELAY_PIN, HIGH);
  delay(2000);
  digitalWrite(PUMP_RELAY_PIN, LOW);
  Serial.println("💧 워터펌프 OFF");
  
  delay(1000);
  
  // 팬 테스트
  Serial.println("🌪️ 팬 ON");
  digitalWrite(FAN_RELAY_PIN, HIGH);
  delay(2000);
  digitalWrite(FAN_RELAY_PIN, LOW);
  Serial.println("🌪️ 팬 OFF");
}

// LED 테스트
void testLEDStrip() {
  Serial.println("🌈 LED 스트립 테스트");
  
  // 빨강
  for (int i = 0; i < LED_COUNT; i++) {
    strip.setPixelColor(i, strip.Color(255, 0, 0));
  }
  strip.show();
  delay(1000);
  
  // 초록  
  for (int i = 0; i < LED_COUNT; i++) {
    strip.setPixelColor(i, strip.Color(0, 255, 0));
  }
  strip.show();
  delay(1000);
  
  // 파랑
  for (int i = 0; i < LED_COUNT; i++) {
    strip.setPixelColor(i, strip.Color(0, 0, 255));
  }
  strip.show();
  delay(1000);
  
  strip.clear();
  strip.show();
}
```

---

## 🔍 **5단계: 문제해결 가이드**

### **일반적인 문제들**

#### **문제 1: ESP32가 인식되지 않음**
```
증상: Arduino IDE에서 포트가 보이지 않음
해결:
1. USB 케이블 확인 (데이터 전송 가능한 케이블 사용)
2. CP210x 드라이버 설치
   - https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
3. 보드를 BOOT 모드로 진입
   - BOOT 버튼 누르고 있는 상태에서 RESET 버튼 누르기
```

#### **문제 2: DHT22 센서가 NaN 값 반환**
```
증상: 온도/습도가 "nan"으로 출력
해결:
1. 연결 확인:
   - VCC → 3.3V (5V 아님!)
   - DATA → GPIO2
   - 10kΩ 풀업저항 확인
2. 센서 불량 체크 (다른 센서로 교체 테스트)
3. 지연 시간 추가 (dht.begin() 후 2초 대기)
```

#### **문제 3: 릴레이가 동작하지 않음**
```
증상: 릴레이 LED는 켜지는데 부하가 동작하지 않음
해결:
1. 부하 연결 확인:
   - COM, NO 단자 올바른 연결
   - 부하 전원 확인
2. 릴레이 전원 확인 (5V 필요)
3. 부하 정격 확인 (릴레이 용량 초과 여부)
```

#### **문제 4: LED 스트립이 켜지지 않음**
```
증상: LED가 전혀 안 켜짐
해결:
1. 전원 확인 (5V, 충분한 전류)
2. 데이터 핀 연결 확인 (DIN → GPIO21)
3. 330Ω 저항 확인
4. LED 스트립 방향 확인 (화살표 방향)
```

### **연결 확인 체크리스트**

```bash
전원 연결:
□ ESP32 3.3V → 센서들 VCC
□ ESP32 GND → 모든 부품 GND  
□ 외부 5V → 릴레이, LED 스트립
□ 전원 용량 확인 (최소 2A)

신호 연결:
□ GPIO2 ← DHT22 DATA (+ 10kΩ 풀업)
□ GPIO4 ← 토양센서 A0
□ GPIO5 ← 조도센서 (분압회로)
□ GPIO18 → 릴레이1 IN
□ GPIO19 → 릴레이2 IN  
□ GPIO21 → LED DIN (+ 330Ω 저항)

부하 연결:
□ 워터펌프 → 릴레이1 (COM-NO)
□ 팬 → 릴레이2 (COM-NO)
□ 5V 전원 → 릴레이 NO단자
```

---

## 📱 **6단계: 웹 대시보드 추가**

### **ESP32 웹서버 코드**

```cpp
#include <WebServer.h>

WebServer server(80);

void setupWebServer() {
  server.on("/", handleRoot);
  server.on("/api/sensors", handleSensors);
  server.on("/api/control", handleControl);
  server.begin();
  Serial.println("🌐 웹 서버 시작됨");
}

void handleRoot() {
  String html = R"(
<!DOCTYPE html>
<html>
<head>
    <title>스마트 온실 대시보드</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; margin: 20px; background: #f0f8f0; }
        .container { max-width: 800px; margin: 0 auto; }
        .card { background: white; padding: 20px; margin: 10px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .sensor-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .sensor-value { font-size: 24px; font-weight: bold; color: #2e7d32; }
        .control-btn { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; }
        .btn-on { background: #4caf50; color: white; }
        .btn-off { background: #f44336; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌱 스마트 온실 모니터링</h1>
        
        <div class="sensor-grid" id="sensors">
            <!-- 센서 데이터가 여기에 로드됩니다 -->
        </div>
        
        <div class="card">
            <h3>🎛️ 수동 제어</h3>
            <button class="control-btn btn-on" onclick="control('pump', 'on')">💧 워터펌프 ON</button>
            <button class="control-btn btn-off" onclick="control('pump', 'off')">💧 워터펌프 OFF</button>
            <br>
            <button class="control-btn btn-on" onclick="control('fan', 'on')">🌪️ 팬 ON</button>
            <button class="control-btn btn-off" onclick="control('fan', 'off')">🌪️ 팬 OFF</button>
        </div>
    </div>

    <script>
        function loadSensors() {
            fetch('/api/sensors')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('sensors').innerHTML = `
                        <div class="card">
                            <h3>🌡️ 온도</h3>
                            <div class="sensor-value">${data.temperature}°C</div>
                        </div>
                        <div class="card">
                            <h3>💧 습도</h3>
                            <div class="sensor-value">${data.humidity}%</div>
                        </div>
                        <div class="card">
                            <h3>🌱 토양수분</h3>
                            <div class="sensor-value">${data.soil}</div>
                        </div>
                        <div class="card">
                            <h3>☀️ 조도</h3>
                            <div class="sensor-value">${data.light}</div>
                        </div>
                    `;
                });
        }
        
        function control(device, action) {
            fetch(`/api/control?device=${device}&action=${action}`)
                .then(response => response.text())
                .then(data => alert(data));
        }
        
        // 5초마다 센서 데이터 업데이트
        setInterval(loadSensors, 5000);
        loadSensors();
    </script>
</body>
</html>
  )";
  
  server.send(200, "text/html", html);
}

void handleSensors() {
  float temp = dht.readTemperature();
  float humid = dht.readHumidity();
  int soil = analogRead(SOIL_PIN);
  int light = analogRead(LIGHT_PIN);
  
  String json = "{";
  json += "\"temperature\":" + String(temp, 1) + ",";
  json += "\"humidity\":" + String(humid, 1) + ",";
  json += "\"soil\":" + String(soil) + ",";
  json += "\"light\":" + String(light);
  json += "}";
  
  server.send(200, "application/json", json);
}

void handleControl() {
  String device = server.arg("device");
  String action = server.arg("action");
  
  if (device == "pump") {
    if (action == "on") {
      digitalWrite(PUMP_RELAY_PIN, HIGH);
      server.send(200, "text/plain", "워터펌프 켜짐");
    } else {
      digitalWrite(PUMP_RELAY_PIN, LOW);
      server.send(200, "text/plain", "워터펌프 꺼짐");
    }
  } else if (device == "fan") {
    if (action == "on") {
      digitalWrite(FAN_RELAY_PIN, HIGH);
      server.send(200, "text/plain", "팬 켜짐");
    } else {
      digitalWrite(FAN_RELAY_PIN, LOW);
      server.send(200, "text/plain", "팬 꺼짐");
    }
  }
}
```

---

## 🎯 **실습 미션**

### **미션 1: 기본 조립 (30분)**
```bash
목표: 모든 센서와 액츄에이터 연결 완료
체크포인트:
□ ESP32 전원 켜짐
□ 모든 센서 정상 읽기
□ 릴레이 수동 제어 가능
□ LED 스트립 색상 변경 가능
```

### **미션 2: 자동화 구현 (1시간)**  
```bash
목표: 센서 값에 따른 자동 제어 구현
조건:
- 토양 수분 < 30% → 자동 급수
- 온도 > 28°C → 자동 환기
- 조도 < 500 → LED 조명 켜기
```

### **미션 3: 웹 대시보드 (1시간)**
```bash
목표: 스마트폰으로 원격 모니터링/제어
기능:
- 실시간 센서 데이터 표시
- 수동 펌프/팬 제어
- 자동/수동 모드 전환
```

### **미션 4: CI/CD 연동 (30분)**
```bash
목표: GitHub Actions로 자동 배포
과정:
1. 코드를 GitHub에 업로드
2. .github/workflows/deploy.yml 작성
3. 코드 수정 시 자동으로 ESP32에 배포
```

---

## 📦 **확장 아이디어**

### **레벨 2: 고급 센서 추가**
- **pH 센서**: 토양 산성도 측정
- **CO2 센서**: 공기질 모니터링  
- **카메라 모듈**: 식물 성장 타임랩스
- **초음파 센서**: 물탱크 수위 감지

### **레벨 3: AI 기능 추가**
- **TensorFlow Lite**: 식물 질병 진단
- **이미지 인식**: 해충 자동 탐지
- **예측 모델**: 수확 시기 예측
- **음성 인식**: 음성 명령 제어

### **레벨 4: IoT 플랫폼 연동**
- **AWS IoT Core**: 클라우드 데이터 저장
- **Google Firebase**: 실시간 알림
- **MQTT 브로커**: 다중 디바이스 통신
- **InfluxDB + Grafana**: 전문 모니터링

---

## 🎉 **완성 후 기대효과**

✅ **기술 습득:**
- Arduino/ESP32 프로그래밍
- 센서/액츄에이터 제어
- WiFi 통신 및 웹서버 구축
- CI/CD 파이프라인 구성

✅ **실무 경험:**
- IoT 시스템 설계 및 구현
- 하드웨어-소프트웨어 통합
- 원격 모니터링 시스템 구축
- 자동화 로직 개발

✅ **포트폴리오:**
- 완전한 IoT 프로젝트
- GitHub 소스코드 관리
- 실시간 웹 대시보드
- 자동 배포 시스템

---

**🚀 이제 실제로 만들어보세요! 궁금한 점이 있으면 언제든지 질문하세요! 🚀**