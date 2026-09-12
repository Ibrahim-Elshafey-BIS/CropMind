--
-- CropMind - Farms Seed Data
-- Realistic Egyptian agricultural data
--
-- Author: CropMind Team
-- Date: 2026
--

-- ============================================
-- 1. Farms
-- ============================================

INSERT INTO farms (name, location, area, crop_type, is_active) VALUES
('مزرعة الفيوم', 'الفيوم', 50.0, 'قمح', TRUE),
('مزرعة الإسماعيلية', 'الإسماعيلية', 30.0, 'طماطم', TRUE),
('مزرعة بني سويف', 'بني سويف', 80.0, 'ذرة', TRUE);

-- ============================================
-- 2. Users (password: "password123" hashed with bcrypt)
-- ============================================

INSERT INTO users (email, hashed_password, full_name, role, farm_id, is_active, is_superuser) VALUES
('ahmed@cropmind.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPjHBHd0qA9Rm', 'أحمد محمد', 'manager', 1, TRUE, FALSE),
('sara@cropmind.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPjHBHd0qA9Rm', 'سارة علي', 'manager', 2, TRUE, FALSE),
('khaled@cropmind.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPjHBHd0qA9Rm', 'خالد حسن', 'manager', 3, TRUE, FALSE);

-- ============================================
-- 3. Workers
-- ============================================

-- Farm 1: مزرعة الفيوم
INSERT INTO workers (farm_id, full_name, phone, role, daily_wage, is_active, hire_date) VALUES
(1, 'محمود إبراهيم', '01012345678', 'laborer', 200.0, TRUE, '2024-01-15'),
(1, 'علي حسن', '01087654321', 'supervisor', 350.0, TRUE, '2023-11-01');

-- Farm 2: مزرعة الإسماعيلية
INSERT INTO workers (farm_id, full_name, phone, role, daily_wage, is_active, hire_date) VALUES
(2, 'سامي عادل', '01112345678', 'laborer', 180.0, TRUE, '2024-03-01'),
(2, 'حسن محمود', '01187654321', 'irrigation_specialist', 300.0, TRUE, '2023-12-15');

-- Farm 3: مزرعة بني سويف
INSERT INTO workers (farm_id, full_name, phone, role, daily_wage, is_active, hire_date) VALUES
(3, 'مصطفى محمد', '01212345678', 'supervisor', 380.0, TRUE, '2023-08-01');

-- ============================================
-- 4. Crops
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
-- 5. Transactions
-- ============================================

-- Farm 1: مزرعة الفيوم
INSERT INTO transactions (farm_id, type, category, amount, description, date) VALUES
(1, 'expense', 'seeds', 2500.0, 'شراء تقاوي قمح', '2024-10-15'),
(1, 'expense', 'fertilizer', 4800.0, 'أسمدة عضوية وكيماوية', '2024-11-01'),
(1, 'expense', 'labor', 6200.0, 'أجور عمال شهر نوفمبر', '2024-11-30'),
(1, 'expense', 'irrigation', 1800.0, 'تكاليف ري', '2024-12-01'),
(1, 'income', 'sales', 15000.0, 'بيع قمح موسم سابق', '2024-10-20');

-- Farm 2: مزرعة الإسماعيلية
INSERT INTO transactions (farm_id, type, category, amount, description, date) VALUES
(2, 'expense', 'seeds', 3200.0, 'شراء تقاوي طماطم وفلفل', '2024-09-01'),
(2, 'expense', 'fertilizer', 5600.0, 'أسمدة عنصرية', '2024-09-15'),
(2, 'expense', 'labor', 4800.0, 'أجور عمال', '2024-10-31'),
(2, 'expense', 'pesticide', 2800.0, 'مبيدات حشرية وفطرية', '2024-10-10'),
(2, 'income', 'sales', 32000.0, 'بيع طماطم وفلفل', '2024-11-15');

-- Farm 3: مزرعة بني سويف
INSERT INTO transactions (farm_id, type, category, amount, description, date) VALUES
(3, 'expense', 'seeds', 4500.0, 'شراء تقاوي ذرة وفول', '2024-04-15'),
(3, 'expense', 'fertilizer', 7200.0, 'أسمدة نيتروجينية وفوسفاتية', '2024-05-01'),
(3, 'expense', 'labor', 8500.0, 'أجور عمال صيف', '2024-08-31'),
(3, 'expense', 'irrigation', 2400.0, 'تكاليف ري صيفي', '2024-07-15'),
(3, 'income', 'sales', 48000.0, 'بيع ذرة صيفي', '2024-09-30');

-- ============================================
-- 6. Inventory Items
-- ============================================

-- Farm 1: مزرعة الفيوم
INSERT INTO inventory_items (farm_id, name, category, quantity, unit, min_quantity, price_per_unit, notes) VALUES
(1, 'تقاوي قمح', 'seeds', 150.0, 'kg', 50.0, 18.0, 'صنف سخا 94'),
(1, 'سماد يوريا', 'fertilizer', 200.0, 'kg', 80.0, 12.0, NULL),
(1, 'سماد سوبر فوسفات', 'fertilizer', 100.0, 'kg', 50.0, 10.0, NULL),
(1, 'مبيد حشري', 'pesticide', 15.0, 'liter', 5.0, 120.0, NULL),
(1, 'خرطوم ري', 'equipment', 200.0, 'meter', 50.0, 8.0, NULL);

-- Farm 2: مزرعة الإسماعيلية
INSERT INTO inventory_items (farm_id, name, category, quantity, unit, min_quantity, price_per_unit, notes) VALUES
(2, 'تقاوي طماطم', 'seeds', 5.0, 'kg', 2.0, 350.0, 'صنف فردوس'),
(2, 'تقاوي فلفل', 'seeds', 3.0, 'kg', 1.0, 280.0, 'حلو بلدي'),
(2, 'سماد NPK', 'fertilizer', 150.0, 'kg', 60.0, 25.0, NULL),
(2, 'مبيد فطري', 'pesticide', 8.0, 'liter', 3.0, 150.0, NULL),
(2, 'مبيد حشري', 'pesticide', 10.0, 'liter', 4.0, 130.0, NULL),
(2, 'شبكة ري تنقيط', 'equipment', 500.0, 'meter', 100.0, 6.0, NULL);

-- Farm 3: مزرعة بني سويف
INSERT INTO inventory_items (farm_id, name, category, quantity, unit, min_quantity, price_per_unit, notes) VALUES
(3, 'تقاوي ذرة', 'seeds', 100.0, 'kg', 40.0, 45.0, 'هجين 321'),
(3, 'تقاوي فول', 'seeds', 80.0, 'kg', 30.0, 30.0, 'سوداني'),
(3, 'سماد يوريا', 'fertilizer', 300.0, 'kg', 120.0, 11.0, NULL),
(3, 'سماد سوبر فوسفات', 'fertilizer', 150.0, 'kg', 60.0, 9.0, NULL),
(3, 'مبيد حشري', 'pesticide', 20.0, 'liter', 8.0, 110.0, NULL),
(3, 'جرار', 'equipment', 1.0, 'piece', 0.0, 250000.0, 'جرار ماسي فيرجسون');
