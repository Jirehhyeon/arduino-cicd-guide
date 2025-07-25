# 🔰 Step 0: 시작하기 전 준비사항

> **"성공적인 학습을 위해 반드시 준비해야 할 것들"**

**⏱️ 예상 소요시간: 30-45분**  
**🎯 목표: 모든 필수 도구와 계정을 준비하여 원활한 학습 환경 구축**

## 📋 체크리스트 - 시작 전 확인사항

### ✅ **하드웨어 준비**
- [ ] 컴퓨터 (Windows 10+, macOS 10.14+, 또는 Ubuntu 18.04+)
- [ ] 최소 4GB RAM, 10GB 여유 공간
- [ ] 안정적인 인터넷 연결
- [ ] 아두이노 보드 (Arduino Uno, ESP32, 또는 ESP8266)
- [ ] USB 케이블 (아두이노 연결용)
- [ ] **선택사항**: DHT22 센서, LED, 저항 등 (실습용)

### ✅ **필수 소프트웨어 설치**
- [ ] 웹 브라우저 (Chrome 권장)
- [ ] Git
- [ ] Arduino IDE 또는 Arduino CLI
- [ ] 텍스트 에디터 (VS Code 권장)

### ✅ **온라인 계정 준비**
- [ ] Google 계정 (Chrome 동기화용)
- [ ] Atlassian 계정 (Jira + Bitbucket)
- [ ] GitHub 계정 (코드 백업용)

---

## 🖥️ 소프트웨어 설치 가이드

### 1️⃣ **Git 설치**

#### Windows 사용자
```bash
# 1. https://git-scm.com/download/win 방문
# 2. "64-bit Git for Windows Setup" 다운로드
# 3. 다운로드된 파일 실행
# 4. 모든 옵션은 기본값으로 설정하고 "Next" 클릭
# 5. "Install" 클릭하여 설치 완료
```

**✅ 설치 확인:**
```bash
# Command Prompt 또는 PowerShell에서 실행
git --version
# 출력 예시: git version 2.41.0.windows.3
```

#### macOS 사용자
```bash
# Homebrew 설치 (없는 경우)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Git 설치
brew install git
```

#### Ubuntu/Linux 사용자
```bash
sudo apt update
sudo apt install git
```

### 2️⃣ **Arduino CLI 설치**

#### Windows 사용자
```bash
# 1. https://github.com/arduino/arduino-cli/releases 방문
# 2. "arduino-cli_X.X.X_Windows_64bit.zip" 다운로드
# 3. 압축 해제하여 C:\Arduino-CLI\ 폴더에 저장
# 4. 환경 변수 PATH에 C:\Arduino-CLI\ 추가
```

**환경 변수 설정 방법:**
1. `윈도우 키 + R` → `sysdm.cpl` 입력 → 확인
2. `고급` 탭 → `환경 변수` 클릭
3. `시스템 변수`에서 `Path` 선택 → `편집` 클릭
4. `새로 만들기` → `C:\Arduino-CLI\` 입력
5. 모든 창에서 `확인` 클릭

#### macOS/Linux 사용자
```bash
# 간편 설치 스크립트 사용
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh

# 설치 위치를 PATH에 추가
echo 'export PATH=$PATH:$PWD/bin' >> ~/.bashrc
source ~/.bashrc
```

**✅ 설치 확인:**
```bash
arduino-cli version
# 출력 예시: arduino-cli version 0.35.3
```

### 3️⃣ **Arduino CLI 초기 설정**

```bash
# 설정 파일 초기화
arduino-cli config init

# 보드 패키지 인덱스 업데이트
arduino-cli core update-index

# Arduino AVR 보드 설치 (Arduino Uno 등)
arduino-cli core install arduino:avr

# ESP32 보드 설치 (ESP32 사용 시)
arduino-cli core install esp32:esp32

# ESP8266 보드 설치 (ESP8266 사용 시)
arduino-cli core install esp8266:esp8266

