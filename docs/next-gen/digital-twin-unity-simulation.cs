/*
 * 🔮 Digital Twin Unity 실시간 시뮬레이션 엔진
 * Arduino IoT 디바이스의 완전한 가상 복제본 및 예측 시뮬레이션
 */

using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Sensors;
using Unity.MLAgents.Actuators;
using Unity.Netcode;
using Unity.Collections;
using Newtonsoft.Json;
using WebSocketSharp;
using System.Threading.Tasks;

namespace ArduinoDigitalTwin
{
    // 📊 센서 데이터 구조체
    [System.Serializable]
    public struct SensorData
    {
        public string deviceId;
        public DateTime timestamp;
        public float temperature;
        public float humidity;
        public float pressure;
        public float lightLevel;
        public float soilMoisture;
        public float batteryVoltage;
        public float cpuUsage;
        public float memoryUsage;
        public int wifiSignalStrength;
        public int errorCount;
        public float uptimeHours;
        
        // 물리 시뮬레이션을 위한 추가 데이터
        public Vector3 devicePosition;
        public Vector3 deviceRotation;
        public float ambientTemperature;
        public float airflow;
        public bool powerStatus;
    }

    // 🎮 예측 결과 구조체
    [System.Serializable]
    public struct PredictionResult
    {
        public float failureProbability;
        public DateTime predictedFailureTime;
        public float healthScore;
        public float[] optimizedSettings;
        public string[] recommendations;
        public float confidenceScore;
    }

    // 🌡️ 환경 시뮬레이션 매니저
    public class EnvironmentSimulation : MonoBehaviour
    {
        [Header("Environment Settings")]
        public float baseTemperature = 25f;
        public float baseHumidity = 60f;
        public float basePressure = 1013f;
        public float temperatureVariance = 5f;
        public float humidityVariance = 15f;
        
        [Header("Weather System")]
        public bool enableWeatherSystem = true;
        public WeatherType currentWeather = WeatherType.Clear;
        public float weatherTransitionSpeed = 1f;
        
        [Header("Day/Night Cycle")]
        public bool enableDayNightCycle = true;
        public float dayDuration = 300f; // 5분 = 24시간
        public AnimationCurve temperatureCurve;
        public AnimationCurve lightCurve;
        
        // 파티클 시스템들
        public ParticleSystem temperatureParticles;
        public ParticleSystem humidityParticles;
        public ParticleSystem airflowParticles;
        public ParticleSystem dustParticles;
        
        // 조명 시스템
        public Light sunLight;
        public Light moonLight;
        public Gradient sunColor;
        public Gradient skyColor;
        
        private float currentTime = 0f;
        private Coroutine weatherCoroutine;
        
        public enum WeatherType
        {
            Clear,
            Cloudy,
            Rainy,
            Stormy,
            Foggy,
            Hot,
            Cold
        }
        
        void Start()
        {
            if (enableWeatherSystem)
                weatherCoroutine = StartCoroutine(WeatherSimulation());
        }
        
        void Update()
        {
            if (enableDayNightCycle)
                UpdateDayNightCycle();
                
            UpdateEnvironmentalEffects();
        }
        
        void UpdateDayNightCycle()
        {
            currentTime += Time.deltaTime;
            float timeRatio = (currentTime % dayDuration) / dayDuration;
            
            // 온도 변화
            float tempModifier = temperatureCurve.Evaluate(timeRatio) * temperatureVariance;
            float currentTemp = baseTemperature + tempModifier;
            
            // 조명 변화
            float lightIntensity = lightCurve.Evaluate(timeRatio);
            sunLight.intensity = lightIntensity;
            moonLight.intensity = Mathf.Max(0, 0.2f - lightIntensity);
            
            // 색상 변화
            sunLight.color = sunColor.Evaluate(timeRatio);
            RenderSettings.ambientSkyColor = skyColor.Evaluate(timeRatio);
        }
        
