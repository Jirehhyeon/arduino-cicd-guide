# 🔌 NeuroCity Smart Sensor v2.0 - Circuit Diagram & Hardware Guide

## 📋 Hardware Overview

### 🧠 Main Processing Unit: ESP32-S3-WROOM-1U
```
┌─────────────────────────────────────────────────────────────────┐
│                    ESP32-S3-WROOM-1U                            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  • Dual-core Xtensa LX7 @ 240MHz                       │    │
│  │  • 512KB SRAM, 384KB ROM                               │    │
│  │  • 16MB Flash, 8MB PSRAM                               │    │
│  │  • WiFi 6 (802.11ax), Bluetooth 5.2 LE               │    │
│  │  • AI 가속기 (Vector Extensions)                        │    │
│  │  • USB-C OTG (펌웨어 업데이트, 디버깅)                    │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 🌡️ Multi-Sensor Array Layout
```
                    ESP32-S3-WROOM-1U
                           │
                    ┌─────────────┐
                    │  I2C Hub    │
                    │  TCA9548A   │
                    └─────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌─────────┐      ┌─────────┐      ┌─────────┐
    │ SHT40   │      │ SGP40   │      │ BME688  │
    │ Temp/   │      │ VOC/    │      │ Gas/    │
    │ Humidity│      │ NOx     │      │ Air Qty │
    │ ±0.1°C  │      │ ppb     │      │ AI-based│
    │ Address:│      │ Address:│      │ Address:│
    │ 0x44    │      │ 0x59    │      │ 0x77    │
    └─────────┘      └─────────┘      └─────────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌─────────┐      ┌─────────┐      ┌─────────┐
    │ SCD41   │      │ INA219  │      │ MPU6050 │
    │ CO2     │      │ Power   │      │ 6-axis  │
    │ Sensor  │      │ Monitor │      │ IMU     │
    │ ±30ppm  │      │ V/I/P   │      │ Accel/  │
    │ Address:│      │ Address:│      │ Gyro    │
    │ 0x62    │      │ 0x40    │      │ Address:│
    │         │      │         │      │ 0x68    │
    └─────────┘      └─────────┘      └─────────┘
