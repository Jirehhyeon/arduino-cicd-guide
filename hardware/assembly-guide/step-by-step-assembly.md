# 🔨 단계별 조립 가이드 - 스마트 온실 시스템

## 📦 **준비물 최종 체크리스트**

### **필수 도구**
```bash
□ 십자 드라이버 (소형)
□ 일자 드라이버 (소형)  
□ 니퍼 (전선 자르기용)
□ 스트리핑 툴 (전선 피복 벗기기)
□ 멀티미터 (연결 확인용)
□ 납땜기 + 납땜선 (필요시)
□ 양면테이프 (부품 고정용)
□ 타이랩 (전선 정리용)
```

### **작업 환경**
```bash
□ 밝은 조명 (LED 데스크 램프 권장)
□ 정전기 방지 매트
□ 부품 정리용 작은 박스들
□ A4 용지 (부품 배치 미리 그려보기)
□ 스마트폰 (각 단계 사진 촬영용)
```

---

## 🎯 **조립 순서 (총 소요시간: 2-3시간)**

### **PHASE 1: 준비 및 계획 (30분)**

#### **Step 1-1: 부품 확인 및 분류**
```bash
시간: 10분

1. 모든 부품을 테이블에 펼쳐놓기
2. 부품 리스트와 대조하여 확인
3. 종류별로 분류:
   ┌─────────────────┐
   │   컨트롤러      │ ESP32 DevKit V1
   ├─────────────────┤
   │   센서류        │ DHT22, 토양센서, CdS
   ├─────────────────┤  
   │   액츄에이터    │ 릴레이, 펌프, 팬, LED
   ├─────────────────┤
   │   연결재료      │ 브레드보드, 점퍼와이어, 저항
   ├─────────────────┤
   │   전원부        │ USB케이블, 5V어댑터
   └─────────────────┘

4. 불량품 체크:
   □ ESP32 USB 포트 손상 여부
   □ 브레드보드 구멍 막힘 여부  
   □ 점퍼와이어 단선 여부
   □ 센서 핀 구부러짐 여부
```

#### **Step 1-2: 작업공간 설정**
```bash
시간: 10분

1. 작업 테이블 정리 (60cm x 40cm 이상 권장)
2. 조명 설정 (그림자 없도록)
3. 멀티미터 동작 확인
4. 브레드보드를 테이블 중앙에 배치
5. 부품들을 접근하기 쉽게 배치

배치 예시:
   ┌─ESP32─┐  ┌─센서들─┐
   │       │  │        │
   └───────┘  └────────┘
       ┌─브레드보드─┐
       │           │  ┌─전선류─┐
       │           │  │        │
       └───────────┘  └────────┘
   ┌─릴레이─┐  ┌─도구들─┐
   │       │  │        │  
   └───────┘  └────────┘
```

#### **Step 1-3: 회로도 숙지**
```bash
시간: 10분

1. 회로도를 프린트하여 옆에 비치
2. 각 부품의 핀 배치 확인:
   
   ESP32 중요 핀들:
   - 3V3: 센서 전원 (DHT22, 토양센서, CdS)
   - GND: 공통 그라운드 (모든 부품)
   - GPIO2: DHT22 데이터
   - GPIO4: 토양센서 아날로그
   - GPIO5: 조도센서
   - GPIO18: 워터펌프 릴레이
   - GPIO19: 팬 릴레이  
   - GPIO21: LED 스트립

3. 연결 실수 방지를 위한 색깔 코딩:
   - 빨간색: 3.3V 전원
   - 주황색: 5V 전원
   - 검은색: GND
   - 기타 색: 신호선
```

---

### **PHASE 2: 기본 연결 (40분)**

