# 🎯 Step 1: Jira 프로젝트 관리 마스터하기

> **"아두이노 프로젝트를 전문적으로 관리하는 Jira 활용법"**

**⏱️ 예상 소요시간: 60-90분**  
**🎯 목표: Jira를 사용하여 아두이노 프로젝트의 완전한 이슈 관리 시스템 구축**  
**📋 사전 요구사항: Atlassian 계정 및 Jira 워크스페이스**

## 📚 이번 단계에서 배울 것들

- ✅ Jira 프로젝트 생성 및 설정
- ✅ 아두이노 프로젝트에 맞는 이슈 타입 커스터마이징  
- ✅ 스마트 온실 모니터링 시스템 프로젝트 계획
- ✅ 스프린트 기반 애자일 프로젝트 관리
- ✅ 자동화를 위한 API 설정

---

## 🏗️ Phase 1: Jira 프로젝트 생성

### 1.1 워크스페이스 접속 및 첫 프로젝트 생성

#### 📱 **단계별 실행**

**1. Jira 워크스페이스 접속**
```
URL: https://your-site.atlassian.net
(예: https://arduino-cicd.atlassian.net)
```

**2. 새 프로젝트 생성**
```
1. 좌측 사이드바에서 "Projects" 클릭
2. "Create project" 버튼 클릭 (우측 상단 파란 버튼)
3. "Use a template" 섹션에서 "Scrum" 선택
4. "Use template" 버튼 클릭
```

![프로젝트 생성 스크린샷 설명]
```
💡 스크린샷 가이드:
- "Scrum" 템플릿: 스프린트 기반 개발에 최적화
- "Kanban" 대신 "Scrum" 선택하는 이유: 정해진 기간 내 목표 달성
```

**3. 프로젝트 정보 입력**
```
Project name: Smart Greenhouse Monitor
Key: SGM
Project type: Team-managed project
```

**✅ 입력값 상세 설명:**
- **Project name**: 프로젝트의 전체 이름 (한글도 가능: "스마트 온실 모니터링")
- **Key**: 이슈 번호 앞에 붙는 접두사 (SGM-1, SGM-2, ... 형태로 생성됨)
- **Project type**: "Team-managed"는 소규모 팀에 적합, 더 유연한 설정 가능

**4. 프로젝트 템플릿 완료**
```
1. "Create project" 버튼 클릭
2. 자동으로 생성된 프로젝트 대시보드 확인
3. 샘플 이슈들이 자동으로 생성된 것 확인
```

### 1.2 프로젝트 기본 설정

#### **프로젝트 상세 정보 설정**

**1. 프로젝트 설정 접근**
```
1. 좌측 사이드바 하단 "Project settings" 클릭
2. "Details" 메뉴 선택
```

**2. 프로젝트 정보 업데이트**
```
Name: Smart Greenhouse Monitor
Key: SGM
Category: Development
Lead: [본인 이름]
Default assignee: Project lead
Description: 
"IoT 기반 스마트 온실 모니터링 시스템 개발 프로젝트.
온도, 습도, 토양 수분, 조도 센서를 활용한 자동화 시스템 구축."
```

**3. 아바타 및 색상 설정**
```
1. 프로젝트 아바타 업로드 (선택사항)
   - 온실/식물 관련 이미지 권장
2. 프로젝트 색상: 녹색 계열 선택 (온실 테마)
```

---

## 🏷️ Phase 2: 아두이노 프로젝트 맞춤 이슈 타입 설정

### 2.1 기본 이슈 타입 이해

**기본 제공 이슈 타입:**
- 📋 **Story**: 사용자 관점의 기능 요구사항
- 🔧 **Task**: 개발 작업 단위
- 🐛 **Bug**: 버그 및 오류 수정
- 📚 **Epic**: 큰 기능 묶음 (여러 Story를 포함)

### 2.2 하드웨어 프로젝트 전용 이슈 타입 추가

#### **커스텀 이슈 타입 생성**

**1. 이슈 타입 설정 접근**
```
1. Project settings → Features → Issue types
2. "Add issue type" 클릭
```

**2. 하드웨어 이슈 타입 생성**

**🔧 Hardware Task**
```
Name: Hardware Task
Description: 하드웨어 설계, 회로 구성, 센서 설치 등 물리적 작업
Icon: 🔧 (또는 기본 아이콘 사용)
```