        IEnumerator WeatherSimulation()
        {
            while (true)
            {
                yield return new WaitForSeconds(UnityEngine.Random.Range(60f, 180f));
                
                // 랜덤 날씨 변화
                WeatherType newWeather = (WeatherType)UnityEngine.Random.Range(0, System.Enum.GetValues(typeof(WeatherType)).Length);
                yield return StartCoroutine(TransitionToWeather(newWeather));
            }
        }
        
        IEnumerator TransitionToWeather(WeatherType targetWeather)
        {
            WeatherType startWeather = currentWeather;
            float transitionTime = 30f; // 30초 전환
            float elapsed = 0f;
            
            while (elapsed < transitionTime)
            {
                elapsed += Time.deltaTime;
                float progress = elapsed / transitionTime;
                
                ApplyWeatherEffects(startWeather, targetWeather, progress);
                
                yield return null;
            }
            
            currentWeather = targetWeather;
        }
        
        void ApplyWeatherEffects(WeatherType from, WeatherType to, float progress)
        {
            switch (to)
            {
                case WeatherType.Rainy:
                    var rainEmission = humidityParticles.emission;
                    rainEmission.rateOverTime = Mathf.Lerp(0, 100, progress);
                    break;
                    
                case WeatherType.Stormy:
                    // 바람 효과
                    var windEmission = airflowParticles.emission;
                    windEmission.rateOverTime = Mathf.Lerp(10, 200, progress);
                    
                    // 번개 효과 (간헐적)
                    if (UnityEngine.Random.value < 0.1f * progress)
                    {
                        StartCoroutine(LightningEffect());
                    }
                    break;
                    
                case WeatherType.Hot:
                    // 열기 효과
                    var heatEmission = temperatureParticles.emission;
                    heatEmission.rateOverTime = Mathf.Lerp(20, 150, progress);
                    break;
                    
                case WeatherType.Foggy:
                    // 안개 효과
                    RenderSettings.fogDensity = Mathf.Lerp(0.01f, 0.05f, progress);
                    break;
            }
        }
        
        IEnumerator LightningEffect()
        {
            float originalIntensity = sunLight.intensity;
            sunLight.intensity = 3f;
            yield return new WaitForSeconds(0.1f);
            sunLight.intensity = originalIntensity;
        }
        
        void UpdateEnvironmentalEffects()
        {
            // 온도에 따른 파티클 효과
            var tempEmission = temperatureParticles.emission;
            tempEmission.rateOverTime = Mathf.Max(0, (GetCurrentTemperature() - 20f) * 3f);
            
            // 습도에 따른 효과
            var humidityEmission = humidityParticles.emission;
            humidityEmission.rateOverTime = Mathf.Max(0, (GetCurrentHumidity() - 40f) * 2f);
        }
        
        public float GetCurrentTemperature()
        {
            float timeRatio = (currentTime % dayDuration) / dayDuration;
            float tempModifier = temperatureCurve.Evaluate(timeRatio) * temperatureVariance;
            float weatherModifier = GetWeatherTemperatureModifier();
            
            return baseTemperature + tempModifier + weatherModifier;
        }
        
        public float GetCurrentHumidity()
        {
            float weatherModifier = GetWeatherHumidityModifier();
            return Mathf.Clamp(baseHumidity + weatherModifier, 0f, 100f);
        }
        
        public float GetCurrentPressure()
        {
            float weatherModifier = GetWeatherPressureModifier();
            return basePressure + weatherModifier;
        }
        
        public float GetCurrentLightLevel()
        {
            if (!enableDayNightCycle) return 50f;
            
            float timeRatio = (currentTime % dayDuration) / dayDuration;
            float lightIntensity = lightCurve.Evaluate(timeRatio);
            return lightIntensity * 100f;
        }
        
        float GetWeatherTemperatureModifier()
        {
            switch (currentWeather)
            {
                case WeatherType.Hot: return 10f;
                case WeatherType.Cold: return -15f;
                case WeatherType.Rainy: return -5f;
                case WeatherType.Stormy: return -8f;
                case WeatherType.Cloudy: return -3f;
                default: return 0f;
            }
        }
        
