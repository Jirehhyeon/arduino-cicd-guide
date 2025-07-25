# 🆘 트러블슈팅 완전 가이드

> **"초보자도 혼자서 해결할 수 있는 단계별 문제 해결 방법"**

## 🎯 이 가이드 사용법

1. **🔍 증상으로 찾기**: 본인의 문제와 가장 비슷한 증상 찾기
2. **📋 체크리스트**: 기본 확인사항부터 차례대로 점검
3. **🔧 해결방법**: 단계별 해결 방법 따라하기
4. **✅ 검증**: 문제가 해결되었는지 확인
5. **💬 도움요청**: 여전히 안 되면 커뮤니티에 질문

---

## 🔰 환경 설정 문제

### ❌ Problem 1: Arduino CLI 명령어 인식 안됨

**증상:**
```bash
arduino-cli version
# 'arduino-cli'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는 배치 파일이 아닙니다.
```

**체크리스트:**
- [ ] Arduino CLI가 실제로 설치되었는지 확인
- [ ] 환경변수 PATH에 Arduino CLI 경로가 추가되었는지 확인
- [ ] 터미널/명령창을 새로 열었는지 확인

**해결방법:**

**Step 1: 설치 확인**
```bash
# Windows
dir C:\Arduino-CLI\
# arduino-cli.exe 파일이 있는지 확인

# Mac/Linux
ls -la /usr/local/bin/arduino-cli
# 파일이 존재하고 실행 권한이 있는지 확인
```

**Step 2: 환경변수 설정 (Windows)**
```bash
# 현재 PATH 확인
echo %PATH%

# 환경변수 영구 추가 (관리자 권한 필요)
setx PATH "%PATH%;C:\Arduino-CLI" /M

# 임시 추가 (현재 세션만)
set PATH=%PATH%;C:\Arduino-CLI
```

**Step 3: 환경변수 설정 (Mac/Linux)**
```bash
# 현재 PATH 확인
echo $PATH

# .bashrc 또는 .zshrc에 추가
echo 'export PATH=$PATH:/usr/local/bin' >> ~/.bashrc
source ~/.bashrc

# 또는 직접 편집
nano ~/.bashrc
# 파일 끝에 추가: export PATH=$PATH:/usr/local/bin
```

**Step 4: 재설치 (위 방법이 안 될 때)**
```bash
# Windows - 새로 다운로드
# 1. https://github.com/arduino/arduino-cli/releases
# 2. Windows_64bit.zip 다운로드
# 3. C:\Arduino-CLI\ 폴더에 압축 해제

# Mac/Linux - 자동 설치 스크립트
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
sudo mv bin/arduino-cli /usr/local/bin/
```

**검증:**
```bash
arduino-cli version
# arduino-cli version 0.35.3 (또는 다른 버전) 출력되면 성공
```

---

### ❌ Problem 2: Git 명령어 인식 안됨

**증상:**
```bash
git --version
# 'git'은(는) 내부 또는 외부 명령이 아닙니다.
```

**해결방법:**

**Windows:**
```bash
# 1. https://git-scm.com/download/win 방문
# 2. 64-bit Git for Windows Setup 다운로드
# 3. 설치 프로그램 실행 (모든 옵션 기본값)
# 4. 설치 후 새 명령창 열기
```

**Mac:**
```bash
# Xcode Command Line Tools 설치
xcode-select --install

# 또는 Homebrew 사용
brew install git
```

**Ubuntu/Linux:**
```bash
sudo apt update
sudo apt install git
```

**검증:**
```bash
git --version
# git version 2.x.x 출력되면 성공
```

---

## 🎯 Jira 관련 문제

### ❌ Problem 3: Jira 워크스페이스 접속 안됨

**증상:**
- 로그인 페이지가 뜨지 않음
- "사이트를 찾을 수 없습니다" 오류
- 무한 로딩

**체크리스트:**
- [ ] 올바른 URL 사용하고 있는지 확인 (`https://your-site.atlassian.net`)
- [ ] 인터넷 연결 상태 확인
- [ ] 브라우저 캐시 문제인지 확인

**해결방법:**

