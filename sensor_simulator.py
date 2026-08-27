import json
import random
import time

import paho.mqtt.client as mqtt


BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "ece-wokwi-2026/environment/telemetry"

READINGS_PER_SCENARIO = 20
SECONDS_BETWEEN_READINGS = 3


# Each scenario contains:
# name, average temperature, average humidity, average light reading
scenarios = [
    {
        "name": "NORMAL",
        "temperature": 25.0,
        "humidity": 50.0,
        "light": 1500,
    },
    {
        "name": "TOO HOT",
        "temperature": 34.0,
        "humidity": 50.0,
        "light": 1500,
    },
    {
        "name": "TOO HUMID",
        "temperature": 25.0,
        "humidity": 80.0,
        "light": 1500,
    },
    {
        "name": "TOO DARK",
        "temperature": 25.0,
        "humidity": 50.0,
        "light": 3800,
    },
]


client = mqtt.Client()
client.connect(BROKER, PORT)
client.loop_start()

# Allow time for the MQTT connection to finish
time.sleep(1)

print("Sensor simulator started")
print("It will test four environmental conditions.")
print("Press Ctrl+C to stop.\n")


try:
    for scenario in scenarios:
        print("=" * 40)
        print("Starting scenario:", scenario["name"])
        print("=" * 40)

        for reading_number in range(1, READINGS_PER_SCENARIO + 1):
            # Generate small variations around each scenario's values
            temperature = scenario["temperature"] + random.uniform(-0.5, 0.5)
            humidity = scenario["humidity"] + random.uniform(-1.5, 1.5)
            light = scenario["light"] + random.randint(-100, 100)

            # Keep readings within sensible limits
            temperature = max(15.0, min(45.0, temperature))
            humidity = max(20.0, min(90.0, humidity))
            light = max(32, min(4060, light))

            # Apply the same thresholds used by the project
            too_hot = temperature > 30
            too_humid = humidity > 70
            too_dark = light > 3500

            warning = too_hot or too_humid or too_dark

            data = {
                "temperature": round(temperature, 1),
                "humidity": round(humidity, 1),
                "light": light,
                "too_hot": too_hot,
                "too_humid": too_humid,
                "too_dark": too_dark,
                "warning": warning,
            }

            payload = json.dumps(data)

            result = client.publish(TOPIC, payload)
            result.wait_for_publish()

            print(
                f'{scenario["name"]} '
                f'({reading_number}/{READINGS_PER_SCENARIO}): '
                f'{payload}'
            )

            time.sleep(SECONDS_BETWEEN_READINGS)

    print("\nAll four scenarios are complete.")
    print("You may now stop the subscriber with Ctrl+C.")

except KeyboardInterrupt:
    print("\nSensor simulator stopped early.")

finally:
    client.loop_stop()
    client.disconnect()