        float GetWeatherHumidityModifier()
        {
            switch (currentWeather)
            {
                case WeatherType.Rainy: return 30f;
                case WeatherType.Stormy: return 25f;
                case WeatherType.Foggy: return 35f;
                case WeatherType.Hot: return -20f;
                default: return 0f;
            }
        }
        
        float GetWeatherPressureModifier()
        {
            switch (currentWeather)
            {
                case WeatherType.Stormy: return -20f;
                case WeatherType.Rainy: return -10f;
                case WeatherType.Clear: return 5f;
                default: return 0f;
            }
        }
    }

    // 🤖 AI 기반 디바이스 에이전트
    public class ArduinoDeviceAgent : Agent
    {
        [Header("Device Configuration")]
        public string deviceId = "ESP32-SIM-001";
        public Transform deviceTransform;
        public Renderer deviceRenderer;
        public ParticleSystem statusIndicator;
        
        [Header("Sensor Configuration")]
        public Transform[] sensorPositions;
        public LineRenderer[] sensorConnections;
        public GameObject[] sensorVisuals;
        
        [Header("AI Learning")]
        public bool enableLearning = true;
        public float learningRate = 0.01f;
        public int maxDecisionSteps = 1000;
        
        // 센서 데이터
        private SensorData currentSensorData;
        private SensorData lastSensorData;
        
        // 환경 참조
        private EnvironmentSimulation environment;
        private ArduinoDigitalTwinManager twinManager;
        
        // 액션 공간 (8개 액션)
        // 0: CPU 주파수 조절, 1: WiFi 파워 세이브, 2: 센서 샘플링 간격, 3: 슬립 모드
        // 4: LED 밝기, 5: 팬 속도, 6: 히터 파워, 7: 워터 펌프
        private float[] currentActions = new float[8];
        
        // 성능 메트릭
        private float energyEfficiency = 100f;
        private float performanceScore = 100f;
        private float reliabilityScore = 100f;
        
        public override void Initialize()
        {
            environment = FindObjectOfType<EnvironmentSimulation>();
            twinManager = FindObjectOfType<ArduinoDigitalTwinManager>();
            
            // 초기 센서 데이터 설정
            currentSensorData = new SensorData
            {
                deviceId = deviceId,
                timestamp = DateTime.Now,
                devicePosition = transform.position,
                deviceRotation = transform.eulerAngles,
                powerStatus = true
            };
            
            SetupVisualElements();
        }
        
        void SetupVisualElements()
        {
            // 센서 시각화 설정
            for (int i = 0; i < sensorConnections.Length; i++)
            {
                if (i < sensorPositions.Length)
                {
                    var line = sensorConnections[i];
                    line.positionCount = 2;
                    line.SetPosition(0, deviceTransform.position);
                    line.SetPosition(1, sensorPositions[i].position);
                }
            }
        }
        
        public override void OnEpisodeBegin()
        {
            // 에피소드 시작 시 랜덤 환경 조건 설정
            energyEfficiency = 100f;
            performanceScore = 100f;
            reliabilityScore = 100f;
            
            // 랜덤 위치 배치 (학습용)
            if (enableLearning)
            {
                transform.position = new Vector3(
                    UnityEngine.Random.Range(-5f, 5f),
                    UnityEngine.Random.Range(0.5f, 2f),
                    UnityEngine.Random.Range(-5f, 5f)
                );
            }
            
            UpdateSensorData();
        }
        
