# 🔀 Bitbucket 연동 및 Git 워크플로우

> 엔터프라이즈급 소스코드 관리 및 협업 워크플로우

## 📋 목차

1. [Git 브랜치 전략](#git-브랜치-전략)
2. [Bitbucket 리포지토리 설정](#bitbucket-리포지토리-설정)
3. [개발 워크플로우](#개발-워크플로우)
4. [코드 리뷰 프로세스](#코드-리뷰-프로세스)
5. [자동화 및 웹훅](#자동화-및-웹훅)
6. [고급 Git 기법](#고급-git-기법)

## 🌳 Git 브랜치 전략

### Git Flow 기반 브랜치 모델
```
main (production)
├── develop (integration)
│   ├── feature/PROJ-123-temperature-sensor
│   ├── feature/PROJ-124-wifi-connectivity
│   └── feature/PROJ-125-web-dashboard
├── release/v1.2.0
├── hotfix/PROJ-126-critical-bug
└── support/v1.1.x
```

### 브랜치 네이밍 컨벤션
```bash
# 기능 개발
feature/JIRA-TICKET-short-description
feature/PROJ-123-temperature-sensor-integration

# 버그 수정
bugfix/JIRA-TICKET-short-description
bugfix/PROJ-124-wifi-connection-timeout

# 핫픽스
hotfix/JIRA-TICKET-short-description
hotfix/PROJ-125-memory-leak-fix

# 릴리즈
release/v1.2.0
release/v2.0.0-beta.1

# 실험적 기능
experiment/proof-of-concept-ai-optimization
experiment/performance-test-esp32-s3
```

### 브랜치 생명주기 관리
```bash
#!/bin/bash
# ~/scripts/branch-manager.sh

create_feature_branch() {
    local jira_ticket=$1
    local description=$2
    
    if [[ ! "$jira_ticket" =~ ^PROJ-[0-9]+$ ]]; then
        echo "❌ Invalid Jira ticket format. Use: PROJ-123"
        return 1
    fi
    
    # develop 브랜치에서 시작
    git checkout develop
    git pull origin develop
    
    # 새 feature 브랜치 생성
    local branch_name="feature/${jira_ticket}-${description}"
    git checkout -b "$branch_name"
    
    # 원격 브랜치 생성
    git push -u origin "$branch_name"
    
    echo "✅ Created feature branch: $branch_name"
    echo "🔗 Link: https://bitbucket.org/your-team/arduino-project/branch/$branch_name"
}

# 사용법: create_feature_branch PROJ-123 "temperature-sensor"
```

## 🏗️ Bitbucket 리포지토리 설정

### 1. 리포지토리 구조
```
arduino-iot-project/
├── .bitbucket/
│   └── pipelines.yml                # Bitbucket Pipelines 설정
├── .vscode/
│   ├── settings.json               # VSCode 설정
│   ├── launch.json                 # 디버그 설정
│   └── extensions.json             # 권장 확장 프로그램
├── docs/
│   ├── api/                        # API 문서
│   ├── hardware/                   # 하드웨어 스펙
│   └── deployment/                 # 배포 가이드
├── src/
│   ├── main/                       # 메인 Arduino 코드
│   ├── lib/                        # 라이브러리
│   └── test/                       # 단위 테스트
├── scripts/
│   ├── build.sh                    # 빌드 스크립트
│   ├── deploy.sh                   # 배포 스크립트
│   └── test.sh                     # 테스트 스크립트
├── config/
│   ├── development.json            # 개발 환경 설정
│   ├── staging.json                # 스테이징 환경 설정
│   └── production.json             # 프로덕션 환경 설정
├── Jenkinsfile                     # Jenkins 파이프라인
├── docker-compose.yml              # 개발 환경 컨테이너
├── README.md
└── .gitignore
```

### 2. 브랜치 권한 설정
```json
{
  "branch_permissions": {
    "main": {
      "push_access": ["admin", "lead-developer"],
      "merge_access": ["admin", "lead-developer", "senior-developer"],
      "require_pr": true,
      "require_approvals": 2,
      "require_builds": true,
      "require_all_tasks_resolved": true
    },
    "develop": {
      "push_access": ["admin", "lead-developer", "senior-developer"],
      "merge_access": ["all-developers"],
      "require_pr": true,
      "require_approvals": 1,
      "require_builds": true
    },
    "feature/*": {
      "push_access": ["all-developers"],
      "merge_access": ["all-developers"],
      "require_pr": false,
      "delete_after_merge": true
    }
  }
}
```

### 3. Bitbucket Pipelines 구성
```yaml
# .bitbucket/pipelines.yml
image: ubuntu:22.04

definitions:
  caches:
    arduino-cli: ~/.arduino15
    node-modules: node_modules
  
  services:
    docker:
      memory: 2048

pipelines:
  default:
    - step:
        name: "Code Quality & Security Scan"
        image: sonarqube/sonar-scanner-cli:latest
        caches:
          - node-modules
        script:
          - sonar-scanner -Dsonar.projectKey=arduino-iot-project
        artifacts:
          - sonar-report.json
    
    - step:
        name: "Build & Test"
        image: node:18
        caches:
          - arduino-cli
          - node-modules
        script:
          # Arduino CLI 설치
          - curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
          - export PATH=$PATH:$PWD/bin
          
          # 보드 패키지 설치
          - arduino-cli core update-index
          - arduino-cli core install arduino:avr
          - arduino-cli core install esp32:esp32
          
          # 라이브러리 설치
          - arduino-cli lib install "DHT sensor library"
          - arduino-cli lib install "WiFi"
          - arduino-cli lib install "ArduinoJson"
          
          # 컴파일 테스트
          - ./scripts/build.sh --verify-only
          
          # 단위 테스트 실행
          - npm install
          - npm run test
        artifacts:
          - build/
          - test-results/
    
    - step:
        name: "Security & Vulnerability Scan"
        image: owasp/dependency-check:latest
        script:
          - dependency-check --project "Arduino IoT Project" --scan . --format JSON
        artifacts:
          - dependency-check-report.json

  branches:
    main:
      - step:
          name: "Production Build"
          deployment: production
          image: node:18
          script:
            - ./scripts/build.sh --production
            - ./scripts/deploy.sh --target production
          artifacts:
            - dist/
      
      - step:
          name: "Release Notification"
          image: curlimages/curl:latest
          script:
            # Jira 이슈 상태 업데이트
            - curl -X POST "$JIRA_API_URL/issue/$BITBUCKET_COMMIT/transitions" \
                -H "Authorization: Bearer $JIRA_TOKEN" \
                -H "Content-Type: application/json" \
                -d '{"transition":{"id":"31"}}'
            
            # Slack 알림
            - curl -X POST "$SLACK_WEBHOOK_URL" \
                -H "Content-Type: application/json" \
                -d "{\"text\":\"🚀 Arduino IoT Project v$BITBUCKET_BUILD_NUMBER deployed to production\"}"

    develop:
      - step:
          name: "Integration Test"
          services:
            - docker
          script:
            - docker-compose -f docker-compose.test.yml up --abort-on-container-exit
            - ./scripts/integration-test.sh
          artifacts:
            - integration-test-results/
```

## 🔄 개발 워크플로우

### 1. 이슈 기반 개발 프로세스
```bash
#!/bin/bash
# ~/scripts/start-development.sh

start_development() {
    local jira_ticket=$1
    local issue_type=${2:-"feature"}  # feature, bugfix, hotfix
    
    echo "🎯 Starting development for $jira_ticket"
    
    # Jira 이슈 정보 가져오기
    local issue_info=$(curl -s -u "$JIRA_USER:$JIRA_TOKEN" \
        "$JIRA_API_URL/issue/$jira_ticket" | jq -r '.fields.summary')
    
    # 브랜치 이름 생성 (자동으로 소문자, 공백을 하이픈으로 변환)
    local branch_description=$(echo "$issue_info" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-')
    local branch_name="${issue_type}/${jira_ticket}-${branch_description}"
    
    # Git 워크플로우 시작
    git checkout develop
    git pull origin develop
    git checkout -b "$branch_name"
    git push -u origin "$branch_name"
    
    # VSCode에서 브랜치 자동 열기
    code .
    
    # Jira 이슈 상태를 "In Progress"로 변경
    curl -X POST "$JIRA_API_URL/issue/$jira_ticket/transitions" \
        -H "Authorization: Bearer $JIRA_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"transition":{"id":"21"}}'
    
    echo "✅ Development environment ready!"
    echo "📋 Issue: $issue_info"
    echo "🌿 Branch: $branch_name"
    echo "🔗 Bitbucket: https://bitbucket.org/your-team/arduino-project/branch/$branch_name"
}

# 사용법: start_development PROJ-123 feature
```

### 2. 커밋 메시지 컨벤션
```
<type>(scope): <description>

[optional body]

[optional footer]

Jira-Issue: PROJ-123
```

**타입별 예시:**
```bash
# 새 기능
feat(sensor): add DHT22 temperature monitoring

- Implement temperature and humidity reading
- Add calibration functionality
- Include error handling for sensor failures

Jira-Issue: PROJ-123

# 버그 수정
fix(wifi): resolve connection timeout issue

- Increase connection timeout to 30 seconds
- Add retry mechanism with exponential backoff
- Improve error logging for debugging

Jira-Issue: PROJ-124
Fixes: #45

# 문서 업데이트
docs(api): update sensor API documentation

- Add new endpoint descriptions
- Include example requests and responses
- Update authentication requirements

Jira-Issue: PROJ-125

# 리팩토링
refactor(network): optimize WiFi connection handling

- Extract connection logic to separate class
- Implement connection pooling
- Reduce memory usage by 15%

Jira-Issue: PROJ-126
```

### 3. Git 훅을 통한 자동화
```bash
#!/bin/bash
# .git/hooks/pre-commit

# 커밋 메시지 검증
commit_msg_file=$1
commit_msg=$(cat "$commit_msg_file")

# Jira 티켓 번호 검증
if ! echo "$commit_msg" | grep -qE "Jira-Issue: PROJ-[0-9]+"; then
    echo "❌ Commit message must include 'Jira-Issue: PROJ-XXX'"
    echo "📝 Format: <type>(scope): <description>"
    echo ""
    echo "   Jira-Issue: PROJ-123"
    exit 1
fi

# 코드 품질 검사
echo "🔍 Running code quality checks..."

# Arduino 코드 컴파일 검증
if [ -f "src/main/main.ino" ]; then
    arduino-cli compile --fqbn arduino:avr:uno src/main/ || {
        echo "❌ Arduino compilation failed"
        exit 1
    }
fi

# JavaScript/Node.js 린팅 (웹 인터페이스용)
if [ -f "package.json" ]; then
    npm run lint || {
        echo "❌ Linting failed"
        exit 1
    }
fi

echo "✅ All checks passed!"
```

## 👥 코드 리뷰 프로세스

### 1. Pull Request 템플릿
```markdown
<!-- .bitbucket/pull_request_template.md -->

## 🎯 개요
**Jira Issue:** [PROJ-123](https://your-company.atlassian.net/browse/PROJ-123)

### 변경 사항
- [ ] 새 기능 추가
- [ ] 버그 수정
- [ ] 성능 개선
- [ ] 리팩토링
- [ ] 문서 업데이트

### 설명
<!-- 변경 사항에 대한 상세한 설명을 작성해주세요 -->

## 🧪 테스트
### 테스트 케이스
- [ ] 단위 테스트 작성/업데이트
- [ ] 통합 테스트 실행
- [ ] 하드웨어 테스트 완료
- [ ] 성능 테스트 통과

### 테스트 환경
- **하드웨어:** Arduino Uno R3 / ESP32 DevKit
- **라이브러리 버전:** DHT v1.4.4, WiFi v1.2.7
- **테스트 도구:** Arduino IDE 2.0, PlatformIO

## 📋 체크리스트
### 코드 품질
- [ ] 코드 스타일 가이드 준수
- [ ] 주석 및 문서화 완료
- [ ] 하드코딩된 값 제거 (상수/설정 파일 사용)
- [ ] 메모리 누수 확인
- [ ] 예외 처리 구현

### 보안
- [ ] 민감한 정보 (WiFi 비밀번호, API 키) 하드코딩 제거
- [ ] 입력 검증 구현
- [ ] 보안 취약점 스캔 통과

### 성능
- [ ] 메모리 사용량 최적화
- [ ] 전력 소비 최적화
- [ ] 응답 시간 요구사항 만족

## 🔗 관련 리소스
- 설계 문서: [링크]
- API 문서: [링크]
- 테스트 결과: [링크]

## 📸 스크린샷/데모
<!-- 시리얼 모니터 출력, 웹 대시보드 등의 스크린샷 첨부 -->

---
**리뷰어:** @senior-developer @hardware-engineer @qa-tester
**예상 머지 일정:** 2024-01-XX
```

### 2. 코드 리뷰 가이드라인
```yaml
# .bitbucket/review-guidelines.yml
review_criteria:
  code_quality:
    - "변수명과 함수명이 의미가 명확한가?"
    - "코드 중복이 제거되었는가?"
    - "적절한 주석이 포함되어 있는가?"
    - "에러 처리가 적절히 구현되었는가?"
  
  arduino_specific:
    - "메모리 사용량이 최적화되었는가?"
    - "전력 소비가 고려되었는가?"
    - "하드웨어 제약사항이 반영되었는가?"
    - "인터럽트 처리가 적절한가?"
  
  security:
    - "민감한 정보가 하드코딩되지 않았는가?"
    - "외부 입력에 대한 검증이 있는가?"
    - "버퍼 오버플로우 가능성이 없는가?"
  
  testing:
    - "단위 테스트가 포함되어 있는가?"
    - "테스트 커버리지가 충분한가?"
    - "하드웨어 테스트가 완료되었는가?"

approval_matrix:
  feature:
    required_approvals: 2
    required_reviewers: ["senior-developer", "hardware-engineer"]
    optional_reviewers: ["qa-tester", "product-owner"]
  
  bugfix:
    required_approvals: 1
    required_reviewers: ["senior-developer"]
    optional_reviewers: ["original-author"]
  
  hotfix:
    required_approvals: 2
    required_reviewers: ["tech-lead", "senior-developer"]
    expedited: true
```

## 🔗 자동화 및 웹훅

### 1. Bitbucket 웹훅 설정
```javascript
// webhook-handler.js - Express.js 기반 웹훅 처리기

const express = require('express');
const crypto = require('crypto');
const axios = require('axios');

const app = express();
app.use(express.json());

// 웹훅 서명 검증
const verifySignature = (req, res, next) => {
    const signature = req.headers['x-hub-signature-256'];
    const payload = JSON.stringify(req.body);
    const hmac = crypto.createHmac('sha256', process.env.WEBHOOK_SECRET);
    const digest = 'sha256=' + hmac.update(payload).digest('hex');
    
    if (signature !== digest) {
        return res.status(401).send('Unauthorized');
    }
    next();
};

// Push 이벤트 처리
app.post('/webhook/push', verifySignature, async (req, res) => {
    const { repository, push } = req.body;
    
    for (const change of push.changes) {
        const branchName = change.new.name;
        const commits = change.commits;
        
        // Jira 이슈 업데이트
        for (const commit of commits) {
            const jiraMatch = commit.message.match(/Jira-Issue: (PROJ-\d+)/);
            if (jiraMatch) {
                await updateJiraIssue(jiraMatch[1], {
                    comment: `Commit: ${commit.hash.substring(0, 7)} - ${commit.message}`,
                    branch: branchName,
                    repository: repository.full_name
                });
            }
        }
        
        // Jenkins 빌드 트리거
        if (branchName === 'develop' || branchName === 'main') {
            await triggerJenkinsBuild(repository.full_name, branchName);
        }
    }
    
    res.status(200).send('OK');
});

// Pull Request 이벤트 처리
app.post('/webhook/pullrequest', verifySignature, async (req, res) => {
    const { pullrequest, repository } = req.body;
    
    if (pullrequest.state === 'OPEN') {
        // 자동 리뷰어 할당
        await assignReviewers(pullrequest, repository);
        
        // 빌드 상태 체크 시작
        await triggerPRChecks(pullrequest, repository);
    }
    
    if (pullrequest.state === 'MERGED') {
        // 브랜치 정리
        await cleanupFeatureBranch(pullrequest.source.branch.name, repository);
        
        // Jira 이슈 상태 업데이트
        const jiraMatch = pullrequest.title.match(/PROJ-\d+/);
        if (jiraMatch) {
            await updateJiraIssue(jiraMatch[0], {
                status: 'Done',
                resolution: 'Fixed'
            });
        }
    }
    
    res.status(200).send('OK');
});

// Jira 이슈 업데이트 함수
async function updateJiraIssue(issueKey, updates) {
    try {
        const response = await axios.post(
            `${process.env.JIRA_API_URL}/issue/${issueKey}`,
            {
                fields: updates,
                update: {
                    comment: [{
                        add: {
                            body: `Automated update from Bitbucket: ${updates.comment || 'Status updated'}`
                        }
                    }]
                }
            },
            {
                headers: {
                    'Authorization': `Bearer ${process.env.JIRA_TOKEN}`,
                    'Content-Type': 'application/json'
                }
            }
        );
        console.log(`✅ Updated Jira issue ${issueKey}`);
    } catch (error) {
        console.error(`❌ Failed to update Jira issue ${issueKey}:`, error.message);
    }
}

// Jenkins 빌드 트리거
async function triggerJenkinsBuild(repository, branch) {
    try {
        await axios.post(
            `${process.env.JENKINS_URL}/job/arduino-project/build`,
            {
                parameter: [
                    { name: 'REPOSITORY', value: repository },
                    { name: 'BRANCH', value: branch }
                ]
            },
            {
                headers: {
                    'Authorization': `Bearer ${process.env.JENKINS_TOKEN}`
                }
            }
        );
        console.log(`✅ Triggered Jenkins build for ${repository}:${branch}`);
    } catch (error) {
        console.error(`❌ Failed to trigger Jenkins build:`, error.message);
    }
}

app.listen(3000, () => {
    console.log('Webhook handler listening on port 3000');
});
```

### 2. 자동 브랜치 관리
```bash
#!/bin/bash
# ~/scripts/branch-cleanup.sh

# 완료된 feature 브랜치 정리
cleanup_merged_branches() {
    echo "🧹 Cleaning up merged branches..."
    
    # 원격 브랜치 정보 업데이트
    git fetch --prune origin
    
    # 머지된 feature 브랜치 찾기
    merged_branches=$(git branch -r --merged origin/develop | \
        grep "origin/feature/" | \
        sed 's|origin/||' | \
        grep -v HEAD)
    
    for branch in $merged_branches; do
        echo "Deleting merged branch: $branch"
        
        # 로컬 브랜치 삭제
        git branch -d "$branch" 2>/dev/null || true
        
        # 원격 브랜치 삭제
        git push origin --delete "$branch"
        
        # Jira 이슈에 완료 알림
        jira_ticket=$(echo "$branch" | grep -oE "PROJ-[0-9]+" | head -1)
        if [ -n "$jira_ticket" ]; then
            curl -X POST "$JIRA_API_URL/issue/$jira_ticket/comment" \
                -H "Authorization: Bearer $JIRA_TOKEN" \
                -H "Content-Type: application/json" \
                -d "{\"body\":\"✅ Feature branch $branch has been merged and cleaned up.\"}"
        fi
    done
    
    echo "✅ Branch cleanup completed"
}

# 오래된 브랜치 알림
check_stale_branches() {
    echo "🔍 Checking for stale branches..."
    
    # 30일 이상 업데이트되지 않은 브랜치 찾기
    stale_branches=$(git for-each-ref --format='%(refname:short) %(committerdate:unix)' refs/remotes/origin/feature/ | \
        while read branch timestamp; do
            if [ $(($(date +%s) - timestamp)) -gt 2592000 ]; then  # 30 days
                echo "$branch"
            fi
        done)
    
    if [ -n "$stale_branches" ]; then
        echo "⚠️ Stale branches found (>30 days):"
        echo "$stale_branches"
        
        # Slack 알림
        curl -X POST "$SLACK_WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "{\"text\":\"⚠️ Stale branches detected in arduino-project:\\n\`\`\`$stale_branches\`\`\`\"}"
    fi
}

# 일일 실행
cleanup_merged_branches
check_stale_branches
```

## 🚀 고급 Git 기법

### 1. Git Worktree를 활용한 멀티 브랜치 개발
```bash
#!/bin/bash
# ~/scripts/worktree-manager.sh

# 새 worktree 생성
create_worktree() {
    local branch_name=$1
    local worktree_path="$HOME/workspace/worktrees/$branch_name"
    
    # 디렉토리 생성
    mkdir -p "$(dirname "$worktree_path")"
    
    # worktree 생성
    git worktree add "$worktree_path" "$branch_name"
    
    # VSCode로 새 worktree 열기
    code "$worktree_path"
    
    echo "✅ Created worktree: $worktree_path"
}

# Worktree 정리
cleanup_worktrees() {
    git worktree prune
    
    # 삭제된 브랜치의 worktree 디렉토리 정리
    find "$HOME/workspace/worktrees" -maxdepth 1 -type d | while read dir; do
        if [ ! -f "$dir/.git" ]; then
            echo "Removing orphaned worktree: $dir"
            rm -rf "$dir"
        fi
    done
}

# 사용법:
# create_worktree feature/PROJ-123-sensor-upgrade
# cleanup_worktrees
```

### 2. Git Submodule을 활용한 라이브러리 관리
```bash
# 공통 라이브러리를 서브모듈로 관리
git submodule add https://bitbucket.org/your-team/arduino-common-lib.git lib/common

# 서브모듈 초기화 및 업데이트
git submodule update --init --recursive

# 서브모듈 자동 업데이트 스크립트
#!/bin/bash
# ~/scripts/update-submodules.sh

echo "🔄 Updating Git submodules..."

git submodule foreach git fetch origin
git submodule foreach git merge origin/main

# 변경사항이 있으면 커밋
if ! git diff --quiet --cached; then
    git add .
    git commit -m "chore: update submodules to latest versions

$(git submodule foreach --quiet 'echo "- $name: $(git log --oneline -1)"')"
    
    echo "✅ Submodules updated and committed"
else
    echo "ℹ️ No submodule updates available"
fi
```

### 3. 고급 Git 설정
```bash
# ~/.gitconfig

[user]
    name = Your Name
    email = your.email@company.com

[core]
    editor = code --wait
    autocrlf = input
    ignorecase = false
    
[push]
    default = simple
    autoSetupRemote = true

[pull]
    rebase = true

[merge]
    tool = vscode
    
[mergetool "vscode"]
    cmd = code --wait $MERGED

[diff]
    tool = vscode

[difftool "vscode"]
    cmd = code --wait --diff $LOCAL $REMOTE

# Git 별칭 설정
[alias]
    # 로그 시각화
    lg = log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit
    
    # 상태 확인
    st = status -s
    
    # 브랜치 관리
    bd = branch -d
    bdr = push origin --delete
    
    # 스테이징
    a = add
    aa = add .
    
    # 커밋
    c = commit
    cm = commit -m
    ca = commit --amend
    
    # 리베이스
    rb = rebase
    rbi = rebase -i
    
    # 원격 저장소
    pom = push origin main
    pod = push origin develop
    
    # Jira 통합
    jira-commit = "!f() { git commit -m \"$1\" -m \"\" -m \"Jira-Issue: $2\"; }; f"
```

---

**다음 단계**: [Jenkins CI/CD 파이프라인 고도화](02-jenkins-advanced-pipeline.md)