**⚡ Firmware**
```
Name: Firmware
Description: 아두이노 스케치 및 펌웨어 개발 작업
Icon: ⚡
```

**🌐 Integration**
```
Name: Integration
Description: 하드웨어-소프트웨어 통합 및 시스템 연동 작업  
Icon: 🌐
```

**🧪 Testing**
```
Name: Testing
Description: 하드웨어 테스트, 센서 검증, 시스템 테스트
Icon: 🧪
```

#### **이슈 타입 생성 단계**
```
1. "Add issue type" 클릭
2. 이슈 타입 이름 입력
3. 설명 입력
4. 아이콘 선택 (이모지 복사-붙여넣기 가능)
5. "Add" 버튼 클릭
6. 각 이슈 타입에 대해 반복
```

### 2.3 커스텀 필드 추가

#### **하드웨어 프로젝트용 커스텀 필드**

**1. 커스텀 필드 설정 접근**
```
Project settings → Features → Fields
"Create field" 클릭
```

**2. 필수 커스텀 필드들**

**🔧 Hardware Component**
```
Field Type: Select List (single choice)
Field Name: Hardware Component
Description: 관련된 하드웨어 컴포넌트
Options:
- Arduino Board
- DHT22 Sensor  
- Soil Moisture Sensor
- Light Sensor
- Relay Module
- LED Strip
- Water Pump
- Power Supply
- Wiring/Breadboard
```

**📊 Complexity Level**
```
Field Type: Select List (single choice)
Field Name: Complexity Level
Description: 작업의 기술적 복잡도
Options:
- Simple (1-2시간)
- Medium (반나절)
- Complex (1일)
- Very Complex (2일+)
```

**🎯 Test Environment**
```
Field Type: Select List (single choice)
Field Name: Test Environment
Description: 테스트 환경
Options:
- Breadboard
- PCB Prototype
- Final Assembly
- Simulation Only
```

**⚠️ Safety Level**
```
Field Type: Select List (single choice) 
Field Name: Safety Level
Description: 안전 고려사항 레벨
Options:
- Low (5V 저전압)
- Medium (12V)
- High (AC 전원 관련)
- Critical (수분+전기)
```

#### **커스텀 필드 생성 과정**
```
1. "Create field" 클릭
2. Field type 선택 (대부분 "Select List" 사용)
3. Field name 입력
4. Description 입력  
5. Options 추가 (각 옵션별로 "Add option" 클릭)
6. "Create" 버튼 클릭
7. 어떤 이슈 타입에서 사용할지 선택
```

---

## 📋 Phase 3: 스마트 온실 프로젝트 계획 수립

### 3.1 Epic 구조 설계

#### **프로젝트 Epic 계층 구조**

**🌿 Epic 1: 센서 시스템 (SGM-1)**
```
Title: 환경 센서 모니터링 시스템
Description: 온실 내부 환경을 실시간으로 모니터링하는 센서 시스템 구축
Expected Timeline: Sprint 1-2 (4주)
Business Value: 기본 모니터링 기능 제공
```

**💧 Epic 2: 자동 제어 시스템 (SGM-2)**  
```
Title: 자동 급수 및 조명 제어
Description: 센서 데이터 기반 자동 급수 및 LED 조명 제어 시스템
Expected Timeline: Sprint 2-3 (4주)
Business Value: 자동화를 통한 관리 효율성 증대
```

**📱 Epic 3: 모니터링 대시보드 (SGM-3)**
```
Title: 웹 기반 모니터링 대시보드
Description: 실시간 데이터 시각화 및 원격 제어 웹 인터페이스
Expected Timeline: Sprint 3-4 (4주)  
Business Value: 원격 모니터링 및 제어 기능
```

**🔔 Epic 4: 알림 및 자동화 (SGM-4)**
```
Title: 스마트 알림 및 고급 자동화
Description: 위험 상황 알림, 예측 분석, 고급 자동화 기능
Expected Timeline: Sprint 4-5 (4주)
Business Value: 예방적 관리 및 고도화
```

#### **Epic 생성 실습**

