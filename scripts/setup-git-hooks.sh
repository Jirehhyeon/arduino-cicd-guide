#!/bin/bash
# Git Hooks Setup Script for Arduino CI/CD Project
# 
# 이 스크립트는 프로젝트에 필요한 Git hooks를 설정합니다.
# 코드 품질 검사, 커밋 메시지 검증, 자동 테스트 등을 수행합니다.

set -e

PROJECT_ROOT=$(git rev-parse --show-toplevel)
HOOKS_DIR="$PROJECT_ROOT/.git/hooks"

echo "🔧 Setting up Git hooks for Arduino CI/CD project..."

# Pre-commit hook 생성
cat > "$HOOKS_DIR/pre-commit" << 'EOF'
#!/bin/bash
# Pre-commit hook for Arduino projects

echo "🔍 Running pre-commit checks..."

# Check if we're in an Arduino project
if [ ! -f "README.md" ] || ! grep -q "Arduino" README.md; then
    echo "⚠️  This doesn't appear to be an Arduino project"
fi

# Arduino CLI 경로 확인
ARDUINO_CLI=""
if command -v arduino-cli &> /dev/null; then
    ARDUINO_CLI="arduino-cli"
elif [ -f "/usr/local/bin/arduino-cli" ]; then
    ARDUINO_CLI="/usr/local/bin/arduino-cli"
else
    echo "⚠️  Arduino CLI not found, skipping compilation check"
fi

# 1. Arduino 스케치 컴파일 검사
if [ -n "$ARDUINO_CLI" ]; then
    echo "🔨 Checking Arduino compilation..."
    
    # Find .ino files in the commit
    INO_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.ino$' || true)
    
    if [ -n "$INO_FILES" ]; then
        for ino_file in $INO_FILES; do
            ino_dir=$(dirname "$ino_file")
            echo "Checking compilation for: $ino_file"
            
            # Try different board types
            BOARDS=("arduino:avr:uno" "esp32:esp32:esp32" "esp8266:esp8266:nodemcuv2")
            COMPILED=false
            
            for board in "${BOARDS[@]}"; do
                if $ARDUINO_CLI compile --verify --fqbn "$board" "$ino_dir" >/dev/null 2>&1; then
                    echo "✅ $ino_file compiles successfully for $board"
                    COMPILED=true
                    break
                fi
            done
            
            if [ "$COMPILED" = false ]; then
                echo "❌ $ino_file failed to compile for any supported board"
                echo "Please fix compilation errors before committing"
                exit 1
            fi
        done
    fi
fi

# 2. 커밋 메시지 형식 검사
echo "📝 Checking commit message format..."

# Read commit message from file
COMMIT_MSG_FILE="$1"
if [ -z "$COMMIT_MSG_FILE" ]; then
    COMMIT_MSG_FILE=".git/COMMIT_EDITMSG"
fi

if [ -f "$COMMIT_MSG_FILE" ]; then
    COMMIT_MSG=$(head -1 "$COMMIT_MSG_FILE")
    
    # Check format: type(scope): description [AIP-XXX]
    COMMIT_REGEX='^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+ \[AIP-[0-9]+\]$|^Merge '
    
    if [[ ! $COMMIT_MSG =~ $COMMIT_REGEX ]]; then
        echo "❌ Invalid commit message format"
        echo "Expected: type(scope): description [AIP-XXX]"
        echo "Examples:"
        echo "  feat(sensor): add DHT22 temperature reading [AIP-123]"
        echo "  fix(wifi): resolve connection timeout issue [AIP-456]"
        echo "  docs: update README with installation guide [AIP-789]"
        echo ""
        echo "Current message: $COMMIT_MSG"
        exit 1
    fi
fi

# 3. 코드 스타일 검사
echo "🎨 Checking code style..."

# Check for tabs vs spaces in Arduino files
ARDUINO_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(ino|cpp|h)$' || true)

if [ -n "$ARDUINO_FILES" ]; then
    for file in $ARDUINO_FILES; do
        if [ -f "$file" ]; then
            # Check for tabs (prefer 4 spaces)
            if grep -q $'\t' "$file"; then
                echo "⚠️  Warning: Found tabs in $file, prefer 4 spaces"
            fi
            
            # Check for trailing whitespace
            if grep -q ' $' "$file"; then
                echo "⚠️  Warning: Found trailing whitespace in $file"
            fi
            
            # Check for long lines (>120 characters)
            if awk 'length > 120 {print NR ": " $0; exit 1}' "$file"; then
                echo "⚠️  Warning: Found lines longer than 120 characters in $file"
            fi
        fi
    done