#### **Step 2-1: 전원 레일 설정**
```bash
시간: 10분

1. 브레드보드 전원 레일 연결:
   
   브레드보드 상단:
   ┌─────────────────────┐
   │ + + + + + + + + + + │ ← 3.3V 레일
   │ - - - - - - - - - - │ ← GND 레일  
   └─────────────────────┘
   
   브레드보드 하단:
   ┌─────────────────────┐
   │ + + + + + + + + + + │ ← 5V 레일 (추후 연결)
   │ - - - - - - - - - - │ ← GND 레일
   └─────────────────────┘

2. 점퍼와이어로 연결:
   - 상단 + 레일 ↔ 하단 + 레일 (빨간선)
   - 상단 - 레일 ↔ 하단 - 레일 (검은선)

3. 멀티미터로 연결 확인:
   - 상단과 하단 + 레일 간 도통 확인
   - 상단과 하단 - 레일 간 도통 확인
   - + 레일과 - 레일 간 절연 확인 (무한대 저항)
```

#### **Step 2-2: ESP32 장착**
```bash
시간: 15분

1. ESP32 방향 확인:
   - USB 포트가 브레드보드 바깥쪽으로
   - 핀 라벨이 보이는 방향으로
   
2. ESP32를 브레드보드에 삽입:
   ⚠️ 주의: 핀이 구부러지지 않도록 천천히!
   
   삽입 방법:
   a) ESP32를 브레드보드 위에 올리기
   b) 한쪽 끝부터 천천히 눌러서 삽입
   c) 반대쪽도 균등하게 눌러서 완전 삽입
   d) 모든 핀이 제대로 들어갔는지 확인

3. 전원 연결:
   - ESP32의 3V3 핀 → 브레드보드 + 레일 (빨간선)
   - ESP32의 GND 핀 → 브레드보드 - 레일 (검은선)

4. 동작 테스트:
   - USB 케이블을 ESP32에 연결
   - 컴퓨터에 연결
   - ESP32 보드의 파워 LED 점등 확인
   - Arduino IDE에서 포트 인식 확인
```

#### **Step 2-3: 기본 테스트 코드 업로드**
```bash
시간: 15분

1. Arduino IDE 설정:
   - 보드: "ESP32 Dev Module" 선택
   - 포트: COM 포트 선택 (디바이스 매니저에서 확인)

2. 기본 테스트 코드 작성:

void setup() {
  Serial.begin(115200);
  Serial.println("ESP32 동작 테스트");
  
  // 내장 LED 설정
  pinMode(2, OUTPUT);
}

void loop() {
  digitalWrite(2, HIGH);
  Serial.println("LED ON");
  delay(1000);
  
  digitalWrite(2, LOW);  
  Serial.println("LED OFF");
  delay(1000);
}

3. 업로드 및 확인:
   - 코드 업로드 (Ctrl+U)
   - 시리얼 모니터 열기 (Ctrl+Shift+M)
   - "ESP32 동작 테스트" 메시지 확인
   - 내장 LED 깜빡임 확인

⚠️ 업로드 안되면:
   - BOOT 버튼 누르고 있는 상태에서 RESET 버튼 누르기
   - 드라이버 재설치 (CP210x USB to UART Bridge)
```

---

### **PHASE 3: 센서 연결 (50분)**

#### **Step 3-1: DHT22 온습도 센서**
```bash
시간: 15분

1. DHT22 핀 확인:
   DHT22 정면 뷰 (센서 정면에서 봤을 때):
   ┌─────┐
   │  1  │ ← VCC (3.3V)
   │  2  │ ← DATA  
   │  3  │ ← NC (사용안함)
   │  4  │ ← GND
   └─────┘

2. 연결 작업:
   a) DHT22를 브레드보드 빈 영역에 삽입
   b) 점퍼와이어로 연결:
      - DHT22 핀1 → 브레드보드 + 레일 (빨간선)
      - DHT22 핀4 → 브레드보드 - 레일 (검은선)
      - DHT22 핀2 → ESP32 GPIO2 (노란선)
   
   c) 풀업 저항 연결:
      - 10kΩ 저항을 DHT22 핀2와 핀1 사이에 연결
      
   연결도:
     3.3V ─── DHT22 핀1
       │
    10kΩ 저항
       │  
     GPIO2 ─── DHT22 핀2
     
     GND ──── DHT22 핀4

3. 테스트 코드:

#include <DHT.h>
#define DHT_PIN 2
DHT dht(DHT_PIN, DHT22);

void setup() {
  Serial.begin(115200);
  dht.begin();
  Serial.println("DHT22 테스트 시작");
}

void loop() {
  float temp = dht.readTemperature();
  float humid = dht.readHumidity();
  
  if (isnan(temp) || isnan(humid)) {
    Serial.println("❌ DHT22 읽기 오류");
  } else {
    Serial.printf("🌡️ 온도: %.1f°C, 💧 습도: %.1f%%\n", temp, humid);
  }
  
  delay(2000);
}

4. 테스트 결과 확인:
   - 정상: 온도/습도 값이 정상 범위로 출력
   - 비정상: "nan" 값 출력 → 연결 재확인
```

