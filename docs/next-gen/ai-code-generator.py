#!/usr/bin/env python3
"""
🤖 AI-Powered Arduino Code Generator
자연어 설명을 Arduino 코드로 자동 변환하는 GPT-4o 기반 시스템
"""

import openai
import ast
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import json
import asyncio
import websockets
from datetime import datetime

@dataclass
class HardwareSpec:
    """하드웨어 사양 정의"""
    board: str  # "ESP32", "Arduino Uno", "Raspberry Pi Pico"
    sensors: List[str]  # ["DHT22", "BMP280", "PIR"]
    actuators: List[str]  # ["Servo", "LED", "Relay"]
    connectivity: List[str]  # ["WiFi", "Bluetooth", "LoRa"]
    power_requirements: str  # "3.3V", "5V", "Battery"

@dataclass
class CodeGenerationRequest:
    """코드 생성 요청 구조"""
    natural_language_description: str
    hardware_spec: HardwareSpec
    target_functionality: List[str]
    optimization_goals: List[str]  # ["energy_efficiency", "response_time", "memory_usage"]
    integration_requirements: List[str]  # ["mqtt", "web_server", "ota_update"]

class AICodeGenerator:
    """GPT-4o 기반 Arduino 코드 생성기"""
    
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.code_templates = self._load_templates()
        self.optimization_patterns = self._load_optimization_patterns()
        
    def _load_templates(self) -> Dict[str, str]:
        """코드 템플릿 로드"""
        return {
            "esp32_base": """
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <AsyncMqttClient.h>

// AI 생성 설정
const char* WIFI_SSID = "{wifi_ssid}";
const char* WIFI_PASSWORD = "{wifi_password}";
const char* MQTT_SERVER = "{mqtt_server}";

// 하드웨어 핀 정의 (AI 최적화)
{pin_definitions}

// 전역 변수 (메모리 최적화)
{global_variables}

// AI 생성 함수들
{ai_generated_functions}

void setup() {{
    Serial.begin(115200);
    {setup_code}
}}

void loop() {{
    {loop_code}
}}
""",
            "sensor_reading": """
float read{sensor_name}() {{
    // AI 최적화된 센서 읽기
    {sensor_specific_code}
    return {return_value};
}}
""",
            "smart_automation": """
void smartAutomation() {{
    // AI 기반 자동화 로직
    float prediction = predictNextValue();
    if (prediction > threshold) {{
        {automation_action}
    }}
}}
"""
        }
    
    def _load_optimization_patterns(self) -> Dict[str, str]:
        """최적화 패턴 로드"""
        return {
            "energy_efficiency": {
                "deep_sleep": "esp_deep_sleep_start();",
                "wifi_power_save": "WiFi.setSleep(true);",
                "cpu_frequency": "setCpuFrequencyMhz(80);"
            },
            "memory_optimization": {
                "progmem": "const char* data PROGMEM = \"{data}\";",
                "string_optimization": "F(\"string\")",
                "array_pooling": "static uint8_t buffer[256];"
            },
            "performance": {
                "interrupt_optimization": "IRAM_ATTR void fastISR() {}",
                "cache_friendly": "volatile uint32_t* reg = (uint32_t*)address;",
                "dma_transfer": "spi_dma_transfer(data, length);"
            }
        }
    
    async def generate_code(self, request: CodeGenerationRequest) -> Dict[str, any]:
        """메인 코드 생성 함수"""
        
        # 1. 하드웨어 분석 및 최적화
        hardware_analysis = await self._analyze_hardware(request.hardware_spec)
        
        # 2. 자연어 → 기능 명세 변환
        functional_spec = await self._parse_natural_language(
            request.natural_language_description,
            request.target_functionality
        )
        
        # 3. AI 코드 생성
        generated_code = await self._generate_arduino_code(
            functional_spec,
            hardware_analysis,
            request.optimization_goals
        )
        
        # 4. 코드 최적화 및 검증
        optimized_code = await self._optimize_code(
            generated_code,
            request.optimization_goals
        )
        
        # 5. 테스트 케이스 자동 생성
        test_cases = await self._generate_test_cases(optimized_code)
        
        # 6. 배포 스크립트 생성
        deployment_script = await self._generate_deployment_script(
            optimized_code,
            request.integration_requirements
        )
        
        return {
            "main_code": optimized_code,
            "test_cases": test_cases,
            "deployment_script": deployment_script,
            "performance_metrics": await self._estimate_performance(optimized_code),
            "energy_analysis": await self._analyze_energy_consumption(optimized_code),
            "security_analysis": await self._security_audit(optimized_code),
            "documentation": await self._generate_documentation(optimized_code)
        }
    
    async def _analyze_hardware(self, spec: HardwareSpec) -> Dict[str, any]:
        """하드웨어 사양 분석 및 최적화 제안"""
        
        prompt = f"""
        하드웨어 사양을 분석하고 최적화 제안을 생성하세요:
        
        보드: {spec.board}
        센서: {', '.join(spec.sensors)}
        액추에이터: {', '.join(spec.actuators)}
        연결성: {', '.join(spec.connectivity)}
        전원: {spec.power_requirements}
        
        다음 형식으로 JSON 응답을 생성하세요:
        {{
            "pin_mapping": {{"sensor_name": "pin_number"}},
            "power_analysis": {{"estimated_current": "mA", "battery_life": "hours"}},
            "performance_constraints": ["constraint1", "constraint2"],
            "optimization_recommendations": ["recommendation1", "recommendation2"]
        }}
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 임베디드 하드웨어 최적화 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _parse_natural_language(self, description: str, functionality: List[str]) -> Dict[str, any]:
        """자연어 설명을 기능 명세로 변환"""
        
        prompt = f"""
        다음 자연어 설명을 구체적인 Arduino 기능 명세로 변환하세요:
        
        설명: {description}
        목표 기능: {', '.join(functionality)}
        
        다음 JSON 형식으로 응답하세요:
        {{
            "main_functions": [
                {{
                    "name": "function_name",
                    "description": "기능 설명",
                    "inputs": ["input1", "input2"],
                    "outputs": ["output1"],
                    "timing_requirements": "실시간/주기적/이벤트기반",
                    "error_handling": "오류 처리 방법"
                }}
            ],
            "data_structures": [
                {{
                    "name": "struct_name",
                    "fields": ["{{"type": "float", "name": "temperature"}}"]
                }}
            ],
            "communication_protocols": ["WiFi", "MQTT", "HTTP"],
            "timing_constraints": {{"max_response_time": "100ms"}}
        }}
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 임베디드 시스템 설계 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _generate_arduino_code(self, 
                                   functional_spec: Dict[str, any],
                                   hardware_analysis: Dict[str, any],
                                   optimization_goals: List[str]) -> str:
        """실제 Arduino 코드 생성"""
        
        # 최적화 목표에 따른 코드 스타일 결정
        optimization_directives = []
        for goal in optimization_goals:
            if goal == "energy_efficiency":
                optimization_directives.append("전력 소모 최소화를 위해 deep sleep 모드 사용")
            elif goal == "response_time":
                optimization_directives.append("인터럽트 기반 빠른 응답 구현")
            elif goal == "memory_usage":
                optimization_directives.append("PROGMEM 사용 및 메모리 풀링")
        
        prompt = f"""
        다음 명세에 따라 최적화된 Arduino C++ 코드를 생성하세요:
        
        기능 명세: {json.dumps(functional_spec, indent=2)}
        하드웨어 분석: {json.dumps(hardware_analysis, indent=2)}
        최적화 목표: {', '.join(optimization_directives)}
        
        요구사항:
        1. 완전한 Arduino 스케치 (.ino 파일)
        2. 에러 처리 및 예외 상황 대응
        3. 주석으로 코드 설명
        4. 모듈화된 함수 구조
        5. 성능 최적화 적용
        6. 메모리 효율성
        7. 실시간 데이터 처리
        8. OTA 업데이트 지원
        
        코드만 응답하세요 (마크다운 코드 블록 없이):
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 최고 수준의 Arduino 개발자입니다. 최적화되고 안정적인 코드를 작성합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=4000
        )
        
        return response.choices[0].message.content
    
    async def _optimize_code(self, code: str, optimization_goals: List[str]) -> str:
        """생성된 코드 최적화"""
        
        optimizations = []
        for goal in optimization_goals:
            if goal in self.optimization_patterns:
                optimizations.extend(self.optimization_patterns[goal].values())
        
        prompt = f"""
        다음 Arduino 코드를 최적화하세요:
        
        원본 코드:
        {code}
        
        적용할 최적화:
        {chr(10).join(optimizations)}
        
        최적화된 코드만 응답하세요:
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "코드 최적화 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        return response.choices[0].message.content
    
    async def _generate_test_cases(self, code: str) -> List[Dict[str, any]]:
        """자동 테스트 케이스 생성"""
        
        prompt = f"""
        다음 Arduino 코드에 대한 포괄적인 테스트 케이스를 생성하세요:
        
        {code}
        
        다음 JSON 형식으로 테스트 케이스들을 응답하세요:
        {{
            "unit_tests": [
                {{
                    "test_name": "test_sensor_reading",
                    "description": "센서 읽기 기능 테스트",
                    "input_conditions": {{"temperature": 25.0}},
                    "expected_output": {{"success": true, "value": 25.0}},
                    "test_code": "Arduino 테스트 코드"
                }}
            ],
            "integration_tests": [
                {{
                    "test_name": "test_wifi_connection",
                    "description": "WiFi 연결 통합 테스트",
                    "setup_requirements": ["WiFi AP 필요"],
                    "test_steps": ["1. WiFi 연결 시도", "2. 연결 상태 확인"],
                    "expected_behavior": "5초 내 연결 완료"
                }}
            ],
            "performance_tests": [
                {{
                    "test_name": "test_response_time",
                    "description": "응답 시간 측정",
                    "metric": "response_time_ms",
                    "threshold": 100,
                    "test_duration": "60초"
                }}
            ]
        }}
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "테스트 자동화 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        return json.loads(response.choices[0].message.content)

# 사용 예시
async def main():
    """AI 코드 생성기 사용 예시"""
    
    # AI 코드 생성기 초기화
    generator = AICodeGenerator(api_key="your-openai-api-key")
    
    # 하드웨어 사양 정의
    hardware = HardwareSpec(
        board="ESP32",
        sensors=["DHT22", "BMP280", "LDR"],
        actuators=["Servo", "WS2812 LED Strip", "Water Pump"],
        connectivity=["WiFi", "MQTT"],
        power_requirements="3.7V LiPo Battery"
    )
    
    # 코드 생성 요청
    request = CodeGenerationRequest(
        natural_language_description="""
        스마트 식물 재배 시스템을 만들어주세요. 
        온도, 습도, 대기압, 조도를 모니터링하고,
        식물의 상태에 따라 자동으로 물을 주고 LED 조명을 조절합니다.
        스마트폰 앱에서 실시간으로 모니터링할 수 있어야 하고,
        AI가 식물 성장 패턴을 학습해서 최적의 환경을 자동으로 조성해주세요.
        """,
        hardware_spec=hardware,
        target_functionality=[
            "실시간 센서 모니터링",
            "자동 급수 시스템",
            "LED 조명 제어",
            "모바일 앱 연동",
            "AI 기반 최적화"
        ],
        optimization_goals=[
            "energy_efficiency",
            "response_time",
            "memory_usage"
        ],
        integration_requirements=[
            "mqtt",
            "web_server",
            "ota_update",
            "mobile_app_api"
        ]
    )
    
    # AI 코드 생성 실행
    print("🤖 AI가 Arduino 코드를 생성하는 중...")
    result = await generator.generate_code(request)
    
    # 결과 저장
    output_dir = Path("generated_code")
    output_dir.mkdir(exist_ok=True)
    
    # 메인 코드 저장
    with open(output_dir / "smart_plant_system.ino", "w", encoding="utf-8") as f:
        f.write(result["main_code"])
    
    # 테스트 케이스 저장
    with open(output_dir / "test_cases.json", "w", encoding="utf-8") as f:
        json.dump(result["test_cases"], f, indent=2, ensure_ascii=False)
    
    # 성능 분석 결과
    print(f"📊 예상 성능: {result['performance_metrics']}")
    print(f"🔋 전력 분석: {result['energy_analysis']}")
    print(f"🛡️ 보안 점수: {result['security_analysis']}")
    
    print("✅ AI 코드 생성 완료!")
    print(f"📁 생성된 파일: {output_dir}")

if __name__ == "__main__":
    asyncio.run(main())