**Step 1: URL 확인**
```
올바른 형식: https://your-site.atlassian.net
잘못된 형식: 
- http://your-site.atlassian.net (https 빠짐)
- https://your-site.atlassian.com (.com 잘못)
- https://atlassian.net/your-site (순서 잘못)
```

**Step 2: 브라우저 문제 해결**
```bash
# Chrome 사용 시
1. Ctrl+Shift+Delete (Windows) 또는 Cmd+Shift+Delete (Mac)
2. "쿠키 및 기타 사이트 데이터" 체크
3. "캐시된 이미지 및 파일" 체크
4. "데이터 삭제" 클릭
5. 브라우저 재시작

# 시크릿/사생활 보호 모드로 테스트
Ctrl+Shift+N (Chrome) 또는 Ctrl+Shift+P (Firefox)
```

**Step 3: 계정 확인**
```
1. https://id.atlassian.com 직접 접속
2. 로그인 시도
3. 계정이 활성화되어 있는지 확인
4. 이메일에서 인증 메일이 있는지 확인
```

---

### ❌ Problem 4: 커스텀 필드가 이슈에 표시되지 않음

**증상:**
- 커스텀 필드를 만들었는데 이슈 생성 시 보이지 않음
- 기존 이슈에서 필드를 찾을 수 없음

**해결방법:**

**Step 1: 필드 화면 설정 확인**
```
1. Project settings → Features → Fields
2. 생성한 커스텀 필드 확인
3. "Screens" 탭 클릭
4. 해당 필드가 적절한 화면에 추가되었는지 확인
```

**Step 2: 이슈 타입별 화면 확인**
```
1. Project settings → Screens
2. 각 이슈 타입(Story, Task, Bug)별로 다른 화면 사용하는지 확인
3. 필요한 화면에 커스텀 필드 추가
```

**Step 3: 필드 추가**
```
1. 해당 화면 편집 클릭
2. "Add field" 버튼 클릭
3. 생성한 커스텀 필드 선택
4. 적절한 위치에 배치
5. "Update" 클릭
```

---

## 🌿 Bitbucket/Git 관련 문제

### ❌ Problem 5: Git Push가 거부됨

**증상:**
```bash
git push origin main
# error: failed to push some refs to 'https://bitbucket.org/...'
# hint: Updates were rejected because the remote contains work that you do not have locally.
```

**해결방법:**

**Step 1: 원격 변경사항 가져오기**
```bash
# 원격 저장소 상태 확인
git fetch origin

# 원격 변경사항과 병합
git pull origin main

# 충돌이 있으면 해결 후
git add .
git commit -m "resolve merge conflicts"

# 다시 푸시
git push origin main
```

**Step 2: 강제 푸시 (주의: 데이터 손실 가능)**
```bash
# ⚠️ 경고: 원격 저장소의 기록이 삭제될 수 있음
# 혼자 개발하고 있고, 원격에 중요한 변경사항이 없을 때만 사용
git push --force origin main
```

---

### ❌ Problem 6: SSH 키 인증 실패

**증상:**
```bash
git push origin main
# Permission denied (publickey).
# fatal: Could not read from remote repository.
```

**해결방법:**

**Step 1: SSH 키 존재 확인**
```bash
# SSH 키 파일 확인
ls -la ~/.ssh/
# id_rsa, id_rsa.pub 파일이 있는지 확인

# 없으면 새로 생성
ssh-keygen -t rsa -b 4096 -C "your.email@example.com"
# Enter 3번 누르기 (기본 설정 사용)
```

**Step 2: 공개키 Bitbucket에 등록**
```bash
# 공개키 내용 확인
cat ~/.ssh/id_rsa.pub
# 출력된 내용 전체 복사

# Windows의 경우
type %USERPROFILE%\.ssh\id_rsa.pub
```

```
1. Bitbucket 로그인
2. 우측 상단 프로필 아이콘 → Personal settings
3. SSH keys → Add key
4. Label: "My Computer"
5. Key: 복사한 공개키 내용 붙여넣기
6. Add key 클릭
```

**Step 3: SSH 연결 테스트**
```bash
ssh -T git@bitbucket.org
# 성공 시: "logged in as username"
# 실패 시: Permission denied 메시지
```