**1. 첫 번째 Epic 생성**
```
1. 프로젝트 메인 화면에서 "Create" 버튼 클릭
2. Issue Type: "Epic" 선택
3. Summary: "환경 센서 모니터링 시스템"
4. Description: 
   "온실 내부의 온도, 습도, 토양 수분, 조도를 실시간으로 
    모니터링하는 센서 시스템을 구축합니다.
    
   주요 기능:
   - DHT22 센서를 통한 온도/습도 측정
   - 토양 수분 센서를 통한 수분 모니터링  
   - 조도 센서를 통한 광량 측정
   - 시리얼 통신을 통한 데이터 출력
   - 기본적인 에러 핸들링"
5. Epic Name: "센서 시스템" (Epic 전용 필드)
6. "Create" 버튼 클릭
```

### 3.2 Story 및 Task 세분화

#### **Epic 1의 하위 Story들**

**📊 Story: 온도/습도 센서 구현 (SGM-5)**
```
Summary: 사용자가 실시간 온도와 습도를 확인할 수 있다
Story Points: 5
Priority: Highest

Acceptance Criteria:
- DHT22 센서에서 온도 데이터를 읽을 수 있어야 함
- DHT22 센서에서 습도 데이터를 읽을 수 있어야 함  
- 센서 오류 시 적절한 에러 메시지 표시
- 1초마다 데이터 업데이트
- 시리얼 모니터에 읽기 가능한 형태로 출력

Epic Link: SGM-1 (환경 센서 모니터링 시스템)
```

**💧 Story: 토양 수분 센서 구현 (SGM-6)**
```
Summary: 사용자가 토양의 수분 상태를 확인할 수 있다
Story Points: 3
Priority: High

Acceptance Criteria:
- 토양 수분 센서에서 아날로그 값을 읽을 수 있어야 함
- 센서 값을 백분율(%)로 변환하여 표시
- 수분 부족 시 경고 표시 (30% 미만)
- 센서 보정 기능 포함

Epic Link: SGM-1
Hardware Component: Soil Moisture Sensor
Complexity Level: Simple
```

#### **Story 하위의 개발 Task들**

**⚡ Task: DHT22 라이브러리 통합 (SGM-7)**
```
Summary: DHT22 센서 라이브러리 통합 및 기본 설정
Parent: SGM-5 (온도/습도 센서 구현)
Story Points: 2
Assignee: [본인]

Description:
"DHT sensor library를 프로젝트에 통합하고 기본 센서 읽기 기능을 구현합니다."

Subtasks:
1. DHT sensor library 설치 확인
2. 센서 핀 연결 및 초기화 코드 작성
3. 기본 온도/습도 읽기 함수 구현
4. 단위 테스트 코드 작성

Hardware Component: DHT22 Sensor
Complexity Level: Simple
```

**🔧 Hardware Task: 센서 회로 설계 (SGM-8)**
```
Summary: DHT22 및 토양 수분 센서 회로 연결
Parent: SGM-5
Story Points: 1

Description:
"센서들을 아두이노에 연결하는 회로를 설계하고 브레드보드에 구현합니다."

Hardware Components: 
- Arduino Board
- DHT22 Sensor  
- Soil Moisture Sensor

Safety Level: Low
Test Environment: Breadboard
```

### 3.3 실제 이슈 생성 실습

#### **Step-by-Step 이슈 생성**

**1. Story 생성**
```
1. "Create" 버튼 클릭
2. Issue Type: "Story" 선택
3. Summary 입력: "사용자가 실시간 온도와 습도를 확인할 수 있다"
4. Description에 Acceptance Criteria 입력
5. Epic Link: 생성한 Epic 선택 (SGM-1)
6. Hardware Component: "DHT22 Sensor" 선택
7. Complexity Level: "Medium" 선택
8. Priority: "Highest" 선택
9. "Create" 버튼 클릭
```

**2. Task 생성 (Story의 하위 작업)**
```
1. 방금 생성한 Story (SGM-5) 클릭하여 상세 페이지 접근
2. "Create subtask" 클릭 또는 "More" → "Create subtask"
3. Issue Type: "Task" 선택
4. Summary: "DHT22 라이브러리 통합 및 기본 설정"
5. Description에 상세 작업 내용 입력
6. 나머지 필드들 설정
7. "Create" 버튼 클릭
```

---

## 🏃‍♂️ Phase 4: 스프린트 계획 및 시작

### 4.1 첫 번째 스프린트 계획

#### **Sprint 1: 기본 센서 시스템 (2주)**

**스프린트 목표:**
```
"온실의 기본 환경 데이터(온도, 습도, 토양수분)를 
아두이노로 수집하고 시리얼 모니터로 출력하는 시스템 완성"
```