#### **Step 3-2: 토양 수분 센서**
```bash
시간: 15분

1. 토양센서 핀 확인:
   센서 뒷면 라벨:
   ┌─────────┐
   │   VCC   │ ← 3.3V
   │   GND   │ ← GND  
   │   A0    │ ← 아날로그 출력
   │   D0    │ ← 디지털 출력 (사용안함)
   └─────────┘

2. 연결 작업:
   - VCC → 브레드보드 + 레일 (빨간선)
   - GND → 브레드보드 - 레일 (검은선)  
   - A0 → ESP32 GPIO4 (파란선)

3. 테스트 코드:

#define SOIL_PIN 4

void setup() {
  Serial.begin(115200);
  Serial.println("토양센서 테스트 시작");
}

void loop() {
  int soilValue = analogRead(SOIL_PIN);
  
  Serial.printf("🌱 토양수분: %d ", soilValue);
  
  if (soilValue > 3500) {
    Serial.println("(매우 건조)");
  } else if (soilValue > 2500) {
    Serial.println("(건조)");  
  } else if (soilValue > 1500) {
    Serial.println("(적당)");
  } else {
    Serial.println("(습함)");
  }
  
  delay(1000);
}

4. 테스트 방법:
   - 센서를 공기 중에: 높은 값 (3500~4095)
   - 센서를 물에: 낮은 값 (500~1500)
   - 젖은 화분에: 중간 값 (1500~2500)
```

#### **Step 3-3: 조도 센서 (CdS)**
```bash
시간: 20분

1. CdS 센서 분압 회로 구성:
   
   회로도:
        3.3V
          │
       ┌──┴──┐
       │ CdS │ (조도센서)
       │     │
       └──┬──┘
          │ ←── GPIO5 (측정점)
       ┌──┴──┐  
       │10kΩ │ (고정저항)
       │     │
       └──┬──┘
          │
         GND

2. 연결 작업:
   a) CdS 센서 한쪽 다리 → 브레드보드 + 레일
   b) CdS 센서 다른쪽 다리 → 브레드보드 임의 줄
   c) 10kΩ 저항 한쪽 → CdS와 연결된 줄
   d) 10kΩ 저항 다른쪽 → 브레드보드 - 레일
   e) 점퍼와이어로 중간 연결점 → ESP32 GPIO5

   ⚠️ 주의: CdS는 극성이 없음 (어느 방향이든 OK)
   ⚠️ 10kΩ 저항 색깔: 갈색-검정-주황-금색

3. 테스트 코드:

#define LIGHT_PIN 5

void setup() {
  Serial.begin(115200);
  Serial.println("조도센서 테스트 시작");
}

void loop() {
  int lightValue = analogRead(LIGHT_PIN);
  
  Serial.printf("☀️ 조도: %d ", lightValue);
  
  if (lightValue > 3000) {
    Serial.println("(매우 밝음)");
  } else if (lightValue > 2000) {
    Serial.println("(밝음)");
  } else if (lightValue > 1000) {
    Serial.println("(보통)");
  } else {
    Serial.println("(어두움)");
  }
  
  delay(1000);
}

4. 테스트 방법:
   - 손으로 센서 가리기: 값 감소 확인
   - 스마트폰 손전등 비추기: 값 증가 확인
   - 정상 범위: 500~3500 (환경에 따라 다름)
```

---

### **PHASE 4: 액츄에이터 연결 (60분)**

