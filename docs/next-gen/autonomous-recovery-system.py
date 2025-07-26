#!/usr/bin/env python3
"""
🤖 자율 복구 시스템 (Autonomous Recovery System)
AI 기반 자동 장애 감지, 진단, 복구 및 학습 시스템
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import numpy as np
import pandas as pd
from pathlib import Path
import websockets
import aiohttp
import paramiko
from kubernetes import client, config
import docker
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import slack_sdk
from twilio.rest import Client as TwilioClient
import openai
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis
from kafka import KafkaProducer
import networkx as nx
from scipy import stats

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 데이터베이스 모델
Base = declarative_base()

class RecoveryIncident(Base):
    """복구 사건 기록"""
    __tablename__ = 'recovery_incidents'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(String(100), nullable=False)
    incident_type = Column(String(50), nullable=False)
    severity_level = Column(Integer, nullable=False)  # 1-5 (5가 가장 심각)
    detection_time = Column(DateTime, nullable=False)
    resolution_time = Column(DateTime)
    recovery_actions = Column(Text)
    success_rate = Column(Float)
    ai_confidence = Column(Float)
    human_intervention = Column(Boolean, default=False)
    lessons_learned = Column(Text)
    
class Enum(Enum):
    """시스템 상태 열거형"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    FAILED = "failed"
    RECOVERING = "recovering"
    MAINTENANCE = "maintenance"

