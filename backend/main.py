from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
import asyncio
from . import database
from pydantic import BaseModel
import sys
import os

# Adujst path to import from parent or sibling
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml.classifier import PollutionClassifier

app = FastAPI(title="AERIS Backend API")
clf = PollutionClassifier()

# Pydantic models
class SensorReading(BaseModel):
    node_id: str
    pm25: float
    pm10: float
    co: float
    no2: float
    temp: float
    humidity: float
    lat: float
    lon: float

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
def read_root():
    return {"message": "AERIS API is running"}

@app.post("/ingest")
@app.post("/data")
async def ingest_data(reading: dict, db: Session = Depends(get_db)):
    # Standardize field names for Aeris.ino compatibility
    node_id = reading.get("node_id") or reading.get("device")
    pm25 = reading.get("pm25", 0)
    pm10 = reading.get("pm10", 0)
    co = reading.get("co", 0)
    no2 = reading.get("no2", 0)
    temp = reading.get("temp") or reading.get("temperature", 0)
    humidity = reading.get("humidity", 0)
    lat = reading.get("lat", 0)
    lon = reading.get("lon", 0)

    # Create DB entry
    db_reading = database.SensorData(
        node_id=node_id,
        pm25=pm25,
        pm10=pm10,
        co=co,
        no2=no2,
        temp=temp,
        humidity=humidity,
        lat=lat,
        lon=lon
    )
    
    # ML Inference
    try:
        source = clf.predict(pm25, pm10, co, no2)
        db_reading.pollution_source = source
    except Exception as e:
        print(f"ML Inference error: {e}")
        db_reading.pollution_source = "Analysis Failed"

    db_reading.risk_level = "Low"
    if pm25 > 50:
        db_reading.risk_level = "Medium"
    if pm25 > 100:
        db_reading.risk_level = "High"

    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)

    # Broadcast to dashboard
    data_dict = {
        "id": db_reading.id,
        "node_id": node_id,
        "timestamp": db_reading.timestamp.isoformat(),
        "pm25": pm25,
        "pm10": pm10,
        "risk_level": db_reading.risk_level,
        "pollution_source": db_reading.pollution_source,
        "lat": lat,
        "lon": lon
    }
    await manager.broadcast(json.dumps(data_dict))
    
    return db_reading

@app.get("/history", response_model=List[dict])
def get_history(limit: int = 100, db: Session = Depends(get_db)):
    readings = db.query(database.SensorData).order_by(database.SensorData.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "node_id": r.node_id,
            "timestamp": r.timestamp.isoformat(),
            "pm25": r.pm25,
            "pm10": r.pm10,
            "co": r.co,
            "no2": r.no2,
            "temp": r.temp,
            "humidity": r.humidity,
            "lat": r.lat,
            "lon": r.lon,
            "pollution_source": r.pollution_source,
            "risk_level": r.risk_level
        } for r in readings
    ]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