#### **Step 4-1: 릴레이 모듈 준비**
```bash
시간: 20분

⚠️ 중요: 이 단계부터 5V 전원을 다루므로 더욱 주의!

1. 외부 5V 어댑터 확인:
   - 출력: 5V, 최소 2A 이상
   - 커넥터: DC 2.1mm 또는 USB
   - 극성 확인 (+ 내부, - 외부)

2. 5V 전원 분배:
   - 어댑터 + → 브레드보드 5V 레일 (하단 + 레일)
   - 어댑터 - → 브레드보드 GND 레일 (하단 - 레일)
   
   ⚠️ 주의사항:
   - 5V와 3.3V 레일 혼동 금지!
   - 전원 연결 전 연결 재확인
   - 쇼트 방지 (멀티미터로 측정)

3. 릴레이 모듈 1 (워터펌프용) 연결:
   
   릴레이 모듈 핀 확인:
   ┌─────────────┐
   │     VCC     │ ← 5V 전원
   │     GND     │ ← GND
   │     IN      │ ← GPIO 제어 신호
   │             │
   │  NO COM NC  │ ← 부하 연결부
   └─────────────┘
   
   연결:
   - VCC → 브레드보드 5V 레일 (주황선)
   - GND → 브레드보드 GND 레일 (검은선)
   - IN → ESP32 GPIO18 (초록선)

4. 릴레이 모듈 2 (팬용) 연결:
   - VCC → 브레드보드 5V 레일 (주황선)  
   - GND → 브레드보드 GND 레일 (검은선)
   - IN → ESP32 GPIO19 (파란선)

5. 테스트 코드 (릴레이만):

#define PUMP_RELAY 18
#define FAN_RELAY 19

void setup() {
  Serial.begin(115200);
  pinMode(PUMP_RELAY, OUTPUT);
  pinMode(FAN_RELAY, OUTPUT);
  
  // 초기값: 릴레이 OFF
  digitalWrite(PUMP_RELAY, LOW);
  digitalWrite(FAN_RELAY, LOW);
  
  Serial.println("릴레이 테스트 시작");
}

void loop() {
  Serial.println("💧 워터펌프 릴레이 ON");
  digitalWrite(PUMP_RELAY, HIGH);
  delay(2000);
  
  Serial.println("💧 워터펌프 릴레이 OFF");  
  digitalWrite(PUMP_RELAY, LOW);
  delay(1000);
  
  Serial.println("🌪️ 팬 릴레이 ON");
  digitalWrite(FAN_RELAY, HIGH);
  delay(2000);
  
  Serial.println("🌪️ 팬 릴레이 OFF");
  digitalWrite(FAN_RELAY, LOW);
  delay(1000);
}

6. 릴레이 동작 확인:
   - 릴레이 모듈의 LED 켜짐/꺼짐 확인
   - "딸깍" 소리 들림 확인
   - GPIO HIGH일 때 릴레이 ON
```

#### **Step 4-2: 워터펌프 연결**
```bash
시간: 15분

1. 워터펌프 사양 확인:
   - 정격전압: 3~6V DC
   - 소비전류: 100~300mA
   - 최대 양정: 40~80cm

2. 워터펌프 부하 연결:
   
   연결도:
   5V 전원 ──── 릴레이1 NO ──── 워터펌프 (+)
                              │
   GND ──────────────────────── 워터펌프 (-)
   
   실제 연결:
   a) 워터펌프 빨간선(+) → 릴레이1의 COM 단자
   b) 5V 전원선 → 릴레이1의 NO 단자  
   c) 워터펌프 검은선(-) → GND

3. 안전 테스트:
   - 펌프를 물그릇에 담그기
   - 물 호스를 연결하여 물이 나오는지 확인
   - 릴레이 ON/OFF에 따른 펌프 동작 확인

⚠️ 주의사항:
- 펌프는 반드시 물에 담근 상태에서 동작 (공회전 금지)
- 물과 전기 부품 분리 철저히
- 릴레이 접점 용량 확인 (보통 10A 250V AC / 10A 30V DC)
```