        public override void CollectObservations(VectorSensor sensor)
        {
            // 환경 데이터 관찰
            sensor.AddObservation(currentSensorData.temperature / 50f); // 정규화
            sensor.AddObservation(currentSensorData.humidity / 100f);
            sensor.AddObservation(currentSensorData.pressure / 1100f);
            sensor.AddObservation(currentSensorData.lightLevel / 100f);
            sensor.AddObservation(currentSensorData.soilMoisture / 100f);
            sensor.AddObservation(currentSensorData.batteryVoltage / 5f);
            sensor.AddObservation(currentSensorData.cpuUsage / 100f);
            sensor.AddObservation(currentSensorData.memoryUsage / 100f);
            sensor.AddObservation(currentSensorData.wifiSignalStrength / -30f);
            
            // 현재 액션 상태
            for (int i = 0; i < currentActions.Length; i++)
            {
                sensor.AddObservation(currentActions[i]);
            }
            
            // 성능 메트릭
            sensor.AddObservation(energyEfficiency / 100f);
            sensor.AddObservation(performanceScore / 100f);
            sensor.AddObservation(reliabilityScore / 100f);
            
            // 시간 정보
            float timeOfDay = ((float)DateTime.Now.Hour) / 24f;
            sensor.AddObservation(timeOfDay);
        }
        
        public override void OnActionReceived(ActionBuffers actionBuffers)
        {
            var continuousActions = actionBuffers.ContinuousActions;
            
            // 액션 적용
            for (int i = 0; i < currentActions.Length; i++)
            {
                currentActions[i] = Mathf.Clamp(continuousActions[i], -1f, 1f);
            }
            
            // 액션에 따른 디바이스 상태 업데이트
            ApplyActions();
            
            // 보상 계산
            float reward = CalculateReward();
            AddReward(reward);
            
            // 시각적 피드백 업데이트
            UpdateVisualFeedback();
            
            // 센서 데이터 업데이트
            UpdateSensorData();
            
            // 종료 조건 체크
            if (energyEfficiency <= 0f || reliabilityScore <= 0f)
            {
                EndEpisode();
            }
        }
        
        void ApplyActions()
        {
            // CPU 주파수 조절 (액션 0)
            float cpuFreqModifier = currentActions[0];
            currentSensorData.cpuUsage = Mathf.Clamp(
                currentSensorData.cpuUsage + cpuFreqModifier * 10f, 
                10f, 100f
            );
            
            // 전력 효율에 영향
            energyEfficiency += cpuFreqModifier < 0 ? 2f : -1f;
            
            // WiFi 파워 세이브 (액션 1)
            float wifiPowerSave = currentActions[1];
            if (wifiPowerSave > 0.5f)
            {
                energyEfficiency += 1f;
                currentSensorData.wifiSignalStrength = Mathf.Max(
                    currentSensorData.wifiSignalStrength - 5, -90
                );
            }
            
            // 센서 샘플링 간격 (액션 2)
            float samplingRate = currentActions[2];
            if (samplingRate < 0)
            {
                // 낮은 샘플링 = 에너지 절약
                energyEfficiency += 1.5f;
                performanceScore -= 0.5f; // 정확도 감소
            }
            else
            {
                // 높은 샘플링 = 높은 정확도
                energyEfficiency -= 1f;
                performanceScore += 1f;
            }
            
            // 슬립 모드 (액션 3)
            float sleepMode = currentActions[3];
            if (sleepMode > 0.5f)
            {
                energyEfficiency += 3f;
                performanceScore -= 2f; // 응답성 감소
            }
            
            // LED 밝기 제어 (액션 4)
            float ledBrightness = (currentActions[4] + 1f) / 2f; // 0-1 변환
            var emission = statusIndicator.emission;
            emission.rateOverTime = ledBrightness * 50f;
            
            // 팬 속도 (액션 5) - 온도 제어
            float fanSpeed = (currentActions[5] + 1f) / 2f;
            if (currentSensorData.temperature > 35f && fanSpeed > 0.5f)
            {
                currentSensorData.temperature -= 2f * fanSpeed;
                energyEfficiency -= fanSpeed * 1f;
                reliabilityScore += 1f; // 과열 방지
            }
            
            // 히터 파워 (액션 6) - 온도 제어
            float heaterPower = (currentActions[6] + 1f) / 2f;
            if (currentSensorData.temperature < 15f && heaterPower > 0.5f)
            {
                currentSensorData.temperature += 3f * heaterPower;
                energyEfficiency -= heaterPower * 2f;
                reliabilityScore += 1f; // 저온 방지
            }
            
            // 워터 펌프 (액션 7) - 습도 제어
            float pumpPower = (currentActions[7] + 1f) / 2f;
            if (currentSensorData.soilMoisture < 30f && pumpPower > 0.5f)
            {
                currentSensorData.soilMoisture += 5f * pumpPower;
                energyEfficiency -= pumpPower * 1.5f;
            }
        }
        
