--
-- CropMind - Crops Seed Data (INSERT INTO Existing Tables)
-- Realistic Egyptian agricultural data
--
-- Author: CropMind Team
-- Date: 2026
--

-- ============================================
-- Crops (Additional crops for each farm)
-- ============================================

-- Farm 1: مزرعة الفيوم (قمح)
INSERT INTO crops (farm_id, name, variety, area, planting_date, expected_harvest_date, status, health_score, notes) VALUES
(1, 'قمح', 'سخا 94', 25.0, '2024-11-01', '2025-04-15', 'growing', 85.0, NULL),
(1, 'قمح', 'جيزة 171', 15.0, '2024-11-15', '2025-05-01', 'growing', 72.0, 'نمو أقل من المتوقع'),
(1, 'برسيم', 'مسقاوي', 10.0, '2024-10-01', '2025-03-01', 'growing', 90.0, NULL);

-- Farm 2: مزرعة الإسماعيلية (طماطم)
INSERT INTO crops (farm_id, name, variety, area, planting_date, expected_harvest_date, status, health_score, notes) VALUES
(2, 'طماطم', 'فردوس', 10.0, '2024-09-15', '2025-01-15', 'harvested', 95.0, 'إنتاج ممتاز'),
(2, 'طماطم', 'الشيف', 8.0, '2024-10-01', '2025-02-01', 'growing', 68.0, 'هجوم حشرات طفيف'),
(2, 'فلفل', 'حلو بلدي', 6.0, '2024-11-01', '2025-03-01', 'growing', 78.0, NULL),
(2, 'خيار', 'صحراوي', 6.0, '2024-10-15', '2025-02-15', 'growing', 82.0, NULL);

-- Farm 3: مزرعة بني سويف (ذرة)
INSERT INTO crops (farm_id, name, variety, area, planting_date, expected_harvest_date, status, health_score, notes) VALUES
(3, 'ذرة', 'هجين 321', 40.0, '2024-05-01', '2024-09-15', 'harvested', 92.0, 'إنتاج 7 طن/فدان'),
(3, 'ذرة', 'هجين 168', 25.0, '2024-06-01', '2024-10-01', 'harvested', 78.0, 'إنتاج 5 طن/فدان'),
(3, 'فول', 'سوداني', 15.0, '2024-07-01', '2024-11-01', 'growing', 85.0, NULL);


-- ============================================
-- Market Prices (Realistic Egyptian Prices)
-- ============================================

-- سوق العبور (القاهرة)
INSERT INTO market_prices (commodity, price, min_price, max_price, unit, market_name, date) VALUES
('طماطم', 45.0, 38.0, 52.0, 'EGP/kg', 'سوق العبور', '2025-01-15'),
('بصل', 28.0, 24.0, 32.0, 'EGP/kg', 'سوق العبور', '2025-01-15'),
('بطاطس', 22.0, 18.0, 26.0, 'EGP/kg', 'سوق العبور', '2025-01-15'),
('قمح', 15000.0, 14200.0, 15800.0, 'EGP/ton', 'سوق العبور', '2025-01-15'),
('ذرة', 12000.0, 11500.0, 12500.0, 'EGP/ton', 'سوق العبور', '2025-01-15'),
('فلفل', 55.0, 48.0, 62.0, 'EGP/kg', 'سوق العبور', '2025-01-15');

-- سوق الجملة الإسماعيلية
INSERT INTO market_prices (commodity, price, min_price, max_price, unit, market_name, date) VALUES
('طماطم', 42.0, 35.0, 48.0, 'EGP/kg', 'سوق الجملة الإسماعيلية', '2025-01-15'),
('بصل', 25.0, 22.0, 28.0, 'EGP/kg', 'سوق الجملة الإسماعيلية', '2025-01-15'),
('بطاطس', 20.0, 17.0, 23.0, 'EGP/kg', 'سوق الجملة الإسماعيلية', '2025-01-15'),
('قمح', 14800.0, 14000.0, 15500.0, 'EGP/ton', 'سوق الجملة الإسماعيلية', '2025-01-15'),
('ذرة', 11800.0, 11200.0, 12300.0, 'EGP/ton', 'سوق الجملة الإسماعيلية', '2025-01-15'),
('فلفل', 50.0, 45.0, 55.0, 'EGP/kg', 'سوق الجملة الإسماعيلية', '2025-01-15');

-- سوق بني سويف
INSERT INTO market_prices (commodity, price, min_price, max_price, unit, market_name, date) VALUES
('طماطم', 40.0, 35.0, 45.0, 'EGP/kg', 'سوق بني سويف', '2025-01-15'),
('بصل', 24.0, 20.0, 28.0, 'EGP/kg', 'سوق بني سويف', '2025-01-15'),
('بطاطس', 19.0, 16.0, 22.0, 'EGP/kg', 'سوق بني سويف', '2025-01-15'),
('قمح', 14500.0, 13800.0, 15200.0, 'EGP/ton', 'سوق بني سويف', '2025-01-15'),
('ذرة', 11500.0, 11000.0, 12000.0, 'EGP/ton', 'سوق بني سويف', '2025-01-15'),
('فلفل', 48.0, 42.0, 54.0, 'EGP/kg', 'سوق بني سويف', '2025-01-15');