**Step 4: HTTPS로 임시 해결**
```bash
# SSH 대신 HTTPS 사용
git remote set-url origin https://your-username@bitbucket.org/workspace/repo.git

# 푸시 시 비밀번호 입력 (또는 App Password 사용)
git push origin main
```

---

## ⚙️ Jenkins 관련 문제

### ❌ Problem 7: Jenkins 접속 안됨

**증상:**
- `http://localhost:8080` 접속 시 "사이트에 연결할 수 없음"
- Jenkins가 시작되지 않음

**체크리스트:**
- [ ] Jenkins 서비스가 실행 중인지 확인
- [ ] 포트 8080이 다른 프로그램에서 사용 중인지 확인
- [ ] 방화벽 설정 확인

**해결방법:**

**Step 1: Jenkins 실행 상태 확인**

**Docker 사용 시:**
```bash
# 실행 중인 컨테이너 확인
docker ps
# jenkins 컨테이너가 있는지 확인

# 없으면 다시 실행
docker run -d -p 8080:8080 -p 50000:50000 --name jenkins jenkins/jenkins:lts

# 로그 확인
docker logs jenkins
```

**일반 설치 시:**
```bash
# Windows
services.msc # 서비스 관리자에서 Jenkins 확인

# Linux
sudo systemctl status jenkins
sudo systemctl start jenkins  # 중지되어 있으면 시작
```

**Step 2: 포트 충돌 확인**
```bash
# 포트 8080 사용 중인 프로세스 확인
# Windows
netstat -ano | findstr :8080

# Mac/Linux
lsof -i :8080
netstat -an | grep 8080
```

**Step 3: 다른 포트로 실행**
```bash
# Docker에서 다른 포트 사용
docker run -d -p 8081:8080 -p 50001:50000 --name jenkins jenkins/jenkins:lts

# 접속: http://localhost:8081
```

---

### ❌ Problem 8: Jenkins 초기 패스워드를 모르겠음

**증상:**
- Jenkins 첫 접속 시 나오는 관리자 패스워드를 찾을 수 없음

**해결방법:**

**Docker 사용 시:**
```bash
# 컨테이너 내부의 패스워드 파일 확인
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# 또는 로그에서 확인
docker logs jenkins | grep -A 5 -B 5 "password"
```

**일반 설치 시:**
```bash
# Windows
type "C:\Program Files\Jenkins\secrets\initialAdminPassword"

# Mac/Linux
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

**패스워드 파일이 없을 때:**
```bash
# Jenkins 재시작하여 새 패스워드 생성
docker restart jenkins

# 새 패스워드 확인
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

---

## 🔧 아두이노/하드웨어 문제

### ❌ Problem 9: 아두이노 보드 인식 안됨

**증상:**
```bash
arduino-cli board list
# No boards found.
```

**체크리스트:**
- [ ] USB 케이블이 제대로 연결되었는지 확인
- [ ] 아두이노 전원 LED가 켜져 있는지 확인
- [ ] USB 케이블이 데이터 전송용인지 확인 (충전 전용 케이블 아님)
- [ ] 다른 USB 포트에 연결해보기

**해결방법:**

**Step 1: 하드웨어 연결 확인**
```bash
# Windows - 장치 관리자에서 확인
1. Win+X → 장치 관리자
2. "포트(COM 및 LPT)" 확장
3. Arduino 관련 항목 확인
4. 노란색 경고 표시가 있으면 드라이버 문제

# Mac/Linux - 시리얼 포트 확인
ls /dev/tty*
# /dev/ttyUSB0, /dev/ttyACM0, /dev/cu.usbmodem* 등 확인
```

**Step 2: 드라이버 설치**
```bash
# Arduino Uno/Nano (CH340 칩셋)
# Windows: CH340 드라이버 설치 필요
# 1. https://sparks.gogo.co.nz/ch340.html
# 2. 드라이버 다운로드 및 설치

# Mac: 자동 인식 (추가 드라이버 불필요)
# Linux: 권한 설정 필요
sudo usermod -a -G dialout $USER
# 로그아웃 후 다시 로그인
```