        float CalculateReward()
        {
            float reward = 0f;
            
            // 에너지 효율성 보상
            reward += (energyEfficiency - 50f) / 50f * 0.3f;
            
            // 성능 보상
            reward += (performanceScore - 50f) / 50f * 0.3f;
            
            // 신뢰성 보상
            reward += (reliabilityScore - 50f) / 50f * 0.4f;
            
            // 온도 최적화 보상
            float tempOptimal = Mathf.Abs(currentSensorData.temperature - 25f);
            reward += (10f - tempOptimal) / 10f * 0.2f;
            
            // 배터리 보상
            if (currentSensorData.batteryVoltage > 3.5f)
                reward += 0.1f;
            else if (currentSensorData.batteryVoltage < 3.2f)
                reward -= 0.3f;
            
            // 에러 페널티
            reward -= currentSensorData.errorCount * 0.01f;
            
            return Mathf.Clamp(reward, -1f, 1f);
        }
        
        void UpdateSensorData()
        {
            lastSensorData = currentSensorData;
            
            // 환경에서 데이터 가져오기
            if (environment != null)
            {
                currentSensorData.temperature = environment.GetCurrentTemperature();
                currentSensorData.humidity = environment.GetCurrentHumidity();
                currentSensorData.pressure = environment.GetCurrentPressure();
                currentSensorData.lightLevel = environment.GetCurrentLightLevel();
            }
            
            // 시뮬레이션된 센서 노이즈 추가
            currentSensorData.temperature += UnityEngine.Random.Range(-0.5f, 0.5f);
            currentSensorData.humidity += UnityEngine.Random.Range(-2f, 2f);
            currentSensorData.pressure += UnityEngine.Random.Range(-1f, 1f);
            
            // 토양 수분은 서서히 감소
            currentSensorData.soilMoisture = Mathf.Max(0f, 
                currentSensorData.soilMoisture - Time.deltaTime * 0.1f);
            
            // 배터리는 사용량에 따라 감소
            float batteryDrain = (currentSensorData.cpuUsage / 100f) * 0.001f * Time.deltaTime;
            currentSensorData.batteryVoltage = Mathf.Max(3.0f, 
                currentSensorData.batteryVoltage - batteryDrain);
            
            // 메모리 사용량 시뮬레이션
            currentSensorData.memoryUsage = Mathf.Clamp(
                currentSensorData.memoryUsage + UnityEngine.Random.Range(-5f, 5f),
                20f, 95f
            );
            
            // WiFi 신호 강도 변동
            currentSensorData.wifiSignalStrength += UnityEngine.Random.Range(-3, 3);
            currentSensorData.wifiSignalStrength = Mathf.Clamp(
                currentSensorData.wifiSignalStrength, -90, -30);
            
            // 에러 카운트 (확률적 증가)
            if (UnityEngine.Random.value < 0.01f) // 1% 확률
            {
                currentSensorData.errorCount++;
            }
            
            // 업타임 증가
            currentSensorData.uptimeHours += Time.deltaTime / 3600f;
            
            currentSensorData.timestamp = DateTime.Now;
        }
        
        void UpdateVisualFeedback()
        {
            // 디바이스 색상 변경 (상태에 따라)
            Color statusColor = Color.green;
            
            if (energyEfficiency < 30f || reliabilityScore < 30f)
                statusColor = Color.red;
            else if (energyEfficiency < 60f || reliabilityScore < 60f)
                statusColor = Color.yellow;
            
            if (deviceRenderer != null)
                deviceRenderer.material.color = statusColor;
            
            // 센서 연결선 업데이트
            UpdateSensorConnections();
            
            // 파티클 시스템 업데이트
            UpdateParticleEffects();
        }
        
