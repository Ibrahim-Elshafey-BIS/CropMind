# ============================================
# FILE: sensor_reading.py
# ============================================

"""
CropMind - Sensor Reading Model
SQLAlchemy async model for IoT sensor readings

Author: CropMind Team
Date: 2026
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class SensorReading(Base):
    """
    Sensor Reading model representing IoT sensor data from farm fields.
    Tracks various environmental parameters for monitoring and anomaly detection.
    """
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    sensor_id = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    is_anomaly = Column(Boolean, default=False, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    farm = relationship("Farm", back_populates="sensor_readings")

    # Indexes
    __table_args__ = (
        Index("ix_sensor_readings_id", "id"),
        Index("ix_sensor_readings_farm_id", "farm_id"),
        Index("ix_sensor_readings_sensor_id", "sensor_id"),
        Index("ix_sensor_readings_type", "type"),
        Index("ix_sensor_readings_timestamp", "timestamp"),
        Index("ix_sensor_readings_is_anomaly", "is_anomaly"),
        CheckConstraint("type IN ('temperature', 'humidity', 'soil_moisture', 'ph', 'light')", name="ck_sensor_readings_type"),
    )

    def __repr__(self) -> str:
        return f"<SensorReading(id={self.id}, sensor_id={self.sensor_id}, type={self.type}, value={self.value}, farm_id={self.farm_id})>"