```

### 📡 Communication Modules
```
┌─────────────────────────────────────────────────────────────────┐
│                      Communication Stack                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                │
│  📶 Primary: WiFi 6 (802.11ax) - Built into ESP32-S3          │
│     • MU-MIMO, OFDMA support                                  │
│     • Max 1.2Gbps, Low latency (<1ms)                         │
│     • WPA3 security                                            │
│     • Pins: Internal WiFi module                              │
│                                                                │
│  🔵 Secondary: Bluetooth 5.2 LE - Built into ESP32-S3        │
│     • Mesh networking capability                              │
│     • 200m range in open space                                │
│     • Ultra-low power (μA level)                              │
│     • Pins: Internal BLE module                               │
│                                                                │
│  📡 Backup: LoRaWAN (Optional)                                │
│     • RFM95W Module                                            │
│     • 15km long-range communication                           │
│     • Emergency cloud connection                              │
│     • Pins: SPI (MISO:19, MOSI:23, SCK:18, CS:5)             │
│                                                                │
└─────────────────────────────────────────────────────────────────┘
```

### ⚡ Smart Power Management System
```
┌─────────────────────────────────────────────────────────────┐
│                   Hybrid Power System                       │
├─────────────────────────────────────────────────────────────┤
│                                                            │
│  ☀️ Solar Panel (6V, 2W) → Pin: ADC1_CH3 (GPIO 4)         │
│      │                                                     │
│      ▼                                                     │
│  🔋 Li-Po Battery (3.7V, 5000mAh) → Pin: ADC1_CH4 (GPIO 5)│
│      │                                                     │
│      ▼                                                     │
│  ⚡ Power Management IC (BQ25895) → I2C Address: 0x6B      │
│      • MPPT solar charging                                 │
│      • USB-C PD 3.0 fast charging                         │
│      • Wireless charging (Qi standard)                    │
│      • Dynamic voltage regulation                          │
│      │                                                     │
│      ▼                                                     │
│  🎛️ Power Distribution:                                    │
│      • ESP32-S3: 3.3V rail                                │
│      • Sensors: 3.3V rail                                 │
│      • LEDs: 3.3V with current limiting                   │
│      • Buzzer: 3.3V with PWM control                      │
│                                                            │
│  📊 Expected Battery Life:                                 │
│      • 30+ days (solar charging)                          │
│      • 7-14 days (battery only)                           │
│      • Unlimited (with adequate solar)                    │
└─────────────────────────────────────────────────────────────┘
```

### 🔒 Hardware Security Module
```
┌─────────────────────────────────────────────────────────┐
│                 Security Hardware                        │
├─────────────────────────────────────────────────────────┤
│                                                        │
│  🔐 ATECC608B Crypto Chip                              │
│      • I2C Address: 0x60                               │
│      • Pins: SDA (GPIO 42), SCL (GPIO 41)             │
│      • ECC P-256 hardware acceleration                 │
│      • Secure key storage (16 slots)                   │
│      • Hardware random number generator                │
│      • Tamper detection                                │
│                                                        │
│  🆔 Device Authentication Features:                    │
│      • X.509 certificate storage                       │
│      • Blockchain identity generation                  │
│      • Zero-knowledge proof support                    │
│      • Secure boot verification                        │
│                                                        │
│  🛡️ Physical Security:                                 │
│      • Tamper detection switch: GPIO 0                │
│      • Secure enclosure with ultrasonic welding        │
│      • Anti-tampering mesh layer                       │
│                                                        │
└─────────────────────────────────────────────────────────┘
```

### 💡 Status Indication System
```
┌─────────────────────────────────────────────────────────┐
│                 Visual & Audio Feedback                 │
├─────────────────────────────────────────────────────────┤
│                                                        │
│  🌈 RGB Status LED Array:                              │
│      • Red LED: GPIO 48 (PWM Channel 0)               │
│      • Green LED: GPIO 47 (PWM Channel 1)             │
│      • Blue LED: GPIO 21 (PWM Channel 2)              │
│      • Common Anode configuration                      │
│      • 220Ω current limiting resistors                │
│                                                        │
│  🔴 Error Indicator LED:                               │
│      • Pin: GPIO 38                                   │
│      • Red LED for critical errors                    │
│      • 330Ω current limiting resistor                 │
│                                                        │
│  📢 Piezo Buzzer:                                      │
│      • Pin: GPIO 39 (PWM Channel 3)                   │
│      • Frequency range: 100Hz - 10kHz                 │
│      • Emergency alerts and status sounds             │
│      • 100Ω current limiting resistor                 │
│                                                        │
│  🎛️ Setup Button:                                      │
│      • Pin: GPIO 0 (Boot button)                      │
│      • Pull-up resistor: 10kΩ                         │
│      • Factory reset and WiFi config                  │
│                                                        │
└─────────────────────────────────────────────────────────┘
```

## 🔌 Complete Circuit Diagram

### Main Schematic
```
                                  NeuroCity Smart Sensor v2.0
                              ┌─────────────────────────────┐
                              │      ESP32-S3-WROOM-1U     │
                              │                             │
                              │  3V3 ●──┬─────────────────  │
                              │        │                   │
                              │  GND ●──┼───────────────┬─  │
                              │        │               │   │
                              │  GPIO42 (SDA) ●────────┼─  │ ← I2C Data
                              │  GPIO41 (SCL) ●────────┼─  │ ← I2C Clock
                              │                       │   │
                              │  GPIO48 ●─────────────┼─  │ ← RGB Red
                              │  GPIO47 ●─────────────┼─  │ ← RGB Green  
                              │  GPIO21 ●─────────────┼─  │ ← RGB Blue
                              │  GPIO38 ●─────────────┼─  │ ← Error LED
                              │  GPIO39 ●─────────────┼─  │ ← Buzzer
                              │                       │   │
                              │  GPIO4 (ADC) ●────────┼─  │ ← Solar Monitor
                              │  GPIO5 (ADC) ●────────┼─  │ ← Battery Monitor
                              │                       │   │
                              │  GPIO0 ●──────────────┼─  │ ← Setup Button
                              │                       │   │
                              │  USB-C ●──────────────┼─  │ ← Programming/Power
                              └───────────────────────┼───┘
                                                     │
                              ┌─────────────────────┴───┐
                              │    I2C Sensor Network   │
                              ├─────────────────────────┤
                              │                         │
                              │  TCA9548A I2C Multiplexer │
                              │  Address: 0x70          │
                              │          │              │
                              │  ┌───────┼───────┐      │
                              │  │       │       │      │
                              │ SHT40   SGP40   BME688  │
                              │ 0x44    0x59    0x77    │
                              │  │       │       │      │
                              │  └───────┼───────┘      │
                              │          │              │
                              │  ┌───────┼───────┐      │
                              │  │       │       │      │
                              │ SCD41   INA219  MPU6050 │
                              │ 0x62    0x40    0x68    │
                              │          │              │
                              │  ┌───────┼───────┐      │
                              │  │       │              │
                              │ ATECC608B              │
                              │ 0x60                    │
                              └─────────────────────────┘