        void UpdateSensorConnections()
        {
            for (int i = 0; i < sensorConnections.Length && i < sensorPositions.Length; i++)
            {
                var line = sensorConnections[i];
                
                // 센서 활성 상태에 따른 색상
                Color lineColor = currentSensorData.powerStatus ? Color.cyan : Color.gray;
                lineColor.a = 0.7f;
                
                line.startColor = lineColor;
                line.endColor = lineColor;
                
                // 데이터 전송 효과 (애니메이션)
                float pulseIntensity = Mathf.Sin(Time.time * 5f) * 0.3f + 0.7f;
                lineColor.a *= pulseIntensity;
                line.material.color = lineColor;
            }
        }
        
        void UpdateParticleEffects()
        {
            if (statusIndicator != null)
            {
                var main = statusIndicator.main;
                
                // 온도에 따른 색상 변화
                if (currentSensorData.temperature > 40f)
                    main.startColor = Color.red;
                else if (currentSensorData.temperature < 10f)
                    main.startColor = Color.blue;
                else
                    main.startColor = Color.green;
                
                // 배터리 레벨에 따른 파티클 수
                var emission = statusIndicator.emission;
                emission.rateOverTime = currentSensorData.batteryVoltage * 10f;
            }
        }
        
        // 외부에서 호출 가능한 메서드들
        public SensorData GetCurrentSensorData()
        {
            return currentSensorData;
        }
        
        public void SetSensorData(SensorData data)
        {
            currentSensorData = data;
            UpdateVisualFeedback();
        }
        
        public PredictionResult GetPredictionResult()
        {
            return new PredictionResult
            {
                failureProbability = (100f - reliabilityScore) / 100f,
                predictedFailureTime = DateTime.Now.AddHours(reliabilityScore / 10f),
                healthScore = (energyEfficiency + performanceScore + reliabilityScore) / 3f,
                optimizedSettings = currentActions,
                recommendations = GenerateRecommendations(),
                confidenceScore = performanceScore / 100f
            };
        }
        
        string[] GenerateRecommendations()
        {
            List<string> recommendations = new List<string>();
            
            if (energyEfficiency < 50f)
                recommendations.Add("Consider enabling power-saving modes");
            
            if (currentSensorData.temperature > 35f)
                recommendations.Add("Improve ventilation or enable cooling");
            
            if (currentSensorData.batteryVoltage < 3.3f)
                recommendations.Add("Battery replacement needed soon");
            
            if (currentSensorData.memoryUsage > 80f)
                recommendations.Add("Memory optimization required");
            
            if (currentSensorData.wifiSignalStrength < -75)
                recommendations.Add("Improve WiFi antenna position");
            
            return recommendations.ToArray();
        }
        
        public override void Heuristic(in ActionBuffers actionsOut)
        {
            // 휴리스틱 (수동 제어) - 테스팅용
            var continuousActionsOut = actionsOut.ContinuousActions;
            
            // 키보드 입력으로 수동 제어
            continuousActionsOut[0] = Input.GetAxis("Horizontal"); // CPU 주파수
            continuousActionsOut[1] = Input.GetKey(KeyCode.P) ? 1f : 0f; // WiFi 파워 세이브
            continuousActionsOut[2] = Input.GetAxis("Vertical"); // 센서 샘플링
            continuousActionsOut[3] = Input.GetKey(KeyCode.S) ? 1f : 0f; // 슬립 모드
            
            // 나머지는 기본값
            for (int i = 4; i < continuousActionsOut.Length; i++)
            {
                continuousActionsOut[i] = 0f;
            }
        }
    }

    // 🎯 Digital Twin 메인 매니저
    public class ArduinoDigitalTwinManager : NetworkBehaviour
    {
        [Header("Network Configuration")]
        public string websocketUrl = "ws://localhost:8080";
        public string mqttBroker = "localhost";
        public int mqttPort = 1883;
        
