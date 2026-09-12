"""
CropMind - MQTT Broker Configuration
MQTT broker settings and topic definitions for IoT sensor data

Author: CropMind Team
Date: 2026
"""

# ============================================
# Broker Settings
# ============================================

BROKER_HOST = "localhost"
BROKER_PORT = 1883
CLIENT_ID = "cropmind_broker"
KEEPALIVE = 60

# ============================================
# Fields and Sensor Types
# ============================================

FIELDS = ['A', 'B', 'C', 'D', 'E']
SENSOR_TYPES = ['temperature', 'humidity', 'soil_moisture', 'ph']

# ============================================
# QoS Levels
# ============================================

# QoS 0: At most once (fire and forget)
# QoS 1: At least once (acknowledged delivery)
# QoS 2: Exactly once (assured delivery)

QOS_0 = 0
QOS_1 = 1
QOS_2 = 2

DEFAULT_QOS = QOS_1

# ============================================
# Topic Definitions
# ============================================

TOPIC_TEMPLATE = "cropmind/field/{field_id}/{sensor_type}"

# ============================================
# Helper Functions
# ============================================

def get_topic(field_id: str, sensor_type: str) -> str:
    """
    Get the MQTT topic for a specific field and sensor type.
    
    Args:
        field_id: Field ID (A, B, C, D, E)
        sensor_type: Type of sensor (temperature, humidity, soil_moisture, ph)
        
    Returns:
        str: Full MQTT topic path
    """
    if field_id not in FIELDS:
        raise ValueError(f"Invalid field_id: {field_id}. Must be one of: {FIELDS}")
    
    if sensor_type not in SENSOR_TYPES:
        raise ValueError(f"Invalid sensor_type: {sensor_type}. Must be one of: {SENSOR_TYPES}")
    
    return TOPIC_TEMPLATE.format(field_id=field_id, sensor_type=sensor_type)


def get_field_topics(field_id: str) -> list:
    """
    Get all MQTT topics for a specific field.
    
    Args:
        field_id: Field ID (A, B, C, D, E)
        
    Returns:
        list: All topic paths for the field
    """
    return [get_topic(field_id, sensor_type) for sensor_type in SENSOR_TYPES]


def get_all_topics() -> list:
    """
    Get all MQTT topics for all fields.
    
    Returns:
        list: All topic paths
    """
    all_topics = []
    for field_id in FIELDS:
        all_topics.extend(get_field_topics(field_id))
    return all_topics