Power Management & Protection:
┌─────────────────────────────────────────────────────────────┐
│                                                            │
│  Solar Panel (6V/2W) ──┬── Schottky Diode (1N5819) ──┐    │
│                        │                              │    │
│  USB-C Power (5V) ─────┼── Protection Circuit ───────┼─┐  │
│                        │                              │ │  │
│  Qi Wireless (5V) ─────┘                              │ │  │
│                                                       │ │  │
│                                    BQ25895 Power IC ──┼─┼─ │
│                                    │                  │ │  │
│  Li-Po Battery (3.7V/5000mAh) ────┼──────────────────┘ │  │
│                                    │                    │  │
│                    3.3V Regulator ─┼────────────────────┼─ │
│                                    │                    │  │
│                    Load Switch ────┼────────────────────┘  │
│                                    │                       │
│                              To ESP32-S3                   │
└─────────────────────────────────────────────────────────────┘

Status LED Circuit:
┌─────────────────────────────────────────────────────────────┐
│                                                            │
│  GPIO48 ──┬── 220Ω ──┬── Red LED ──┬── Common Anode       │
│  GPIO47 ──┼── 220Ω ──┼── Green LED ┼── (+3.3V)            │
│  GPIO21 ──┼── 220Ω ──┼── Blue LED ─┘                      │
│           │          │                                    │
│  GPIO38 ──┼── 330Ω ──┼── Error LED ── GND                 │
│           │          │                                    │
│  GPIO39 ──┴── 100Ω ──┴── Buzzer ── GND                    │
│                                                            │
└─────────────────────────────────────────────────────────────┘
```

## 🏗️ PCB Layout Guidelines

### Layer Stack-up (4-layer PCB)
```
Layer 1 (Top):    Component placement and signal routing
Layer 2 (GND):    Ground plane with thermal relief
Layer 3 (Power):  3.3V power plane with decoupling
Layer 4 (Bottom): Additional routing and shield traces
```

### Design Rules
- **Trace Width**: 0.2mm minimum, 0.5mm for power
- **Via Size**: 0.2mm drill, 0.4mm pad
- **Clearance**: 0.15mm minimum
- **Board Thickness**: 1.6mm standard
- **Copper Weight**: 1oz (35μm) for all layers

### Component Placement Strategy
1. **ESP32-S3**: Center of board for optimal RF performance
2. **Sensors**: Grouped by I2C address to minimize crosstalk
3. **Power Management**: Isolated section with thick traces
4. **Crystal**: Close to ESP32-S3 with ground guards
5. **Antenna**: Keep-out zones for optimal radiation

## 📦 3D Enclosure Design

### Enclosure Specifications
```
┌─────────────────────────────────────────────────────────────┐
│                    NeuroSensor Enclosure v2.0               │
├─────────────────────────────────────────────────────────────┤
│                                                            │
│  📏 Dimensions: 120mm × 80mm × 40mm                        │
│  🏗️ Material: UV-resistant ABS + Carbon Fiber             │
│  🌡️ Operating Temperature: -40°C to +85°C                 │
│  💧 IP Rating: IP67 (waterproof)                          │
│  🔧 Mounting: Magnetic base + screw holes                  │
│  🌬️ Ventilation: PTFE membrane for gas sensors           │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    Top View                         │   │
│  │  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐      │   │
│  │  │ LED │  │Solar│  │WiFi │  │Vent │  │ NFC │      │   │
│  │  │Panel│  │Panel│  │Ant. │  │Mesh │  │ Tag │      │   │
│  │  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘      │   │
│  │                                                    │   │
│  │  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐      │   │
│  │  │ QR  │  │Setup│  │ BLE │  │USB-C│  │Reset│      │   │
│  │  │Code │  │ BTN │  │Ant. │  │Port │  │Hole │      │   │
│  │  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                            │
│  💡 Smart Features:                                        │
│     • RGB LED status indication                           │
│     • QR code for easy configuration                      │
│     • NFC tag for mobile setup                            │
│     • Magnetic mounting system                            │
│     • Tool-free battery access                            │
│                                                            │
└─────────────────────────────────────────────────────────────┘
```

### Internal Layout
```
┌─────────────────────────────────────────────────────────────┐
│                    Internal Component Layout                │
├─────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                     Top Chamber                      │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │   Solar     │  │    Main     │  │   Antenna   │  │  │
│  │  │   Panel     │  │    PCB      │  │   Section   │  │  │
│  │  │   Module    │  │  (Sensors)  │  │ (WiFi/BLE)  │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   Bottom Chamber                     │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │   Battery   │  │   Power     │  │   Crypto    │  │  │
│  │  │   Pack      │  │   Mgmt      │  │   Chip      │  │  │
│  │  │ (Li-Po)     │  │  (BQ25895)  │  │(ATECC608B) │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Assembly Instructions