-- ============================================
-- Sensor Readings (Last 7 Days)
-- ============================================

-- Farm 1: مزرعة الفيوم
INSERT INTO sensor_readings (farm_id, sensor_id, type, value, unit, is_anomaly, timestamp) VALUES
-- Temperature
(1, 'sensor_temp_01', 'temperature', 28.5, '°C', FALSE, NOW() - INTERVAL '0 days'),
(1, 'sensor_temp_01', 'temperature', 29.0, '°C', FALSE, NOW() - INTERVAL '1 days'),
(1, 'sensor_temp_01', 'temperature', 27.5, '°C', FALSE, NOW() - INTERVAL '2 days'),
(1, 'sensor_temp_01', 'temperature', 32.0, '°C', FALSE, NOW() - INTERVAL '3 days'),
(1, 'sensor_temp_01', 'temperature', 33.5, '°C', FALSE, NOW() - INTERVAL '4 days'),
(1, 'sensor_temp_01', 'temperature', 26.0, '°C', FALSE, NOW() - INTERVAL '5 days'),
(1, 'sensor_temp_01', 'temperature', 24.5, '°C', FALSE, NOW() - INTERVAL '6 days'),
(1, 'sensor_temp_02', 'temperature', 46.0, '°C', TRUE, NOW() - INTERVAL '2 hours'),

-- Humidity
(1, 'sensor_hum_01', 'humidity', 65.0, '%', FALSE, NOW() - INTERVAL '0 days'),
(1, 'sensor_hum_01', 'humidity', 62.0, '%', FALSE, NOW() - INTERVAL '1 days'),
(1, 'sensor_hum_01', 'humidity', 58.0, '%', FALSE, NOW() - INTERVAL '2 days'),
(1, 'sensor_hum_01', 'humidity', 55.0, '%', FALSE, NOW() - INTERVAL '3 days'),
(1, 'sensor_hum_01', 'humidity', 60.0, '%', FALSE, NOW() - INTERVAL '4 days'),
(1, 'sensor_hum_01', 'humidity', 12.0, '%', TRUE, NOW() - INTERVAL '12 hours'),

-- Soil Moisture
(1, 'sensor_mois_01', 'soil_moisture', 45.0, '%', FALSE, NOW() - INTERVAL '0 days'),
(1, 'sensor_mois_01', 'soil_moisture', 42.0, '%', FALSE, NOW() - INTERVAL '1 days'),
(1, 'sensor_mois_01', 'soil_moisture', 38.0, '%', FALSE, NOW() - INTERVAL '2 days'),
(1, 'sensor_mois_01', 'soil_moisture', 8.0, '%', TRUE, NOW() - INTERVAL '6 hours'),

-- pH
(1, 'sensor_ph_01', 'ph', 6.8, '', FALSE, NOW() - INTERVAL '0 days'),
(1, 'sensor_ph_01', 'ph', 6.7, '', FALSE, NOW() - INTERVAL '1 days'),
(1, 'sensor_ph_01', 'ph', 6.9, '', FALSE, NOW() - INTERVAL '2 days'),
(1, 'sensor_ph_01', 'ph', 4.2, '', TRUE, NOW() - INTERVAL '1 days'),

-- Light
(1, 'sensor_light_01', 'light', 450.0, 'lux', FALSE, NOW() - INTERVAL '0 days'),
(1, 'sensor_light_01', 'light', 420.0, 'lux', FALSE, NOW() - INTERVAL '1 days'),
(1, 'sensor_light_01', 'light', 380.0, 'lux', FALSE, NOW() - INTERVAL '2 days');


-- Farm 2: مزرعة الإسماعيلية
INSERT INTO sensor_readings (farm_id, sensor_id, type, value, unit, is_anomaly, timestamp) VALUES
-- Temperature
(2, 'sensor_temp_03', 'temperature', 30.5, '°C', FALSE, NOW() - INTERVAL '0 days'),
(2, 'sensor_temp_03', 'temperature', 31.0, '°C', FALSE, NOW() - INTERVAL '1 days'),
(2, 'sensor_temp_03', 'temperature', 29.5, '°C', FALSE, NOW() - INTERVAL '2 days'),
(2, 'sensor_temp_03', 'temperature', 28.0, '°C', FALSE, NOW() - INTERVAL '3 days'),
(2, 'sensor_temp_03', 'temperature', 52.0, '°C', TRUE, NOW() - INTERVAL '4 hours'),