**Step 3: 수동 포트 지정**
```bash
# 보드가 인식되지 않아도 포트가 보이면 직접 지정
arduino-cli upload -p COM3 --fqbn arduino:avr:uno ./sketch

# Mac/Linux
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:uno ./sketch
```

---

### ❌ Problem 10: 컴파일은 되는데 업로드 실패

**증상:**
```bash
arduino-cli upload -p COM3 --fqbn arduino:avr:uno ./sketch
# Error during upload: uploading error: exit status 1
```

**해결방법:**

**Step 1: 포트 권한 확인**
```bash
# Linux/Mac - 포트 권한 설정
sudo chmod 666 /dev/ttyUSB0

# 또는 사용자를 dialout 그룹에 추가
sudo usermod -a -G dialout $USER
sudo usermod -a -G tty $USER
```

**Step 2: 다른 프로그램에서 포트 사용 중인지 확인**
```bash
# Arduino IDE, 시리얼 모니터 등이 포트를 사용 중이면 닫기
# Windows - 작업 관리자에서 Arduino IDE 프로세스 종료
# Mac/Linux
lsof /dev/ttyUSB0  # 포트 사용 중인 프로세스 확인
```

**Step 3: 업로드 모드 확인**
```bash
# ESP32/ESP8266의 경우 부트 모드 진입 필요
# 1. BOOT 버튼 누른 상태로 RESET 버튼 누르기
# 2. RESET 버튼 놓기
# 3. BOOT 버튼 놓기
# 4. 업로드 명령 실행
```

**Step 4: 보드 타입 재확인**
```bash
# 정확한 보드 FQBN 사용하고 있는지 확인
arduino-cli board listall | grep -i uno
# arduino:avr:uno 확인

arduino-cli board listall | grep -i esp32
# esp32:esp32:esp32 확인
```

---

## 🔗 통합 연동 문제

### ❌ Problem 11: Jira-Bitbucket 연동 안됨

**증상:**
- Git 커밋을 해도 Jira 이슈 상태가 변경되지 않음
- Smart Commits가 작동하지 않음

**해결방법:**

**Step 1: Smart Commits 문법 확인**
```bash
# 올바른 커밋 메시지 형식
git commit -m "SGM-123 #time 1w 2d 4h 30m Total work logged"
git commit -m "SGM-123 #comment 작업 진행 중입니다"
git commit -m "SGM-123 #resolve #comment 이슈 해결 완료"

# 잘못된 형식
git commit -m "SGM123 작업 완료"  # 하이픈 빠짐
git commit -m "sgm-123 작업 완료"  # 소문자
git commit -m "작업 완료 SGM-123"  # 이슈 키가 맨 앞에 없음
```

**Step 2: Bitbucket-Jira 연결 확인**
```
1. Bitbucket 워크스페이스 설정
2. Integrations → Jira
3. 연결 상태 확인
4. 필요시 재연결
```

**Step 3: 권한 확인**
```
1. Jira 프로젝트 권한 확인
2. Bitbucket 사용자가 Jira 프로젝트에 접근 권한이 있는지 확인
3. 필요시 사용자를 프로젝트에 추가
```

---

### ❌ Problem 12: Jenkins 빌드가 트리거되지 않음

**증상:**
- Git push를 해도 Jenkins 빌드가 자동으로 시작되지 않음

**해결방법:**

**Step 1: 웹훅 설정 확인**
```
1. Bitbucket 저장소 설정
2. Webhooks 확인
3. Jenkins URL이 올바른지 확인: http://your-jenkins:8080/bitbucket-hook/
4. 테스트 웹훅 실행해보기
```

**Step 2: Jenkins 플러그인 확인**
```
1. Jenkins 관리 → 플러그인 관리
2. 설치된 플러그인에서 "Bitbucket Plugin" 확인
3. 없으면 설치 후 Jenkins 재시작
```

**Step 3: 파이프라인 설정 확인**
```groovy
// Jenkinsfile에서 트리거 설정 확인
pipeline {
    agent any
    
    triggers {
        // 웹훅 트리거 설정
        bitbucketPush()
    }
    
    // 또는 SCM 폴링 사용
    triggers {
        pollSCM('H/5 * * * *')  # 5분마다 체크
    }
}
```