**포함될 이슈들:**
- SGM-5: 온도/습도 센서 구현 (Story, 5 points)
- SGM-6: 토양 수분 센서 구현 (Story, 3 points)  
- SGM-7: DHT22 라이브러리 통합 (Task, 2 points)
- SGM-8: 센서 회로 설계 (Hardware Task, 1 point)
- SGM-9: 센서 데이터 출력 포맷 설계 (Task, 2 points)

**총 Story Points: 13점** (2주 스프린트에 적절)

#### **스프린트 생성 실습**

**1. 백로그 접근**
```
1. 좌측 사이드바에서 "Backlog" 클릭
2. 생성된 이슈들이 "Backlog" 섹션에 표시됨 확인
```

**2. 새 스프린트 생성**
```
1. "Create sprint" 버튼 클릭 (백로그 상단)
2. Sprint name: "Sprint 1 - 기본 센서 시스템"
3. Duration: 2 weeks
4. Goal: "기본 환경 센서 데이터 수집 시스템 구축"
```

**3. 스프린트에 이슈 할당**
```
1. 백로그에서 이슈들을 드래그앤드롭으로 스프린트 섹션으로 이동
2. 또는 이슈 체크박스 선택 후 "Move to sprint" 클릭
3. 총 스토리 포인트가 13점인지 확인
```

**4. 스프린트 시작**
```
1. 스프린트 섹션의 "Start sprint" 버튼 클릭
2. Start date: 오늘 날짜
3. End date: 2주 후 날짜
4. Sprint goal 재확인
5. "Start" 버튼 클릭
```

### 4.2 칸반 보드 활용

#### **Active Sprint 보드 확인**

**1. 스프린트 보드 접근**
```
좌측 사이드바 "Active sprints" 클릭
```

**2. 칸반 보드 컬럼 이해**
```
TO DO: 아직 시작하지 않은 작업
IN PROGRESS: 현재 진행 중인 작업  
DONE: 완료된 작업
```

**3. 이슈 상태 변경 연습**
```
1. 첫 번째 Task (SGM-7) 선택
2. 드래그앤드롭으로 "IN PROGRESS"로 이동
3. 이슈 상세에서 "Assign to me" 클릭
4. 작업 시작 시간 기록됨 확인
```

### 4.3 이슈 작업 및 업데이트

#### **이슈 작업 프로세스**

**1. 작업 시작**
```
1. SGM-7 (DHT22 라이브러리 통합) 이슈 클릭
2. "Start progress" 버튼 클릭 또는 드래그앤드롭으로 IN PROGRESS 이동
3. "Assign to me" 클릭
4. Work log 추가: "작업 시작 - 라이브러리 설치 중"
```

**2. 진행상황 업데이트**
```
1. 이슈 상세 페이지에서 "Add a comment" 클릭
2. 진행상황 입력:
   "DHT sensor library 설치 완료. 
   센서 초기화 코드 작성 중.
   예상 완료: 오늘 오후"
3. "Save" 클릭
```

**3. 작업 완료**
```
1. 작업 완료 후 이슈를 "DONE"으로 이동
2. Resolution: "Done" 선택
3. Comment 추가: "DHT22 라이브러리 통합 완료. 온도/습도 읽기 기능 동작 확인"
4. Time tracking: 실제 소요 시간 기록 (예: 2h 30m)
```

---

## 🔗 Phase 5: Jenkins 연동을 위한 API 설정

### 5.1 Jira API 토큰 생성

#### **API 토큰 생성 단계**

**1. Atlassian 계정 설정 접근**
```
1. 우측 상단 프로필 아이콘 클릭
2. "Manage account" 선택
3. "Security" 탭 클릭
4. "Create and manage API tokens" 클릭
```

**2. API 토큰 생성**
```
1. "Create API token" 버튼 클릭
2. Label: "Jenkins Integration"
3. "Create" 버튼 클릭
4. 생성된 토큰을 안전한 곳에 복사하여 저장
   (⚠️ 이 토큰은 다시 확인할 수 없으므로 반드시 저장!)
```

### 5.2 Jenkins용 웹훅 설정 준비

#### **자동화 규칙 생성**

**1. 자동화 설정 접근**
```
Project settings → Automation → Rules
"Create rule" 클릭
```

