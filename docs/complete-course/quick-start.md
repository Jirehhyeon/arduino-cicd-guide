# ⚡ 30분 퀵스타트 가이드

> **"바쁜 분들을 위한 최소한의 설정으로 동작하는 CI/CD 시스템 구축"**

**⏱️ 소요시간: 30분**  
**🎯 목표: 아두이노 → Git → 자동 빌드까지 한 번에!**  
**📋 결과물: 코드 푸시하면 자동으로 컴파일되는 시스템**

## 🚀 빠른 개요

이 가이드는 **최소한의 설정**으로 다음을 구현합니다:
- ✅ Git 저장소에 아두이노 코드 저장
- ✅ 코드 푸시 시 자동 컴파일 확인
- ✅ 빌드 성공/실패 알림

**⚠️ 주의**: 이는 맛보기 버전입니다. 완전한 기능을 원한다면 [전체 가이드](00-prerequisites.md)를 따라주세요.

---

## 📋 필요한 것 (체크리스트)

### ✅ **필수 준비물**
- [ ] 컴퓨터 (Windows/Mac/Linux 상관없음)
- [ ] 아두이노 보드 (있으면 좋지만 없어도 됨)
- [ ] 인터넷 연결
- [ ] 30분의 시간

### ✅ **계정 준비** (무료)
- [ ] GitHub 계정
- [ ] GitHub Actions 활성화 (무료 한도 있음)

---

## 🏃‍♂️ Step 1: GitHub 저장소 생성 (5분)

### 1.1 새 저장소 만들기

```bash
1. https://github.com 로그인
2. 우측 상단 "+" → "New repository" 클릭
3. Repository name: "arduino-ci-test"
4. Description: "Arduino CI/CD Quick Test"
5. Public 선택 (Private도 가능하지만 무료 Actions 한도 다름)
6. "Add a README file" 체크
7. "Add .gitignore" → "Arduino" 선택
8. "Create repository" 클릭
```

### 1.2 로컬에 클론

```bash
# 터미널/CMD에서 실행
git clone https://github.com/your-username/arduino-ci-test.git
cd arduino-ci-test
```

---

## 🔧 Step 2: 간단한 아두이노 프로젝트 생성 (5분)

### 2.1 프로젝트 구조 생성

```bash
# 폴더 구조 생성
mkdir -p src/main
mkdir -p .github/workflows
```

### 2.2 기본 아두이노 스케치 작성

**파일: `src/main/main.ino`**
```cpp
/*
 * 30분 퀵스타트 테스트 프로젝트
 * LED 깜빡이기 + 시리얼 출력
 */

#define LED_PIN 13
#define SERIAL_BAUD 9600

unsigned long lastBlink = 0;
const unsigned long BLINK_INTERVAL = 1000;
bool ledState = false;

void setup() {
  Serial.begin(SERIAL_BAUD);
  pinMode(LED_PIN, OUTPUT);
  
  Serial.println("=== Arduino CI/CD Test Started ===");
  Serial.println("Build time: " __DATE__ " " __TIME__);
  Serial.println("Ready to blink!");
}

void loop() {
  // LED 깜빡이기
  if (millis() - lastBlink >= BLINK_INTERVAL) {
    ledState = !ledState;
    digitalWrite(LED_PIN, ledState);
    
    Serial.print("LED State: ");
    Serial.println(ledState ? "ON" : "OFF");
    Serial.print("Uptime: ");
    Serial.print(millis() / 1000);
    Serial.println(" seconds");
    
    lastBlink = millis();
  }
  
  delay(10); // CPU 절약
}

// 기본 테스트 함수들
int addNumbers(int a, int b) {
  return a + b;
}

bool isEven(int number) {
  return (number % 2) == 0;
}

float celsiusToFahrenheit(float celsius) {
  return (celsius * 9.0 / 5.0) + 32.0;
}
```

### 2.3 라이브러리 의존성 파일