### Step 1: PCB Component Placement
1. **SMD Components**: Place resistors, capacitors, and ICs using reflow soldering
2. **Connectors**: Solder USB-C, antenna connectors, and test points
3. **Modules**: Attach ESP32-S3, sensor modules, and crypto chip
4. **Final Inspection**: AOI (Automated Optical Inspection) for quality control

### Step 2: Initial Testing
1. **Power-on Test**: Verify 3.3V rails and current consumption
2. **Communication Test**: I2C device detection and sensor readings
3. **RF Test**: WiFi and Bluetooth connectivity verification
4. **Security Test**: Crypto chip functionality and key generation

### Step 3: Enclosure Assembly
1. **Gasket Installation**: Place waterproof gaskets around seams
2. **PCB Mounting**: Secure PCB with shock-absorbing standoffs
3. **Battery Integration**: Connect battery with proper polarity
4. **Antenna Routing**: Position antennas for optimal performance

### Step 4: Final Calibration
1. **Sensor Calibration**: Reference gas and temperature calibration
2. **Power Calibration**: Battery and solar voltage calibration
3. **AI Model Loading**: Flash optimized TensorFlow Lite models
4. **Quality Assurance**: Full system test and certification

## 📊 Bill of Materials (BOM)

### Main Components
| Component | Part Number | Quantity | Description | Price (USD) |
|-----------|-------------|----------|-------------|-------------|
| ESP32-S3-WROOM-1U | ESP32-S3-WROOM-1U-N16R8 | 1 | Main MCU with 16MB Flash, 8MB PSRAM | $8.50 |
| SHT40 | SHT40-AD1B-R2 | 1 | Digital Temperature/Humidity Sensor | $3.20 |
| SGP40 | SGP40-D-R4 | 1 | Digital VOC Sensor | $7.50 |
| BME688 | BME688 | 1 | 4-in-1 Gas Sensor with AI | $15.80 |
| SCD41 | SCD41-D-R2 | 1 | CO2 Sensor | $45.00 |
| MPU6050 | MPU-6050 | 1 | 6-axis IMU | $2.50 |
| INA219 | INA219AIDCNT | 1 | High-Side Current/Power Monitor | $2.80 |
| ATECC608B | ATECC608B-TNGTLS | 1 | Crypto Authentication IC | $1.25 |
| TCA9548A | TCA9548APWR | 1 | 8-Channel I2C Multiplexer | $1.95 |
| BQ25895 | BQ25895RTWR | 1 | Battery Charger with MPPT | $3.85 |
| Li-Po Battery | LP5025100 | 1 | 3.7V 5000mAh Lithium Polymer | $25.00 |
| Solar Panel | SP-6V-2W | 1 | 6V 2W Monocrystalline | $15.00 |

