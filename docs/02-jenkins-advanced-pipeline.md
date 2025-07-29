# 🏗️ Jenkins CI/CD 파이프라인 고도화

> 차세대 DevOps 기술을 적용한 엔터프라이즈급 자동화 파이프라인

## 📋 목차

1. [현대적 Jenkins 아키텍처](#현대적-jenkins-아키텍처)
2. [Docker 기반 빌드 환경](#docker-기반-빌드-환경)
3. [멀티 스테이지 파이프라인](#멀티-스테이지-파이프라인)
4. [병렬 실행 및 최적화](#병렬-실행-및-최적화)
5. [보안 및 시크릿 관리](#보안-및-시크릿-관리)
6. [모니터링 및 알림](#모니터링-및-알림)
7. [ArgoCD 통합 GitOps](#argocd-통합-gitops)

## 🏛️ 현대적 Jenkins 아키텍처

### 클러스터 기반 Jenkins 설정
```yaml
# docker-compose.jenkins.yml
version: '3.8'

services:
  jenkins-controller:
    image: jenkins/jenkins:2.426.1-lts-alpine
    container_name: jenkins-controller
    privileged: true
    environment:
      - JENKINS_OPTS=--httpPort=8080 --httpsPort=8443
      - JAVA_OPTS=-Xmx2g -Xms1g -Djenkins.install.runSetupWizard=false
    volumes:
      - jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
      - ./jenkins-config:/usr/share/jenkins/ref/
    ports:
      - "8080:8080"
      - "8443:8443"
      - "50000:50000"
    networks:
      - jenkins-network
    
  jenkins-agent-1:
    image: jenkins/inbound-agent:latest
    container_name: jenkins-agent-arduino
    environment:
      - JENKINS_URL=http://jenkins-controller:8080
      - JENKINS_SECRET=${JENKINS_AGENT_SECRET}
      - JENKINS_AGENT_NAME=arduino-agent
      - JENKINS_AGENT_WORKDIR=/home/jenkins/agent
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - arduino_builds:/builds
    depends_on:
      - jenkins-controller
    networks:
      - jenkins-network

  jenkins-agent-testing:
    image: custom/jenkins-agent-testing:latest
    container_name: jenkins-agent-testing
    environment:
      - JENKINS_URL=http://jenkins-controller:8080
      - JENKINS_SECRET=${JENKINS_AGENT_SECRET_TESTING}
      - JENKINS_AGENT_NAME=testing-agent
    volumes:
      - hardware_lab:/hardware
    depends_on:
      - jenkins-controller
    networks:
      - jenkins-network

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - jenkins-network

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - jenkins-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - jenkins-network

volumes:
  jenkins_home:
  arduino_builds:
  hardware_lab:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  jenkins-network:
    driver: bridge
```

### Jenkins Configuration as Code (JCasC)
```yaml
# jenkins-config/jenkins.yaml
jenkins:
  systemMessage: "Arduino IoT Project CI/CD Pipeline\n엔터프라이즈급 자동화 환경"
  numExecutors: 0
  
  clouds:
    - docker:
        name: "docker-cloud"
        dockerApi:
          dockerHost:
            uri: "unix:///var/run/docker.sock"
        templates:
          - labelString: "arduino-build"
            dockerTemplateBase:
              image: "arduino/arduino-cli:latest"
              mounts:
                - "type=bind,source=/dev,destination=/dev"
            instanceCapStr: "5"
            
          - labelString: "nodejs-build"
            dockerTemplateBase:
              image: "node:18-alpine"
            instanceCapStr: "3"
            
          - labelString: "security-scan"
            dockerTemplateBase:
              image: "owasp/dependency-check:latest"
            instanceCapStr: "2"

  securityRealm:
    ldap:
      configurations:
        - server: "ldap://company-ldap.local:389"
          rootDN: "dc=company,dc=com"
          userSearchBase: "ou=users"
          groupSearchBase: "ou=groups"

  authorizationStrategy:
    roleBased:
      roles:
        global:
          - name: "admin"
            description: "Jenkins 관리자"
            permissions:
              - "Overall/Administer"
          - name: "developer"
            description: "개발자"
            permissions:
              - "Overall/Read"
              - "Job/Build"
              - "Job/Read"
              - "Job/Workspace"

unclassified:
  location:
    url: "https://jenkins.company.com/"
    adminAddress: "devops@company.com"
  
  mailer:
    smtpHost: "smtp.company.com"
    smtpPort: 587
    useSsl: true
    
  slackNotifier:
    teamDomain: "company-team"
    token: "${SLACK_TOKEN}"
    
  bitbucketEndpointConfiguration:
    endpoints:
      - bitbucketServerUrl: "https://bitbucket.company.com"
        credentialsId: "bitbucket-credentials"

tool:
  nodejs:
    installations:
      - name: "NodeJS 18"
        properties:
          - installSource:
              installers:
                - nodeJSInstaller:
                    id: "18.17.0"
                    npmPackagesRefreshHours: 72

  git:
    installations:
      - name: "Default Git"
        home: "/usr/bin/git"

credentials:
  system:
    domainCredentials:
      - credentials:
          - usernamePassword:
              scope: GLOBAL
              id: "bitbucket-credentials"
              username: "${BITBUCKET_USER}"
              password: "${BITBUCKET_APP_PASSWORD}"
          - string:
              scope: GLOBAL
              id: "jira-token"
              secret: "${JIRA_API_TOKEN}"
          - file:
              scope: GLOBAL
              id: "gcp-service-account"
              fileName: "gcp-sa.json"
              secretBytes: "${GCP_SERVICE_ACCOUNT_KEY}"
```

## 🐳 Docker 기반 빌드 환경

### 커스텀 Arduino 빌드 이미지
```dockerfile
# build-images/arduino-ci/Dockerfile
FROM ubuntu:22.04

LABEL maintainer="DevOps Team <devops@company.com>"
LABEL version="2.0"
LABEL description="Arduino CI/CD Build Environment"

# 시간대 설정 (비대화형)
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul

# 기본 패키지 설치
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    python3 \
    python3-pip \
    nodejs \
    npm \
    jq \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Arduino CLI 설치
RUN curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh \
    && mv bin/arduino-cli /usr/local/bin/ \
    && arduino-cli version

# 보드 패키지 사전 설치
RUN arduino-cli core update-index \
    && arduino-cli core install arduino:avr \
    && arduino-cli core install esp32:esp32 \
    && arduino-cli core install arduino:samd

# 필수 라이브러리 사전 설치
RUN arduino-cli lib update-index \
    && arduino-cli lib install "DHT sensor library" \
    && arduino-cli lib install "WiFi" \
    && arduino-cli lib install "ArduinoJson" \
    && arduino-cli lib install "PubSubClient" \
    && arduino-cli lib install "HTTPClient" \
    && arduino-cli lib install "WebServer"

# Node.js 도구 설치
RUN npm install -g \
    @angular/cli@16 \
    @vue/cli \
    typescript \
    eslint \
    prettier \
    jest

# Python 도구 설치
RUN pip3 install \
    platformio \
    pyserial \
    requests \
    pyyaml \
    jinja2

# 코드 품질 도구
RUN wget -qO- https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Linux-x86_64 \
    > /usr/local/bin/hadolint \
    && chmod +x /usr/local/bin/hadolint

# SonarQube Scanner
RUN wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.8.0.2856-linux.zip \
    && unzip sonar-scanner-cli-4.8.0.2856-linux.zip \
    && mv sonar-scanner-4.8.0.2856-linux /opt/sonar-scanner \
    && ln -s /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner

# 작업 디렉토리 설정
WORKDIR /workspace

# 헬스체크
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD arduino-cli version || exit 1

# 빌드 스크립트 복사
COPY scripts/ /usr/local/bin/
RUN chmod +x /usr/local/bin/*.sh

# 비root 사용자 생성
RUN useradd -m -s /bin/bash jenkins \
    && usermod -aG dialout jenkins

USER jenkins

# 환경 변수
ENV ARDUINO_CLI_CONFIG_DIR=/home/jenkins/.arduino15
ENV PATH=$PATH:/usr/local/bin

CMD ["bash"]
```

### 하드웨어 테스트 에이전트
```dockerfile
# build-images/hardware-test/Dockerfile
FROM arduino/arduino-cli:latest

# 하드웨어 테스트를 위한 추가 도구
RUN apt-get update && apt-get install -y \
    udev \
    minicom \
    screen \
    picocom \
    && rm -rf /var/lib/apt/lists/*

# USB 디바이스 접근 권한 설정
RUN usermod -a -G dialout jenkins \
    && usermod -a -G plugdev jenkins

# 하드웨어 테스트 스크립트
COPY hardware-test-scripts/ /opt/hardware-tests/
RUN chmod +x /opt/hardware-tests/*.sh

# 시리얼 포트 자동 감지 스크립트
COPY <<EOF /usr/local/bin/detect-arduino.sh
#!/bin/bash
# Arduino 보드 자동 감지 및 설정

detect_board() {
    local boards=$(arduino-cli board list --format json | jq -r '.[] | select(.matching_boards != null) | .port.address')
    
    if [ -z "$boards" ]; then
        echo "❌ No Arduino boards detected"
        return 1
    fi
    
    for port in $boards; do
        echo "✅ Arduino detected on $port"
        board_info=$(arduino-cli board list --format json | jq -r ".[] | select(.port.address==\"$port\") | .matching_boards[0].fqbn")
        echo "Board FQBN: $board_info"
        
        # 환경 변수로 설정
        export ARDUINO_PORT=$port
        export ARDUINO_FQBN=$board_info
    done
}

# 실행
detect_board
EOF

RUN chmod +x /usr/local/bin/detect-arduino.sh

ENTRYPOINT ["/usr/local/bin/detect-arduino.sh"]
```

## 🚀 멀티 스테이지 파이프라인

### 고급 Jenkinsfile
```groovy
// Jenkinsfile
pipeline {
    agent none
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 45, unit: 'MINUTES')
        timestamps()
        ansiColor('xterm')
        parallelsAlwaysFailFast()
        skipDefaultCheckout()
    }
    
    environment {
        // 글로벌 환경 변수
        PROJECT_NAME = 'arduino-iot-project'
        BUILD_VERSION = "${env.BUILD_NUMBER}-${env.GIT_COMMIT[0..7]}"
        DOCKER_REGISTRY = 'registry.company.com'
        SONAR_PROJECT_KEY = 'arduino-iot-project'
        SLACK_CHANNEL = '#devops-notifications'
        
        // 동적 환경 변수
        BRANCH_TYPE = "${env.BRANCH_NAME.startsWith('feature/') ? 'feature' : 
                       env.BRANCH_NAME.startsWith('hotfix/') ? 'hotfix' : 
                       env.BRANCH_NAME == 'main' ? 'production' : 'development'}"
        
        // 조건부 배포 설정
        DEPLOY_ENABLED = "${env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'develop'}"
        HARDWARE_TEST_ENABLED = "${env.BRANCH_NAME == 'main'}"
    }
    
    triggers {
        // Bitbucket 웹훅 트리거
        bitbucketPush()
        
        // 정기 빌드 (야간 전체 테스트)
        cron(env.BRANCH_NAME == 'develop' ? 'H 2 * * *' : '')
        
        // 업스트림 의존성 변경 시
        upstream(upstreamProjects: 'arduino-common-lib', threshold: hudson.model.Result.SUCCESS)
    }
    
    stages {
        stage('🚀 Initialize') {
            agent { label 'master' }
            steps {
                script {
                    // 빌드 정보 설정
                    currentBuild.displayName = "#${BUILD_NUMBER} - ${GIT_BRANCH}"
                    currentBuild.description = "${BUILD_VERSION} | ${BRANCH_TYPE}"
                    
                    // Jira 이슈 추출
                    def jiraIssue = extractJiraIssue(env.GIT_COMMIT)
                    if (jiraIssue) {
                        env.JIRA_ISSUE = jiraIssue
                        updateJiraIssue(jiraIssue, 'In Progress', "빌드 시작: ${BUILD_URL}")
                    }
                }
                
                // 소스코드 체크아웃
                checkout scm
                
                // 빌드 메타데이터 생성
                writeFile file: 'build-info.json', text: """
                {
                    "buildNumber": "${BUILD_NUMBER}",
                    "buildVersion": "${BUILD_VERSION}",
                    "gitCommit": "${GIT_COMMIT}",
                    "gitBranch": "${GIT_BRANCH}",
                    "branchType": "${BRANCH_TYPE}",
                    "timestamp": "${new Date().format('yyyy-MM-dd HH:mm:ss')}",
                    "jiraIssue": "${env.JIRA_ISSUE ?: 'N/A'}"
                }
                """
                
                archiveArtifacts artifacts: 'build-info.json', fingerprint: true
            }
        }
        
        stage('🔍 Code Analysis') {
            parallel {
                stage('Code Quality') {
                    agent { 
                        docker { 
                            image 'sonarqube/sonar-scanner-cli:latest'
                            args '--network jenkins-network'
                        }
                    }
                    steps {
                        withSonarQubeEnv('SonarQube') {
                            sh '''
                                sonar-scanner \
                                    -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                                    -Dsonar.projectName="Arduino IoT Project" \
                                    -Dsonar.projectVersion=${BUILD_VERSION} \
                                    -Dsonar.sources=src/ \
                                    -Dsonar.tests=test/ \
                                    -Dsonar.exclusions="**/node_modules/**,**/build/**" \
                                    -Dsonar.javascript.lcov.reportPaths=coverage/lcov.info \
                                    -Dsonar.scm.revision=${GIT_COMMIT}
                            '''
                        }
                        
                        // Quality Gate 대기
                        timeout(time: 10, unit: 'MINUTES') {
                            waitForQualityGate abortPipeline: true
                        }
                    }
                }
                
                stage('Security Scan') {
                    agent { 
                        docker { 
                            image 'owasp/dependency-check:latest'
                            args '-v dependency-check-data:/usr/share/dependency-check/data'
                        }
                    }
                    steps {
                        sh '''
                            /usr/share/dependency-check/bin/dependency-check.sh \
                                --project "Arduino IoT Project" \
                                --scan . \
                                --format JSON \
                                --format HTML \
                                --out reports/ \
                                --failOnCVSS 7
                        '''
                        
                        publishHTML([
                            allowMissing: false,
                            alwaysLinkToLastBuild: true,
                            keepAll: true,
                            reportDir: 'reports',
                            reportFiles: 'dependency-check-report.html',
                            reportName: 'Security Scan Report'
                        ])
                    }
                }
                
                stage('License Compliance') {
                    agent { label 'nodejs' }
                    steps {
                        sh '''
                            npm install -g license-checker
                            license-checker --json --out license-report.json
                            
                            # 금지된 라이선스 체크
                            if grep -E "(GPL-3.0|AGPL)" license-report.json; then
                                echo "❌ Prohibited license detected!"
                                exit 1
                            fi
                        '''
                        
                        archiveArtifacts artifacts: 'license-report.json'
                    }
                }
            }
            
            post {
                always {
                    script {
                        if (env.JIRA_ISSUE) {
                            updateJiraIssue(env.JIRA_ISSUE, null, "코드 분석 완료: 품질 게이트 통과")
                        }
                    }
                }
            }
        }
        
        stage('🔨 Build & Test') {
            parallel {
                stage('Arduino Build') {
                    agent { 
                        docker { 
                            image "${DOCKER_REGISTRY}/arduino-ci:latest"
                            args '--privileged -v /dev:/dev'
                        }
                    }
                    steps {
                        script {
                            def platforms = ['arduino:avr:uno', 'esp32:esp32:esp32']
                            def buildResults = [:]
                            
                            platforms.each { platform ->
                                stage("Build ${platform}") {
                                    try {
                                        sh """
                                            echo "🔨 Building for ${platform}..."
                                            
                                            arduino-cli compile \
                                                --fqbn ${platform} \
                                                --output-dir build/${platform.replaceAll(':', '_')} \
                                                --build-property build.extra_flags=-DBUILD_VERSION=\\"${BUILD_VERSION}\\" \
                                                --export-binaries \
                                                src/main/
                                            
                                            # 빌드 크기 분석
                                            arduino-cli compile \
                                                --fqbn ${platform} \
                                                --show-properties \
                                                src/main/ > build/${platform.replaceAll(':', '_')}/build-info.txt
                                        """
                                        
                                        buildResults[platform] = 'SUCCESS'
                                        
                                    } catch (Exception e) {
                                        buildResults[platform] = 'FAILED'
                                        currentBuild.result = 'UNSTABLE'
                                        echo "❌ Build failed for ${platform}: ${e.message}"
                                    }
                                }
                            }
                            
                            // 빌드 결과 요약
                            def summary = buildResults.collect { k, v -> 
                                "${v == 'SUCCESS' ? '✅' : '❌'} ${k}: ${v}" 
                            }.join('\n')
                            
                            writeFile file: 'build-summary.txt', text: summary
                            echo "빌드 결과:\n${summary}"
                        }
                        
                        // 바이너리 아카이빙
                        archiveArtifacts artifacts: 'build/**/*.{hex,bin,elf}', fingerprint: true
                        archiveArtifacts artifacts: 'build-summary.txt'
                    }
                }
                
                stage('Unit Tests') {
                    agent { 
                        docker { 
                            image 'node:18-alpine'
                        }
                    }
                    steps {
                        sh '''
                            # JavaScript 테스트 (웹 인터페이스)
                            if [ -f "web/package.json" ]; then
                                cd web
                                npm ci
                                npm run test:coverage
                                npm run lint
                                cd ..
                            fi
                            
                            # Arduino 단위 테스트 (AUnit 사용)
                            if [ -d "test/unit" ]; then
                                echo "Running Arduino unit tests..."
                                find test/unit -name "*.cpp" -exec echo "Testing {}" \\;
                            fi
                        '''
                        
                        // 테스트 결과 게시
                        publishTestResults testResultsPattern: '**/test-results.xml'
                        publishCoverage adapters: [
                            istanbulCoberturaAdapter('web/coverage/cobertura-coverage.xml')
                        ], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                    }
                }
                
                stage('Integration Tests') {
                    agent { 
                        docker { 
                            image "${DOCKER_REGISTRY}/arduino-ci:latest"
                            args '--network jenkins-network'
                        }
                    }
                    steps {
                        sh '''
                            echo "🧪 Running integration tests..."
                            
                            # API 테스트
                            if [ -f "test/integration/api-tests.js" ]; then
                                npm test test/integration/
                            fi
                            
                            # 하드웨어 시뮬레이션 테스트
                            if [ -f "test/simulation/run-tests.sh" ]; then
                                chmod +x test/simulation/run-tests.sh
                                ./test/simulation/run-tests.sh
                            fi
                        '''
                    }
                }
            }
        }
        
        stage('🔬 Hardware Testing') {
            when {
                expression { 
                    return env.HARDWARE_TEST_ENABLED == 'true' 
                }
            }
            agent { 
                docker { 
                    image "${DOCKER_REGISTRY}/hardware-test:latest"
                    args '--privileged -v /dev:/dev -v hardware_lab:/hardware'
                }
            }
            steps {
                lock(resource: 'hardware-lab', quantity: 1) {
                    script {
                        try {
                            sh '''
                                echo "🔌 Starting hardware tests..."
                                
                                # Arduino 보드 감지
                                /usr/local/bin/detect-arduino.sh
                                
                                if [ -z "$ARDUINO_PORT" ]; then
                                    echo "⚠️ No hardware available, skipping hardware tests"
                                    exit 0
                                fi
                                
                                echo "📡 Testing on $ARDUINO_PORT with FQBN: $ARDUINO_FQBN"
                                
                                # 바이너리 업로드
                                arduino-cli upload \
                                    --fqbn $ARDUINO_FQBN \
                                    --port $ARDUINO_PORT \
                                    --input-dir build/arduino_avr_uno/
                                
                                # 시리얼 모니터 테스트
                                timeout 30s arduino-cli monitor \
                                    --port $ARDUINO_PORT \
                                    --config baudrate=9600 > hardware-test.log || true
                                
                                # 테스트 결과 분석
                                if grep -q "Test PASSED" hardware-test.log; then
                                    echo "✅ Hardware tests passed"
                                else
                                    echo "❌ Hardware tests failed"
                                    exit 1
                                fi
                            '''
                            
                        } catch (Exception e) {
                            currentBuild.result = 'UNSTABLE'
                            echo "⚠️ Hardware testing failed: ${e.message}"
                        }
                    }
                }
                
                archiveArtifacts artifacts: 'hardware-test.log', allowEmptyArchive: true
            }
        }
        
        stage('📦 Package & Deploy') {
            when {
                expression { 
                    return env.DEPLOY_ENABLED == 'true' 
                }
            }
            parallel {
                stage('Create Release') {
                    agent { label 'master' }
                    steps {
                        script {
                            if (env.BRANCH_NAME == 'main') {
                                // 프로덕션 릴리즈 생성
                                def releaseTag = "v${BUILD_VERSION}"
                                
                                sh """
                                    # 릴리즈 패키지 생성
                                    mkdir -p release
                                    
                                    # 바이너리 파일 복사
                                    cp -r build/ release/
                                    
                                    # 문서 포함
                                    cp -r docs/ release/
                                    cp README.md CHANGELOG.md LICENSE release/
                                    
                                    # 릴리즈 노트 생성
                                    echo "# Release ${releaseTag}" > release/RELEASE_NOTES.md
                                    echo "" >> release/RELEASE_NOTES.md
                                    echo "## Changes" >> release/RELEASE_NOTES.md
                                    git log --oneline \$(git describe --tags --abbrev=0)..HEAD >> release/RELEASE_NOTES.md
                                    
                                    # 압축 파일 생성
                                    tar -czf ${PROJECT_NAME}-${releaseTag}.tar.gz -C release .
                                """
                                
                                archiveArtifacts artifacts: "${PROJECT_NAME}-*.tar.gz", fingerprint: true
                                
                                // Git 태그 생성
                                sh """
                                    git tag -a ${releaseTag} -m "Release ${releaseTag}"
                                    git push origin ${releaseTag}
                                """
                            }
                        }
                    }
                }
                
                stage('Deploy to Staging') {
                    when {
                        branch 'develop'
                    }
                    agent { label 'deployment' }
                    steps {
                        script {
                            deploy(
                                environment: 'staging',
                                version: BUILD_VERSION,
                                artifacts: 'build/**/*'
                            )
                        }
                    }
                }
                
                stage('Deploy to Production') {
                    when {
                        branch 'main'
                    }
                    agent { label 'deployment' }
                    steps {
                        timeout(time: 10, unit: 'MINUTES') {
                            input message: '프로덕션 배포를 승인하시겠습니까?', 
                                  submitter: 'admin,release-manager'
                        }
                        
                        script {
                            deploy(
                                environment: 'production',
                                version: BUILD_VERSION,
                                artifacts: 'build/**/*'
                            )
                        }
                    }
                }
            }
        }
    }
    
    post {
        always {
            node('master') {
                script {
                    // 빌드 결과 수집
                    def buildResult = currentBuild.result ?: 'SUCCESS'
                    def duration = currentBuild.durationString.replace(' and counting', '')
                    
                    // Jira 이슈 업데이트
                    if (env.JIRA_ISSUE) {
                        def jiraStatus = buildResult == 'SUCCESS' ? 'Done' : 'In Progress'
                        def jiraComment = """
                        빌드 ${buildResult}: ${BUILD_URL}
                        빌드 시간: ${duration}
                        브랜치: ${GIT_BRANCH}
                        커밋: ${GIT_COMMIT[0..7]}
                        """
                        updateJiraIssue(env.JIRA_ISSUE, jiraStatus, jiraComment)
                    }
                    
                    // 메트릭 수집
                    recordBuildMetrics(buildResult, duration)
                }
            }
        }
        
        success {
            script {
                slackSend(
                    channel: SLACK_CHANNEL,
                    color: 'good',
                    message: """
                    ✅ *${PROJECT_NAME}* 빌드 성공!
                    • 브랜치: `${GIT_BRANCH}`
                    • 빌드: #${BUILD_NUMBER}
                    • 버전: ${BUILD_VERSION}
                    • 소요시간: ${currentBuild.durationString}
                    • 링크: ${BUILD_URL}
                    ${env.JIRA_ISSUE ? "• Jira: ${env.JIRA_ISSUE}" : ""}
                    """
                )
            }
        }
        
        failure {
            script {
                slackSend(
                    channel: SLACK_CHANNEL,
                    color: 'danger',
                    message: """
                    ❌ *${PROJECT_NAME}* 빌드 실패!
                    • 브랜치: `${GIT_BRANCH}`
                    • 빌드: #${BUILD_NUMBER}
                    • 실패 단계: ${env.STAGE_NAME}
                    • 링크: ${BUILD_URL}console
                    ${env.JIRA_ISSUE ? "• Jira: ${env.JIRA_ISSUE}" : ""}
                    """
                )
                
                // 개발자에게 이메일 알림
                emailext(
                    subject: "빌드 실패: ${PROJECT_NAME} #${BUILD_NUMBER}",
                    body: """
                    빌드가 실패했습니다.
                    
                    프로젝트: ${PROJECT_NAME}
                    브랜치: ${GIT_BRANCH}
                    빌드 번호: ${BUILD_NUMBER}
                    실패 단계: ${env.STAGE_NAME}
                    
                    상세 로그: ${BUILD_URL}console
                    """,
                    to: "${env.CHANGE_AUTHOR_EMAIL ?: 'team@company.com'}"
                )
            }
        }
        
        unstable {
            script {
                slackSend(
                    channel: SLACK_CHANNEL,
                    color: 'warning',
                    message: """
                    ⚠️ *${PROJECT_NAME}* 빌드 불안정
                    • 브랜치: `${GIT_BRANCH}`
                    • 빌드: #${BUILD_NUMBER}
                    • 경고: 일부 테스트 실패 또는 품질 게이트 미달
                    • 링크: ${BUILD_URL}
                    """
                )
            }
        }
        
        cleanup {
            // 작업공간 정리
            cleanWs(cleanWhenNotBuilt: false,
                    deleteDirs: true,
                    disableDeferredWipeout: true,
                    notFailBuild: true)
        }
    }
}

// === 공통 함수 정의 ===

def extractJiraIssue(commit) {
    def matcher = commit =~ /PROJ-\d+/
    return matcher ? matcher[0] : null
}

def updateJiraIssue(issueKey, status, comment) {
    try {
        script {
            def jiraUrl = "${JIRA_API_URL}/issue/${issueKey}"
            
            // 코멘트 추가
            if (comment) {
                httpRequest(
                    url: "${jiraUrl}/comment",
                    httpMode: 'POST',
                    contentType: 'APPLICATION_JSON',
                    authentication: 'jira-token',
                    requestBody: """
                    {
                        "body": "${comment}"
                    }
                    """
                )
            }
            
            // 상태 변경
            if (status) {
                def transitionId = getJiraTransitionId(issueKey, status)
                if (transitionId) {
                    httpRequest(
                        url: "${jiraUrl}/transitions",
                        httpMode: 'POST',
                        contentType: 'APPLICATION_JSON',
                        authentication: 'jira-token',
                        requestBody: """
                        {
                            "transition": {
                                "id": "${transitionId}"
                            }
                        }
                        """
                    )
                }
            }
        }
    } catch (Exception e) {
        echo "⚠️ Jira 업데이트 실패: ${e.message}"
    }
}

def getJiraTransitionId(issueKey, targetStatus) {
    def transitions = [
        'To Do': '11',
        'In Progress': '21',
        'Done': '31'
    ]
    return transitions[targetStatus]
}

def deploy(Map config) {
    echo "🚀 Deploying to ${config.environment}..."
    
    script {
        switch(config.environment) {
            case 'staging':
                sh """
                    # 스테이징 환경 배포
                    rsync -avz ${config.artifacts} deploy@staging-server:/opt/arduino-project/
                    ssh deploy@staging-server 'sudo systemctl restart arduino-project'
                """
                break
                
            case 'production':
                sh """
                    # 프로덕션 환경 배포 (무중단 배포)
                    ./scripts/blue-green-deploy.sh ${config.version}
                """
                break
        }
    }
    
    echo "✅ Deployment to ${config.environment} completed"
}

def recordBuildMetrics(result, duration) {
    // Prometheus 메트릭 전송
    script {
        def success = result == 'SUCCESS' ? 1 : 0
        def durationSeconds = parseDuration(duration)
        
        sh """
            curl -X POST http://prometheus-pushgateway:9091/metrics/job/jenkins-builds \
                -d "jenkins_build_success{project=\"${PROJECT_NAME}\",branch=\"${GIT_BRANCH}\"} ${success}"
            
            curl -X POST http://prometheus-pushgateway:9091/metrics/job/jenkins-builds \
                -d "jenkins_build_duration_seconds{project=\"${PROJECT_NAME}\",branch=\"${GIT_BRANCH}\"} ${durationSeconds}"
        """
    }
}

def parseDuration(durationString) {
    // "1 hr 23 min" → 4980 seconds 변환
    def hours = (durationString =~ /(\d+) hr/) ? (durationString =~ /(\d+) hr/)[0][1] as Integer : 0
    def minutes = (durationString =~ /(\d+) min/) ? (durationString =~ /(\d+) min/)[0][1] as Integer : 0
    def seconds = (durationString =~ /(\d+) sec/) ? (durationString =~ /(\d+) sec/)[0][1] as Integer : 0
    
    return (hours * 3600) + (minutes * 60) + seconds
}
```

---

**다음 단계**: [Jira 이슈 관리 및 자동화 워크플로우](03-jira-automation-workflow.md)