fi

# 4. 보안 검사
echo "🔒 Running security checks..."

# Check for hardcoded credentials
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)
for file in $STAGED_FILES; do
    if [ -f "$file" ]; then
        # Check for potential secrets
        if grep -i -E "(password|secret|key|token).*=.*['\"][^'\"]{8,}" "$file" >/dev/null; then
            echo "❌ Potential hardcoded credentials found in $file"
            echo "Please remove sensitive data before committing"
            exit 1
        fi
        
        # Check for common secret patterns
        if grep -E "(api[_-]?key|access[_-]?token|secret[_-]?key)" "$file" >/dev/null; then
            echo "⚠️  Warning: Potential API keys or secrets found in $file"
            echo "Please verify no sensitive data is being committed"
        fi
    fi
done

# 5. TODO/FIXME 검사
echo "📋 Checking for TODO/FIXME comments..."

TODO_COUNT=$(git diff --cached | grep -c -E "TODO|FIXME|XXX|HACK" || true)
if [ "$TODO_COUNT" -gt 0 ]; then
    echo "⚠️  Found $TODO_COUNT TODO/FIXME comments in staged changes"
    echo "Consider resolving these before committing to main branch"
    
    # Block TODOs on main branch
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
        echo "❌ TODO/FIXME comments are not allowed on main branch"
        exit 1
    fi
fi

# 6. 파일 크기 검사
echo "📏 Checking file sizes..."

LARGE_FILES=$(git diff --cached --name-only --diff-filter=ACM | xargs -I {} sh -c 'test -f "{}" && test $(wc -c < "{}") -gt 1048576 && echo "{}"' || true)

if [ -n "$LARGE_FILES" ]; then
    echo "❌ Large files (>1MB) detected:"
    echo "$LARGE_FILES"
    echo "Consider using Git LFS for large binary files"
    exit 1
fi

# 7. 라이선스 헤더 검사 (선택사항)
echo "⚖️  Checking license headers..."

CPP_FILES=$(git diff --cached --name-only --diff-filter=A | grep -E '\.(cpp|h)$' || true)
for file in $CPP_FILES; do
    if [ -f "$file" ] && ! head -10 "$file" | grep -q -i "license\|copyright"; then
        echo "⚠️  Warning: $file might be missing license header"
    fi
done

echo "✅ All pre-commit checks passed!"
EOF

# Pre-push hook 생성
cat > "$HOOKS_DIR/pre-push" << 'EOF'
#!/bin/bash
# Pre-push hook for Arduino projects

echo "🚀 Running pre-push checks..."

# 현재 브랜치 확인
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Pushing branch: $CURRENT_BRANCH"

# main 브랜치로 푸시하는 경우 추가 검사
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
    echo "🛡️  Extra checks for main branch..."
    
    # 빌드 테스트 실행 (Arduino CLI가 있는 경우)
    if command -v arduino-cli &> /dev/null; then
        echo "🔨 Running build test..."
        
        # Find Arduino sketches
        SKETCHES=$(find . -name "*.ino" -not -path "./.git/*")
        
        for sketch in $SKETCHES; do
            sketch_dir=$(dirname "$sketch")
            echo "Testing build for: $sketch"
            
            if ! arduino-cli compile --verify --fqbn arduino:avr:uno "$sketch_dir" >/dev/null 2>&1; then
                echo "❌ Build test failed for $sketch"
                echo "Cannot push to main branch with broken builds"
                exit 1
            fi
        done
        
        echo "✅ Build tests passed"
    fi
    
    # 단위 테스트 실행 (있는 경우)
    if [ -f "scripts/run-tests.sh" ]; then
        echo "🧪 Running unit tests..."
        if ! bash scripts/run-tests.sh; then
            echo "❌ Unit tests failed"
            echo "Cannot push to main branch with failing tests"
            exit 1
        fi
        echo "✅ Unit tests passed"
    fi
fi

# 원격 브랜치와 동기화 확인
echo "🔄 Checking if branch is up to date..."

git fetch origin >/dev/null 2>&1 || true

if git rev-list HEAD..origin/$CURRENT_BRANCH >/dev/null 2>&1; then
    BEHIND_COUNT=$(git rev-list --count HEAD..origin/$CURRENT_BRANCH 2>/dev/null || echo "0")
    if [ "$BEHIND_COUNT" -gt 0 ]; then
        echo "⚠️  Your branch is $BEHIND_COUNT commits behind origin/$CURRENT_BRANCH"
        echo "Consider pulling latest changes before pushing"
    fi
