import json
import sqlite3
from datetime import datetime, timezone

import paho.mqtt.client as mqtt


BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "ece-wokwi-2026/environment/telemetry"
DATABASE = "readings.db"


def create_database():
    connection = sqlite3.connect(DATABASE)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recorded_at TEXT NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            light INTEGER NOT NULL,
            too_hot INTEGER NOT NULL,
            too_humid INTEGER NOT NULL,
            too_dark INTEGER NOT NULL,
            warning INTEGER NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


def save_reading(data):
    connection = sqlite3.connect(DATABASE)

    connection.execute(
        """
        INSERT INTO readings (
            recorded_at,
            temperature,
            humidity,
            light,
            too_hot,
            too_humid,
            too_dark,
            warning
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now(timezone.utc).isoformat(),
            data["temperature"],
            data["humidity"],
            data["light"],
            int(data["too_hot"]),
            int(data["too_humid"]),
            int(data["too_dark"]),
            int(data["warning"]),
        ),
    )

    connection.commit()
    connection.close()


def on_connect(
    client,
    userdata,
    flags,
    reason_code,
    properties
):
    if reason_code == 0:
        print("Connected to MQTT broker")
        client.subscribe(TOPIC)
        print(f"Listening to: {TOPIC}")
    else:
        print(f"Connection failed: {reason_code}")


def on_message(client, userdata, message):
    text = message.payload.decode("utf-8")

    try:
        data = json.loads(text)
        save_reading(data)

        print(
            "Saved:",
            data["temperature"],
            data["humidity"],
            data["light"],
            data["warning"],
        )

    except (json.JSONDecodeError, KeyError) as error:
        print("Invalid message:", error)


create_database()

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = on_connect
client.on_message = on_message

print("Connecting...")

client.connect(BROKER, PORT, 60)
client.loop_forever()