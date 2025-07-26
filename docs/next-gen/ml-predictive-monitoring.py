#!/usr/bin/env python3
"""
🧠 AI/ML 기반 예측적 모니터링 시스템
Arduino IoT 디바이스의 장애 예측, 성능 최적화, 자율 복구 시스템
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, classification_report
import joblib
import asyncio
import websockets
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import redis
import paho.mqtt.client as mqtt
from kafka import KafkaProducer, KafkaConsumer
import plotly.graph_objs as go
import plotly.offline as pyo
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import warnings
warnings.filterwarnings('ignore')

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SensorReading:
    """센서 데이터 구조"""
    device_id: str
    timestamp: datetime
    temperature: float
    humidity: float
    pressure: float
    light_level: float
    soil_moisture: float
    battery_voltage: float
    cpu_usage: float
    memory_usage: float
    wifi_signal_strength: int
    error_count: int
    uptime_hours: float

@dataclass
class PredictionResult:
    """예측 결과 구조"""
    device_id: str
    timestamp: datetime
    failure_probability: float
    predicted_failure_time: Optional[datetime]
    anomaly_score: float
    recommended_actions: List[str]
    confidence_score: float
    health_score: float  # 0-100
    performance_metrics: Dict[str, float]

@dataclass
class OptimizationRecommendation:
    """최적화 권고사항"""
    device_id: str
    optimization_type: str  # "energy", "performance", "reliability"
    current_value: float
    recommended_value: float
    expected_improvement: float
    implementation_code: str
    risk_assessment: str

class ArduinoMLPredictor:
    """Arduino IoT 디바이스 ML 예측 시스템"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models = {}
        self.scalers = {}
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            decode_responses=True
        )
        
        # InfluxDB 연결 (시계열 데이터)
        self.influx_client = InfluxDBClient(
            url=config.get('influxdb_url', 'http://localhost:8086'),
            token=config.get('influxdb_token'),
            org=config.get('influxdb_org', 'arduino-devops')
        )
        self.write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
        
        # Kafka Producer (실시간 알림)
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=config.get('kafka_servers', ['localhost:9092']),
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
        # MQTT Client (디바이스 통신)
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self._on_mqtt_connect
        self.mqtt_client.on_message = self._on_mqtt_message
        
        # 모델 초기화
        self._initialize_models()
        
    def _initialize_models(self):
        """ML 모델들 초기화"""
        
        # 1. 장애 예측 모델 (LSTM)
        self.models['failure_prediction'] = self._create_lstm_failure_model()
        
        # 2. 이상 탐지 모델 (Isolation Forest)
        self.models['anomaly_detection'] = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        
        # 3. 성능 예측 모델 (Random Forest)
        self.models['performance_prediction'] = RandomForestRegressor(
            n_estimators=200,
            random_state=42,
            max_depth=15
        )
        
        # 4. 에너지 최적화 모델 (Neural Network)
        self.models['energy_optimization'] = self._create_energy_optimization_model()
        
        # 5. 자가 치유 추천 모델 (Decision Tree Ensemble)
        self.models['self_healing'] = self._create_self_healing_model()
        
        logger.info("All ML models initialized successfully")
    
    def _create_lstm_failure_model(self) -> keras.Model:
        """LSTM 기반 장애 예측 모델"""
        model = keras.Sequential([
            keras.layers.LSTM(64, return_sequences=True, input_shape=(24, 12)),  # 24시간, 12개 피처
            keras.layers.Dropout(0.2),
            keras.layers.LSTM(32, return_sequences=False),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(16, activation='relu'),
            keras.layers.Dense(8, activation='relu'),
            keras.layers.Dense(1, activation='sigmoid')  # 장애 확률 (0-1)
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        return model
    
    def _create_energy_optimization_model(self) -> keras.Model:
        """에너지 최적화 Neural Network"""
        model = keras.Sequential([
            keras.layers.Dense(128, activation='relu', input_shape=(12,)),
            keras.layers.BatchNormalization(),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.BatchNormalization(),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(16, activation='relu'),
            keras.layers.Dense(4, activation='linear')  # [cpu_freq, wifi_power, sleep_interval, sensor_interval]
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def _create_self_healing_model(self) -> keras.Model:
        """자가 치유 액션 추천 모델"""
        model = keras.Sequential([
            keras.layers.Dense(64, activation='relu', input_shape=(15,)),  # 확장된 피처
            keras.layers.Dropout(0.2),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(16, activation='relu'),
            keras.layers.Dense(8, activation='softmax')  # 8가지 치유 액션
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    async def train_models(self, historical_data: pd.DataFrame):
        """모델 학습"""
        logger.info("Starting model training...")
        
        # 데이터 전처리
        X, y_failure, y_performance, y_energy = self._preprocess_training_data(historical_data)
        
        # 1. 장애 예측 모델 학습
        await self._train_failure_prediction(X, y_failure)
        
        # 2. 이상 탐지 모델 학습
        await self._train_anomaly_detection(X)
        
        # 3. 성능 예측 모델 학습
        await self._train_performance_prediction(X, y_performance)
        
        # 4. 에너지 최적화 모델 학습
        await self._train_energy_optimization(X, y_energy)
        
        # 5. 자가 치유 모델 학습
        await self._train_self_healing(X, historical_data)
        
        # 모델 저장
        self._save_models()
        
        logger.info("Model training completed successfully")
    
    async def _train_failure_prediction(self, X: np.ndarray, y: np.ndarray):
        """장애 예측 모델 학습"""
        # 시계열 데이터로 변환 (24시간 윈도우)
        X_seq, y_seq = self._create_sequences(X, y, seq_length=24)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X_seq, y_seq, test_size=0.2, random_state=42
        )
        
        # 스케일링
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train.reshape(-1, X_train.shape[-1]))
        X_train_scaled = X_train_scaled.reshape(X_train.shape)
        X_test_scaled = scaler.transform(X_test.reshape(-1, X_test.shape[-1]))
        X_test_scaled = X_test_scaled.reshape(X_test.shape)
        
        self.scalers['failure_prediction'] = scaler
        
        # 모델 학습
        history = self.models['failure_prediction'].fit(
            X_train_scaled, y_train,
            epochs=100,
            batch_size=32,
            validation_data=(X_test_scaled, y_test),
            callbacks=[
                keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
                keras.callbacks.ReduceLROnPlateau(patience=5, factor=0.5)
            ],
            verbose=0
        )
        
        # 성능 평가
        test_loss, test_acc, test_prec, test_recall = self.models['failure_prediction'].evaluate(
            X_test_scaled, y_test, verbose=0
        )
        
        logger.info(f"Failure prediction model - Accuracy: {test_acc:.4f}, Precision: {test_prec:.4f}, Recall: {test_recall:.4f}")
    
    async def _train_anomaly_detection(self, X: np.ndarray):
        """이상 탐지 모델 학습"""
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers['anomaly_detection'] = scaler
        
        self.models['anomaly_detection'].fit(X_scaled)
        
        # 이상치 점수 계산
        anomaly_scores = self.models['anomaly_detection'].decision_function(X_scaled)
        threshold = np.percentile(anomaly_scores, 10)  # 하위 10%를 이상치로 간주
        
        logger.info(f"Anomaly detection model trained. Threshold: {threshold:.4f}")
    
    async def _train_performance_prediction(self, X: np.ndarray, y: np.ndarray):
        """성능 예측 모델 학습"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers['performance_prediction'] = scaler
        
        self.models['performance_prediction'].fit(X_train_scaled, y_train)
        
        # 성능 평가
        y_pred = self.models['performance_prediction'].predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        
        logger.info(f"Performance prediction model - MSE: {mse:.4f}")
    
    async def _train_energy_optimization(self, X: np.ndarray, y: np.ndarray):
        """에너지 최적화 모델 학습"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        scaler = MinMaxScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers['energy_optimization'] = scaler
        
        history = self.models['energy_optimization'].fit(
            X_train_scaled, y_train,
            epochs=200,
            batch_size=64,
            validation_data=(X_test_scaled, y_test),
            callbacks=[
                keras.callbacks.EarlyStopping(patience=20, restore_best_weights=True)
            ],
            verbose=0
        )
        
        test_loss = self.models['energy_optimization'].evaluate(X_test_scaled, y_test, verbose=0)
        logger.info(f"Energy optimization model - Test Loss: {test_loss:.4f}")
    
    async def predict_device_health(self, sensor_data: List[SensorReading]) -> PredictionResult:
        """디바이스 건강 상태 예측"""
        if not sensor_data:
            raise ValueError("No sensor data provided")
        
        device_id = sensor_data[0].device_id
        
        # 데이터 전처리
        features = self._extract_features(sensor_data)
        
        # 1. 장애 예측
        failure_prob = await self._predict_failure(features)
        
        # 2. 이상 탐지
        anomaly_score = await self._detect_anomaly(features)
        
        # 3. 성능 예측
        performance_metrics = await self._predict_performance(features)
        
        # 4. 건강 점수 계산
        health_score = self._calculate_health_score(
            failure_prob, anomaly_score, performance_metrics
        )
        
        # 5. 권고사항 생성
        recommendations = await self._generate_recommendations(
            features, failure_prob, anomaly_score, performance_metrics
        )
        
        # 6. 예측된 장애 시간 계산
        predicted_failure_time = self._estimate_failure_time(
            failure_prob, sensor_data[-1].timestamp
        )
        
        result = PredictionResult(
            device_id=device_id,
            timestamp=datetime.now(),
            failure_probability=failure_prob,
            predicted_failure_time=predicted_failure_time,
            anomaly_score=anomaly_score,
            recommended_actions=recommendations,
            confidence_score=self._calculate_confidence(features),
            health_score=health_score,
            performance_metrics=performance_metrics
        )
        
        # 결과 저장 및 알림
        await self._store_prediction_result(result)
        await self._send_alerts_if_needed(result)
        
        return result
    
    async def _predict_failure(self, features: np.ndarray) -> float:
        """장애 확률 예측"""
        if 'failure_prediction' not in self.models:
            return 0.0
        
        # 시계열 형태로 변환
        if len(features.shape) == 1:
            features = features.reshape(1, 1, -1)
        elif len(features.shape) == 2:
            features = features.reshape(features.shape[0], 1, features.shape[1])
        
        # 스케일링
        scaler = self.scalers.get('failure_prediction')
        if scaler:
            original_shape = features.shape
            features_scaled = scaler.transform(features.reshape(-1, features.shape[-1]))
            features_scaled = features_scaled.reshape(original_shape)
        else:
            features_scaled = features
        
        prediction = self.models['failure_prediction'].predict(features_scaled, verbose=0)
        return float(prediction[0][0]) if prediction.ndim > 1 else float(prediction[0])
    
    async def _detect_anomaly(self, features: np.ndarray) -> float:
        """이상 점수 계산"""
        if 'anomaly_detection' not in self.models:
            return 0.0
        
        # 최신 데이터만 사용
        if len(features.shape) > 1:
            features = features[-1]
        
        scaler = self.scalers.get('anomaly_detection')
        if scaler:
            features_scaled = scaler.transform(features.reshape(1, -1))
        else:
            features_scaled = features.reshape(1, -1)
        
        anomaly_score = self.models['anomaly_detection'].decision_function(features_scaled)
        # 점수를 0-1 범위로 정규화
        return float(max(0, min(1, (anomaly_score[0] + 0.5) * 2)))
    
    async def _predict_performance(self, features: np.ndarray) -> Dict[str, float]:
        """성능 메트릭 예측"""
        if 'performance_prediction' not in self.models:
            return {}
        
        # 최신 데이터만 사용
        if len(features.shape) > 1:
            features = features[-1]
        
        scaler = self.scalers.get('performance_prediction')
        if scaler:
            features_scaled = scaler.transform(features.reshape(1, -1))
        else:
            features_scaled = features.reshape(1, -1)
        
        prediction = self.models['performance_prediction'].predict(features_scaled)
        
        return {
            'response_time_ms': float(prediction[0]),
            'throughput_ops_sec': float(prediction[0] * 1.2),
            'cpu_efficiency': float(min(100, max(0, 100 - prediction[0] * 0.1))),
            'memory_efficiency': float(min(100, max(0, 100 - prediction[0] * 0.05)))
        }
    
    def _calculate_health_score(self, 
                               failure_prob: float, 
                               anomaly_score: float, 
                               performance_metrics: Dict[str, float]) -> float:
        """종합 건강 점수 계산 (0-100)"""
        # 가중치 적용
        failure_weight = 0.4
        anomaly_weight = 0.3
        performance_weight = 0.3
        
        # 장애 확률 점수 (낮을수록 좋음)
        failure_score = (1 - failure_prob) * 100
        
        # 이상 점수 (낮을수록 좋음)
        anomaly_health_score = (1 - anomaly_score) * 100
        
        # 성능 점수
        performance_score = 0
        if performance_metrics:
            cpu_eff = performance_metrics.get('cpu_efficiency', 50)
            mem_eff = performance_metrics.get('memory_efficiency', 50)
            performance_score = (cpu_eff + mem_eff) / 2
        else:
            performance_score = 50  # 기본값
        
        # 가중 평균 계산
        health_score = (
            failure_score * failure_weight +
            anomaly_health_score * anomaly_weight +
            performance_score * performance_weight
        )
        
        return max(0, min(100, health_score))
    
    async def _generate_recommendations(self, 
                                      features: np.ndarray,
                                      failure_prob: float,
                                      anomaly_score: float,
                                      performance_metrics: Dict[str, float]) -> List[str]:
        """권고사항 생성"""
        recommendations = []
        
        # 장애 확률이 높은 경우
        if failure_prob > 0.7:
            recommendations.append("CRITICAL: Immediate maintenance required")
            recommendations.append("Schedule device replacement within 24 hours")
            recommendations.append("Backup all critical data immediately")
        elif failure_prob > 0.5:
            recommendations.append("WARNING: Monitor device closely")
            recommendations.append("Schedule maintenance within 72 hours")
        
        # 이상 점수가 높은 경우
        if anomaly_score > 0.8:
            recommendations.append("Anomaly detected: Check sensor calibration")
            recommendations.append("Review recent environmental changes")
        elif anomaly_score > 0.6:
            recommendations.append("Mild anomaly: Monitor sensor readings")
        
        # 성능 기반 권고사항
        if performance_metrics:
            cpu_eff = performance_metrics.get('cpu_efficiency', 100)
            mem_eff = performance_metrics.get('memory_efficiency', 100)
            
            if cpu_eff < 60:
                recommendations.append("Optimize CPU usage: Reduce sampling frequency")
                recommendations.append("Consider deep sleep mode implementation")
            
            if mem_eff < 60:
                recommendations.append("Memory optimization needed")
                recommendations.append("Clear unnecessary buffers and cache")
        
        # AI 기반 최적화 권고
        optimization_recs = await self._get_ai_optimization_recommendations(features)
        recommendations.extend(optimization_recs)
        
        return recommendations
    
    async def _get_ai_optimization_recommendations(self, features: np.ndarray) -> List[str]:
        """AI 기반 최적화 권고사항"""
        if 'energy_optimization' not in self.models:
            return []
        
        try:
            # 최신 데이터만 사용
            if len(features.shape) > 1:
                features = features[-1]
            
            scaler = self.scalers.get('energy_optimization')
            if scaler:
                features_scaled = scaler.transform(features.reshape(1, -1))
            else:
                features_scaled = features.reshape(1, -1)
            
            optimization_params = self.models['energy_optimization'].predict(features_scaled, verbose=0)
            
            recommendations = []
            
            # CPU 주파수 최적화
            cpu_freq = optimization_params[0][0]
            if cpu_freq < 160:
                recommendations.append(f"Reduce CPU frequency to {cpu_freq:.0f}MHz for energy savings")
            
            # WiFi 전력 최적화
            wifi_power = optimization_params[0][1]
            if wifi_power < 0.5:
                recommendations.append("Enable WiFi power saving mode")
            
            # 슬립 간격 최적화
            sleep_interval = optimization_params[0][2]
            if sleep_interval > 30:
                recommendations.append(f"Increase sleep interval to {sleep_interval:.0f} seconds")
            
            # 센서 샘플링 최적화
            sensor_interval = optimization_params[0][3]
            if sensor_interval > 10:
                recommendations.append(f"Reduce sensor sampling to every {sensor_interval:.0f} seconds")
            
            return recommendations
        
        except Exception as e:
            logger.error(f"Error generating AI optimization recommendations: {e}")
            return []
    
    def _extract_features(self, sensor_data: List[SensorReading]) -> np.ndarray:
        """센서 데이터에서 특징 추출"""
        if not sensor_data:
            return np.array([])
        
        # 최신 데이터 포인트들을 사용
        recent_data = sensor_data[-24:] if len(sensor_data) >= 24 else sensor_data
        
        features_list = []
        for reading in recent_data:
            features = [
                reading.temperature,
                reading.humidity,
                reading.pressure,
                reading.light_level,
                reading.soil_moisture,
                reading.battery_voltage,
                reading.cpu_usage,
                reading.memory_usage,
                reading.wifi_signal_strength,
                reading.error_count,
                reading.uptime_hours,
                # 시간 기반 특징
                reading.timestamp.hour,  # 시간
            ]
            features_list.append(features)
        
        return np.array(features_list)
    
    async def optimize_device_settings(self, device_id: str, 
                                     current_settings: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """디바이스 설정 최적화"""
        recommendations = []
        
        # 최근 센서 데이터 가져오기
        recent_data = await self._get_recent_sensor_data(device_id, hours=24)
        if not recent_data:
            return recommendations
        
        features = self._extract_features(recent_data)
        
        # 에너지 최적화
        energy_recs = await self._generate_energy_optimizations(
            device_id, features, current_settings
        )
        recommendations.extend(energy_recs)
        
        # 성능 최적화
        performance_recs = await self._generate_performance_optimizations(
            device_id, features, current_settings
        )
        recommendations.extend(performance_recs)
        
        # 안정성 최적화
        reliability_recs = await self._generate_reliability_optimizations(
            device_id, features, current_settings
        )
        recommendations.extend(reliability_recs)
        
        return recommendations
    
    async def _generate_energy_optimizations(self, 
                                           device_id: str,
                                           features: np.ndarray,
                                           current_settings: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """에너지 효율성 최적화"""
        recommendations = []
        
        if 'energy_optimization' not in self.models:
            return recommendations
        
        try:
            # 최신 데이터만 사용
            if len(features.shape) > 1:
                features = features[-1]
            
            scaler = self.scalers.get('energy_optimization')
            if scaler:
                features_scaled = scaler.transform(features.reshape(1, -1))
            else:
                features_scaled = features.reshape(1, -1)
            
            optimized_params = self.models['energy_optimization'].predict(features_scaled, verbose=0)[0]
            
            # CPU 주파수 최적화
            current_cpu_freq = current_settings.get('cpu_frequency_mhz', 240)
            recommended_cpu_freq = max(80, min(240, optimized_params[0]))
            
            if abs(current_cpu_freq - recommended_cpu_freq) > 20:
                energy_savings = (current_cpu_freq - recommended_cpu_freq) / current_cpu_freq * 30  # 예상 절약율
                
                recommendations.append(OptimizationRecommendation(
                    device_id=device_id,
                    optimization_type="energy",
                    current_value=current_cpu_freq,
                    recommended_value=recommended_cpu_freq,
                    expected_improvement=energy_savings,
                    implementation_code=f"setCpuFrequencyMhz({int(recommended_cpu_freq)});",
                    risk_assessment="Low risk - Reversible change"
                ))
            
            # 센서 샘플링 간격 최적화
            current_sampling_interval = current_settings.get('sensor_interval_sec', 10)
            recommended_sampling_interval = max(5, min(60, optimized_params[3]))
            
            if abs(current_sampling_interval - recommended_sampling_interval) > 5:
                energy_savings = (recommended_sampling_interval - current_sampling_interval) / current_sampling_interval * 20
                
                recommendations.append(OptimizationRecommendation(
                    device_id=device_id,
                    optimization_type="energy",
                    current_value=current_sampling_interval,
                    recommended_value=recommended_sampling_interval,
                    expected_improvement=max(0, energy_savings),
                    implementation_code=f"const int SENSOR_INTERVAL = {int(recommended_sampling_interval)} * 1000; // ms",
                    risk_assessment="Low risk - May reduce data granularity"
                ))
        
        except Exception as e:
            logger.error(f"Error generating energy optimizations: {e}")
        
        return recommendations
    
    async def start_real_time_monitoring(self):
        """실시간 모니터링 시작"""
        logger.info("Starting real-time monitoring system...")
        
        # MQTT 연결
        await self._connect_mqtt()
        
        # Kafka 컨슈머 시작
        await self._start_kafka_consumer()
        
        # 웹소켓 서버 시작
        await self._start_websocket_server()
        
        logger.info("Real-time monitoring system started successfully")
    
    async def _connect_mqtt(self):
        """MQTT 브로커 연결"""
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.info("Connected to MQTT broker")
                client.subscribe("arduino/+/sensors")  # 모든 디바이스 센서 데이터
                client.subscribe("arduino/+/status")   # 디바이스 상태
            else:
                logger.error(f"Failed to connect to MQTT broker: {rc}")
        
        def on_message(client, userdata, msg):
            try:
                topic_parts = msg.topic.split('/')
                device_id = topic_parts[1]
                data_type = topic_parts[2]
                
                payload = json.loads(msg.payload.decode())
                
                if data_type == 'sensors':
                    # 센서 데이터 처리
                    asyncio.create_task(self._process_sensor_data(device_id, payload))
                elif data_type == 'status':
                    # 상태 데이터 처리
                    asyncio.create_task(self._process_status_data(device_id, payload))
                    
            except Exception as e:
                logger.error(f"Error processing MQTT message: {e}")
        
        self.mqtt_client.on_connect = on_connect
        self.mqtt_client.on_message = on_message
        
        mqtt_host = self.config.get('mqtt_host', 'localhost')
        mqtt_port = self.config.get('mqtt_port', 1883)
        
        self.mqtt_client.connect_async(mqtt_host, mqtt_port, 60)
        self.mqtt_client.loop_start()
    
    async def _process_sensor_data(self, device_id: str, payload: Dict[str, Any]):
        """센서 데이터 처리 및 예측 실행"""
        try:
            # 센서 데이터 파싱
            sensor_reading = SensorReading(
                device_id=device_id,
                timestamp=datetime.now(),
                temperature=payload.get('temperature', 0.0),
                humidity=payload.get('humidity', 0.0),
                pressure=payload.get('pressure', 0.0),
                light_level=payload.get('light_level', 0.0),
                soil_moisture=payload.get('soil_moisture', 0.0),
                battery_voltage=payload.get('battery_voltage', 0.0),
                cpu_usage=payload.get('cpu_usage', 0.0),
                memory_usage=payload.get('memory_usage', 0.0),
                wifi_signal_strength=payload.get('wifi_signal_strength', 0),
                error_count=payload.get('error_count', 0),
                uptime_hours=payload.get('uptime_hours', 0.0)
            )
            
            # InfluxDB에 저장
            await self._store_sensor_data(sensor_reading)
            
            # 최근 데이터 가져와서 예측 실행
            recent_data = await self._get_recent_sensor_data(device_id, hours=1)
            recent_data.append(sensor_reading)
            
            if len(recent_data) >= 5:  # 최소 5개 데이터 포인트 필요
                prediction_result = await self.predict_device_health(recent_data)
                
                # 예측 결과 브로드캐스트
                await self._broadcast_prediction(prediction_result)
        
        except Exception as e:
            logger.error(f"Error processing sensor data for device {device_id}: {e}")
    
    def _save_models(self):
        """모델들을 디스크에 저장"""
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        
        # TensorFlow 모델들 저장
        for name, model in self.models.items():
            if hasattr(model, 'save'):
                model.save(models_dir / f"{name}.h5")
            else:
                joblib.dump(model, models_dir / f"{name}.pkl")
        
        # 스케일러들 저장
        scalers_dir = models_dir / "scalers"
        scalers_dir.mkdir(exist_ok=True)
        
        for name, scaler in self.scalers.items():
            joblib.dump(scaler, scalers_dir / f"{name}.pkl")
        
        logger.info("All models and scalers saved successfully")

# 사용 예시 및 메인 실행부
async def main():
    """메인 실행 함수"""
    
    # 설정
    config = {
        'redis_host': 'localhost',
        'redis_port': 6379,
        'influxdb_url': 'http://localhost:8086',
        'influxdb_token': 'your-influxdb-token',
        'influxdb_org': 'arduino-devops',
        'kafka_servers': ['localhost:9092'],
        'mqtt_host': 'localhost',
        'mqtt_port': 1883
    }
    
    # ML 예측 시스템 초기화
    predictor = ArduinoMLPredictor(config)
    
    # 예시 학습 데이터 생성 (실제로는 데이터베이스에서 로드)
    print("🧠 생성 중: 예시 학습 데이터...")
    historical_data = generate_sample_training_data(1000)  # 1000개 샘플
    
    # 모델 학습
    print("🚀 시작: AI 모델 학습...")
    await predictor.train_models(historical_data)
    
    # 실시간 모니터링 시작
    print("📊 시작: 실시간 모니터링...")
    await predictor.start_real_time_monitoring()
    
    # 예시 예측 실행
    print("🔮 실행: 디바이스 건강 예측...")
    sample_sensor_data = generate_sample_sensor_data("ESP32-001")
    prediction = await predictor.predict_device_health(sample_sensor_data)
    
    print(f"""
    🎯 예측 결과:
    - 디바이스: {prediction.device_id}
    - 장애 확률: {prediction.failure_probability:.3f}
    - 이상 점수: {prediction.anomaly_score:.3f}
    - 건강 점수: {prediction.health_score:.1f}/100
    - 신뢰도: {prediction.confidence_score:.3f}
    
    🔧 권고사항:
    """)
    
    for i, action in enumerate(prediction.recommended_actions, 1):
        print(f"    {i}. {action}")
    
    print("\n✅ AI 기반 예측 모니터링 시스템 구동 완료!")

def generate_sample_training_data(n_samples: int) -> pd.DataFrame:
    """예시 학습 데이터 생성"""
    np.random.seed(42)
    
    data = []
    for i in range(n_samples):
        # 정상 데이터 (80%)
        if i < n_samples * 0.8:
            temperature = np.random.normal(25, 5)
            humidity = np.random.normal(60, 15)
            battery_voltage = np.random.normal(3.7, 0.2)
            error_count = np.random.poisson(0.1)
            failure = 0
        # 이상 데이터 (20%)
        else:
            temperature = np.random.normal(40, 10)  # 높은 온도
            humidity = np.random.normal(80, 20)     # 높은 습도
            battery_voltage = np.random.normal(3.2, 0.3)  # 낮은 배터리
            error_count = np.random.poisson(2)      # 많은 에러
            failure = 1
        
        data.append({
            'device_id': f'ESP32-{i%10:03d}',
            'timestamp': datetime.now() - timedelta(hours=i),
            'temperature': temperature,
            'humidity': humidity,
            'pressure': np.random.normal(1013, 20),
            'light_level': np.random.uniform(0, 100),
            'soil_moisture': np.random.uniform(20, 80),
            'battery_voltage': battery_voltage,
            'cpu_usage': np.random.uniform(10, 90),
            'memory_usage': np.random.uniform(20, 80),
            'wifi_signal_strength': np.random.randint(-80, -30),
            'error_count': error_count,
            'uptime_hours': np.random.uniform(1, 168),
            'failure': failure
        })
    
    return pd.DataFrame(data)

def generate_sample_sensor_data(device_id: str) -> List[SensorReading]:
    """예시 센서 데이터 생성"""
    readings = []
    base_time = datetime.now()
    
    for i in range(24):  # 24시간 데이터
        reading = SensorReading(
            device_id=device_id,
            timestamp=base_time - timedelta(hours=23-i),
            temperature=25 + np.random.normal(0, 2),
            humidity=60 + np.random.normal(0, 10),
            pressure=1013 + np.random.normal(0, 10),
            light_level=np.random.uniform(0, 100),
            soil_moisture=np.random.uniform(40, 70),
            battery_voltage=3.7 + np.random.normal(0, 0.1),
            cpu_usage=np.random.uniform(20, 60),
            memory_usage=np.random.uniform(30, 70),
            wifi_signal_strength=np.random.randint(-70, -40),
            error_count=np.random.poisson(0.1),
            uptime_hours=i + 1
        )
        readings.append(reading)
    
    return readings

if __name__ == "__main__":
    asyncio.run(main())