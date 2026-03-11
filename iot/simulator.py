import requests
import time
import random
import uuid

BACKEND_URL = "http://localhost:8000/ingest"

nodes = [
    {"id": "NODE_01", "lat": 28.6139, "lon": 77.2090}, # Delhi
    {"id": "NODE_02", "lat": 28.5355, "lon": 77.3910}, # Noida
    {"id": "NODE_03", "lat": 28.4595, "lon": 77.0266}, # Gurgaon
]

def generate_reading(node):
    # Simulate some variety in data
    base_pm25 = random.uniform(10, 150)
    
    return {
        "node_id": node["id"],
        "pm25": base_pm25,
        "pm10": base_pm25 * random.uniform(1.2, 1.5),
        "co": random.uniform(0.1, 4.0),
        "no2": random.uniform(10, 100),
        "temp": random.uniform(20, 35),
        "humidity": random.uniform(30, 80),
        "lat": node["lat"] + random.uniform(-0.01, 0.01),
        "lon": node["lon"] + random.uniform(-0.01, 0.01)
    }

def run_simulator():
    print("Starting IoT Node Simulator...")
    while True:
        for node in nodes:
            reading = generate_reading(node)
            try:
                response = requests.post(BACKEND_URL, json=reading)
                # print(f"Sent reading from {node['id']}: {response.status_code}")
            except Exception as e:
                print(f"Error sending reading from {node['id']}: {e}")
        time.sleep(5)

if __name__ == "__main__":
    run_simulator()