**파일: `arduino_deps.txt`**
```
# 이 프로젝트에서 사용하는 라이브러리들
# GitHub Actions에서 자동으로 설치됩니다

# 기본 아두이노 코어 (자동 포함됨)
# arduino:avr

# 추가 라이브러리 (필요시 주석 해제)
# DHT sensor library
# ArduinoJson
# WiFi
```

---

## 🤖 Step 3: GitHub Actions CI 설정 (10분)

### 3.1 워크플로우 파일 생성

**파일: `.github/workflows/arduino-ci.yml`**
```yaml
name: Arduino CI/CD Quick Test

# 트리거: main 브랜치에 푸시 또는 Pull Request
on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  arduino-compile:
    name: 아두이노 컴파일 테스트
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        # 여러 보드에서 테스트
        board:
          - arduino:avr:uno
          - arduino:avr:nano
          # ESP32 테스트 (선택사항)
          # - esp32:esp32:esp32
    
    steps:
    # 1. 코드 체크아웃
    - name: 📥 코드 가져오기
      uses: actions/checkout@v4
    
    # 2. Arduino CLI 설치
    - name: 🔧 Arduino CLI 설치
      uses: arduino/setup-arduino-cli@v1
      
    # 3. 보드 패키지 설치
    - name: 📦 보드 패키지 설치
      run: |
        arduino-cli core update-index
        arduino-cli core install arduino:avr
        
    # 4. 필요한 라이브러리 설치 (있는 경우)
    - name: 📚 라이브러리 설치
      run: |
        # 기본 라이브러리들 (필요시 추가)
        echo "기본 라이브러리만 사용 중..."
        
    # 5. 스케치 컴파일
    - name: 🔨 아두이노 스케치 컴파일
      run: |
        echo "컴파일 시작: ${{ matrix.board }}"
        arduino-cli compile --fqbn ${{ matrix.board }} src/main --verbose
        
    # 6. 빌드 결과 확인
    - name: ✅ 빌드 결과 확인
      run: |
        if [ -f "src/main/build/*/src.main.ino.hex" ]; then
          echo "🎉 빌드 성공!"
          ls -la src/main/build/*/src.main.ino.*
        else
          echo "❌ 빌드 파일을 찾을 수 없습니다"
          ls -la src/main/build/ || echo "build 폴더가 없습니다"
        fi

  # 간단한 코드 품질 검사
  code-quality:
    name: 코드 품질 검사
    runs-on: ubuntu-latest
    
    steps:
    - name: 📥 코드 가져오기
      uses: actions/checkout@v4
      
    - name: 🔍 기본 코드 검사
      run: |
        echo "=== 코드 품질 검사 시작 ==="
        
        # .ino 파일 찾기
        INO_FILES=$(find . -name "*.ino" -type f)
        
        if [ -z "$INO_FILES" ]; then
          echo "❌ .ino 파일을 찾을 수 없습니다!"
          exit 1
        fi
        
        echo "✅ 발견된 .ino 파일들:"
        echo "$INO_FILES"
        
        # 기본 문법 검사
        for file in $INO_FILES; do
          echo "검사 중: $file"
          
          # setup() 함수 존재 확인
          if ! grep -q "void setup(" "$file"; then
            echo "❌ $file에 setup() 함수가 없습니다!"
            exit 1
          fi
          
          # loop() 함수 존재 확인  
          if ! grep -q "void loop(" "$file"; then
            echo "❌ $file에 loop() 함수가 없습니다!"
            exit 1
          fi
          
          echo "✅ $file 기본 구조 확인 완료"
        done
        
        echo "🎉 모든 코드 품질 검사 통과!"

  # 성공 시 알림 (선택사항)
  notify-success:
    name: 성공 알림
    runs-on: ubuntu-latest
    needs: [arduino-compile, code-quality]
    if: success()
    
    steps:
    - name: 🎉 성공 메시지
      run: |
        echo "🚀 모든 테스트 통과!"
        echo "✅ 아두이노 컴파일 성공"
        echo "✅ 코드 품질 검사 통과"
        echo "🎯 배포 준비 완료!"
```