        [Header("Twin Configuration")]
        public int maxConcurrentDevices = 10;
        public float updateInterval = 1f;
        public bool enablePredictiveAnalysis = true;
        public bool enableRealTimeSync = true;
        
        [Header("Prefabs")]
        public GameObject devicePrefab;
        public GameObject environmentPrefab;
        
        // 디바이스 관리
        private Dictionary<string, ArduinoDeviceAgent> digitalTwins = new Dictionary<string, ArduinoDeviceAgent>();
        private EnvironmentSimulation environment;
        
        // 네트워크 연결
        private WebSocket webSocket;
        private bool isConnected = false;
        
        // 데이터 관리
        private Queue<SensorData> dataQueue = new Queue<SensorData>();
        private Dictionary<string, List<SensorData>> historicalData = new Dictionary<string, List<SensorData>>();
        
        void Start()
        {
            // 환경 초기화
            if (environmentPrefab != null)
            {
                GameObject envObj = Instantiate(environmentPrefab);
                environment = envObj.GetComponent<EnvironmentSimulation>();
            }
            
            // 네트워크 연결 시작
            if (enableRealTimeSync)
            {
                StartCoroutine(InitializeConnections());
            }
            
            // 정기 업데이트 시작
            InvokeRepeating(nameof(UpdateAllTwins), 1f, updateInterval);
        }
        
        IEnumerator InitializeConnections()
        {
            yield return StartCoroutine(ConnectWebSocket());
            // 추가 연결들 (MQTT 등) 초기화 가능
        }
        
        IEnumerator ConnectWebSocket()
        {
            try
            {
                webSocket = new WebSocket(websocketUrl);
                
                webSocket.OnOpen += (sender, e) =>
                {
                    Debug.Log("WebSocket connected to real hardware");
                    isConnected = true;
                };
                
                webSocket.OnMessage += (sender, e) =>
                {
                    try
                    {
                        var sensorData = JsonConvert.DeserializeObject<SensorData>(e.Data);
                        ProcessRealHardwareData(sensorData);
                    }
                    catch (Exception ex)
                    {
                        Debug.LogError($"Error processing WebSocket message: {ex.Message}");
                    }
                };
                
                webSocket.OnError += (sender, e) =>
                {
                    Debug.LogError($"WebSocket error: {e.Message}");
                    isConnected = false;
                };
                
                webSocket.OnClose += (sender, e) =>
                {
                    Debug.Log("WebSocket connection closed");
                    isConnected = false;
                };
                
                webSocket.Connect();
                
                // 연결 대기
                float timeout = 10f;
                while (!isConnected && timeout > 0)
                {
                    yield return new WaitForSeconds(0.1f);
                    timeout -= 0.1f;
                }
                
                if (!isConnected)
                {
                    Debug.LogWarning("WebSocket connection timeout - running in simulation mode only");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"WebSocket connection failed: {ex.Message}");
            }
        }
        
        void ProcessRealHardwareData(SensorData data)
        {
            // 실제 하드웨어 데이터 처리
            if (digitalTwins.ContainsKey(data.deviceId))
            {
                // 기존 Digital Twin 업데이트
                digitalTwins[data.deviceId].SetSensorData(data);
            }
            else
            {
                // 새로운 Digital Twin 생성
                CreateDigitalTwin(data.deviceId, data);
            }
            
            // 히스토리 저장
            if (!historicalData.ContainsKey(data.deviceId))
            {
                historicalData[data.deviceId] = new List<SensorData>();
            }
            
            historicalData[data.deviceId].Add(data);
            
            // 큐에 추가 (후처리용)
            dataQueue.Enqueue(data);
        }
        
        public void CreateDigitalTwin(string deviceId, SensorData initialData)
        {
            if (digitalTwins.Count >= maxConcurrentDevices)
            {
                Debug.LogWarning("Maximum concurrent devices reached");
                return;
            }
            
            Vector3 spawnPosition = new Vector3(
                digitalTwins.Count * 3f, 1f, 0f
            );
            
            GameObject twinObj = Instantiate(devicePrefab, spawnPosition, Quaternion.identity);
            ArduinoDeviceAgent agent = twinObj.GetComponent<ArduinoDeviceAgent>();
            
            if (agent != null)
            {
                agent.deviceId = deviceId;
                agent.SetSensorData(initialData);
                digitalTwins[deviceId] = agent;
                
                Debug.Log($"Digital Twin created for device: {deviceId}");
            }
        }
        
