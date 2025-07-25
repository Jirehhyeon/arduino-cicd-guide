# 1단계: 프로젝트 초기 설정

## 📋 개요
아두이노 프로젝트의 기본 구조를 설정하고 개발 환경을 준비합니다.

## 🏗️ 프로젝트 구조 생성

### 표준 디렉터리 구조
```
arduino-iot-project/
├── src/                    # 소스 코드
│   ├── main/
│   │   └── main.ino       # 메인 스케치
│   ├── libraries/         # 커스텀 라이브러리
│   └── tests/             # 단위 테스트
├── hardware/              # 회로도 및 하드웨어 문서
│   ├── schematics/
│   └── datasheets/
├── docs/                  # 프로젝트 문서
│   ├── api/
│   └── guides/
├── config/                # 설정 파일
│   ├── boards.txt
│   └── platformio.ini
├── scripts/               # 자동화 스크립트
│   ├── build.sh
│   └── deploy.sh
├── .github/               # GitHub Actions (선택사항)
│   └── workflows/
├── Jenkinsfile           # Jenkins 파이프라인
├── README.md
├── .gitignore
└── LICENSE
```

### 프로젝트 초기화

1. **디렉터리 생성**
```bash
mkdir arduino-iot-project
cd arduino-iot-project

# 기본 디렉터리 구조 생성
mkdir -p src/main src/libraries src/tests
mkdir -p hardware/schematics hardware/datasheets
mkdir -p docs/api docs/guides
mkdir -p config scripts
```

2. **Git 초기화**
```bash
git init
git branch -M main
```

3. **.gitignore 파일 생성**
```bash
cat > .gitignore << 'EOF'
# Arduino
*.hex
*.elf
*.map
build/
.pioenvs/
.piolibdeps/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
EOF
```

## ⚙️ 아두이노 환경 설정

### Arduino CLI 설치

**Linux/MacOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
```

**Windows:**
```powershell
# Chocolatey 사용
choco install arduino-cli

# 또는 직접 다운로드
# https://github.com/arduino/arduino-cli/releases
```

### Arduino CLI 설정

1. **설정 파일 생성**
```bash
arduino-cli config init
```

2. **보드 패키지 인덱스 업데이트**
```bash
arduino-cli core update-index
```

3. **필요한 보드 패키지 설치**
```bash
# Arduino AVR 보드 (Uno, Nano 등)
arduino-cli core install arduino:avr

# ESP32 보드
arduino-cli core install esp32:esp32

# ESP8266 보드
arduino-cli core install esp8266:esp8266
```

4. **필수 라이브러리 설치**
```bash
arduino-cli lib install "DHT sensor library"
arduino-cli lib install "ArduinoJson"
arduino-cli lib install "WiFi"
arduino-cli lib install "PubSubClient"
```

### PlatformIO 설정 (선택사항)

1. **PlatformIO 설치**
```bash
pip install platformio
```

2. **platformio.ini 설정 파일**
```ini
[env:uno]
platform = atmelavr
board = uno
framework = arduino

[env:esp32]
platform = espressif32
board = esp32dev
framework = arduino

[env:esp8266]
platform = espressif8266
board = nodemcuv2
framework = arduino

; 공통 라이브러리
lib_deps = 
    adafruit/DHT sensor library@^1.4.4
    bblanchon/ArduinoJson@^6.21.2
    knolleary/PubSubClient@^2.8

; 시리얼 모니터 설정
monitor_speed = 115200
```

## 📝 기본 스케치 작성

### main.ino 템플릿
```cpp
/*
 * Arduino IoT Project Template
 * 
 * 설명: 기본 템플릿 스케치
 * 작성자: Your Name
 * 생성일: 2024-01-01
 * 버전: 1.0.0
 */

// 라이브러리 포함
#include <Arduino.h>

// 상수 정의
#define LED_PIN 13
#define SERIAL_BAUD 115200

// 전역 변수
unsigned long lastUpdate = 0;
const unsigned long UPDATE_INTERVAL = 1000; // 1초

// 함수 선언
void setup();
void loop();
void initializeSystem();
void handleTasks();

/**
 * 시스템 초기화
 */
void setup() {
    // 시리얼 통신 초기화
    Serial.begin(SERIAL_BAUD);
    while (!Serial) {
        ; // 시리얼 포트 연결 대기
    }
    
    Serial.println("=== Arduino IoT Project Starting ===");
    
    // 시스템 초기화
    initializeSystem();
    
    Serial.println("System initialized successfully!");
}

/**
 * 메인 루프
 */
void loop() {
    // 주기적 작업 실행
    if (millis() - lastUpdate >= UPDATE_INTERVAL) {
        handleTasks();
        lastUpdate = millis();
    }
    
    // 기타 비동기 작업들
    delay(10); // CPU 사용률 조절
}

/**
 * 시스템 초기화 함수
 */
void initializeSystem() {
    // LED 핀 초기화
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
    
    // 추가 초기화 작업들...
    Serial.println("Hardware initialized");
}

/**
 * 주기적 작업 처리 함수
 */
