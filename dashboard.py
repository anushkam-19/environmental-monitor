import sqlite3

import joblib
import pandas as pd
import streamlit as st


DATABASE = "readings.db"
MODEL_FILE = "anomaly_model.joblib"

FEATURES = [
    "temperature",
    "humidity",
    "light",
]


st.set_page_config(
    page_title="Environmental Monitor",
    page_icon="🌡️",
    layout="wide",
)

st.title("AI-Assisted Environmental Monitor")
st.caption("Environmental readings received through MQTT")


@st.cache_resource
def load_ai_model():
    return joblib.load(MODEL_FILE)


def load_readings():
    connection = sqlite3.connect(DATABASE)

    dataframe = pd.read_sql_query(
        """
        SELECT
            recorded_at,
            temperature,
            humidity,
            light,
            too_hot,
            too_humid,
            too_dark,
            warning
        FROM readings
        ORDER BY recorded_at ASC
        """,
        connection,
    )

    connection.close()

    dataframe["recorded_at"] = pd.to_datetime(
        dataframe["recorded_at"]
    )

    return dataframe


data = load_readings()

if data.empty:
    st.warning("No readings are available yet.")
    st.stop()


try:
    model = load_ai_model()
except FileNotFoundError:
    st.error(
        "The AI model was not found. "
        "Run train_model.py before opening the dashboard."
    )
    st.stop()


# Generate AI predictions for all saved readings
data["ai_anomaly"] = (
    model.predict(data[FEATURES]) == -1
)


# Most recent reading
latest = data.iloc[-1]

temperature = float(latest["temperature"])
humidity = float(latest["humidity"])
light = int(latest["light"])


# Current measurements
temperature_column, humidity_column, light_column = st.columns(3)

temperature_column.metric(
    "Temperature",
    f"{temperature:.1f} °C",
)

humidity_column.metric(
    "Humidity",
    f"{humidity:.1f} %",
)

light_column.metric(
    "Light reading",
    light,
)


# Rule-based status
warning_reasons = []

if temperature > 30:
    warning_reasons.append("Too Hot")

if humidity > 70:
    warning_reasons.append("Too Humid")

if light > 3500:
    warning_reasons.append("Too Dark")


# AI prediction for the latest reading
latest_features = pd.DataFrame(
    [
        {
            "temperature": temperature,
            "humidity": humidity,
            "light": light,
        }
    ]
)

ai_prediction = model.predict(latest_features)[0]
ai_score = float(
    model.decision_function(latest_features)[0]
)


rule_column, ai_column = st.columns(2)

with rule_column:
    st.subheader("Rule-based status")

    if warning_reasons:
        status_text = ", ".join(warning_reasons)
        st.error(f"⚠️ {status_text}")
    else:
        st.success("✅ Normal")


with ai_column:
    st.subheader("AI anomaly status")

    if ai_prediction == -1:
        st.error("🤖 Anomaly detected")
    else:
        st.success("🤖 Pattern appears normal")

    st.caption(f"AI anomaly score: {ai_score:.3f}")


# Temperature graph
st.subheader("Temperature history")

temperature_chart = data.set_index("recorded_at")[
    ["temperature"]
]

st.line_chart(temperature_chart)


# Humidity graph
st.subheader("Humidity history")

humidity_chart = data.set_index("recorded_at")[
    ["humidity"]
]

st.line_chart(humidity_chart)


# Light graph
st.subheader("Light history")

light_chart = data.set_index("recorded_at")[
    ["light"]
]

st.line_chart(light_chart)


# Summary
st.subheader("Monitoring summary")

warning_count = int(data["warning"].sum())
ai_anomaly_count = int(data["ai_anomaly"].sum())

summary_one, summary_two, summary_three = st.columns(3)

summary_one.metric(
    "Total readings",
    len(data),
)

summary_two.metric(
    "Rule warnings",
    warning_count,
)

summary_three.metric(
    "AI anomalies",
    ai_anomaly_count,
)


# Recent readings
st.subheader("Recent readings")

recent = data.sort_values(
    "recorded_at",
    ascending=False,
).head(10)

st.dataframe(
    recent,
    use_container_width=True,
)


if st.button("Refresh readings"):
    st.rerun()