# 필수 라이브러리 설치
arduino-cli lib install "DHT sensor library"
arduino-cli lib install "ArduinoJson"
arduino-cli lib install "WiFi"
arduino-cli lib install "PubSubClient"
```

### 4️⃣ **VS Code 설치 및 설정**

#### 설치
1. https://code.visualstudio.com/ 방문
2. 본인의 운영체제에 맞는 버전 다운로드
3. 설치 프로그램 실행 (모든 옵션 기본값으로 설정)

#### 필수 확장 프로그램 설치
VS Code 실행 후 왼쪽 사이드바의 Extensions 아이콘 클릭하여 다음 확장 프로그램 설치:

```
✅ Arduino (Microsoft)
✅ C/C++ (Microsoft)  
✅ GitLens (GitKraken)
✅ Prettier (Prettier)
✅ Thunder Client (RangaV)
```

---

## 🌐 온라인 계정 생성

### 1️⃣ **Atlassian 계정 생성**

#### 단계별 가이드

**1. 계정 생성**
```
1. https://id.atlassian.com/signup 방문
2. 이메일 주소 입력 (gmail 권장)
3. "Continue" 클릭
4. 이메일에서 인증 링크 클릭
5. 비밀번호 설정 (최소 8자, 대소문자+숫자+특수문자)
6. 이름 입력 후 "Continue"
```

**2. Jira 워크스페이스 생성**
```
1. https://www.atlassian.com/software/jira/free 방문
2. "Get it free" 클릭
3. 워크스페이스 이름 입력 (예: "arduino-cicd-workspace")
4. 사이트 이름 입력 (예: "arduino-cicd")
   → 최종 URL: https://arduino-cicd.atlassian.net
5. "Agree and create" 클릭
```

**3. Bitbucket 워크스페이스 생성**
```
1. https://bitbucket.org/ 방문
2. 방금 생성한 Atlassian 계정으로 로그인
3. "Create workspace" 클릭
4. 워크스페이스 이름: "Arduino CI/CD Projects"
5. 워크스페이스 ID: "arduino-cicd-projects"
6. "Create workspace" 클릭
```

**✅ 확인 방법:**
- Jira: `https://your-site.atlassian.net` 접속 가능
- Bitbucket: `https://bitbucket.org/your-workspace/` 접속 가능

### 2️⃣ **GitHub 계정 생성** (백업용)

```
1. https://github.com 방문
2. "Sign up" 클릭
3. 이메일/사용자명/비밀번호 입력
4. 이메일 인증 완료
5. 무료 플랜 선택
```

---

## 🔧 하드웨어 연결 테스트

### 아두이노 보드 연결 확인

**1. 아두이노를 USB로 컴퓨터에 연결**

**2. 연결 확인**
```bash
# Windows
arduino-cli board list
# COM 포트 확인 (예: COM3, COM4)

# macOS/Linux  
arduino-cli board list
# USB 포트 확인 (예: /dev/ttyUSB0, /dev/cu.usbmodem)
```

**3. 기본 스케치 업로드 테스트**

**Blink.ino 생성:**
```cpp
// 파일: test-blink/test-blink.ino
void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(1000);
  digitalWrite(LED_BUILTIN, LOW);
  delay(1000);
}
```

**컴파일 및 업로드:**
```bash
# 프로젝트 폴더 생성
mkdir test-blink
cd test-blink

# 위의 코드를 test-blink.ino 파일로 저장

# Arduino Uno의 경우
arduino-cli compile --fqbn arduino:avr:uno .
arduino-cli upload -p COM3 --fqbn arduino:avr:uno .

# ESP32의 경우  
arduino-cli compile --fqbn esp32:esp32:esp32 .
arduino-cli upload -p COM3 --fqbn esp32:esp32:esp32 .
```

**✅ 성공 확인:**
- 아두이노의 내장 LED가 1초마다 깜빡임
- 업로드 과정에서 오류 메시지 없음

---

## 🌐 네트워크 및 방화벽 설정

### Jenkins 서버 준비

#### 옵션 1: 로컬 설치 (권장)
```bash
# Windows (Docker 사용)
# 1. Docker Desktop 설치
# 2. PowerShell에서 실행:
docker run -d -p 8080:8080 -p 50000:50000 --name jenkins jenkins/jenkins:lts

# macOS/Linux
# Docker 설치 후 동일한 명령어 실행
```

#### 옵션 2: 클라우드 서비스 (고급 사용자)
- AWS EC2 또는 Google Cloud Platform 사용
- 본 가이드에서는 로컬 설치 기준으로 설명