class IncidentSeverity(Enum):
    """사건 심각도"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    CATASTROPHIC = 5

class RecoveryAction(Enum):
    """복구 액션 타입"""
    RESTART_SERVICE = "restart_service"
    REBOOT_DEVICE = "reboot_device"
    RECALIBRATE_SENSORS = "recalibrate_sensors"
    UPDATE_FIRMWARE = "update_firmware"
    SCALE_RESOURCES = "scale_resources"
    NETWORK_RESET = "network_reset"
    FACTORY_RESET = "factory_reset"
    REPLACE_HARDWARE = "replace_hardware"
    MANUAL_INTERVENTION = "manual_intervention"

@dataclass
class IncidentReport:
    """사건 보고서"""
    incident_id: str
    device_id: str
    incident_type: str
    severity: IncidentSeverity
    detection_time: datetime
    symptoms: List[str]
    root_cause: Optional[str]
    recovery_plan: List[Dict[str, Any]]
    estimated_recovery_time: int  # minutes
    business_impact: str
    stakeholders: List[str]

@dataclass
class RecoveryResult:
    """복구 결과"""
    incident_id: str
    success: bool
    actions_taken: List[str]
    recovery_time: int  # minutes
    ai_confidence: float
    manual_intervention: bool
    lessons_learned: List[str]
    follow_up_actions: List[str]

class AutonomousRecoverySystem:
    """자율 복구 시스템 메인 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            decode_responses=True
        )
        
        # OpenAI 클라이언트 (GPT-4 기반 진단)
        self.openai_client = openai.AsyncOpenAI(
            api_key=config.get('openai_api_key')
        )
        
        # 알림 클라이언트들
        self._setup_notification_clients()
        
        # 데이터베이스 설정
        self._setup_database()
        
        # Kubernetes 클라이언트
        try:
            config.load_incluster_config()  # Pod 내에서 실행 시
        except:
            config.load_kube_config()  # 로컬 개발 시
        self.k8s_apps_v1 = client.AppsV1Api()
        self.k8s_core_v1 = client.CoreV1Api()
        
        # Docker 클라이언트
        self.docker_client = docker.from_env()
        
        # 복구 액션 매핑
        self.recovery_actions = {
            RecoveryAction.RESTART_SERVICE: self._restart_service,
            RecoveryAction.REBOOT_DEVICE: self._reboot_device,
            RecoveryAction.RECALIBRATE_SENSORS: self._recalibrate_sensors,
            RecoveryAction.UPDATE_FIRMWARE: self._update_firmware,
            RecoveryAction.SCALE_RESOURCES: self._scale_resources,
            RecoveryAction.NETWORK_RESET: self._network_reset,
            RecoveryAction.FACTORY_RESET: self._factory_reset,
            RecoveryAction.REPLACE_HARDWARE: self._replace_hardware,
            RecoveryAction.MANUAL_INTERVENTION: self._request_manual_intervention
        }
        
        # 학습된 복구 패턴
        self.recovery_patterns = {}
        self._load_recovery_patterns()
        
        # 의존성 그래프 (서비스 간 의존 관계)
        self.dependency_graph = nx.DiGraph()
        self._build_dependency_graph()
        
    def _setup_notification_clients(self):
        """알림 클라이언트 설정"""
        # Slack
        slack_token = self.config.get('slack_bot_token')
        if slack_token:
            self.slack_client = slack_sdk.WebClient(token=slack_token)
        
        # Twilio (SMS/전화)
        twilio_sid = self.config.get('twilio_account_sid')
        twilio_token = self.config.get('twilio_auth_token')
        if twilio_sid and twilio_token:
            self.twilio_client = TwilioClient(twilio_sid, twilio_token)
        
        # 이메일
        self.smtp_config = {
            'server': self.config.get('smtp_server', 'smtp.gmail.com'),
            'port': self.config.get('smtp_port', 587),
            'username': self.config.get('smtp_username'),
            'password': self.config.get('smtp_password')
        }
    
    def _setup_database(self):
        """데이터베이스 설정"""
        db_url = self.config.get('database_url', 'sqlite:///recovery_system.db')
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def _build_dependency_graph(self):
        """서비스 의존성 그래프 구축"""
        # 예시 의존성 (실제로는 서비스 디스커버리에서 가져옴)
        dependencies = [
            ('mobile-app', 'api-gateway'),
            ('api-gateway', 'auth-service'),
            ('api-gateway', 'device-manager'),
            ('device-manager', 'database'),
            ('device-manager', 'message-queue'),
            ('monitoring-service', 'database'),
            ('ai-service', 'gpu-cluster'),
            ('ai-service', 'message-queue')
        ]
        
        self.dependency_graph.add_edges_from(dependencies)
    
    async def detect_incident(self, device_data: Dict[str, Any]) -> Optional[IncidentReport]:
        """사건 감지 및 분석"""
        device_id = device_data.get('device_id')
        if not device_id:
            return None
        
        # 1. 이상 징후 감지
        symptoms = await self._detect_symptoms(device_data)
        if not symptoms:
            return None
        
        # 2. 심각도 평가
        severity = await self._assess_severity(symptoms, device_data)
        
        # 3. AI 기반 근본 원인 분석
        root_cause = await self._analyze_root_cause(symptoms, device_data)
        
        # 4. 복구 계획 생성
        recovery_plan = await self._generate_recovery_plan(root_cause, severity)
        
        # 5. 비즈니스 영향 평가
        business_impact = await self._assess_business_impact(device_id, severity)
        
        # 6. 이해관계자 식별
        stakeholders = await self._identify_stakeholders(device_id, severity)
        
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{device_id}"
        
        incident = IncidentReport(
            incident_id=incident_id,
            device_id=device_id,
            incident_type=self._classify_incident_type(symptoms),
            severity=severity,
            detection_time=datetime.now(),
            symptoms=symptoms,
            root_cause=root_cause,
            recovery_plan=recovery_plan,
            estimated_recovery_time=self._estimate_recovery_time(recovery_plan),
            business_impact=business_impact,
            stakeholders=stakeholders
        )
        
        # 사건 기록
        await self._record_incident(incident)
        
        # 즉시 알림 (Critical/Catastrophic인 경우)
        if severity.value >= IncidentSeverity.CRITICAL.value:
            await self._send_immediate_alert(incident)
        
        return incident
    
    async def _detect_symptoms(self, device_data: Dict[str, Any]) -> List[str]:
        """이상 징후 감지"""
        symptoms = []
        
        # 배터리 레벨 확인
        battery_voltage = device_data.get('battery_voltage', 0)
        if battery_voltage < 3.2:
            symptoms.append(f"Low battery voltage: {battery_voltage}V")
        
        # 온도 이상 확인
        temperature = device_data.get('temperature', 0)
        if temperature > 50 or temperature < -10:
            symptoms.append(f"Extreme temperature: {temperature}°C")
        
        # 메모리 사용량 확인
        memory_usage = device_data.get('memory_usage', 0)
        if memory_usage > 90:
            symptoms.append(f"High memory usage: {memory_usage}%")
        
        # CPU 사용량 확인
        cpu_usage = device_data.get('cpu_usage', 0)
        if cpu_usage > 95:
            symptoms.append(f"High CPU usage: {cpu_usage}%")
        
        # 에러 카운트 확인
        error_count = device_data.get('error_count', 0)
        if error_count > 10:
            symptoms.append(f"High error count: {error_count}")
        
        # WiFi 신호 강도 확인
        wifi_signal = device_data.get('wifi_signal_strength', 0)
        if wifi_signal < -80:
            symptoms.append(f"Weak WiFi signal: {wifi_signal}dBm")
        
        # 업타임 확인 (너무 짧으면 재부팅 루프 의심)
        uptime_hours = device_data.get('uptime_hours', 0)
        if uptime_hours < 0.1:  # 6분 미만
            symptoms.append(f"Frequent reboots detected: uptime {uptime_hours}h")
        
        # 센서 데이터 유효성 확인
        sensor_data = {
            'temperature': device_data.get('temperature'),
            'humidity': device_data.get('humidity'),
            'pressure': device_data.get('pressure')
        }
        
        for sensor, value in sensor_data.items():
            if value is None or np.isnan(value):
                symptoms.append(f"Invalid {sensor} reading: {value}")
        
        return symptoms
    
    async def _assess_severity(self, symptoms: List[str], device_data: Dict[str, Any]) -> IncidentSeverity:
        """심각도 평가"""
        severity_score = 0
        
        # 증상 기반 점수 계산
        critical_keywords = ['battery', 'temperature', 'memory', 'reboot']
        for symptom in symptoms:
            if any(keyword in symptom.lower() for keyword in critical_keywords):
                severity_score += 2
            else:
                severity_score += 1
        
        # 디바이스 중요도 고려
        device_id = device_data.get('device_id', '')
        if 'critical' in device_id.lower() or 'production' in device_id.lower():
            severity_score *= 1.5
        
        # 점수를 심각도로 변환
        if severity_score >= 10:
            return IncidentSeverity.CATASTROPHIC
        elif severity_score >= 7:
            return IncidentSeverity.CRITICAL
        elif severity_score >= 4:
            return IncidentSeverity.HIGH
        elif severity_score >= 2:
            return IncidentSeverity.MEDIUM
        else:
            return IncidentSeverity.LOW
    
    async def _analyze_root_cause(self, symptoms: List[str], device_data: Dict[str, Any]) -> str:
        """GPT-4 기반 근본 원인 분석"""
        try:
            prompt = f"""
            IoT 디바이스 장애 분석을 수행하세요.
            
            디바이스 정보:
            - ID: {device_data.get('device_id')}
            - 타입: {device_data.get('device_type', 'Unknown')}
            
            관찰된 증상:
            {chr(10).join(f'- {symptom}' for symptom in symptoms)}
            
            센서 데이터:
            - 온도: {device_data.get('temperature')}°C
            - 습도: {device_data.get('humidity')}%
            - 배터리: {device_data.get('battery_voltage')}V
            - CPU 사용률: {device_data.get('cpu_usage')}%
            - 메모리 사용률: {device_data.get('memory_usage')}%
            - WiFi 신호: {device_data.get('wifi_signal_strength')}dBm
            - 에러 횟수: {device_data.get('error_count')}
            - 가동 시간: {device_data.get('uptime_hours')}시간
            
            가장 가능성 높은 근본 원인을 한 문장으로 설명하세요.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "당신은 IoT 시스템 장애 진단 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Error analyzing root cause: {e}")
            return "Unable to determine root cause due to analysis error"
    
    async def _generate_recovery_plan(self, root_cause: str, severity: IncidentSeverity) -> List[Dict[str, Any]]:
        """복구 계획 생성"""
        recovery_plan = []
        
        # 기본 진단 단계
        recovery_plan.append({
            "step": 1,
            "action": "diagnostic_check",
            "description": "Perform comprehensive diagnostic check",
            "estimated_time": 2,
            "risk_level": "low"
        })
        
        # 근본 원인 기반 복구 액션
        if "battery" in root_cause.lower():
            recovery_plan.extend([
                {
                    "step": 2,
                    "action": RecoveryAction.RESTART_SERVICE.value,
                    "description": "Restart power management service",
                    "estimated_time": 1,
                    "risk_level": "low"
                },
                {
                    "step": 3,
                    "action": "battery_optimization",
                    "description": "Optimize power consumption settings",
                    "estimated_time": 5,
                    "risk_level": "medium"
                }
            ])
        
        elif "temperature" in root_cause.lower():
            recovery_plan.extend([
                {
                    "step": 2,
                    "action": "cooling_check",
                    "description": "Check cooling system and ventilation",
                    "estimated_time": 3,
                    "risk_level": "low"
                },
                {
                    "step": 3,
                    "action": RecoveryAction.RECALIBRATE_SENSORS.value,
                    "description": "Recalibrate temperature sensors",
                    "estimated_time": 5,
                    "risk_level": "medium"
                }
            ])
        
        elif "memory" in root_cause.lower() or "cpu" in root_cause.lower():
            recovery_plan.extend([
                {
                    "step": 2,
                    "action": RecoveryAction.RESTART_SERVICE.value,
                    "description": "Restart affected services",
                    "estimated_time": 2,
                    "risk_level": "low"
                },
                {
                    "step": 3,
                    "action": "memory_cleanup",
                    "description": "Clear memory leaks and optimize usage",
                    "estimated_time": 3,
                    "risk_level": "medium"
                }
            ])
        
        elif "reboot" in root_cause.lower() or "crash" in root_cause.lower():
            recovery_plan.extend([
                {
                    "step": 2,
                    "action": RecoveryAction.UPDATE_FIRMWARE.value,
                    "description": "Update to stable firmware version",
                    "estimated_time": 10,
                    "risk_level": "medium"
                },
                {
                    "step": 3,
                    "action": "stability_test",
                    "description": "Run stability test for 30 minutes",
                    "estimated_time": 30,
                    "risk_level": "low"
                }
            ])
        
        elif "wifi" in root_cause.lower() or "network" in root_cause.lower():
            recovery_plan.extend([
                {
                    "step": 2,
                    "action": RecoveryAction.NETWORK_RESET.value,
                    "description": "Reset network configuration",
                    "estimated_time": 3,
                    "risk_level": "medium"
                },
                {
                    "step": 3,
                    "action": "network_optimization",
                    "description": "Optimize WiFi settings and antenna",
                    "estimated_time": 5,
                    "risk_level": "low"
                }
            ])
        
        # 심각도에 따른 추가 조치
        if severity.value >= IncidentSeverity.CRITICAL.value:
            recovery_plan.append({
                "step": len(recovery_plan) + 1,
                "action": RecoveryAction.MANUAL_INTERVENTION.value,
                "description": "Request immediate manual intervention",
                "estimated_time": 30,
                "risk_level": "low"
            })
        
        return recovery_plan
    
    async def execute_recovery(self, incident: IncidentReport) -> RecoveryResult:
        """복구 실행"""
        logger.info(f"Starting recovery for incident {incident.incident_id}")
        
        start_time = datetime.now()
        actions_taken = []
        success = False
        manual_intervention = False
        lessons_learned = []
        
        try:
            # 의존성 체크 - 다른 서비스에 영향을 줄 수 있는지 확인
            impact_analysis = await self._analyze_dependency_impact(incident.device_id)
            if impact_analysis['high_risk']:
                lessons_learned.append("High dependency risk detected - proceeding with caution")
            
            # 복구 계획 실행
            for step in incident.recovery_plan:
                action = step['action']
                description = step['description']
                
                logger.info(f"Executing step {step['step']}: {description}")
                
                try:
                    if action in [ra.value for ra in RecoveryAction]:
                        # 정의된 복구 액션 실행
                        recovery_action = RecoveryAction(action)
                        result = await self.recovery_actions[recovery_action](
                            incident.device_id, step
                        )
                        
                        if recovery_action == RecoveryAction.MANUAL_INTERVENTION:
                            manual_intervention = True
                        
                        actions_taken.append(f"{description}: {result['status']}")
                        
                        if not result['success']:
                            lessons_learned.append(f"Failed action: {description} - {result.get('error', 'Unknown error')}")
                    else:
                        # 커스텀 액션 실행
                        result = await self._execute_custom_action(action, incident.device_id, step)
                        actions_taken.append(f"{description}: {result['status']}")
                    
                    # 단계별 검증
                    if await self._verify_recovery_step(incident.device_id, action):
                        logger.info(f"Step {step['step']} verified successfully")
                    else:
                        logger.warning(f"Step {step['step']} verification failed")
                        lessons_learned.append(f"Verification failed for: {description}")
                
                except Exception as e:
                    logger.error(f"Error executing step {step['step']}: {e}")
                    actions_taken.append(f"{description}: FAILED - {str(e)}")
                    lessons_learned.append(f"Exception in {description}: {str(e)}")
            
            # 최종 검증
            success = await self._verify_full_recovery(incident.device_id)
            
            if success:
                logger.info(f"Recovery successful for incident {incident.incident_id}")
            else:
                logger.warning(f"Recovery incomplete for incident {incident.incident_id}")
                lessons_learned.append("Full recovery verification failed")
        
        except Exception as e:
            logger.error(f"Recovery execution failed: {e}")
            actions_taken.append(f"Critical error during recovery: {str(e)}")
            lessons_learned.append(f"Recovery process exception: {str(e)}")
        
        end_time = datetime.now()
        recovery_time = int((end_time - start_time).total_seconds() / 60)
        
        # AI 신뢰도 계산
        ai_confidence = await self._calculate_ai_confidence(incident, actions_taken, success)
        
        # 후속 조치 생성
        follow_up_actions = await self._generate_follow_up_actions(incident, success, lessons_learned)
        
        result = RecoveryResult(
            incident_id=incident.incident_id,
            success=success,
            actions_taken=actions_taken,
            recovery_time=recovery_time,
            ai_confidence=ai_confidence,
            manual_intervention=manual_intervention,
            lessons_learned=lessons_learned,
            follow_up_actions=follow_up_actions
        )
        
        # 결과 기록 및 학습
        await self._record_recovery_result(result)
        await self._learn_from_recovery(incident, result)
        
        # 알림 발송
        await self._send_recovery_notification(incident, result)
        
        return result
    
    async def _restart_service(self, device_id: str, step: Dict[str, Any]) -> Dict[str, Any]:
        """서비스 재시작"""
        try:
            # Kubernetes에서 서비스 재시작
            service_name = f"device-{device_id.lower()}-service"
            
            # 파드 재시작 (deployment를 scale down/up)
            deployment = self.k8s_apps_v1.read_namespaced_deployment(
                name=service_name,
                namespace="arduino-devops-ecosystem"
            )
            
            # 스케일을 0으로 설정
            deployment.spec.replicas = 0
            self.k8s_apps_v1.patch_namespaced_deployment(
                name=service_name,
                namespace="arduino-devops-ecosystem",
                body=deployment
            )
            
            await asyncio.sleep(5)  # 5초 대기
            
            # 스케일을 다시 1로 설정
            deployment.spec.replicas = 1
            self.k8s_apps_v1.patch_namespaced_deployment(
                name=service_name,
                namespace="arduino-devops-ecosystem",
                body=deployment
            )
            
            return {"success": True, "status": "Service restarted successfully"}
        
        except Exception as e:
            logger.error(f"Failed to restart service for {device_id}: {e}")
            return {"success": False, "status": "Service restart failed", "error": str(e)}
    
    async def _reboot_device(self, device_id: str, step: Dict[str, Any]) -> Dict[str, Any]:
        """디바이스 재부팅"""
        try:
            # MQTT를 통해 디바이스에 재부팅 명령 전송
            reboot_command = {
                "command": "reboot",
                "timestamp": datetime.now().isoformat(),
                "reason": "Automated recovery"
            }
            
            # 실제 구현에서는 MQTT 클라이언트를 사용
            # mqtt_client.publish(f"arduino/{device_id}/commands", json.dumps(reboot_command))
            
            logger.info(f"Reboot command sent to device {device_id}")
            
            # 재부팅 완료 대기 (실제로는 디바이스에서 온라인 신호를 기다림)
            await asyncio.sleep(30)
            
            return {"success": True, "status": "Device reboot initiated"}
        
        except Exception as e:
            logger.error(f"Failed to reboot device {device_id}: {e}")
            return {"success": False, "status": "Device reboot failed", "error": str(e)}
    
    async def _recalibrate_sensors(self, device_id: str, step: Dict[str, Any]) -> Dict[str, Any]:
        """센서 재보정"""
        try:
            calibration_command = {
                "command": "recalibrate_sensors",
                "sensors": ["temperature", "humidity", "pressure"],
                "timestamp": datetime.now().isoformat()
            }
            
            # MQTT를 통해 보정 명령 전송
            logger.info(f"Sensor recalibration command sent to device {device_id}")
            
            return {"success": True, "status": "Sensor recalibration initiated"}
        
        except Exception as e:
            logger.error(f"Failed to recalibrate sensors for {device_id}: {e}")
            return {"success": False, "status": "Sensor recalibration failed", "error": str(e)}
    
    async def _update_firmware(self, device_id: str, step: Dict[str, Any]) -> Dict[str, Any]:
        """펌웨어 업데이트"""
        try:
            # OTA 업데이트 명령
            update_command = {
                "command": "ota_update",
                "firmware_version": "stable-latest",
                "update_url": self.config.get('firmware_update_url'),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Firmware update command sent to device {device_id}")
            
            # 업데이트 완료 대기
            await asyncio.sleep(120)  # 2분 대기
            
            return {"success": True, "status": "Firmware update initiated"}
        
        except Exception as e:
            logger.error(f"Failed to update firmware for {device_id}: {e}")
            return {"success": False, "status": "Firmware update failed", "error": str(e)}
    
    async def _scale_resources(self, device_id: str, step: Dict[str, Any]) -> Dict[str, Any]:
        """리소스 스케일링"""
        try:
            # Kubernetes HPA 조정
            service_name = f"device-{device_id.lower()}-service"
            
            # HPA 설정 업데이트
            hpa = self.k8s_autoscaling_v2.read_namespaced_horizontal_pod_autoscaler(
                name=f"{service_name}-hpa",
                namespace="arduino-devops-ecosystem"
            )
            
            # 최대 레플리카 수 증가
            hpa.spec.max_replicas = min(hpa.spec.max_replicas * 2, 10)
            
            self.k8s_autoscaling_v2.patch_namespaced_horizontal_pod_autoscaler(
                name=f"{service_name}-hpa",
                namespace="arduino-devops-ecosystem",
                body=hpa
            )
            
            return {"success": True, "status": "Resources scaled successfully"}
        
        except Exception as e:
            logger.error(f"Failed to scale resources for {device_id}: {e}")
            return {"success": False, "status": "Resource scaling failed", "error": str(e)}
    
    async def _network_reset(self, device_id: str, step: Dict[str, Any]) -> Dict[str, Any]:
        """네트워크 리셋"""
        try:
            network_reset_command = {
                "command": "network_reset",
                "reset_wifi": True,
                "reset_mqtt": True,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Network reset command sent to device {device_id}")
            
            return {"success": True, "status": "Network reset initiated"}
        
        except Exception as e:
            logger.error(f"Failed to reset network for {device_id}: {e}")
            return {"success": False, "status": "Network reset failed", "error": str(e)}
    
    async def _factory_reset(self, device_id: str, step: Dict[str, Any]) -> Dict[str, Any]:
        """팩토리 리셋"""
        try:
            factory_reset_command = {
                "command": "factory_reset",
                "preserve_config": False,
                "timestamp": datetime.now().isoformat(),
                "confirmation": "CONFIRMED"
            }
            
            logger.warning(f"Factory reset command sent to device {device_id}")
            
            return {"success": True, "status": "Factory reset initiated"}
        
        except Exception as e:
            logger.error(f"Failed to factory reset device {device_id}: {e}")
            return {"success": False, "status": "Factory reset failed", "error": str(e)}
    
    async def _replace_hardware(self, device_id: str, step: Dict[str, Any]) -> Dict[str, Any]:
        """하드웨어 교체 요청"""
        try:
            replacement_request = {
                "device_id": device_id,
                "request_type": "hardware_replacement",
                "priority": "high",
                "reason": step.get('description', 'Automated recovery system request'),
                "timestamp": datetime.now().isoformat()
            }
            
            # 교체 요청을 작업 관리 시스템에 전송
            await self._create_work_order(replacement_request)
            
            return {"success": True, "status": "Hardware replacement request created"}
        
        except Exception as e:
            logger.error(f"Failed to request hardware replacement for {device_id}: {e}")
            return {"success": False, "status": "Hardware replacement request failed", "error": str(e)}
    
    async def _request_manual_intervention(self, device_id: str, step: Dict[str, Any]) -> Dict[str, Any]:
        """수동 개입 요청"""
        try:
            # 긴급 알림 발송
            alert_message = f"""
            🚨 URGENT: Manual intervention required for device {device_id}
            
            Automated recovery has been exhausted. 
            Please investigate immediately.
            
            Incident ID: {step.get('incident_id')}
            Time: {datetime.now().isoformat()}
            """
            
            await self._send_urgent_alert(alert_message, device_id)
            
            return {"success": True, "status": "Manual intervention requested"}
        
        except Exception as e:
            logger.error(f"Failed to request manual intervention for {device_id}: {e}")
            return {"success": False, "status": "Manual intervention request failed", "error": str(e)}
    
    async def _send_urgent_alert(self, message: str, device_id: str):
        """긴급 알림 발송 (모든 채널)"""
        try:
            # Slack 알림
            if hasattr(self, 'slack_client'):
                await self.slack_client.chat_postMessage(
                    channel="#critical-alerts",
                    text=message,
                    username="Recovery System",
                    icon_emoji=":rotating_light:"
                )
            
            # SMS 알림
            if hasattr(self, 'twilio_client'):
                emergency_contacts = self.config.get('emergency_contacts', [])
                for contact in emergency_contacts:
                    self.twilio_client.messages.create(
                        body=f"CRITICAL: Device {device_id} needs immediate attention",
                        from_=self.config.get('twilio_phone_number'),
                        to=contact
                    )
            
            # 이메일 알림
            await self._send_email_alert(message, urgent=True)
            
        except Exception as e:
            logger.error(f"Failed to send urgent alert: {e}")
    
    async def start_monitoring(self):
        """실시간 모니터링 시작"""
        logger.info("Starting autonomous recovery monitoring...")
        
        # 여러 모니터링 태스크를 병렬로 실행
        tasks = [
            self._monitor_device_health(),
            self._monitor_service_health(),
            self._monitor_infrastructure_health(),
            self._cleanup_old_incidents(),
            self._update_recovery_patterns()
        ]
        
        await asyncio.gather(*tasks)
    
    async def _monitor_device_health(self):
        """디바이스 건강 상태 모니터링"""
        while True:
            try:
                # Redis에서 최신 디바이스 데이터 가져오기
                device_keys = self.redis_client.keys("device:*:latest")
                
                for key in device_keys:
                    device_data = json.loads(self.redis_client.get(key))
                    
                    # 사건 감지
                    incident = await self.detect_incident(device_data)
                    
                    if incident:
                        logger.info(f"Incident detected: {incident.incident_id}")
                        
                        # 자동 복구 실행
                        if incident.severity.value >= IncidentSeverity.HIGH.value:
                            recovery_result = await self.execute_recovery(incident)
                            logger.info(f"Recovery completed: {recovery_result.success}")
                
                await asyncio.sleep(30)  # 30초마다 체크
                
            except Exception as e:
                logger.error(f"Error in device health monitoring: {e}")
                await asyncio.sleep(60)  # 에러 시 1분 대기
    
    async def generate_health_report(self, device_id: str) -> Dict[str, Any]:
        """디바이스 건강 보고서 생성"""
        session = self.Session()
        
        try:
            # 최근 30일간의 사건 기록
            thirty_days_ago = datetime.now() - timedelta(days=30)
            incidents = session.query(RecoveryIncident).filter(
                RecoveryIncident.device_id == device_id,
                RecoveryIncident.detection_time >= thirty_days_ago
            ).all()
            
            # 통계 계산
            total_incidents = len(incidents)
            resolved_incidents = len([i for i in incidents if i.resolution_time])
            avg_resolution_time = np.mean([
                (i.resolution_time - i.detection_time).total_seconds() / 60
                for i in incidents if i.resolution_time
            ]) if resolved_incidents > 0 else 0
            
            success_rate = np.mean([i.success_rate for i in incidents if i.success_rate]) if incidents else 100
            
            # 건강 점수 계산 (0-100)
            health_score = self._calculate_device_health_score(incidents)
            
            # 예측 분석
            failure_prediction = await self._predict_future_failures(device_id, incidents)
            
            # 개선 권고사항
            recommendations = await self._generate_health_recommendations(device_id, incidents)
            
            report = {
                "device_id": device_id,
                "report_date": datetime.now().isoformat(),
                "health_score": health_score,
                "statistics": {
                    "total_incidents": total_incidents,
                    "resolved_incidents": resolved_incidents,
                    "resolution_rate": resolved_incidents / total_incidents * 100 if total_incidents > 0 else 100,
                    "avg_resolution_time_minutes": avg_resolution_time,
                    "success_rate": success_rate
                },
                "failure_prediction": failure_prediction,
                "recommendations": recommendations,
                "incident_history": [
                    {
                        "incident_type": i.incident_type,
                        "severity": i.severity_level,
                        "detection_time": i.detection_time.isoformat(),
                        "resolution_time": i.resolution_time.isoformat() if i.resolution_time else None,
                        "success_rate": i.success_rate
                    }
                    for i in incidents[-10:]  # 최근 10개만
                ]
            }
            
            return report
            
        finally:
            session.close()

# 사용 예시
async def main():
    """메인 실행 함수"""
    
    config = {
        'redis_host': 'localhost',
        'redis_port': 6379,
        'openai_api_key': 'your-openai-api-key',
        'slack_bot_token': 'your-slack-bot-token',
        'twilio_account_sid': 'your-twilio-sid',
        'twilio_auth_token': 'your-twilio-token',
        'smtp_username': 'your-email@gmail.com',
        'smtp_password': 'your-email-password',
        'emergency_contacts': ['+821012345678'],
        'database_url': 'postgresql://user:pass@localhost/recovery_db'
    }
    
    # 자율 복구 시스템 초기화
    recovery_system = AutonomousRecoverySystem(config)
    
    print("🤖 자율 복구 시스템 시작...")
    
    # 예시 디바이스 데이터 (문제 상황)
    problem_device_data = {
        'device_id': 'ESP32-CRITICAL-001',
        'device_type': 'ESP32',
        'temperature': 65.0,  # 과열
        'humidity': 45.0,
        'pressure': 1013.0,
        'battery_voltage': 3.1,  # 낮은 배터리
        'cpu_usage': 98.0,  # 높은 CPU 사용률
        'memory_usage': 95.0,  # 높은 메모리 사용률
        'wifi_signal_strength': -85,  # 약한 WiFi
        'error_count': 15,  # 많은 에러
        'uptime_hours': 0.05  # 잦은 재부팅
    }
    
    # 사건 감지
    print("🔍 사건 감지 중...")
    incident = await recovery_system.detect_incident(problem_device_data)
    
    if incident:
        print(f"🚨 사건 감지됨: {incident.incident_id}")
        print(f"   심각도: {incident.severity.name}")
        print(f"   근본 원인: {incident.root_cause}")
        print(f"   예상 복구 시간: {incident.estimated_recovery_time}분")
        
        # 자동 복구 실행
        print("🔧 자동 복구 실행 중...")
        recovery_result = await recovery_system.execute_recovery(incident)
        
        print(f"✅ 복구 완료: {'성공' if recovery_result.success else '실패'}")
        print(f"   복구 시간: {recovery_result.recovery_time}분")
        print(f"   AI 신뢰도: {recovery_result.ai_confidence:.3f}")
        print(f"   수동 개입: {'필요' if recovery_result.manual_intervention else '불필요'}")
        
        print("\n📋 수행된 액션:")
        for i, action in enumerate(recovery_result.actions_taken, 1):
            print(f"   {i}. {action}")
        
        print("\n💡 학습된 교훈:")
        for i, lesson in enumerate(recovery_result.lessons_learned, 1):
            print(f"   {i}. {lesson}")
        
        print("\n📝 후속 조치:")
        for i, follow_up in enumerate(recovery_result.follow_up_actions, 1):
            print(f"   {i}. {follow_up}")
    
    # 건강 보고서 생성
    print("\n📊 건강 보고서 생성 중...")
    health_report = await recovery_system.generate_health_report('ESP32-CRITICAL-001')
    
    print(f"🏥 디바이스 건강 점수: {health_report['health_score']:.1f}/100")
    print(f"📈 해결률: {health_report['statistics']['resolution_rate']:.1f}%")
    print(f"⏱️ 평균 복구 시간: {health_report['statistics']['avg_resolution_time_minutes']:.1f}분")
    
    print("\n🎯 개선 권고사항:")
    for i, rec in enumerate(health_report['recommendations'], 1):
        print(f"   {i}. {rec}")
    
    print("\n🚀 실시간 모니터링 시작...")
    # await recovery_system.start_monitoring()  # 실제 운영에서는 이 라인을 활성화

if __name__ == "__main__":
    asyncio.run(main())