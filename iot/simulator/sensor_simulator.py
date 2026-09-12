"""
CropMind - Sensor Simulator
Simulates sensor data and publishes to MQTT broker

Author: CropMind Team
Date: 2026
"""

import json
import random
import time
import argparse
from datetime import datetime
import paho.mqtt.client as mqtt

from iot.mqtt.broker_config import (
    BROKER_HOST,
    BROKER_PORT,
    FIELDS,
    SENSOR_TYPES,
    DEFAULT_QOS,
    KEEPALIVE,
    get_topic
)


class SensorSimulator:
    """
    Sensor simulator that generates realistic sensor data and publishes to MQTT.
    """
    
    def __init__(self):
        """Initialize the sensor simulator."""
        self.client = mqtt.Client("cropmind_simulator")
        self.client.on_connect = self.on_connect
        
        # Normal ranges for each sensor type
        self.normal_ranges = {
            "temperature": (15.0, 35.0),
            "humidity": (40.0, 80.0),
            "soil_moisture": (20.0, 80.0),
            "ph": (6.0, 7.5),
        }
        
        # Anomaly ranges for each sensor type
        self.anomaly_ranges = {
            "temperature": (45.0, 60.0),
            "humidity": (0.0, 15.0),
            "soil_moisture": (0.0, 10.0),
            "ph": (3.0, 4.5),
        }
        
        # Track current values for each field and sensor type
        self.current_values = {}
        
        print("[Sensor Simulator] ✅ Initialized")
    
    def on_connect(self, client, userdata, flags, rc):
        """
        Callback when connected to broker.
        """
        if rc == 0:
            print("[Sensor Simulator] ✅ Connected to MQTT broker")
        else:
            print(f"[Sensor Simulator] ❌ Failed to connect: {rc}")
    
    def connect(self):
        """
        Connect to MQTT broker.
        """
        try:
            self.client.connect(BROKER_HOST, BROKER_PORT, KEEPALIVE)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"[Sensor Simulator] ❌ Connection error: {e}")
            return False
    
    def disconnect(self):
        """
        Disconnect from MQTT broker.
        """
        self.client.loop_stop()
        self.client.disconnect()
        print("[Sensor Simulator] ✅ Disconnected")
    
    def generate_value(self, sensor_type: str) -> tuple:
        """
        Generate a sensor value with 5% chance of anomaly.
        
        Args:
            sensor_type: Type of sensor
            
        Returns:
            tuple: (value, is_anomaly)
        """
        # 5% chance of anomaly
        is_anomaly = random.random() < 0.05
        
        if is_anomaly:
            # Generate anomaly value
            low, high = self.anomaly_ranges[sensor_type]
            value = random.uniform(low, high)
        else:
            # Generate normal value
            low, high = self.normal_ranges[sensor_type]
            # Add some Gaussian-like distribution (more values near center)
            mean = (low + high) / 2
            std = (high - low) / 6
            value = random.gauss(mean, std)
            # Clamp to range
            value = max(low, min(high, value))
        
        return round(value, 2), is_anomaly
    
    def publish_reading(self, field_id: str, sensor_type: str, value: float):
        """
        Publish a sensor reading to MQTT.
        
        Args:
            field_id: Field ID (A, B, C, D, E)
            sensor_type: Type of sensor
            value: Sensor value
        """
        topic = get_topic(field_id, sensor_type)
        
        payload = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        
        self.client.publish(topic, json.dumps(payload), qos=DEFAULT_QOS)
        print(f"[Sensor Simulator] 📤 {topic}: {value}")
    
    def generate_and_publish(self):
        """
        Generate and publish readings for all fields and sensor types.
        """
        for field_id in FIELDS:
            for sensor_type in SENSOR_TYPES:
                value, is_anomaly = self.generate_value(sensor_type)
                
                # Add small variation based on previous value for realism
                key = f"{field_id}_{sensor_type}"
                if key in self.current_values:
                    prev_value = self.current_values[key]
                    # Random walk with small step
                    step = random.uniform(-0.5, 0.5)
                    value = prev_value + step
                    # Clamp to range
                    if is_anomaly:
                        low, high = self.anomaly_ranges[sensor_type]
                    else:
                        low, high = self.normal_ranges[sensor_type]
                    value = max(low, min(high, value))
                    value = round(value, 2)
                
                self.current_values[key] = value
                self.publish_reading(field_id, sensor_type, value)
                
                # Add anomaly indicator to log
                if is_anomaly:
                    print(f"[Sensor Simulator] ⚠️ Anomaly detected: {field_id} {sensor_type} = {value}")
    
    def run_realtime(self, interval: int = 5):
        """
        Run the simulator in real-time mode.
        
        Args:
            interval: Interval between readings in seconds
        """
        print("[Sensor Simulator] 🚀 Starting real-time simulation")
        print(f"[Sensor Simulator] ⏱️  Interval: {interval} seconds")
        print(f"[Sensor Simulator] 📡 Broker: {BROKER_HOST}:{BROKER_PORT}")
        print("-" * 60)
        
        if not self.connect():
            return
        
        try:
            while True:
                self.generate_and_publish()
                print("-" * 60)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[Sensor Simulator] 🛑 Stopped by user")
        finally:
            self.disconnect()


def main():
    """
    Main entry point for the sensor simulator.
    """
    parser = argparse.ArgumentParser(
        description="CropMind - IoT Sensor Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sensor_simulator.py --mode realtime
  python sensor_simulator.py --mode realtime --interval 10
        """
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        required=True,
        choices=['realtime'],
        help='Mode: realtime (stream data to MQTT)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Interval in seconds between readings (default: 5)'
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("🌾 CropMind - Sensor Simulator")
    print("="*60)
    
    simulator = SensorSimulator()
    
    if args.mode == 'realtime':
        simulator.run_realtime(args.interval)


if __name__ == "__main__":
    main()