### 방화벽 설정
```bash
# Windows Defender 방화벽
# 1. 제어판 → 시스템 및 보안 → Windows Defender 방화벽
# 2. "앱 또는 기능이 Windows Defender 방화벽을 통과하도록 허용"
# 3. "설정 변경" → "다른 앱 허용"
# 4. Jenkins (포트 8080) 허용

# macOS
sudo ufw allow 8080

# Linux (Ubuntu)
sudo ufw allow 8080
sudo ufw enable
```

---

## 📝 Git 기본 설정

### 전역 사용자 정보 설정
```bash
# 사용자 이름 설정 (GitHub과 동일하게)
git config --global user.name "Your Name"

# 이메일 설정 (GitHub과 동일하게)  
git config --global user.email "your.email@example.com"

# 기본 브랜치 이름을 main으로 설정
git config --global init.defaultBranch main

# 자동 줄바꿈 설정
git config --global core.autocrlf true  # Windows
git config --global core.autocrlf input # macOS/Linux

# 설정 확인
git config --list
```

### SSH 키 생성 및 등록
```bash
# SSH 키 생성
ssh-keygen -t rsa -b 4096 -C "your.email@example.com"
# Enter 3번 누르기 (기본 위치, 패스워드 없음)

# 공개키 내용 확인
# Windows
type %USERPROFILE%\.ssh\id_rsa.pub

# macOS/Linux
cat ~/.ssh/id_rsa.pub

# 출력된 내용을 복사하여 Bitbucket/GitHub에 등록
```

**Bitbucket SSH 키 등록:**
1. Bitbucket 로그인
2. 우측 상단 프로필 아이콘 → Personal settings
3. SSH keys → Add key
4. 복사한 공개키 붙여넣기 → Add key

---

## ✅ 최종 점검 체크리스트

### 🔧 **소프트웨어 설치 확인**
```bash
# 모든 명령어가 버전을 출력해야 함
git --version
arduino-cli version
code --version  # VS Code
docker --version  # Docker (Jenkins용)
```

### 🌐 **계정 접속 확인**  
- [ ] Jira 워크스페이스 접속: `https://your-site.atlassian.net`
- [ ] Bitbucket 워크스페이스 접속: `https://bitbucket.org/your-workspace/`
- [ ] GitHub 계정 접속: `https://github.com/your-username`

### 🔌 **하드웨어 연결 확인**
- [ ] 아두이노 보드 인식: `arduino-cli board list`
- [ ] Blink 스케치 업로드 성공
- [ ] LED 깜빡임 동작 확인

### 🛡️ **네트워크 설정 확인**
- [ ] Jenkins 포트 8080 방화벽 허용
- [ ] SSH 키 Bitbucket 등록 완료
- [ ] `ssh -T git@bitbucket.org` 연결 테스트 성공

---

## 🚀 다음 단계

모든 준비가 완료되었나요? 축하합니다! 🎉

이제 본격적인 학습을 시작할 준비가 되었습니다.

### 👉 **다음으로 이동:**
**[Step 1: Jira 프로젝트 관리 마스터하기](01-jira-master.md)**

---

## 🆘 문제 해결

### 자주 발생하는 문제들

#### ❌ **Arduino CLI 명령어를 인식하지 못할 때**
```bash
# 해결방법 1: 환경변수 PATH 확인
echo $PATH  # macOS/Linux
echo %PATH%  # Windows

# 해결방법 2: 직접 경로로 실행
/full/path/to/arduino-cli version
C:\Arduino-CLI\arduino-cli.exe version
```

#### ❌ **Git SSH 연결 실패**
```bash
# SSH 연결 테스트
ssh -T git@bitbucket.org

# 실패 시 HTTPS 사용
git config --global url."https://".insteadOf git://
```

#### ❌ **Docker Jenkins 실행 실패**
```bash
# 포트 충돌 확인
netstat -an | grep 8080

# 다른 포트로 실행
docker run -d -p 8081:8080 -p 50001:50000 --name jenkins jenkins/jenkins:lts
```

### 💬 **추가 도움이 필요하시면:**
- [FAQ 페이지](../faq.md) 확인
- [GitHub Issues](https://github.com/your-username/arduino-cicd-guide/issues)에 질문 등록
- [Discord 커뮤니티](https://discord.gg/arduino-cicd) 참여

---

**🎯 준비 완료! 이제 진짜 재미있는 부분이 시작됩니다! 💪**