### 3.2 README 파일 업데이트

**파일: `README.md` (기존 파일 수정)**
```markdown
# 🚀 Arduino CI/CD Quick Test

30분 만에 구축한 아두이노 CI/CD 시스템!

## 📊 빌드 상태

![Arduino CI](https://github.com/your-username/arduino-ci-test/workflows/Arduino%20CI%2FCD%20Quick%20Test/badge.svg)

## 🎯 프로젝트 개요

- **목적**: 아두이노 코드 자동 빌드 테스트
- **기능**: LED 깜빡이기 + 시리얼 출력
- **보드**: Arduino Uno, Nano 지원

## 🔧 하드웨어 연결

```
Arduino Uno:
- LED: Pin 13 (내장 LED 사용)
- 전원: USB 연결
```

## 💻 사용법

1. 아두이노를 컴퓨터에 연결
2. Arduino IDE에서 `src/main/main.ino` 열기
3. 업로드
4. 시리얼 모니터 확인 (9600 baud)

## 🤖 CI/CD 기능

- ✅ 자동 컴파일 테스트 (Uno, Nano)
- ✅ 기본 코드 품질 검사
- ✅ 빌드 상태 뱃지

## 📈 확장 계획

이 프로젝트는 30분 퀵스타트입니다. 더 많은 기능을 원한다면:

- [ ] 실제 하드웨어 테스트
- [ ] 센서 라이브러리 통합
- [ ] 자동 배포
- [ ] Jira 연동
- [ ] Slack 알림

## 🔗 링크

- [전체 Arduino CI/CD 가이드](https://github.com/your-username/arduino-cicd-guide)
- [Arduino 공식 문서](https://arduino.cc)
```

---

## 🚀 Step 4: 테스트 및 확인 (10분)

### 4.1 모든 파일 커밋 및 푸시

```bash
# 모든 파일 추가
git add .

# 커밋 (의미있는 메시지 작성)
git commit -m "feat: add basic Arduino CI/CD setup

- Add LED blink sketch with serial output
- Add GitHub Actions workflow for compilation
- Support Arduino Uno and Nano boards
- Add basic code quality checks"

# GitHub에 푸시
git push origin main
```

### 4.2 GitHub Actions 확인

```bash
1. GitHub 저장소 페이지로 이동
2. "Actions" 탭 클릭
3. 방금 푸시한 워크플로우 실행 확인
4. 각 단계별 진행상황 모니터링
```

**✅ 성공적인 실행 결과:**
```
✅ 아두이노 컴파일 테스트 (arduino:avr:uno) - 성공
✅ 아두이노 컴파일 테스트 (arduino:avr:nano) - 성공  
✅ 코드 품질 검사 - 성공
✅ 성공 알림 - 성공
```

### 4.3 빌드 뱃지 확인

```bash
1. GitHub 저장소 메인 페이지로 이동
2. README.md에서 빌드 뱃지 확인
3. 녹색 "passing" 뱃지가 표시되면 성공!
```

---

## 🧪 Step 5: 시스템 테스트 (보너스)

### 5.1 의도적 오류 만들기

**테스트: 컴파일 오류 발생시키기**

`src/main/main.ino` 파일을 수정:
```cpp
void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  // 의도적 오류: 세미콜론 제거
  Serial.println("Test error")  // <- 세미콜론 없음
}
```

### 5.2 실패 확인

```bash
git add .
git commit -m "test: intentional compilation error"
git push origin main
```

**예상 결과:**
- ❌ GitHub Actions 실패
- ❌ 빌드 뱃지가 빨간색 "failing"으로 변경
- 📧 실패 알림 이메일 수신 (GitHub 설정에 따라)

