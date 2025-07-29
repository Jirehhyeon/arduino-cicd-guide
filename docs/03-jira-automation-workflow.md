# 🎯 Jira 이슈 관리 및 자동화 워크플로우

> AI 기반 지능형 프로젝트 관리 및 완전 자동화 워크플로우

## 📋 목차

1. [현대적 Jira 프로젝트 설정](#현대적-jira-프로젝트-설정)
2. [지능형 이슈 관리](#지능형-이슈-관리)
3. [자동화 룰 엔진](#자동화-룰-엔진)
4. [개발 워크플로우 통합](#개발-워크플로우-통합)
5. [AI 기반 예측 분석](#ai-기반-예측-분석)
6. [대시보드 및 리포팅](#대시보드-및-리포팅)

## 🏗️ 현대적 Jira 프로젝트 설정

### 애자일 프로젝트 구조
```json
{
  "project": {
    "key": "ARDUINO",
    "name": "Arduino IoT Project",
    "type": "software",
    "template": "scrum",
    "lead": "project.lead@company.com",
    "settings": {
      "issueTypes": [
        {
          "name": "Epic",
          "description": "대규모 기능 또는 프로젝트",
          "iconUrl": "/epic-icon.png",
          "color": "#0052CC"
        },
        {
          "name": "Story",
          "description": "사용자 스토리",
          "iconUrl": "/story-icon.png",
          "color": "#00875A"
        },
        {
          "name": "Task",
          "description": "개발 작업",
          "iconUrl": "/task-icon.png",
          "color": "#0747A6"
        },
        {
          "name": "Sub-task",
          "description": "하위 작업",
          "iconUrl": "/subtask-icon.png",
          "color": "#42526E"
        },
        {
          "name": "Bug",
          "description": "버그 수정",
          "iconUrl": "/bug-icon.png",
          "color": "#DE350B"
        },
        {
          "name": "Hotfix",
          "description": "긴급 수정",
          "iconUrl": "/hotfix-icon.png",
          "color": "#FF5630"
        }
      ],
      "priorities": [
        {
          "name": "Critical",
          "color": "#FF0000",
          "description": "시스템 다운, 보안 취약점"
        },
        {
          "name": "High",
          "color": "#FF6600",
          "description": "주요 기능 장애"
        },
        {
          "name": "Medium",
          "color": "#FFCC00",
          "description": "일반적인 개발 작업"
        },
        {
          "name": "Low",
          "color": "#00CC00",
          "description": "개선사항, 문서화"
        }
      ]
    }
  }
}
```

### 커스텀 필드 정의
```javascript
// Jira 커스텀 필드 스크립트
const customFields = [
    {
        name: "Hardware Platform",
        type: "select",
        options: ["Arduino Uno", "ESP32", "ESP8266", "Raspberry Pi"],
        required: true,
        description: "대상 하드웨어 플랫폼"
    },
    {
        name: "Firmware Version", 
        type: "text",
        pattern: "^v\\d+\\.\\d+\\.\\d+$",
        description: "대상 펌웨어 버전 (v1.0.0 형식)"
    },
    {
        name: "Test Coverage",
        type: "number",
        min: 0,
        max: 100,
        description: "테스트 커버리지 (%)"
    },
    {
        name: "Power Consumption",
        type: "text",
        description: "예상 전력 소비량 (mA)"
    },
    {
        name: "Memory Usage",
        type: "text", 
        description: "메모리 사용량 (KB)"
    },
    {
        name: "Git Branch",
        type: "text",
        readonly: true,
        description: "연결된 Git 브랜치 (자동 설정)"
    },
    {
        name: "Build Status",
        type: "select",
        options: ["Pending", "Building", "Success", "Failed"],
        readonly: true,
        description: "CI/CD 빌드 상태"
    },
    {
        name: "Deployment Environment",
        type: "multiselect",
        options: ["Development", "Staging", "Production"],
        description: "배포 대상 환경"
    }
];

// 커스텀 필드 생성 API 호출
customFields.forEach(field => {
    createJiraCustomField(field);
});

function createJiraCustomField(fieldConfig) {
    const payload = {
        name: fieldConfig.name,
        description: fieldConfig.description,
        type: fieldConfig.type,
        options: fieldConfig.options || null,
        required: fieldConfig.required || false,
        readonly: fieldConfig.readonly || false
    };
    
    // Jira REST API 호출
    fetch('/rest/api/3/field', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${JIRA_TOKEN}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });
}
```

### 워크플로우 설계
```yaml
# jira-workflow.yml
workflows:
  arduino_development:
    name: "Arduino Development Workflow"
    description: "IoT 프로젝트 전용 워크플로우"
    
    statuses:
      - id: "open"
        name: "To Do"
        category: "to-do"
        description: "작업 대기 중"
        
      - id: "in-analysis"
        name: "Analysis"
        category: "in-progress"
        description: "요구사항 분석 중"
        
      - id: "in-development"
        name: "In Development" 
        category: "in-progress"
        description: "개발 진행 중"
        
      - id: "code-review"
        name: "Code Review"
        category: "in-progress"
        description: "코드 리뷰 중"
        
      - id: "testing"
        name: "Testing"
        category: "in-progress"
        description: "테스트 진행 중"
        
      - id: "hardware-validation"
        name: "Hardware Validation"
        category: "in-progress"
        description: "하드웨어 검증 중"
        
      - id: "deployed"
        name: "Deployed"
        category: "done"
        description: "배포 완료"
        
      - id: "closed"
        name: "Done"
        category: "done"
        description: "작업 완료"

    transitions:
      - name: "Start Analysis"
        from: ["open"]
        to: "in-analysis"
        conditions:
          - assignee_present
        validators:
          - required_fields: ["Hardware Platform", "Firmware Version"]
          
      - name: "Start Development"
        from: ["in-analysis"]
        to: "in-development"
        post_functions:
          - create_git_branch
          - assign_to_developer
          
      - name: "Submit for Review"
        from: ["in-development"]
        to: "code-review"
        conditions:
          - git_branch_exists
          - pull_request_created
        post_functions:
          - trigger_build_pipeline
          - notify_reviewers
          
      - name: "Start Testing"
        from: ["code-review"]
        to: "testing"
        conditions:
          - code_review_approved
          - build_successful
        post_functions:
          - merge_to_develop
          - trigger_integration_tests
          
      - name: "Hardware Validation"
        from: ["testing"]
        to: "hardware-validation"
        conditions:
          - integration_tests_passed
        post_functions:
          - schedule_hardware_test

      - name: "Deploy"
        from: ["hardware-validation"]
        to: "deployed"
        conditions:
          - hardware_tests_passed
          - deployment_approved
        post_functions:
          - trigger_deployment
          - update_documentation
          
      - name: "Complete"
        from: ["deployed"]
        to: "closed"
        post_functions:
          - cleanup_branches
          - update_metrics
```

## 🤖 지능형 이슈 관리

### AI 기반 이슈 분류 시스템
```python
#!/usr/bin/env python3
# jira-ai-classifier.py

import re
import json
import requests
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import openai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib

class JiraAIClassifier:
    """AI 기반 Jira 이슈 분류 및 우선순위 예측"""
    
    def __init__(self, jira_url: str, jira_token: str, openai_key: str):
        self.jira_url = jira_url
        self.jira_token = jira_token
        self.openai = openai
        self.openai.api_key = openai_key
        
        # 사전 훈련된 모델 로드
        self.load_models()
        
    def load_models(self):
        """사전 훈련된 ML 모델 로드"""
        try:
            self.priority_model = joblib.load('models/priority_classifier.pkl')
            self.category_model = joblib.load('models/category_classifier.pkl') 
            self.vectorizer = joblib.load('models/tfidf_vectorizer.pkl')
        except FileNotFoundError:
            # 모델이 없으면 새로 훈련
            self.train_models()
    
    def analyze_issue(self, issue_data: Dict) -> Dict:
        """이슈 내용을 분석하여 메타데이터 추출"""
        
        title = issue_data.get('summary', '')
        description = issue_data.get('description', '')
        combined_text = f"{title} {description}"
        
        # AI 기반 분석
        analysis = self.ai_analyze_text(combined_text)
        
        # ML 기반 분류
        predicted_priority = self.predict_priority(combined_text)
        predicted_category = self.predict_category(combined_text)
        
        # 하드웨어 플랫폼 감지
        hardware_platform = self.detect_hardware_platform(combined_text)
        
        # 복잡도 추정
        complexity_score = self.estimate_complexity(combined_text, analysis)
        
        # 예상 작업 시간
        estimated_hours = self.estimate_effort(complexity_score, predicted_category)
        
        return {
            'priority': predicted_priority,
            'category': predicted_category,
            'hardware_platform': hardware_platform,
            'complexity_score': complexity_score,
            'estimated_hours': estimated_hours,
            'ai_analysis': analysis,
            'auto_tags': self.generate_tags(combined_text),
            'related_issues': self.find_related_issues(combined_text)
        }
    
    def ai_analyze_text(self, text: str) -> Dict:
        """OpenAI GPT를 사용한 텍스트 분석"""
        
        prompt = f"""
        다음 Arduino/IoT 프로젝트 이슈를 분석해주세요:
        
        {text}
        
        다음 JSON 형식으로 분석 결과를 제공해주세요:
        {{
            "issue_type": "bug|feature|improvement|task",
            "severity": "critical|high|medium|low", 
            "components": ["list", "of", "affected", "components"],
            "technical_complexity": "1-10 scale",
            "hardware_requirements": ["list", "of", "hardware"],
            "dependencies": ["list", "of", "dependencies"],
            "testing_requirements": ["unit", "integration", "hardware"],
            "documentation_needed": true/false,
            "security_impact": true/false,
            "performance_impact": true/false
        }}
        """
        
        try:
            response = self.openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 Arduino/IoT 프로젝트 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            analysis_text = response.choices[0].message.content
            return json.loads(analysis_text)
            
        except Exception as e:
            print(f"AI 분석 실패: {e}")
            return {"error": "AI 분석 실패"}
    
    def predict_priority(self, text: str) -> str:
        """ML 모델을 사용한 우선순위 예측"""
        
        # 키워드 기반 긴급도 판단
        critical_keywords = [
            'crash', 'down', 'fail', 'error', 'broken', 'critical',
            '작동안함', '오류', '장애', '크래시', '중단'
        ]
        
        high_keywords = [
            'bug', 'issue', 'problem', 'slow', 'performance',
            '버그', '문제', '느림', '성능'
        ]
        
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in critical_keywords):
            return 'Critical'
        elif any(keyword in text_lower for keyword in high_keywords):
            return 'High'
        else:
            # ML 모델 예측 사용
            if hasattr(self, 'priority_model'):
                text_vector = self.vectorizer.transform([text])
                prediction = self.priority_model.predict(text_vector)[0]
                return prediction
            else:
                return 'Medium'
    
    def detect_hardware_platform(self, text: str) -> List[str]:
        """하드웨어 플랫폼 자동 감지"""
        
        platforms = {
            'Arduino Uno': ['uno', 'arduino uno', 'atmega328'],
            'ESP32': ['esp32', 'esp-32', 'espressif'],
            'ESP8266': ['esp8266', 'esp-8266', 'nodemcu'],
            'Raspberry Pi': ['raspberry', 'raspi', 'rpi']
        }
        
        detected = []
        text_lower = text.lower()
        
        for platform, keywords in platforms.items():
            if any(keyword in text_lower for keyword in keywords):
                detected.append(platform)
                
        return detected if detected else ['Arduino Uno']  # 기본값
    
    def estimate_complexity(self, text: str, ai_analysis: Dict) -> int:
        """복잡도 점수 계산 (1-10)"""
        
        base_score = 3
        
        # 텍스트 길이에 따른 복잡도
        if len(text) > 1000:
            base_score += 2
        elif len(text) > 500:
            base_score += 1
            
        # AI 분석 결과 반영
        if ai_analysis.get('technical_complexity'):
            try:
                ai_score = int(ai_analysis['technical_complexity'])
                base_score = (base_score + ai_score) // 2
            except:
                pass
                
        # 키워드 기반 복잡도 조정
        complex_keywords = [
            'integration', 'api', 'database', 'network', 'protocol',
            'security', 'encryption', 'authentication',
            '통합', 'API', '데이터베이스', '네트워크', '보안'
        ]
        
        text_lower = text.lower()
        complexity_boost = sum(1 for keyword in complex_keywords if keyword in text_lower)
        
        final_score = min(10, base_score + complexity_boost)
        return max(1, final_score)
    
    def estimate_effort(self, complexity: int, category: str) -> float:
        """예상 작업 시간 계산 (시간)"""
        
        base_hours = {
            'bug': 4,
            'feature': 16,
            'improvement': 8,
            'task': 6
        }
        
        base = base_hours.get(category.lower(), 8)
        multiplier = complexity / 5.0
        
        estimated = base * multiplier
        
        # 반올림 (0.5 시간 단위)
        return round(estimated * 2) / 2
    
    def generate_tags(self, text: str) -> List[str]:
        """자동 태그 생성"""
        
        tag_patterns = {
            'sensor': ['sensor', 'temperature', 'humidity', 'pressure', '센서'],
            'wifi': ['wifi', 'wireless', 'network', '무선'],
            'bluetooth': ['bluetooth', 'ble', '블루투스'],
            'display': ['display', 'lcd', 'oled', 'screen', '디스플레이'],
            'motor': ['motor', 'servo', 'stepper', '모터'],
            'power': ['power', 'battery', 'voltage', '전원', '배터리'],
            'memory': ['memory', 'storage', 'eeprom', '메모리'],
            'communication': ['uart', 'spi', 'i2c', 'serial', '통신'],
            'security': ['security', 'encryption', 'auth', '보안'],
            'performance': ['performance', 'optimization', 'speed', '성능']
        }
        
        tags = []
        text_lower = text.lower()
        
        for tag, keywords in tag_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(tag)
                
        return tags
    
    def find_related_issues(self, text: str) -> List[str]:
        """관련 이슈 찾기"""
        
        # 벡터 유사도를 사용한 유사 이슈 검색
        try:
            jql = f'project = ARDUINO AND status != Closed'
            
            response = requests.get(
                f'{self.jira_url}/rest/api/3/search',
                headers={'Authorization': f'Bearer {self.jira_token}'},
                params={'jql': jql, 'maxResults': 50}
            )
            
            if response.status_code == 200:
                issues = response.json()['issues']
                
                # 텍스트 유사도 계산 (간단한 구현)
                related = []
                for issue in issues[:5]:  # 상위 5개만
                    issue_text = f"{issue['fields']['summary']} {issue['fields'].get('description', '')}"
                    similarity = self.calculate_similarity(text, issue_text)
                    
                    if similarity > 0.3:  # 임계값
                        related.append(issue['key'])
                        
                return related
                
        except Exception as e:
            print(f"관련 이슈 검색 실패: {e}")
            
        return []
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """두 텍스트 간 유사도 계산"""
        # 간단한 Jaccard 유사도 구현
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0

# 이슈 생성 시 자동 분류 실행
def auto_classify_issue(issue_key: str):
    """새 이슈 생성 시 자동 분류 실행"""
    
    classifier = JiraAIClassifier(
        jira_url=os.environ['JIRA_URL'],
        jira_token=os.environ['JIRA_TOKEN'], 
        openai_key=os.environ['OPENAI_API_KEY']
    )
    
    # 이슈 정보 조회
    issue_data = get_jira_issue(issue_key)
    
    # AI 분석 실행
    analysis = classifier.analyze_issue(issue_data)
    
    # 이슈 필드 업데이트
    update_fields = {
        'priority': {'name': analysis['priority']},
        'customfield_hardware_platform': analysis['hardware_platform'],
        'labels': analysis['auto_tags'],
        'timeoriginalestimate': int(analysis['estimated_hours'] * 3600)  # 초 단위
    }
    
    # 코멘트 추가
    comment = f"""
    🤖 **AI 자동 분석 결과**
    
    **우선순위**: {analysis['priority']}
    **예상 복잡도**: {analysis['complexity_score']}/10
    **예상 작업시간**: {analysis['estimated_hours']}시간
    **하드웨어 플랫폼**: {', '.join(analysis['hardware_platform'])}
    **자동 태그**: {', '.join(analysis['auto_tags'])}
    
    **AI 분석 요약**:
    - 이슈 유형: {analysis['ai_analysis'].get('issue_type', 'N/A')}
    - 기술적 복잡도: {analysis['ai_analysis'].get('technical_complexity', 'N/A')}/10
    - 보안 영향: {'있음' if analysis['ai_analysis'].get('security_impact') else '없음'}
    - 성능 영향: {'있음' if analysis['ai_analysis'].get('performance_impact') else '없음'}
    
    _이 분석은 AI에 의해 자동 생성되었습니다. 필요시 수정해 주세요._
    """
    
    update_jira_issue(issue_key, update_fields, comment)
    
    print(f"✅ 이슈 {issue_key} 자동 분류 완료")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        auto_classify_issue(sys.argv[1])
```

## ⚙️ 자동화 룰 엔진

### Jira Automation Rules
```yaml
# jira-automation-rules.yml
automation_rules:
  
  # 1. 새 이슈 생성 시 자동 분류
  - name: "Auto-classify New Issues"
    trigger:
      type: "issue_created"
      projects: ["ARDUINO"]
    conditions:
      - issue_type: ["Story", "Task", "Bug"]
    actions:
      - type: "webhook"
        url: "https://automation.company.com/jira/auto-classify"
        method: "POST"
        headers:
          Authorization: "Bearer {{secrets.automation_token}}"
        body: |
          {
            "issueKey": "{{issue.key}}",
            "summary": "{{issue.summary}}",
            "description": "{{issue.description}}",
            "reporter": "{{issue.reporter.emailAddress}}"
          }
  
  # 2. Git 브랜치 자동 생성
  - name: "Auto-create Git Branch"
    trigger:
      type: "issue_transitioned"
      from_status: ["To Do"]
      to_status: ["In Development"]
    conditions:
      - field_value:
          field: "assignee"
          operator: "is_not_empty"
    actions:
      - type: "webhook" 
        url: "https://bitbucket.company.com/webhook/create-branch"
        method: "POST"
        body: |
          {
            "repository": "arduino-iot-project",
            "branchName": "feature/{{issue.key}}-{{issue.summary | slugify}}",
            "sourceRef": "develop",
            "assignee": "{{issue.assignee.emailAddress}}"
          }
      - type: "edit_issue"
        fields:
          customfield_git_branch: "feature/{{issue.key}}-{{issue.summary | slugify}}"
      - type: "comment"
        body: |
          🌿 **Git 브랜치 자동 생성**
          
          브랜치명: `feature/{{issue.key}}-{{issue.summary | slugify}}`
          
          개발을 시작하려면:
          ```bash
          git fetch origin
          git checkout feature/{{issue.key}}-{{issue.summary | slugify}}
          ```
  
  # 3. 빌드 상태 자동 업데이트
  - name: "Update Build Status"
    trigger:
      type: "webhook"
      endpoint: "/build-status-update"
    conditions:
      - webhook_data:
          field: "buildStatus" 
          operator: "in"
          values: ["SUCCESS", "FAILED", "UNSTABLE"]
    actions:
      - type: "edit_issue"
        issue_key: "{{webhookData.issueKey}}"
        fields:
          customfield_build_status: "{{webhookData.buildStatus}}"
      - type: "comment"
        issue_key: "{{webhookData.issueKey}}"
        body: |
          🏗️ **빌드 상태 업데이트**
          
          **상태**: {{webhookData.buildStatus}}
          **빌드 번호**: #{{webhookData.buildNumber}}
          **브랜치**: {{webhookData.branch}}
          **소요시간**: {{webhookData.duration}}
          
          {{#if webhookData.buildStatus == "FAILED"}}
          ❌ **빌드 실패**
          **실패 원인**: {{webhookData.failureReason}}
          **로그 링크**: [빌드 로그 보기]({{webhookData.buildUrl}})
          {{/if}}
          
          {{#if webhookData.buildStatus == "SUCCESS"}}
          ✅ **빌드 성공**
          **아티팩트**: [다운로드]({{webhookData.artifactUrl}})
          {{/if}}
  
  # 4. 자동 테스터 할당
  - name: "Auto-assign Tester"
    trigger:
      type: "issue_transitioned"
      from_status: ["Code Review"]
      to_status: ["Testing"]
    conditions:
      - field_value:
          field: "customfield_build_status"
          operator: "equals"
          value: "SUCCESS"
    actions:
      - type: "assign_user"
        user: "{{project.qa_lead}}"
      - type: "comment"
        body: |
          🧪 **테스트 단계로 이동**
          
          {{project.qa_lead.displayName}}님에게 자동 할당되었습니다.
          
          **테스트 체크리스트**:
          - [ ] 기능 테스트 완료
          - [ ] 회귀 테스트 실행
          - [ ] 하드웨어 호환성 확인
          - [ ] 성능 테스트 수행
          - [ ] 문서 업데이트 확인
          
          테스트 완료 시 "Hardware Validation" 단계로 이동해 주세요.
  
  # 5. 배포 승인 워크플로우
  - name: "Deployment Approval Workflow"
    trigger:
      type: "issue_transitioned"
      from_status: ["Hardware Validation"]
      to_status: ["Ready for Deployment"]
    conditions:
      - field_value:
          field: "priority"
          operator: "in"
          values: ["Critical", "High"]
    actions:
      - type: "create_subtask"
        summary: "배포 승인 요청 - {{issue.summary}}"
        issue_type: "Approval"
        assignee: "{{project.release_manager}}"
        description: |
          **배포 승인 요청**
          
          **원본 이슈**: {{issue.key}} - {{issue.summary}}
          **우선순위**: {{issue.priority.name}}
          **대상 환경**: {{issue.customfield_deployment_environment}}
          **하드웨어 플랫폼**: {{issue.customfield_hardware_platform}}
          
          **변경 사항**:
          {{issue.description}}
          
          **테스트 결과**:
          - 빌드 상태: ✅ SUCCESS
          - 하드웨어 검증: ✅ PASSED
          - 테스트 커버리지: {{issue.customfield_test_coverage}}%
          
          **승인 후 작업**:
          1. 프로덕션 배포 실행
          2. 모니터링 설정
          3. 롤백 계획 준비
      - type: "transition_issue"
        transition: "Pending Approval"
  
  # 6. SLA 모니터링 및 에스컬레이션
  - name: "SLA Monitoring and Escalation"
    trigger:
      type: "scheduled"
      schedule: "0 */4 * * *"  # 4시간마다
    conditions:
      - jql: |
          project = ARDUINO 
          AND status IN ("To Do", "In Progress", "Code Review", "Testing")
          AND priority IN ("Critical", "High")
          AND created < -1d
    actions:
      - type: "comment"
        body: |
          ⚠️ **SLA 알림**
          
          이 이슈가 24시간 이상 진행 중입니다.
          
          **현재 상태**: {{issue.status.name}}
          **우선순위**: {{issue.priority.name}}
          **생성일**: {{issue.created | date("yyyy-MM-dd HH:mm")}}
          **담당자**: {{issue.assignee.displayName}}
          
          빠른 처리를 위해 확인해 주세요.
      - type: "send_email"
        to: ["{{issue.assignee.emailAddress}}", "{{project.lead.emailAddress}}"]
        subject: "SLA 알림: {{issue.key}} - {{issue.summary}}"
        body: |
          고우선순위 이슈가 24시간 이상 지연되고 있습니다.
          
          이슈 링크: {{baseUrl}}/browse/{{issue.key}}
          
          즉시 확인하여 처리해 주세요.
  
  # 7. 자동 문서화
  - name: "Auto-generate Documentation"
    trigger:
      type: "issue_transitioned"
      to_status: ["Done"]
    conditions:
      - field_value:
          field: "issuetype"
          operator: "equals"
          value: "Story"
      - field_value:
          field: "customfield_documentation_needed"
          operator: "equals"
          value: true
    actions:
      - type: "create_subtask"
        summary: "문서 업데이트 - {{issue.summary}}"
        issue_type: "Task"
        assignee: "{{issue.assignee.emailAddress}}"
        description: |
          **문서 업데이트 작업**
          
          다음 문서들을 업데이트해 주세요:
          
          1. **API 문서** (해당 시)
             - 새 엔드포인트 추가
             - 파라미터 및 응답 형식 문서화
          
          2. **사용자 가이드**
             - 새 기능 사용법 추가
             - 스크린샷 업데이트
          
          3. **기술 문서**
             - 아키텍처 다이어그램 업데이트
             - 설정 가이드 수정
          
          4. **README.md**
             - 설치/실행 가이드 업데이트
             - 의존성 정보 확인
          
          **참고 이슈**: {{issue.key}} - {{issue.summary}}
```

### 고급 자동화 스크립트
```javascript
// jira-advanced-automation.js
const JiraApi = require('jira-client');
const { WebhookClient } = require('discord.js');
const moment = require('moment');

class JiraAdvancedAutomation {
    constructor(config) {
        this.jira = new JiraApi({
            protocol: 'https',
            host: config.jiraHost,
            apiVersion: '3',
            strictSSL: true,
            bearer: config.jiraToken
        });
        
        this.discordWebhook = new WebhookClient({
            url: config.discordWebhookUrl
        });
        
        this.slackWebhook = config.slackWebhookUrl;
    }
    
    // 스프린트 자동 관리
    async autoManageSprints() {
        try {
            const activeBoards = await this.jira.getAllBoards();
            
            for (const board of activeBoards.values) {
                if (board.name.includes('Arduino')) {
                    const sprints = await this.jira.getAllSprints(board.id);
                    const activeSprint = sprints.values.find(s => s.state === 'active');
                    
                    if (activeSprint) {
                        await this.checkSprintHealth(activeSprint, board);
                        await this.suggestSprintAdjustments(activeSprint, board);
                    }
                }
            }
        } catch (error) {
            console.error('스프린트 자동 관리 오류:', error);
        }
    }
    
    async checkSprintHealth(sprint, board) {
        const sprintIssues = await this.jira.getIssuesForSprint(sprint.id);
        const totalStoryPoints = sprintIssues.issues.reduce((sum, issue) => {
            return sum + (issue.fields.customfield_story_points || 0);
        }, 0);
        
        const completedStoryPoints = sprintIssues.issues
            .filter(issue => issue.fields.status.statusCategory.key === 'done')
            .reduce((sum, issue) => {
                return sum + (issue.fields.customfield_story_points || 0);
            }, 0);
        
        const sprintProgress = completedStoryPoints / totalStoryPoints;
        const daysRemaining = moment(sprint.endDate).diff(moment(), 'days');
        const sprintDuration = moment(sprint.endDate).diff(moment(sprint.startDate), 'days');
        const timeProgress = (sprintDuration - daysRemaining) / sprintDuration;
        
        // 진행률이 시간 진행률보다 20% 이상 뒤처지면 알림
        if (sprintProgress < timeProgress - 0.2) {
            await this.sendSprintAlert(sprint, {
                type: 'BEHIND_SCHEDULE',
                sprintProgress: Math.round(sprintProgress * 100),
                timeProgress: Math.round(timeProgress * 100),
                daysRemaining
            });
        }
        
        // 번다운 차트 업데이트
        await this.updateBurndownChart(sprint, sprintProgress, timeProgress);
    }
    
    // 이슈 예측 분석
    async predictIssueMetrics() {
        try {
            // 최근 6개월 데이터 수집
            const sixMonthsAgo = moment().subtract(6, 'months').format('YYYY-MM-DD');
            const jql = `project = ARDUINO AND created >= "${sixMonthsAgo}"`;
            
            const issues = await this.jira.searchJira(jql, {
                maxResults: 1000,
                fields: ['created', 'resolutiondate', 'priority', 'issuetype', 'status']
            });
            
            // 패턴 분석
            const patterns = this.analyzeIssuePatterns(issues.issues);
            
            // 예측 모델 실행
            const predictions = this.generatePredictions(patterns);
            
            // 대시보드 업데이트
            await this.updatePredictionDashboard(predictions);
            
            return predictions;
            
        } catch (error) {
            console.error('이슈 예측 분석 오류:', error);
        }
    }
    
    analyzeIssuePatterns(issues) {
        const patterns = {
            creationTrends: {},
            resolutionTimes: {},
            priorityDistribution: {},
            typeDistribution: {}
        };
        
        issues.forEach(issue => {
            const created = moment(issue.fields.created);
            const month = created.format('YYYY-MM');
            
            // 생성 트렌드
            patterns.creationTrends[month] = (patterns.creationTrends[month] || 0) + 1;
            
            // 해결 시간
            if (issue.fields.resolutiondate) {
                const resolved = moment(issue.fields.resolutiondate);
                const resolutionTime = resolved.diff(created, 'hours');
                
                const priority = issue.fields.priority?.name || 'Medium';
                if (!patterns.resolutionTimes[priority]) {
                    patterns.resolutionTimes[priority] = [];
                }
                patterns.resolutionTimes[priority].push(resolutionTime);
            }
            
            // 우선순위 분포
            const priority = issue.fields.priority?.name || 'Medium';
            patterns.priorityDistribution[priority] = (patterns.priorityDistribution[priority] || 0) + 1;
            
            // 타입 분포
            const type = issue.fields.issuetype?.name || 'Task';
            patterns.typeDistribution[type] = (patterns.typeDistribution[type] || 0) + 1;
        });
        
        return patterns;
    }
    
    generatePredictions(patterns) {
        const predictions = {};
        
        // 다음 달 이슈 수 예측 (단순 이동평균)
        const recentMonths = Object.keys(patterns.creationTrends)
            .sort()
            .slice(-3)
            .map(month => patterns.creationTrends[month]);
        
        predictions.nextMonthIssues = Math.round(
            recentMonths.reduce((a, b) => a + b, 0) / recentMonths.length
        );
        
        // 평균 해결 시간 예측
        predictions.avgResolutionTimes = {};
        Object.keys(patterns.resolutionTimes).forEach(priority => {
            const times = patterns.resolutionTimes[priority];
            predictions.avgResolutionTimes[priority] = Math.round(
                times.reduce((a, b) => a + b, 0) / times.length
            );
        });
        
        // 리소스 필요량 예측
        predictions.resourceNeeds = this.calculateResourceNeeds(patterns);
        
        return predictions;
    }
    
    // 자동 리포트 생성
    async generateWeeklyReport() {
        const lastWeek = moment().subtract(7, 'days').format('YYYY-MM-DD');
        const jql = `project = ARDUINO AND updated >= "${lastWeek}"`;
        
        const issues = await this.jira.searchJira(jql, {
            maxResults: 500,
            fields: ['summary', 'status', 'assignee', 'priority', 'created', 'updated']
        });
        
        const report = {
            period: `${moment().subtract(7, 'days').format('YYYY-MM-DD')} ~ ${moment().format('YYYY-MM-DD')}`,
            totalIssues: issues.issues.length,
            newIssues: issues.issues.filter(i => moment(i.fields.created).isAfter(moment().subtract(7, 'days'))).length,
            closedIssues: issues.issues.filter(i => i.fields.status.statusCategory.key === 'done').length,
            inProgressIssues: issues.issues.filter(i => i.fields.status.statusCategory.key === 'indeterminate').length,
            highPriorityIssues: issues.issues.filter(i => ['Critical', 'High'].includes(i.fields.priority?.name)).length,
            topContributors: this.getTopContributors(issues.issues),
            trends: await this.calculateTrends()
        };
        
        // 리포트 전송
        await this.sendWeeklyReport(report);
        
        return report;
    }
    
    async sendWeeklyReport(report) {
        const reportMessage = `
📊 **Arduino 프로젝트 주간 리포트** (${report.period})

**📈 이슈 현황**
• 전체 이슈: ${report.totalIssues}개
• 신규 이슈: ${report.newIssues}개
• 완료된 이슈: ${report.closedIssues}개  
• 진행 중 이슈: ${report.inProgressIssues}개
• 높은 우선순위: ${report.highPriorityIssues}개

**🏆 주요 기여자**
${report.topContributors.slice(0, 3).map((contributor, index) => 
    `${index + 1}. ${contributor.name} (${contributor.count}개 이슈)`
).join('\n')}

**📊 트렌드 분석**
• 이슈 생성률: ${report.trends.creationRate > 0 ? '📈' : '📉'} ${Math.abs(report.trends.creationRate)}%
• 해결률: ${report.trends.resolutionRate > 0 ? '📈' : '📉'} ${Math.abs(report.trends.resolutionRate)}%
• 평균 해결 시간: ${report.trends.avgResolutionTime}시간

---
_자동 생성된 리포트입니다._
        `;
        
        // Discord 알림
        await this.discordWebhook.send({
            content: reportMessage,
            username: 'Jira Bot',
            avatarURL: 'https://jira-icon.png'
        });
        
        // Slack 알림 (Webhook 사용)
        await fetch(this.slackWebhook, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: reportMessage,
                channel: '#project-updates',
                username: 'Jira Bot'
            })
        });
    }
}

// 주기적 실행을 위한 스케줄러
const cron = require('node-cron');

const automation = new JiraAdvancedAutomation({
    jiraHost: process.env.JIRA_HOST,
    jiraToken: process.env.JIRA_TOKEN,
    discordWebhookUrl: process.env.DISCORD_WEBHOOK_URL,
    slackWebhookUrl: process.env.SLACK_WEBHOOK_URL
});

// 매일 오전 9시 스프린트 체크
cron.schedule('0 9 * * *', () => {
    automation.autoManageSprints();
});

// 매주 월요일 오전 10시 주간 리포트
cron.schedule('0 10 * * 1', () => {
    automation.generateWeeklyReport();
});

// 매시간 예측 분석 업데이트
cron.schedule('0 * * * *', () => {
    automation.predictIssueMetrics();
});

module.exports = JiraAdvancedAutomation;
```

---

**다음 단계**: [전체 개발 프로세스 통합 및 문서 구조화](04-integrated-development-process.md)