from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./aeris.db"

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

engine = sa.create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    pm25 = Column(Float)
    pm10 = Column(Float)
    co = Column(Float)
    no2 = Column(Float)
    temp = Column(Float)
    humidity = Column(Float)
    lat = Column(Float)
    lon = Column(Float)
    pollution_source = Column(String, nullable=True) # Predicted by ML
    risk_level = Column(String, default="Low") # Predicted by ML

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    severity = Column(String)
    message = Column(String)
    location = Column(String)

Base.metadata.create_all(bind=engine)