#### **Step 4-3: 팬 연결**
```bash
시간: 10분

1. 팬 사양 확인:
   - 정격전압: 5V DC
   - 소비전류: 50~200mA
   - 크기: 40x40mm 또는 60x60mm

2. 팬 부하 연결:
   - 팬 빨간선(+) → 릴레이2의 COM 단자
   - 5V 전원선 → 릴레이2의 NO 단자
   - 팬 검은선(-) → GND

3. 동작 테스트:
   - 릴레이2 ON 시 팬 회전 확인
   - 풍량 및 소음 확인
   - 역방향 연결 시 반대로 회전 (문제없음)
```

#### **Step 4-4: LED 스트립 연결**
```bash
시간: 15분

1. WS2812B LED 스트립 사양:
   - 입력전압: 5V DC
   - 소비전류: LED 1개당 약 60mA (최대)
   - 10개 LED = 최대 600mA

2. 연결 작업:
   
   LED 스트립 커넥터 확인:
   ┌─────────────┐
   │     5V      │ ← 빨간선 (전원)
   │     GND     │ ← 검은선 (접지)  
   │     DIN     │ ← 초록/흰선 (데이터)
   └─────────────┘
   
   연결:
   a) LED 5V → 브레드보드 5V 레일
   b) LED GND → 브레드보드 GND 레일
   c) 330Ω 저항을 ESP32 GPIO21과 LED DIN 사이에 연결
   
   보호회로:
   ESP32 GPIO21 ──[330Ω]── LED DIN

3. 라이브러리 설치:
   - Arduino IDE → 라이브러리 매니저
   - "Adafruit NeoPixel" 검색 후 설치

4. 테스트 코드:

#include <Adafruit_NeoPixel.h>

#define LED_PIN 21
#define LED_COUNT 10

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  Serial.begin(115200);
  strip.begin();
  strip.show(); // 모든 LED 끄기
  Serial.println("LED 스트립 테스트 시작");
}

void loop() {
  // 빨간색
  for(int i=0; i<LED_COUNT; i++) {
    strip.setPixelColor(i, strip.Color(255, 0, 0));
  }
  strip.show();
  Serial.println("🔴 빨간색");
  delay(1000);
  
  // 초록색  
  for(int i=0; i<LED_COUNT; i++) {
    strip.setPixelColor(i, strip.Color(0, 255, 0));
  }
  strip.show();
  Serial.println("🟢 초록색");
  delay(1000);
  
  // 파란색
  for(int i=0; i<LED_COUNT; i++) {
    strip.setPixelColor(i, strip.Color(0, 0, 255));
  }
  strip.show();
  Serial.println("🔵 파란색");
  delay(1000);
  
  // 모든 LED 끄기
  strip.clear();
  strip.show();
  delay(1000);
}

5. 문제해결:
   - LED 안켜짐: 전원(5V) 및 GND 연결 확인
   - 첫번째만 켜짐: DIN 연결 및 저항 확인
   - 색깔 이상: NEO_GRB 설정 확인 (NEO_RGB로 변경 시도)
```

---

### **PHASE 5: 통합 테스트 (40분)**

#### **Step 5-1: 전체 시스템 통합**
```bash
시간: 20분

1. 최종 연결 확인 체크리스트:

전원 연결:
□ ESP32 3V3 → 브레드보드 3.3V 레일  
□ ESP32 GND → 브레드보드 GND 레일
□ 외부 5V → 브레드보드 5V 레일
□ 모든 GND 공통 연결

센서 연결:
□ DHT22: VCC(3V3), GND, DATA(GPIO2) + 10kΩ 풀업
□ 토양센서: VCC(3V3), GND, A0(GPIO4)  
□ 조도센서: 3V3 - CdS - GPIO5 - 10kΩ - GND

액츄에이터 연결:
□ 릴레이1: VCC(5V), GND, IN(GPIO18)
□ 릴레이2: VCC(5V), GND, IN(GPIO19)
□ 워터펌프: 릴레이1 COM/NO를 통해 5V 연결
□ 팬: 릴레이2 COM/NO를 통해 5V 연결  
□ LED스트립: 5V, GND, DIN(GPIO21+330Ω저항)

2. 멀티미터로 전압 측정:
   - 3.3V 레일: 3.2~3.4V 확인
   - 5V 레일: 4.8~5.2V 확인
   - 각 센서 VCC 핀에서 정상 전압 확인

3. 단계별 전원 투입:
   a) ESP32 USB 연결 (3.3V 시스템 동작)
   b) 외부 5V 어댑터 연결 (5V 시스템 동작)
   c) 각 부품별 LED 점등 확인
```

