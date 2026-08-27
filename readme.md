# AI-Assisted Environmental Monitor

A beginner-friendly IoT and machine-learning prototype that monitors temperature, humidity, and light readings.

The current version uses a Python sensor simulator. Readings are transmitted through MQTT, stored in SQLite, analysed using an Isolation Forest anomaly-detection model, and displayed in a Streamlit dashboard.

A physical ESP32 and environmental sensors can replace the Python simulator in a future hardware version.

## System Architecture

```text
Python Sensor Simulator
          |
          | MQTT
          v
     HiveMQ Broker
          |
          v
   Python Subscriber
          |
          v
    SQLite Database
          |
          +-------------------+
          |                   |
          v                   v
  Rule-Based Alerts    Isolation Forest AI
          |                   |
          +---------+---------+
                    |
                    v
           Streamlit Dashboard

Features
- Simulates temperature, humidity, and light readings
- Publishes readings through MQTT
- Stores readings with timestamps in SQLite
- Displays current measurements and historical graphs
- Detects fixed warning conditions:
  - Temperature above 30°C
  - Humidity above 70%
  - Light reading above 3500, representing darkness
- Uses Isolation Forest to detect unusual environmental patterns
- Separates rule-based warnings from AI anomaly detection


AI Component
The Isolation Forest model is trained using readings classified as normal by the fixed rules.
It learns the typical relationship between:
- Temperature
- Humidity
- Light
For each new reading, the model predicts whether the combined pattern appears normal or anomalous.
The current model is trained on simulated data and should be treated as a proof of concept. It can later be retrained using readings collected from physical sensors.
Project Files
Environmental Monitor/
├── sensor_simulator.py
├── subscriber.py
├── train_model.py
├── dashboard.py
├── requirements.txt
├── README.md
├── .gitignore
└── screenshots/
    ├── normal.png
    ├── too-hot.png
    ├── too-humid.png
    └── too-dark.png
Installation
Install Python, then open PowerShell inside the project folder.
Install the dependencies:
pip install -r requirements.txt
Running the Project
1. Start the MQTT subscriber
python subscriber.py
The subscriber receives MQTT messages and saves them in readings.db.
2. Start the sensor simulator
Open another PowerShell window:
python sensor_simulator.py
The simulator publishes normal, hot, humid, and dark environmental conditions.
3. Train the AI model
After collecting enough readings, stop the programs and run:
python train_model.py
This creates anomaly_model.joblib.
4. Start the dashboard
streamlit run dashboard.py

Rule-Based Alerts vs AI Detection
The rule-based system checks whether a fixed threshold has been crossed.
The AI model checks whether the complete combination of temperature, humidity, and light is unusual compared with its learned normal patterns.
These systems can sometimes disagree because they answer different questions.
Future Improvements
- Replace the Python simulator with a physical ESP32
- Add a DHT22 temperature and humidity sensor
- Add a physical light sensor
- Collect real environmental data
- Retrain and evaluate the AI model using real data
- Add notifications for sustained warning conditions
- Deploy the dashboard online

Current Status
The MQTT pipeline, database storage, dashboard, fixed alerts, and AI anomaly-detection prototype are working with simulated sensor data.