fi

echo "✅ Pre-push checks completed!"
EOF

# Commit-msg hook 생성
cat > "$HOOKS_DIR/commit-msg" << 'EOF'
#!/bin/bash
# Commit message hook for Arduino projects

COMMIT_MSG_FILE=$1
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

echo "📝 Validating commit message..."

# 커밋 메시지 길이 검사
FIRST_LINE=$(head -1 "$COMMIT_MSG_FILE")
if [ ${#FIRST_LINE} -gt 72 ]; then
    echo "❌ Commit message first line too long (${#FIRST_LINE} chars, max 72)"
    echo "Please shorten your commit message"
    exit 1
fi

# 커밋 메시지 형식 검사
COMMIT_REGEX='^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+ \[AIP-[0-9]+\]$|^Merge |^Revert '

if [[ ! $FIRST_LINE =~ $COMMIT_REGEX ]]; then
    echo "❌ Invalid commit message format"
    echo ""
    echo "Format: type(scope): description [AIP-XXX]"
    echo ""
    echo "Types:"
    echo "  feat:     새로운 기능"
    echo "  fix:      버그 수정"
    echo "  docs:     문서 변경"
    echo "  style:    코드 포맷팅 (기능 변경 없음)"
    echo "  refactor: 리팩토링"
    echo "  test:     테스트 추가 또는 수정"
    echo "  chore:    빌드 프로세스나 도구 변경"
    echo ""
    echo "Examples:"
    echo "  feat(sensor): add DHT22 temperature reading [AIP-123]"
    echo "  fix(wifi): resolve connection timeout issue [AIP-456]"
    echo "  docs: update README with setup instructions [AIP-789]"
    echo ""
    echo "Your message: $FIRST_LINE"
    exit 1
fi

# Jira 이슈 번호 추출 및 검증
JIRA_ISSUE=$(echo "$FIRST_LINE" | grep -o '\[AIP-[0-9]\+\]' | tr -d '[]')

if [ -n "$JIRA_ISSUE" ]; then
    echo "✅ Linked to Jira issue: $JIRA_ISSUE"
fi

echo "✅ Commit message format is valid"
EOF

# Post-commit hook 생성 (선택사항)
cat > "$HOOKS_DIR/post-commit" << 'EOF'
#!/bin/bash
# Post-commit hook for Arduino projects

COMMIT_HASH=$(git rev-parse HEAD)
COMMIT_MSG=$(git log -1 --pretty=%B)
BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "📝 Post-commit actions for $COMMIT_HASH"

# Jira 이슈 번호 추출
JIRA_ISSUE=$(echo "$COMMIT_MSG" | grep -o '\[AIP-[0-9]\+\]' | tr -d '[]')

if [ -n "$JIRA_ISSUE" ]; then
    echo "🔗 Linked to Jira issue: $JIRA_ISSUE"
    
    # TODO: Jira API 호출로 이슈 업데이트 (선택사항)
    # curl -X POST "https://your-jira.atlassian.net/rest/api/2/issue/$JIRA_ISSUE/comment" \
    #      -H "Content-Type: application/json" \
    #      -d "{\"body\": \"Commit: $COMMIT_HASH on branch $BRANCH\"}"
fi

# 빌드 상태 업데이트 (로컬 빌드 로그)
echo "$(date): $COMMIT_HASH - $COMMIT_MSG" >> .git/build-log.txt

echo "✅ Post-commit actions completed"
EOF

# 모든 hook 파일을 실행 가능하게 만들기
chmod +x "$HOOKS_DIR/pre-commit"
chmod +x "$HOOKS_DIR/pre-push"
chmod +x "$HOOKS_DIR/commit-msg"
chmod +x "$HOOKS_DIR/post-commit"

echo "✅ Git hooks installed successfully!"
echo ""
echo "📋 Installed hooks:"
echo "  - pre-commit:  코드 품질, 보안, 컴파일 검사"
echo "  - pre-push:    빌드 테스트 및 동기화 확인"
echo "  - commit-msg:  커밋 메시지 형식 검증"
echo "  - post-commit: 이슈 링크 및 로깅"
echo ""
echo "🎯 Next steps:"
echo "  1. Test the hooks by making a commit"
echo "  2. Ensure Arduino CLI is installed for compilation checks"
echo "  3. Configure Jira integration if needed"
echo ""
echo "ℹ️  To disable hooks temporarily: git commit --no-verify"