#### **Step 5-2: 통합 코드 업로드**
```bash
시간: 20분

1. 완전한 통합 코드:

#include <WiFi.h>
#include <DHT.h>
#include <Adafruit_NeoPixel.h>
#include <WebServer.h>

// 핀 정의
#define DHT_PIN 2
#define SOIL_PIN 4
#define LIGHT_PIN 5  
#define PUMP_RELAY 18
#define FAN_RELAY 19
#define LED_PIN 21
#define LED_COUNT 10

// 센서 및 액츄에이터 초기화
DHT dht(DHT_PIN, DHT22);
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);
WebServer server(80);

// WiFi 설정 (본인 WiFi로 변경)
const char* ssid = "당신의_WiFi_이름";
const char* password = "WiFi_비밀번호";

// 센서 데이터 저장 변수
float temperature = 0;
float humidity = 0;
int soilMoisture = 0;
int lightLevel = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("🌱 스마트 온실 시스템 시작!");
  
  // 센서 초기화
  dht.begin();
  strip.begin();
  strip.show();
  
  // 릴레이 핀 설정
  pinMode(PUMP_RELAY, OUTPUT);
  pinMode(FAN_RELAY, OUTPUT);
  digitalWrite(PUMP_RELAY, LOW);
  digitalWrite(FAN_RELAY, LOW);
  
  // WiFi 연결
  WiFi.begin(ssid, password);
  Serial.print("WiFi 연결 중");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("✅ WiFi 연결 완료!");
  Serial.print("IP 주소: ");
  Serial.println(WiFi.localIP());
  
  // 웹서버 시작
  setupWebServer();
  
  // 시작 알림 효과
  startupEffect();
}

void loop() {
  // 웹서버 처리
  server.handleClient();
  
  // 센서 데이터 읽기
  readSensors();
  
  // 센서 데이터 출력
  printSensorData();
  
  // 자동 제어 실행
  autoControl();
  
  // LED 효과 업데이트
  updateLEDs();
  
  delay(5000); // 5초마다 실행
}

void readSensors() {
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();
  soilMoisture = analogRead(SOIL_PIN);
  lightLevel = analogRead(LIGHT_PIN);
  
  // NaN 값 처리
  if (isnan(temperature)) temperature = 0;
  if (isnan(humidity)) humidity = 0;
}

void printSensorData() {
  Serial.println("=== 센서 데이터 ===");
  Serial.printf("🌡️ 온도: %.1f°C\n", temperature);
  Serial.printf("💧 습도: %.1f%%\n", humidity);  
  Serial.printf("🌱 토양수분: %d\n", soilMoisture);
  Serial.printf("☀️ 조도: %d\n", lightLevel);
}

void autoControl() {
  Serial.println("=== 자동 제어 ===");
  
  // 토양이 건조하면 급수 (값이 클수록 건조)
  if (soilMoisture > 3000) {
    Serial.println("💧 토양 건조 - 워터펌프 ON");
    digitalWrite(PUMP_RELAY, HIGH);
    delay(3000); // 3초간 급수
    digitalWrite(PUMP_RELAY, LOW);
    Serial.println("💧 급수 완료");
  }
  
  // 온도가 높으면 팬 작동
  if (temperature > 28.0) {
    Serial.println("🌪️ 온도 높음 - 팬 ON");
    digitalWrite(FAN_RELAY, HIGH);
  } else if (temperature < 24.0) {
    Serial.println("❄️ 온도 적정 - 팬 OFF");  
    digitalWrite(FAN_RELAY, LOW);
  }
}

void updateLEDs() {
  uint32_t color;
  
  // 온도에 따른 색상 결정
  if (temperature < 20) {
    color = strip.Color(0, 0, 255);      // 파란색 (차가움)
  } else if (temperature < 25) {
    color = strip.Color(0, 255, 0);      // 초록색 (적정)  
  } else if (temperature < 30) {
    color = strip.Color(255, 255, 0);    // 노란색 (따뜻)
  } else {
    color = strip.Color(255, 0, 0);      // 빨간색 (뜨거움)
  }
  
  // 조도가 낮으면 LED 밝게, 높으면 어둡게
  int brightness = map(lightLevel, 0, 4095, 255, 50);
  brightness = constrain(brightness, 50, 255);
  
  for(int i=0; i<LED_COUNT; i++) {
    strip.setPixelColor(i, color);
  }
  strip.setBrightness(brightness);
  strip.show();
}

void startupEffect() {
  // 무지개 효과로 시작 알림
  uint32_t colors[] = {
    strip.Color(255, 0, 0),    // 빨강
    strip.Color(255, 127, 0),  // 주황  
    strip.Color(255, 255, 0),  // 노랑
    strip.Color(0, 255, 0),    // 초록
    strip.Color(0, 0, 255),    // 파랑
    strip.Color(75, 0, 130),   // 남색
    strip.Color(148, 0, 211)   // 보라
  };
  
  for (int c = 0; c < 7; c++) {
    for (int i = 0; i < LED_COUNT; i++) {
      strip.setPixelColor(i, colors[c]);
    }
    strip.show();
    delay(200);
  }
  
  strip.clear();
  strip.show();
}

void setupWebServer() {
  server.on("/", []() {
    String html = generateWebPage();
    server.send(200, "text/html", html);
  });
  
  server.on("/api/sensors", []() {
    String json = "{";
    json += "\"temperature\":" + String(temperature, 1) + ",";
    json += "\"humidity\":" + String(humidity, 1) + ",";
    json += "\"soil\":" + String(soilMoisture) + ",";
    json += "\"light\":" + String(lightLevel);
    json += "}";
    server.send(200, "application/json", json);
  });
  
  server.begin();
  Serial.println("🌐 웹서버 시작: http://" + WiFi.localIP().toString());
}

String generateWebPage() {
  return R"(
<!DOCTYPE html>
<html>
<head>
    <title>스마트 온실</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; margin: 20px; background: #f0f8f0; }
        .container { max-width: 600px; margin: 0 auto; }
        .card { background: white; padding: 20px; margin: 10px; border-radius: 10px; }
        .sensor { display: inline-block; margin: 10px; text-align: center; }
        .value { font-size: 24px; font-weight: bold; color: #2e7d32; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌱 스마트 온실 모니터링</h1>
        <div class="card" id="sensors">
            <!-- 센서 데이터 로드됨 -->
        </div>
    </div>
    <script>
        function loadSensors() {
            fetch('/api/sensors')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('sensors').innerHTML = `
                        <div class="sensor">
                            <div>🌡️ 온도</div>
                            <div class="value">${data.temperature}°C</div>
                        </div>
                        <div class="sensor">
                            <div>💧 습도</div>
                            <div class="value">${data.humidity}%</div>
                        </div>
                        <div class="sensor">
                            <div>🌱 토양</div>
                            <div class="value">${data.soil}</div>
                        </div>
                        <div class="sensor">
                            <div>☀️ 조도</div>
                            <div class="value">${data.light}</div>
                        </div>
                    `;
                });
        }
        setInterval(loadSensors, 5000);
        loadSensors();
    </script>
</body>
</html>
  )";
}

2. 라이브러리 설치 확인:
   - DHT sensor library
   - Adafruit NeoPixel
   - ESP32 WiFi (기본 포함)

3. 코드 업로드 및 테스트:
   - WiFi 정보 수정 후 업로드
   - 시리얼 모니터에서 동작 확인
   - 웹 브라우저에서 IP 접속 확인
```