-- Humidity
(2, 'sensor_hum_02', 'humidity', 70.0, '%', FALSE, NOW() - INTERVAL '0 days'),
(2, 'sensor_hum_02', 'humidity', 72.0, '%', FALSE, NOW() - INTERVAL '1 days'),
(2, 'sensor_hum_02', 'humidity', 68.0, '%', FALSE, NOW() - INTERVAL '2 days'),
(2, 'sensor_hum_02', 'humidity', 8.0, '%', TRUE, NOW() - INTERVAL '8 hours'),

-- Soil Moisture
(2, 'sensor_mois_02', 'soil_moisture', 55.0, '%', FALSE, NOW() - INTERVAL '0 days'),
(2, 'sensor_mois_02', 'soil_moisture', 52.0, '%', FALSE, NOW() - INTERVAL '1 days'),
(2, 'sensor_mois_02', 'soil_moisture', 48.0, '%', FALSE, NOW() - INTERVAL '2 days'),
(2, 'sensor_mois_02', 'soil_moisture', 5.0, '%', TRUE, NOW() - INTERVAL '1 days'),

-- pH
(2, 'sensor_ph_02', 'ph', 7.0, '', FALSE, NOW() - INTERVAL '0 days'),
(2, 'sensor_ph_02', 'ph', 6.9, '', FALSE, NOW() - INTERVAL '1 days'),
(2, 'sensor_ph_02', 'ph', 7.1, '', FALSE, NOW() - INTERVAL '2 days'),
(2, 'sensor_ph_02', 'ph', 3.8, '', TRUE, NOW() - INTERVAL '6 hours'),

-- Light
(2, 'sensor_light_02', 'light', 500.0, 'lux', FALSE, NOW() - INTERVAL '0 days'),
(2, 'sensor_light_02', 'light', 480.0, 'lux', FALSE, NOW() - INTERVAL '1 days'),
(2, 'sensor_light_02', 'light', 520.0, 'lux', FALSE, NOW() - INTERVAL '2 days');


-- Farm 3: مزرعة بني سويف
INSERT INTO sensor_readings (farm_id, sensor_id, type, value, unit, is_anomaly, timestamp) VALUES
-- Temperature
(3, 'sensor_temp_05', 'temperature', 27.0, '°C', FALSE, NOW() - INTERVAL '0 days'),
(3, 'sensor_temp_05', 'temperature', 26.5, '°C', FALSE, NOW() - INTERVAL '1 days'),
(3, 'sensor_temp_05', 'temperature', 28.0, '°C', FALSE, NOW() - INTERVAL '2 days'),
(3, 'sensor_temp_05', 'temperature', 25.5, '°C', FALSE, NOW() - INTERVAL '3 days'),
(3, 'sensor_temp_05', 'temperature', 49.0, '°C', TRUE, NOW() - INTERVAL '3 hours'),

-- Humidity
(3, 'sensor_hum_03', 'humidity', 60.0, '%', FALSE, NOW() - INTERVAL '0 days'),
(3, 'sensor_hum_03', 'humidity', 58.0, '%', FALSE, NOW() - INTERVAL '1 days'),
(3, 'sensor_hum_03', 'humidity', 55.0, '%', FALSE, NOW() - INTERVAL '2 days'),
(3, 'sensor_hum_03', 'humidity', 10.0, '%', TRUE, NOW() - INTERVAL '10 hours'),

-- Soil Moisture
(3, 'sensor_mois_03', 'soil_moisture', 50.0, '%', FALSE, NOW() - INTERVAL '0 days'),
(3, 'sensor_mois_03', 'soil_moisture', 48.0, '%', FALSE, NOW() - INTERVAL '1 days'),
(3, 'sensor_mois_03', 'soil_moisture', 45.0, '%', FALSE, NOW() - INTERVAL '2 days'),
(3, 'sensor_mois_03', 'soil_moisture', 3.0, '%', TRUE, NOW() - INTERVAL '4 hours'),

-- pH
(3, 'sensor_ph_03', 'ph', 6.5, '', FALSE, NOW() - INTERVAL '0 days'),
(3, 'sensor_ph_03', 'ph', 6.4, '', FALSE, NOW() - INTERVAL '1 days'),
(3, 'sensor_ph_03', 'ph', 6.6, '', FALSE, NOW() - INTERVAL '2 days'),
(3, 'sensor_ph_03', 'ph', 4.5, '', TRUE, NOW() - INTERVAL '12 hours'),

-- Light
(3, 'sensor_light_03', 'light', 430.0, 'lux', FALSE, NOW() - INTERVAL '0 days'),
(3, 'sensor_light_03', 'light', 410.0, 'lux', FALSE, NOW() - INTERVAL '1 days'),
(3, 'sensor_light_03', 'light', 390.0, 'lux', FALSE, NOW() - INTERVAL '2 days');