### Passive Components
| Component | Value | Package | Quantity | Description |
|-----------|-------|---------|----------|-------------|
| Resistor | 220Ω | 0603 | 3 | LED current limiting |
| Resistor | 330Ω | 0603 | 1 | Error LED current limiting |
| Resistor | 100Ω | 0603 | 1 | Buzzer current limiting |
| Resistor | 10kΩ | 0603 | 5 | Pull-up resistors |
| Capacitor | 100nF | 0603 | 10 | Decoupling capacitors |
| Capacitor | 10μF | 0805 | 3 | Power supply filtering |
| Capacitor | 47μF | 1206 | 2 | Main power filtering |
| Inductor | 2.2μH | 0805 | 1 | Power supply filtering |

### Mechanical Components
| Component | Part Number | Quantity | Description |
|-----------|-------------|----------|-------------|
| Enclosure Top | NC-ENC-TOP-V2 | 1 | ABS+CF top cover with vents |
| Enclosure Bottom | NC-ENC-BOT-V2 | 1 | ABS+CF bottom with magnetic mount |
| Gasket Set | NC-GASKET-SET | 1 | IP67 waterproof gaskets |
| Antenna (WiFi) | ANT-WiFi6-2.4G | 1 | 2.4GHz ceramic antenna |
| Antenna (BLE) | ANT-BLE-5.2 | 1 | Bluetooth LE antenna |
| RGB LED | WS2812B | 1 | Addressable RGB LED |
| Buzzer | PKM17EPP-4001-B0 | 1 | Piezo buzzer 4kHz |

### **Total Estimated Cost: $165.50 per unit** (excluding assembly)

## 🔧 Testing & Validation

### Functional Tests
- [ ] Power system validation (solar, battery, USB-C)
- [ ] Sensor accuracy verification against references
- [ ] AI model inference timing and accuracy
- [ ] Communication range and reliability
- [ ] Security chip functionality
- [ ] Enclosure IP67 rating validation

### Environmental Tests
- [ ] Temperature cycling (-40°C to +85°C)
- [ ] Humidity testing (0% to 95% RH)
- [ ] Vibration resistance (automotive standards)
- [ ] UV radiation exposure
- [ ] Salt spray corrosion test
- [ ] Drop test from 2 meters

### Regulatory Compliance
- [ ] FCC Part 15 (WiFi/Bluetooth)
- [ ] CE Marking (European Conformity)
- [ ] IC RSS-247 (Canada)
- [ ] RoHS Compliance (Lead-free)
- [ ] WEEE Directive (Recycling)

---

**⚡ Ready to build the future of smart cities with NeuroCity Smart Sensor v2.0!**

*For technical support and latest updates, visit: https://docs.neurocity.io/hardware*