---

### **PHASE 6: 최종 검증 및 마무리 (30분)**

#### **Step 6-1: 기능별 검증**
```bash
시간: 20분

1. 센서 정확도 검증:
   □ DHT22: 실제 온도계와 비교 (±2°C 내외)
   □ 토양센서: 건조/습윤 상태 구분 확인
   □ 조도센서: 밝기 변화에 따른 값 변화 확인

2. 액츄에이터 동작 검증:
   □ 릴레이1: 워터펌프 정상 동작
   □ 릴레이2: 팬 정상 회전
   □ LED스트립: 색상 및 밝기 변화 확인

3. 자동제어 로직 검증:
   □ 토양 건조 시 자동 급수 동작
   □ 고온 시 팬 자동 가동
   □ 조도에 따른 LED 밝기 조절
   □ 온도에 따른 LED 색상 변화

4. 웹 인터페이스 검증:
   □ WiFi 연결 및 IP 할당
   □ 웹페이지 정상 표시
   □ 실시간 센서 데이터 업데이트
   □ 모바일 기기에서 접속 확인

5. 안정성 테스트:
   □ 30분 이상 연속 동작 확인
   □ 메모리 누수 없음 확인
   □ WiFi 재연결 기능 확인
   □ 센서 오류 시 시스템 안정성 확인
```

