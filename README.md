# 🌱 CropMind

## An Integrated AI Digital Operating System for Smart Agriculture in Egypt

CropMind is an AI-powered digital operating system designed to support smart agriculture in Egypt by integrating Artificial Intelligence, Machine Learning, Computer Vision, IoT telemetry, predictive analytics, and automated workflows into a unified platform.

The system aims to help farmers and agricultural managers monitor crop health, optimize resources, detect anomalies, forecast crop yields and market prices, and automate operational workflows.

---

## 🎯 Project Overview

CropMind addresses major agricultural challenges including:

- Water scarcity and irrigation inefficiency
- Crop disease and late-stage detection
- Climate and environmental uncertainty
- Crop productivity gaps
- Agricultural market price volatility
- Fragmented farm management systems

The platform combines field data, AI models, predictive analytics, and automated workflows to provide integrated decision support.

---

## 🏗️ System Architecture

CropMind follows a five-layer architecture:

1. **Field Data Acquisition**
2. **MQTT Communication Broker**
3. **FastAPI / PostgreSQL Backend**
4. **AI & Intelligence Engine**
5. **User Experience & Event Automation**

### Main Components

- React 18 Web Dashboard
- React Native / Expo Mobile Application
- Python FastAPI Backend
- PostgreSQL Database
- LangChain AI Engine
- LLM-powered Farm Copilot
- XGBoost Machine Learning Models
- Prophet / LSTM Forecasting
- Isolation Forest Anomaly Detection
- TensorFlow Lite Computer Vision
- ESP32 IoT Devices
- MQTT / Mosquitto
- n8n Workflow Automation

---

## 🤖 AI & Machine Learning

CropMind integrates multiple AI and Machine Learning capabilities:

### Plant Disease Detection

A CNN-based computer vision model deployed using TensorFlow Lite for plant disease classification.

- 23 plant disease classes
- INT8 quantization
- On-device inference
- PlantVillage dataset

### Crop Yield Estimation

An XGBoost regression model using agricultural and environmental features such as:

- Soil NPK
- Soil moisture
- Weather conditions
- Crop-related features

### Price Forecasting

A forecasting pipeline combining:

- Prophet
- LSTM

for agricultural commodity price prediction.

### Anomaly Detection

Isolation Forest is used to detect:

- Sensor anomalies
- Telemetry outliers
- Abnormal field measurements

---

## 🧠 Autonomous AI Agents

The CropMind intelligence layer contains seven specialized agents:

1. Farm Intelligence Agent
2. Resource Optimization Agent
3. Finance Agent
4. Market Intelligence Agent
5. Inventory Agent
6. Workforce Agent
7. Arabic Farm Copilot

These agents are designed to support different operational aspects of smart farm management.

---

## 📊 Farm DNA Score

CropMind introduces a composite Farm DNA Score based on six dimensions:

| Dimension | Weight |
|---|---:|
| Crop Health | 22% |
| Soil Health | 20% |
| Water Efficiency | 18% |
| Operational Efficiency | 15% |
| Market Readiness | 13% |
| Risk Exposure | 12% |

The score provides an overall representation of farm operational health and readiness.

---

## ⚙️ Automation

CropMind uses n8n for event-driven workflow automation.

Implemented workflows include:

- Daily Health Check
- Weather Alert
- Disease Outbreak Alert
- Price Spike Alert
- Weekly Report

---

## 📈 Experimental Results

The project demonstrated the following results:

| Component | Result |
|---|---:|
| Plant Disease Classification | 94% Accuracy |
| Crop Yield Regression | R² = 0.91 |
| Price Forecasting | MAE < 10% |
| Farm DNA Score | 84% |
| Event Automation | 100% Trigger Success |

The plant disease classification experiment used 34,500 PlantVillage images across 23 classes.

---

# 👨‍💻 My Contribution

## Ibrahim Elshafey

My contribution to the CropMind project focused on the **Data Analytics and Machine Learning pipeline**, including data preparation, preprocessing, model-related workflows, and integration of AI-driven agricultural insights into the overall system.

### Main Responsibilities

- Data preprocessing and preparation
- Agricultural dataset organization and cleaning
- Feature preparation for Machine Learning models
- Supporting predictive analytics workflows
- Machine Learning experimentation
- Model evaluation and validation
- Supporting integration of AI models into the CropMind platform
- Contributing to the project's technical documentation and analysis

### Technologies

```text
Python
Pandas
NumPy
Scikit-Learn
XGBoost
Machine Learning
Data Analytics
Data Preprocessing
Predictive Analytics
