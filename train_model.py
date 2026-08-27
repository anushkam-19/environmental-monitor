import sqlite3

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


DATABASE = "readings.db"
MODEL_FILE = "anomaly_model.joblib"

FEATURES = [
    "temperature",
    "humidity",
    "light",
]


# Load historical readings
connection = sqlite3.connect(DATABASE)

data = pd.read_sql_query(
    """
    SELECT
        temperature,
        humidity,
        light,
        warning
    FROM readings
    """,
    connection,
)

connection.close()


# Train only on readings considered normal by the original rules
normal_data = data[data["warning"] == 0].copy()

if len(normal_data) < 50:
    raise ValueError(
        "At least 50 normal readings are required. "
        f"Only {len(normal_data)} were found."
    )


training_features = normal_data[FEATURES]


# Create the AI pipeline
model = Pipeline(
    steps=[
        ("scaler", StandardScaler()),
        (
            "detector",
            IsolationForest(
                n_estimators=200,
                contamination=0.05,
                random_state=42,
            ),
        ),
    ]
)


# Train the model
model.fit(training_features)


# Test the model on all existing readings
predictions = model.predict(data[FEATURES])

data["ai_anomaly"] = predictions == -1

anomaly_count = int(data["ai_anomaly"].sum())


# Save the trained model
joblib.dump(model, MODEL_FILE)


print("AI model training complete.")
print("Normal training readings:", len(normal_data))
print("Total readings checked:", len(data))
print("AI anomalies detected:", anomaly_count)
print("Model saved as:", MODEL_FILE)