#### **Step 6-2: 마무리 작업**
```bash
시간: 10분

1. 배선 정리:
   - 타이랩으로 전선 묶기
   - 브레드보드 위 부품 고정 (양면테이프)
   - 라벨 부착 (각 센서와 릴레이 표시)

2. 보호 조치:
   - 전자부품을 물로부터 분리
   - 워터펌프 주변 방수 처리
   - 브레드보드 아래 절연 매트 배치

3. 문서화:
   - 최종 연결 상태 사진 촬영
   - 센서 교정값 기록
   - WiFi IP 주소 메모
   - 문제 발생 시 체크포인트 정리

4. 백업:
   - 최종 코드를 GitHub에 업로드
   - 설정값들을 별도 파일로 저장
   - 회로도를 이미지로 저장
```

---

## 🎉 **완성 후 활용 가이드**

### **일상 사용법**
```bash
1. 시스템 시작:
   - ESP32 USB 연결 (PC 또는 파워뱅크)
   - 5V 어댑터 연결
   - 2-3분 후 WiFi 연결 완료

2. 모니터링:
   - 스마트폰으로 웹페이지 접속
   - 실시간 센서 데이터 확인
   - 자동 제어 동작 상태 확인

3. 유지보수:
   - 주 1회 워터펌프 물 보충
   - 월 1회 센서 청소
   - 분기 1회 코드 업데이트
```

### **문제해결 가이드**
```bash
증상: 센서값이 이상함
→ 전원 연결 확인
→ 센서 청소
→ 코드 재시작

증상: 릴레이 안됨  
→ 5V 전원 확인
→ GPIO 핀 연결 확인
→ 릴레이 모듈 교체

증상: WiFi 안됨
→ 네트워크 이름/비밀번호 확인  
→ ESP32 리셋
→ 코드 재업로드

증상: LED 안켜짐
→ 5V 전원 및 전류 용량 확인
→ 데이터핀 연결 및 저항 확인
→ LED 스트립 방향 확인
```

### **확장 아이디어**
```bash
레벨 2: 센서 추가
- pH 센서로 토양 산성도 측정
- CO2 센서로 공기질 모니터링
- 카메라로 식물 성장 기록

레벨 3: 스마트 기능
- 스마트폰 알림 (Push notification)
- 음성 명령 제어 (Google Assistant)
- AI 기반 최적화 (TensorFlow Lite)

레벨 4: IoT 연동
- AWS IoT Core 클라우드 연동
- 다중 온실 관리 시스템
- 빅데이터 분석 및 예측
```

---

**🎊 축하합니다! 완전한 스마트 온실 시스템을 구축했습니다! 🎊**

이제 CI/CD 파이프라인과 연동하여 코드 수정 시 자동으로 ESP32에 배포되도록 설정할 차례입니다!