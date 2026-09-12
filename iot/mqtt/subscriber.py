"""
CropMind - MQTT Subscriber
MQTT subscriber that receives sensor data and forwards to backend API

Author: CropMind Team
Date: 2026
"""

import json
import paho.mqtt.client as mqtt
import requests
from datetime import datetime
from typing import Dict, Any

from iot.mqtt.broker_config import (
    BROKER_HOST,
    BROKER_PORT,
    CLIENT_ID,
    DEFAULT_QOS,
    get_all_topics,
    FIELDS,
    SENSOR_TYPES,
    KEEPALIVE
)


class MQTTSubscriber:
    """
    MQTT subscriber that receives sensor data and forwards to backend API.
    """
    
    def __init__(self):
        """Initialize the MQTT subscriber."""
        self.client = mqtt.Client(CLIENT_ID)
        self.api_url = "http://localhost:8000/api/irrigation/readings"
        
        # Field ID to Farm ID mapping
        self.field_mapping = {
            "A": 1,
            "B": 1,
            "C": 2,
            "D": 2,
            "E": 3,
        }
        
        # Sensor type to unit mapping
        self.unit_mapping = {
            "temperature": "°C",
            "humidity": "%",
            "soil_moisture": "%",
            "ph": "",
        }
        
        # Set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        print("[MQTT Subscriber] ✅ Initialized")
    
    def on_connect(self, client, userdata, flags, rc):
        """
        Callback when connected to broker.
        """
        if rc == 0:
            print("[MQTT Subscriber] ✅ Connected to MQTT broker")
            
            # Subscribe to all topics
            all_topics = get_all_topics()
            for topic in all_topics:
                client.subscribe(topic, qos=DEFAULT_QOS)
                print(f"[MQTT Subscriber] 📡 Subscribed to: {topic}")
        else:
            print(f"[MQTT Subscriber] ❌ Failed to connect: {rc}")
    
    def on_message(self, client, userdata, msg):
        """
        Callback when a message is received.
        """
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            print(f"[MQTT Subscriber] 📩 Received: {topic} -> {payload}")
            
            # Parse topic
            # Format: cropmind/field/{field_id}/{sensor_type}
            parts = topic.split('/')
            if len(parts) != 4 or parts[0] != "cropmind" or parts[1] != "field":
                print(f"[MQTT Subscriber] ⚠️ Invalid topic format: {topic}")
                return
            
            field_id = parts[2]
            sensor_type = parts[3]
            
            # Validate field_id and sensor_type
            if field_id not in self.field_mapping:
                print(f"[MQTT Subscriber] ⚠️ Unknown field_id: {field_id}")
                return
            
            if sensor_type not in SENSOR_TYPES:
                print(f"[MQTT Subscriber] ⚠️ Unknown sensor_type: {sensor_type}")
                return
            
            # Parse payload
            try:
                data = json.loads(payload)
                value = float(data.get("value", 0))
            except (json.JSONDecodeError, ValueError, TypeError):
                # If payload is not JSON, try to parse as float directly
                try:
                    value = float(payload.strip())
                except ValueError:
                    print(f"[MQTT Subscriber] ⚠️ Invalid payload: {payload}")
                    return
            
            # Map to farm_id
            farm_id = self.field_mapping[field_id]
            sensor_id = f"sensor_{field_id}_{sensor_type}"
            unit = self.unit_mapping.get(sensor_type, "")
            timestamp = datetime.now().isoformat()
            
            # Build reading data
            reading = {
                "farm_id": farm_id,
                "sensor_id": sensor_id,
                "type": sensor_type,
                "value": value,
                "unit": unit,
                "is_anomaly": False,  # Will be determined by backend
                "timestamp": timestamp
            }
            
            print(f"[MQTT Subscriber] 📤 Sending to API: {reading}")
            
            # Send to backend API
            self.send_to_api(reading)
            
        except Exception as e:
            print(f"[MQTT Subscriber] ❌ Error processing message: {e}")
    
    def send_to_api(self, reading: Dict[str, Any]) -> bool:
        """
        Send reading to backend API.
        
        Args:
            reading: Sensor reading data
            
        Returns:
            bool: True if successful
        """
        try:
            response = requests.post(
                self.api_url,
                json=reading,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code == 201:
                print(f"[MQTT Subscriber] ✅ Reading sent successfully")
                return True
            else:
                print(f"[MQTT Subscriber] ⚠️ API error: {response.status_code} - {response.text}")
                return False
                
        except requests.ConnectionError:
            print(f"[MQTT Subscriber] ❌ Cannot connect to API at {self.api_url}")
            return False
        except Exception as e:
            print(f"[MQTT Subscriber] ❌ Error sending to API: {e}")
            return False
    
    def start(self):
        """
        Start the MQTT subscriber.
        """
        try:
            print("[MQTT Subscriber] 🚀 Starting subscriber...")
            self.client.connect(BROKER_HOST, BROKER_PORT, KEEPALIVE)
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("\n[MQTT Subscriber] 🛑 Stopped by user")
            self.client.disconnect()
        except Exception as e:
            print(f"[MQTT Subscriber] ❌ Error: {e}")
            self.client.disconnect()


def main():
    """
    Main entry point for the MQTT subscriber.
    """
    print("="*60)
    print("🌾 CropMind - MQTT Subscriber")
    print("="*60)
    print(f"📡 Broker: {BROKER_HOST}:{BROKER_PORT}")
    print(f"🔗 API: http://localhost:8000/api/irrigation/readings")
    print("="*60)
    
    subscriber = MQTTSubscriber()
    subscriber.start()


if __name__ == "__main__":
    main()