void handleTasks() {
    // LED 토글
    static bool ledState = false;
    ledState = !ledState;
    digitalWrite(LED_PIN, ledState);
    
    // 상태 출력
    Serial.print("System running - Uptime: ");
    Serial.print(millis());
    Serial.println(" ms");
}
```

### 라이브러리 구조 예시

**src/libraries/SensorManager/SensorManager.h**
```cpp
#ifndef SENSOR_MANAGER_H
#define SENSOR_MANAGER_H

#include <Arduino.h>

class SensorManager {
private:
    bool initialized;
    
public:
    SensorManager();
    bool begin();
    float readTemperature();
    float readHumidity();
    bool isReady();
};

#endif
```

**src/libraries/SensorManager/SensorManager.cpp**
```cpp
#include "SensorManager.h"

SensorManager::SensorManager() : initialized(false) {
}

bool SensorManager::begin() {
    // 센서 초기화 로직
    initialized = true;
    return true;
}

float SensorManager::readTemperature() {
    if (!initialized) return -999.0;
    // 온도 읽기 로직
    return 25.0; // 예시 값
}

float SensorManager::readHumidity() {
    if (!initialized) return -999.0;
    // 습도 읽기 로직
    return 60.0; // 예시 값
}

bool SensorManager::isReady() {
    return initialized;
}
```

## 🧪 기본 테스트 설정

### 단위 테스트 프레임워크 설정

**src/tests/test_main.cpp**
```cpp
#include <unity.h>
#include "../libraries/SensorManager/SensorManager.h"

// 테스트 케이스
void test_sensor_initialization() {
    SensorManager sensor;
    TEST_ASSERT_TRUE(sensor.begin());
    TEST_ASSERT_TRUE(sensor.isReady());
}

void test_sensor_readings() {
    SensorManager sensor;
    sensor.begin();
    
    float temp = sensor.readTemperature();
    float hum = sensor.readHumidity();
    
    TEST_ASSERT_TRUE(temp > -100 && temp < 100);
    TEST_ASSERT_TRUE(hum >= 0 && hum <= 100);
}

void setup() {
    UNITY_BEGIN();
    
    RUN_TEST(test_sensor_initialization);
    RUN_TEST(test_sensor_readings);
    
    UNITY_END();
}

void loop() {
    // 테스트는 setup에서 실행됨
}
```

### Makefile 생성

**src/tests/Makefile**
```makefile
# 테스트 빌드 설정
CXX = g++
CXXFLAGS = -std=c++11 -Wall -Wextra
INCLUDES = -I../libraries -I.

# Unity 테스트 프레임워크
UNITY_ROOT = ./unity
UNITY_SRC = $(UNITY_ROOT)/unity.c

# 테스트 대상
TEST_SRC = test_main.cpp
TARGET = test_runner

# 빌드 규칙
all: $(TARGET)

$(TARGET): $(TEST_SRC) $(UNITY_SRC)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $@ $^

test: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(TARGET)

.PHONY: all test clean
```

## 🔧 개발 도구 설정

### VSCode 설정

**.vscode/c_cpp_properties.json**
```json
{
    "configurations": [
        {
            "name": "Arduino",
            "includePath": [
                "${workspaceFolder}/**",
                "~/Arduino/libraries/**",
                "/usr/share/arduino/hardware/arduino/avr/libraries/**"
            ],
            "defines": [
                "ARDUINO=10819",
                "ARDUINO_AVR_UNO",
                "F_CPU=16000000L"
            ],
            "compilerPath": "/usr/bin/avr-gcc",
            "cStandard": "c11",
            "cppStandard": "c++11",
            "intelliSenseMode": "gcc-x64"
        }
    ],
    "version": 4
}
```

**.vscode/tasks.json**
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Arduino: Verify",
            "type": "shell",
            "command": "arduino-cli",
            "args": [
                "compile",
                "--fqbn",
                "arduino:avr:uno",
                "${workspaceFolder}/src/main"
            ],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "Arduino: Upload",
            "type": "shell",
            "command": "arduino-cli",
            "args": [
                "upload",
                "-p",
                "/dev/ttyUSB0",
                "--fqbn",
                "arduino:avr:uno",
                "${workspaceFolder}/src/main"
            ],
            "group": "build"
        }
    ]
}
```

## ✅ 검증 단계

### 1. 빌드 테스트
```bash
# Arduino CLI로 컴파일 확인
arduino-cli compile --fqbn arduino:avr:uno src/main

# PlatformIO로 빌드 확인 (선택사항)
pio run
```

### 2. 단위 테스트 실행
```bash
cd src/tests
make test
```

### 3. 기본 업로드 테스트
```bash
# 보드 연결 확인
arduino-cli board list

# 업로드 테스트
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:uno src/main
```

## 🎯 다음 단계

프로젝트 초기 설정이 완료되었습니다. 다음 단계로 진행하세요:

➡️ **[2단계: Jira 설정](02-jira-setup.md)**

## 📚 참고 자료

- [Arduino CLI 공식 문서](https://arduino.github.io/arduino-cli/)
- [PlatformIO 가이드](https://docs.platformio.org/)
- [Unity 테스트 프레임워크](http://www.throwtheswitch.org/unity)