---

## 🚨 응급 복구 방법

### 🆘 Emergency 1: 모든 게 다 꼬였을 때

**상황:** 뭔가 실수해서 전체 시스템이 망가진 것 같음

**침착하게 복구하기:**

**Step 1: 백업 확인**
```bash
# Git 저장소가 있다면 최신 코드는 안전함
git status
git log --oneline -5  # 최근 5개 커밋 확인

# 로컬 변경사항이 있으면 백업
git stash  # 임시 저장
git stash list  # 저장된 내용 확인
```

**Step 2: 새로운 폴더에서 다시 시작**
```bash
# 새 폴더에 클론
cd ..
git clone https://bitbucket.org/workspace/repo.git repo-backup
cd repo-backup

# 여기서 다시 작업하고 원래 폴더는 나중에 정리
```

**Step 3: 서비스별 재설정**
```bash
# Jenkins 컨테이너 완전 재시작
docker stop jenkins
docker rm jenkins
docker run -d -p 8080:8080 --name jenkins jenkins/jenkins:lts

# Arduino CLI 재설정
arduino-cli config init
arduino-cli core update-index
arduino-cli core install arduino:avr
```

---

### 🆘 Emergency 2: 중요한 코드를 실수로 삭제했을 때

**Step 1: Git 히스토리에서 복구**
```bash
# 삭제된 파일 찾기
git log --diff-filter=D --summary | grep delete

# 특정 파일의 삭제 커밋 찾기
git log --oneline --follow -- path/to/deleted/file.ino

# 삭제 직전 버전으로 복구
git checkout [커밋해시]~1 -- path/to/deleted/file.ino
```

**Step 2: 로컬 백업에서 복구**
```bash
# VS Code에서 자동 백업 확인
# Windows: %APPDATA%\Code\User\History\
# Mac: ~/Library/Application Support/Code/User/History/
# Linux: ~/.config/Code/User/History/
```

---

## 📞 추가 도움 받기

### 🔍 문제 해결 체크리스트

문제가 해결되지 않을 때 다음 정보를 정리해서 질문하세요:

```
🖥️ 환경 정보:
- OS: Windows 10 / macOS Big Sur / Ubuntu 20.04
- 브라우저: Chrome 버전
- Arduino CLI 버전: 
- Git 버전:
- Docker 버전 (사용하는 경우):

🎯 문제 상황:
- 어떤 단계에서 문제가 발생했는지
- 정확한 오류 메시지 (스크린샷 포함)
- 문제 발생 전에 수행한 작업
- 시도해본 해결 방법

📋 재현 방법:
- 문제를 재현할 수 있는 단계별 방법
- 항상 발생하는지, 가끔 발생하는지
```

### 💬 도움 요청 채널

**1. GitHub Issues (권장)**
- URL: https://github.com/your-username/arduino-cicd-guide/issues
- 장점: 체계적인 문제 추적, 다른 사람도 참고 가능
- 사용법: 위의 정보를 정리해서 새 Issue 생성

**2. Discord 커뮤니티**
- URL: https://discord.gg/arduino-cicd
- 장점: 실시간 대화, 빠른 답변
- 사용법: #troubleshooting 채널에 질문

**3. 이메일 문의**
- 개인적인 문의나 민감한 정보 포함 시
- 응답 시간: 1-2일 소요

### 🎓 추가 학습 자료

**공식 문서:**
- [Arduino CLI](https://arduino.github.io/arduino-cli/)
- [Git 기초](https://git-scm.com/book/ko/v2)
- [Jenkins 파이프라인](https://www.jenkins.io/doc/book/pipeline/)
- [Jira 사용법](https://support.atlassian.com/jira-software-cloud/)

**커뮤니티:**
- [Arduino Forums](https://forum.arduino.cc/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/arduino)
- [Reddit r/arduino](https://reddit.com/r/arduino)

---

**💪 포기하지 마세요! 모든 문제에는 해결책이 있습니다!**  
**🤝 혼자 해결하려고 애쓰지 말고 커뮤니티의 도움을 받으세요!**  
**🎯 문제 해결 과정도 소중한 학습 경험입니다!**