        void UpdateAllTwins()
        {
            foreach (var twin in digitalTwins.Values)
            {
                if (twin != null)
                {
                    // 예측 분석 실행
                    if (enablePredictiveAnalysis)
                    {
                        var prediction = twin.GetPredictionResult();
                        ProcessPredictionResult(twin.deviceId, prediction);
                    }
                }
            }
            
            // 큐 처리
            ProcessDataQueue();
        }
        
        void ProcessPredictionResult(string deviceId, PredictionResult prediction)
        {
            // 예측 결과에 따른 알림 또는 액션
            if (prediction.failureProbability > 0.8f)
            {
                Debug.LogWarning($"High failure probability for device {deviceId}: {prediction.failureProbability:F2}");
                
                // 실제 하드웨어에 최적화 명령 전송
                if (isConnected && webSocket != null)
                {
                    var optimizationCommand = new
                    {
                        deviceId = deviceId,
                        command = "optimize_settings",
                        settings = prediction.optimizedSettings,
                        timestamp = DateTime.Now
                    };
                    
                    webSocket.Send(JsonConvert.SerializeObject(optimizationCommand));
                }
            }
        }
        
        void ProcessDataQueue()
        {
            int processed = 0;
            int maxProcessPerFrame = 5;
            
            while (dataQueue.Count > 0 && processed < maxProcessPerFrame)
            {
                var data = dataQueue.Dequeue();
                // 추가 데이터 처리 로직
                processed++;
            }
        }
        
        // 외부 API
        public Dictionary<string, SensorData> GetAllCurrentData()
        {
            var result = new Dictionary<string, SensorData>();
            
            foreach (var kvp in digitalTwins)
            {
                result[kvp.Key] = kvp.Value.GetCurrentSensorData();
            }
            
            return result;
        }
        
        public List<SensorData> GetHistoricalData(string deviceId, int hours = 24)
        {
            if (historicalData.ContainsKey(deviceId))
            {
                var cutoff = DateTime.Now.AddHours(-hours);
                return historicalData[deviceId]
                    .Where(d => d.timestamp >= cutoff)
                    .ToList();
            }
            
            return new List<SensorData>();
        }
        
        public PredictionResult GetDevicePrediction(string deviceId)
        {
            if (digitalTwins.ContainsKey(deviceId))
            {
                return digitalTwins[deviceId].GetPredictionResult();
            }
            
            return new PredictionResult();
        }
        
        void OnDestroy()
        {
            // 연결 정리
            if (webSocket != null && isConnected)
            {
                webSocket.Close();
            }
        }
        
        // Unity Editor용 GUI
        void OnGUI()
        {
            if (!Application.isPlaying) return;
            
            GUILayout.BeginVertical("box");
            GUILayout.Label($"Digital Twins: {digitalTwins.Count}/{maxConcurrentDevices}");
            GUILayout.Label($"WebSocket: {(isConnected ? "Connected" : "Disconnected")}");
            GUILayout.Label($"Data Queue: {dataQueue.Count}");
            
            if (GUILayout.Button("Create Test Device"))
            {
                var testData = new SensorData
                {
                    deviceId = $"TEST-{UnityEngine.Random.Range(1000, 9999)}",
                    timestamp = DateTime.Now,
                    temperature = UnityEngine.Random.Range(20f, 30f),
                    humidity = UnityEngine.Random.Range(40f, 80f),
                    batteryVoltage = UnityEngine.Random.Range(3.2f, 4.0f),
                    powerStatus = true
                };
                
                CreateDigitalTwin(testData.deviceId, testData);
            }
            
            GUILayout.EndVertical();
        }
    }
}