**2. 커밋 연동 규칙 생성**
```
Rule name: "Git Commit Integration"
Trigger: "Issue transitioned"
Condition: "Transition to any status"
Action: "Send web request"
  URL: http://localhost:8080/jenkins-webhook
  Method: POST
  Headers: 
    Content-Type: application/json
  Body:
    {
      "issueKey": "{{issue.key}}",
      "status": "{{issue.status}}",
      "summary": "{{issue.summary}}"
    }
```

---

## ✅ 검증 체크리스트

### 🎯 **프로젝트 설정 완료 확인**
- [ ] Smart Greenhouse Monitor 프로젝트 생성 완료
- [ ] 커스텀 이슈 타입 4개 추가 (Hardware Task, Firmware, Integration, Testing)
- [ ] 커스텀 필드 4개 추가 (Hardware Component, Complexity Level, Test Environment, Safety Level)
- [ ] Epic 4개 생성 완료 (센서 시스템, 자동 제어, 대시보드, 알림)

### 📋 **이슈 관리 시스템 확인**
- [ ] Story 2개 이상 생성 (온도/습도, 토양수분)
- [ ] Task 3개 이상 생성 (라이브러리 통합, 회로 설계, 출력 포맷)
- [ ] Epic-Story-Task 계층 구조 정상 연결
- [ ] 모든 이슈에 적절한 커스텀 필드 값 설정

### 🏃‍♂️ **스프린트 관리 확인**  
- [ ] Sprint 1 생성 및 시작 완료
- [ ] 13 스토리 포인트 적절히 분배
- [ ] 칸반 보드에서 이슈 상태 변경 테스트 완료
- [ ] 최소 1개 이슈 IN PROGRESS 상태로 변경

### 🔗 **API 연동 준비 확인**
- [ ] Jira API 토큰 생성 및 안전한 저장
- [ ] 자동화 규칙 생성 (웹훅 준비)
- [ ] 프로젝트 URL 및 키 정보 확인

---

## 🏆 완주 보상: Jira 마스터 인증!

축하합니다! 🎉 Jira 프로젝트 관리 마스터 단계를 완주하셨습니다!

### 📜 **성취 내역**
- ✅ **프로젝트 관리자 레벨**: 복잡한 하드웨어 프로젝트 구조화 완료
- ✅ **커스터마이징 전문가**: 아두이노 특화 이슈 타입 및 필드 설계
- ✅ **애자일 실무자**: 스프린트 기반 프로젝트 관리 시스템 구축
- ✅ **자동화 준비자**: CI/CD 연동을 위한 API 설정 완료

### 🎯 **다음 단계 미리보기**
다음에는 이 Jira 프로젝트와 **Bitbucket Git 저장소를 연동**하여 코드 커밋과 이슈를 자동으로 연결하는 방법을 배워보겠습니다!

---

## 🚀 다음 단계

Jira 프로젝트 관리 시스템이 완벽하게 구축되었습니다!  
이제 소스코드 관리를 위한 Bitbucket Git 워크플로우를 마스터해보겠습니다.

### 👉 **다음으로 이동:**
**[Step 2: Bitbucket Git 워크플로우 마스터하기](02-bitbucket-master.md)**

---

## 🆘 트러블슈팅

### 자주 발생하는 문제들

#### ❌ **커스텀 필드가 이슈에 표시되지 않을 때**
```
해결방법:
1. Project settings → Fields → Field configuration
2. 해당 필드가 적절한 화면(Screen)에 추가되었는지 확인
3. 이슈 타입별로 다른 화면을 사용하는지 확인
```

#### ❌ **Epic과 Story 연결이 안 될 때**
```
해결방법:
1. Story 편집 시 "Epic Link" 필드 확인
2. Epic이 같은 프로젝트에 있는지 확인
3. Epic Name이 올바르게 설정되었는지 확인
```

#### ❌ **스프린트 시작이 안 될 때**
```
해결방법:
1. 스프린트에 최소 1개 이상의 이슈가 있는지 확인
2. 프로젝트 권한 확인 (관리자 권한 필요)
3. 이미 활성화된 스프린트가 있는지 확인 (동시에 1개만 가능)
```

### 💬 **추가 도움:**
- [Jira 공식 문서](https://support.atlassian.com/jira-software-cloud/)
- [GitHub Issues](https://github.com/your-username/arduino-cicd-guide/issues)
- [Discord 커뮤니티](https://discord.gg/arduino-cicd)

---

**🎊 1단계 완료! 벌써 전문가 수준의 프로젝트 관리 시스템을 갖추셨네요! 💪**