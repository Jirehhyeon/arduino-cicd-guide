# 🖥️ VSCode 원격 개발 환경 구성

> 엔터프라이즈급 Windows ↔ Linux 통합 개발 환경 구축

## 📋 목차

1. [개요](#개요)
2. [환경 준비](#환경-준비)
3. [SSH 연결 설정](#ssh-연결-설정)
4. [VSCode Remote Development](#vscode-remote-development)
5. [개발 환경 최적화](#개발-환경-최적화)
6. [보안 및 성능 최적화](#보안-및-성능-최적화)

## 🎯 개요

### 아키텍처 구성
```
Windows Workstation (VSCode) 
    ↕ SSH/SFTP
Linux Development Server (Git, Build Tools, Arduino CLI)
    ↕ HTTPS/SSH
Bitbucket Repository
    ↕ Webhook
Jenkins CI/CD Server
    ↕ REST API
Jira Issue Management
```

### 핵심 특징
- **🔄 실시간 동기화**: Windows-Linux 파일 시스템 투명 연동
- **⚡ 고성능**: 원격 실행으로 로컬 리소스 절약
- **🛡️ 보안**: SSH 키 인증 및 VPN 연동
- **🎨 통합 IDE**: 로컬과 동일한 VSCode 경험

## ⚙️ 환경 준비

### Windows 클라이언트 요구사항
```powershell
# PowerShell Core 설치 (관리자 권한)
winget install Microsoft.PowerShell

# Windows Terminal 설치
winget install Microsoft.WindowsTerminal

# Git for Windows
winget install Git.Git

# VSCode 설치
winget install Microsoft.VisualStudioCode
```

### Linux 서버 요구사항
```bash
# Ubuntu/Debian 기반 패키지 설치
sudo apt update && sudo apt install -y \
    openssh-server \
    git \
    build-essential \
    nodejs \
    npm \
    python3 \
    python3-pip \
    curl \
    wget

# Arduino CLI 설치
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh

# Docker 설치 (Jenkins 컨테이너용)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

## 🔑 SSH 연결 설정

### 1. SSH 키 생성 (Windows)
```powershell
# Ed25519 키 생성 (RSA보다 안전하고 빠름)
ssh-keygen -t ed25519 -C "your-email@company.com" -f ~/.ssh/id_ed25519_dev

# SSH Agent 서비스 시작
Get-Service ssh-agent | Set-Service -StartupType Automatic
Start-Service ssh-agent

# 키 등록
ssh-add ~/.ssh/id_ed25519_dev
```

### 2. 공개키 Linux 서버에 등록
```powershell
# Windows에서 공개키 복사
Get-Content ~/.ssh/id_ed25519_dev.pub | Set-Clipboard

# 또는 직접 전송
scp ~/.ssh/id_ed25519_dev.pub user@linux-server:~/temp_key.pub
```

```bash
# Linux 서버에서 인증 키 등록
mkdir -p ~/.ssh
cat ~/temp_key.pub >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
rm ~/temp_key.pub

# SSH 서버 설정 최적화
sudo nano /etc/ssh/sshd_config
```

### 3. SSH 설정 파일 구성 (Windows)
```ini
# ~/.ssh/config
Host dev-server
    HostName your-linux-server.com
    User your-username
    Port 22
    IdentityFile ~/.ssh/id_ed25519_dev
    ForwardAgent yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
    Compression yes
    # 고성능 네트워크용 최적화
    TCPKeepAlive yes
    IPQoS throughput
```

### 4. 연결 테스트
```powershell
# SSH 연결 테스트
ssh dev-server

# 포트 포워딩 테스트 (Jenkins용)
ssh -L 8080:localhost:8080 dev-server
```

## 🚀 VSCode Remote Development

### 1. 필수 확장 프로그램 설치
```json
{
    "recommendations": [
        "ms-vscode-remote.remote-ssh",
        "ms-vscode-remote.remote-ssh-edit",
        "ms-vscode-remote.remote-containers",
        "ms-vscode-remote.vscode-remote-extensionpack",
        "ms-vscode.remote-explorer",
        "ms-python.python",
        "ms-vscode.cpptools",
        "arduino.arduino-vscode"
    ]
}
```

### 2. Remote SSH 연결 설정
**단계 1: 연결 추가**
1. `Ctrl + Shift + P` → "Remote-SSH: Add New SSH Host"
2. `ssh dev-server` 입력
3. SSH config 파일 선택

**단계 2: 원격 연결**
1. `Ctrl + Shift + P` → "Remote-SSH: Connect to Host"
2. `dev-server` 선택
3. 새 VSCode 창에서 원격 환경 로드

### 3. 원격 환경 설정
```bash
# 원격 서버에서 개발 환경 설정
mkdir -p ~/workspace/arduino-projects
cd ~/workspace/arduino-projects

# Arduino CLI 보드 설치
arduino-cli core update-index
arduino-cli core install arduino:avr
arduino-cli core install esp32:esp32

# Node.js 의존성 (웹 인터페이스용)
npm install -g @angular/cli @vue/cli express
```

### 4. 워크스페이스 설정
```json
// .vscode/settings.json (원격 워크스페이스)
{
    "arduino.path": "/home/user/bin",
    "arduino.commandPath": "arduino-cli",
    "arduino.logLevel": "info",
    "arduino.enableUSBDetection": true,
    "terminal.integrated.shell.linux": "/bin/bash",
    "files.watcherExclude": {
        "**/node_modules/**": true,
        "**/.git/objects/**": true,
        "**/.git/subtree-cache/**": true,
        "**/build/**": true
    },
    "remote.SSH.remotePlatform": {
        "dev-server": "linux"
    }
}
```

## 🔧 개발 환경 최적화

### 1. 파일 동기화 설정
```json
// .vscode/settings.json
{
    "files.autoSave": "afterDelay",
    "files.autoSaveDelay": 1000,
    "remote.SSH.useLocalServer": false,
    "remote.SSH.connectTimeout": 15,
    "remote.downloadExtensionsLocally": true
}
```

### 2. Git 구성 (원격 서버)
```bash
# Git 글로벌 설정
git config --global user.name "Your Name"
git config --global user.email "your-email@company.com"
git config --global init.defaultBranch main
git config --global core.editor "code --wait"

# SSH 키를 통한 Bitbucket 인증
ssh-keygen -t ed25519 -C "bitbucket-key"
cat ~/.ssh/id_ed25519.pub
# → Bitbucket Settings > SSH Keys에 등록
```

### 3. 개발 스크립트 자동화
```bash
#!/bin/bash
# ~/scripts/setup-project.sh

PROJECT_NAME=$1
if [ -z "$PROJECT_NAME" ]; then
    echo "Usage: $0 <project-name>"
    exit 1
fi

# 프로젝트 디렉토리 생성
mkdir -p ~/workspace/$PROJECT_NAME/{src,lib,test,docs}
cd ~/workspace/$PROJECT_NAME

# Arduino 프로젝트 초기화
cat > src/$PROJECT_NAME.ino << EOF
// $PROJECT_NAME - Arduino Project
// Generated on $(date)

void setup() {
    Serial.begin(9600);
    Serial.println("$PROJECT_NAME initialized");
}

void loop() {
    // Main loop
}
EOF

# Git 저장소 초기화
git init
git add .
git commit -m "Initial commit: $PROJECT_NAME project setup"

echo "✅ Project $PROJECT_NAME created successfully!"
```

### 4. 통합 터미널 구성
```json
// .vscode/settings.json
{
    "terminal.integrated.profiles.linux": {
        "bash": {
            "path": "bash",
            "args": ["-l"]
        },
        "zsh": {
            "path": "zsh"
        },
        "dev-shell": {
            "path": "bash",
            "args": ["-c", "source ~/scripts/dev-env.sh && bash"]
        }
    },
    "terminal.integrated.defaultProfile.linux": "dev-shell"
}
```

## 🛡️ 보안 및 성능 최적화

### 1. SSH 보안 강화
```bash
# /etc/ssh/sshd_config (Linux 서버)
Protocol 2
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
X11Forwarding no
AllowUsers your-username
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2

# 방화벽 설정
sudo ufw enable
sudo ufw allow from YOUR_IP_RANGE to any port 22
```

### 2. 성능 최적화
```ini
# ~/.ssh/config (Windows)
Host dev-server
    # ... 기존 설정 ...
    # 성능 최적화 옵션
    ControlMaster auto
    ControlPath ~/.ssh/control-%h-%p-%r
    ControlPersist 10m
    # 압축 최적화
    Compression yes
    CompressionLevel 6
    # 암호화 최적화 (보안과 성능 균형)
    Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com
```

### 3. 네트워크 최적화
```bash
# Linux 서버 네트워크 최적화
echo 'net.core.rmem_max = 16777216' | sudo tee -a /etc/sysctl.conf
echo 'net.core.wmem_max = 16777216' | sudo tee -a /etc/sysctl.conf
echo 'net.ipv4.tcp_rmem = 4096 87380 16777216' | sudo tee -a /etc/sysctl.conf
echo 'net.ipv4.tcp_wmem = 4096 65536 16777216' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 4. 모니터링 및 디버깅
```powershell
# Windows에서 연결 상태 모니터링
# ~/.config/powershell/Microsoft.PowerShell_profile.ps1

function Test-SSHConnection {
    param([string]$Host = "dev-server")
    
    $result = ssh -o ConnectTimeout=5 -o BatchMode=yes $Host "echo 'Connection OK'"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SSH connection to $Host is healthy" -ForegroundColor Green
    } else {
        Write-Host "❌ SSH connection to $Host failed" -ForegroundColor Red
    }
}

# VSCode Remote 상태 확인
function Get-RemoteStatus {
    $processes = Get-Process | Where-Object {$_.ProcessName -like "*code*"}
    $remoteProcesses = $processes | Where-Object {$_.MainWindowTitle -like "*[SSH:*"}
    
    Write-Host "Active Remote Connections: $($remoteProcesses.Count)" -ForegroundColor Cyan
    $remoteProcesses | ForEach-Object {
        Write-Host "  - $($_.MainWindowTitle)" -ForegroundColor Yellow
    }
}
```

## 🚀 고급 기능

### 1. 포트 포워딩 자동화
```json
// .vscode/settings.json
{
    "remote.SSH.defaultForwardedPorts": [
        {
            "localPort": 3000,
            "remotePort": 3000,
            "name": "Web Server"
        },
        {
            "localPort": 8080,
            "remotePort": 8080,
            "name": "Jenkins"
        }
    ]
}
```

### 2. 개발 컨테이너 통합
```dockerfile
# .devcontainer/Dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    python3 \
    python3-pip \
    nodejs \
    npm

# Arduino CLI 설치
RUN curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
```

### 3. 자동 백업 및 동기화
```bash
#!/bin/bash
# ~/scripts/sync-workspace.sh

# 원격 → 로컬 백업
rsync -avz --exclude='.git' \
    dev-server:~/workspace/ \
    /mnt/c/backup/workspace/

# Git 상태 동기화
cd ~/workspace
find . -name ".git" -type d | while read repo; do
    echo "Syncing $repo"
    cd "$repo/.."
    git push --all origin
    cd - > /dev/null
done
```

## ✅ 검증 체크리스트

- [ ] SSH 키 기반 인증 설정 완료
- [ ] VSCode Remote SSH 연결 정상 동작
- [ ] 파일 편집 및 저장 실시간 동기화 확인
- [ ] 터미널 명령어 실행 정상 동작
- [ ] Git 인증 및 푸시/풀 동작 확인
- [ ] Arduino CLI 및 빌드 도구 정상 동작
- [ ] 포트 포워딩을 통한 서비스 접근 확인
- [ ] 네트워크 끊김 시 자동 재연결 동작

---

**다음 단계**: [Bitbucket 연동 및 Git 워크플로우](01-bitbucket-git-workflow.md)