### 5.3 수정 및 복원

```cpp
// 오류 수정: 세미콜론 추가
Serial.println("Test error");
```

```bash
git add .
git commit -m "fix: restore semicolon to fix compilation"
git push origin main
```

**예상 결과:**
- ✅ GitHub Actions 성공
- ✅ 빌드 뱃지 다시 녹색으로 변경

---

## 🎉 완료! 축하합니다!

### 🏆 **30분 만에 구축한 것들:**

✅ **자동 빌드 시스템**: 코드 푸시 시 자동 컴파일  
✅ **다중 보드 지원**: Arduino Uno, Nano 동시 테스트  
✅ **코드 품질 검사**: 기본 문법 및 구조 검증  
✅ **실시간 알림**: 빌드 성공/실패 즉시 확인  
✅ **상태 모니터링**: GitHub 뱃지로 프로젝트 상태 표시  

### 📊 **시스템 동작 흐름:**
```
코드 작성 → Git Push → GitHub Actions 트리거 
→ 아두이노 컴파일 → 결과 알림 → 뱃지 업데이트
```

---

## 🚀 다음 단계 옵션

### 🔰 **더 간단하게 (추가 10분)**
- 실제 아두이노에 업로드해서 LED 깜빡임 확인
- 다른 센서 코드로 테스트해보기

### 🎯 **더 전문적으로 (완전 가이드)**
본격적인 CI/CD 시스템을 원한다면:

👉 **[완전한 Arduino CI/CD 마스터 가이드 시작하기](00-prerequisites.md)**

**완전 가이드에서 추가로 배우는 것들:**
- 🎯 **Jira 프로젝트 관리**: 이슈 추적, 스프린트 계획
- 🌿 **Bitbucket Git 고급 워크플로우**: 브랜치 전략, Pull Request  
- ⚙️ **Jenkins 고급 파이프라인**: 실제 하드웨어 배포, 테스트 자동화
- 📱 **실제 IoT 프로젝트**: 스마트 온실 모니터링 시스템 구축
- 🔔 **알림 시스템**: Slack, 이메일 연동
- 🛡️ **보안**: API 키 관리, 코드 검증

---

## 🆘 문제 해결

### ❌ **GitHub Actions 실행이 안 될 때**
```
해결방법:
1. 저장소가 Public인지 확인 (Private는 무료 한도 제한)
2. .github/workflows/ 폴더 경로가 정확한지 확인
3. YAML 파일 문법 오류 확인 (들여쓰기 주의)
```

### ❌ **컴파일 실패가 계속될 때**
```
해결방법:
1. 로컬에서 Arduino IDE로 컴파일 테스트
2. 사용된 라이브러리가 GitHub Actions에서 설치되었는지 확인
3. 보드 타입이 올바른지 확인 (arduino:avr:uno)
```

### ❌ **뱃지가 표시되지 않을 때**
```
해결방법:
1. README.md의 사용자명/저장소명이 정확한지 확인
2. 워크플로우 이름이 YAML 파일의 name과 일치하는지 확인
3. 몇 분 기다린 후 새로고침 (캐시 지연)
```

---

## 💬 도움받기

### 🆘 **막혔을 때:**
- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [Arduino CLI 문서](https://arduino.github.io/arduino-cli/)
- [커뮤니티 Discord](https://discord.gg/arduino-cicd)

### 🎯 **더 배우고 싶다면:**
- [완전한 Arduino CI/CD 가이드](00-prerequisites.md)
- [GitHub Issues](https://github.com/your-username/arduino-cicd-guide/issues)

---

**🎊 축하합니다! 30분 만에 전문가급 CI/CD 시스템을 구축하셨습니다! 🚀**

이제 **코드만 푸시하면 자동으로 검증되는 시스템**이 있습니다!  
더 고급 기능이 궁금하시면 완전 가이드로 오세요! 💪