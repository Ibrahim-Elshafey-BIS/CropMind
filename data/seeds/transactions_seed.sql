--
-- CropMind - Additional Transactions Seed Data (6 months)
-- July - December 2024 for all 3 farms
--
-- Author: CropMind Team
-- Date: 2026
--

-- ============================================
-- Farm 1: مزرعة الفيوم (قمح)
-- ============================================

-- July 2024
INSERT INTO transactions (farm_id, type, category, amount, description, date) VALUES
(1, 'expense', 'irrigation', 1200.0, 'تكاليف ري يوليو', '2024-07-15'),
(1, 'expense', 'labor', 4000.0, 'أجور عمال يوليو', '2024-07-31');

-- August 2024
INSERT INTO transactions (farm_id, type, category, amount, description, date) VALUES
(1, 'expense', 'irrigation', 1350.0, 'تكاليف ري أغسطس', '2024-08-15'),
(1, 'expense', 'labor', 4200.0, 'أجور عمال أغسطس', '2024-08-31'),
(1, 'expense', 'equipment', 2500.0, 'صيانة جرار', '2024-08-20');

-- September 2024
INSERT INTO transactions (farm_id, type, category, amount, description, date) VALUES
(1, 'expense', 'irrigation', 1100.0, 'تكاليف ري سبتمبر', '2024-09-15'),
(1, 'expense', 'labor', 3800.0, 'أجور عمال سبتمبر', '2024-09-30'),
(1, 'income', 'sales', 18000.0, 'بيع قمح موسم الربيع', '2024-09-10');

-- October 2024
INSERT INTO transactions (farm_id, type, category, amount, description, date) VALUES
(1, 'expense', 'seeds', 2500.0, 'شراء تقاوي قمح للموسم الجديد', '2024-10-01'),
(1, 'expense', 'fertilizer', 3200.0, 'أسمدة للموسم الجديد', '2024-10-05'),
(1, 'expense', 'labor', 4500.0, 'أجور عمال أكتوبر', '2024-10-31');

-- November 2024
INSERT INTO transactions (farm_id, type, category, amount, description, date) VALUES
(1, 'expense', 'fertilizer', 4800.0, 'أسمدة عضوية وكيماوية', '2024-11-01'),
(1, 'expense', 'labor', 6200.0, 'أجور عمال نوفمبر', '2024-11-30'),
(1, 'expense', 'pesticide', 800.0, 'مبيدات حشرية', '2024-11-15');

-- December 2024
INSERT INTO transactions (farm_id, type, category, amount, description, date) VALUES
(1, 'expense', 'irrigation', 1800.0, 'تكاليف ري ديسمبر', '2024-12-01'),
(1, 'expense', 'labor', 5800.0, 'أجور عمال ديسمبر', '2024-12-31'),
(1, 'expense', 'equipment', 1200.0, 'قطع غيار للجرار', '2024-12-15');


-- ============================================
-- Farm 2: مزرعة الإسماعيلية (طماطم)
-- ============================================

-- July 2024
INSERT INTO transactions (farm_id, type, category, amount, description, date) VALUES
(2, 'expense', 'irrigation', 2500.0, 'تكاليف ري يوليو', '2024-07-15'),
(2, 'expense', 'labor', 5000.0, 'أجور عمال يوليو', '2024-07-31'),
(2, 'expense', 'pesticide', 2800.0, 'مبيدات حشرية وفطرية', '2024-07-20');

-- August 2024
INSERT INTO transactions (farm_id, type, category, amount, description, date) VALUES
(2, 'expense', 'irrigation', 2800.0, 'تكاليف ري أغسطس', '2024-08-15'),
(2, 'expense', 'labor', 5200.0, 'أجور عمال أغسطس', '2024-08-31'),
(2, 'income', 'sales', 45000.0, 'بيع طماطم صيفي', '2024-08-25');

-- September 2024
INSERT INTO transactions (farm_id, type, category, amount, description, date) VALUES
(2, 'expense', 'seeds', 3200.0, 'شراء تقاوي طماطم وفلفل', '2024-09-01'),
(2, 'expense', 'fertilizer', 3800.0, 'أسمدة عنصرية', '2024-09-10'),
(2, 'expense', 'labor', 4800.0, 'أجور عمال سبتمبر', '2024-09-30');

-- October 2024
INSERT INTO transactions (farm_id, type, category, amount, description, date) VALUES
(2, 'expense', 'fertilizer', 5600.0, 'أسمدة NPK', '2024-10-05'),
(2, 'expense', 'labor', 5500.0, 'أجور عمال أكتوبر', '2024-10-31'),
(2, 'expense', 'pesticide', 2000.0, 'مبيدات حشرية', '2024-10-15');

-- November 2024
INSERT INTO transactions (farm_id, type, category, amount, description, date) VALUES
(2, 'income', 'sales', 32000.0, 'بيع طماطم وفلفل', '2024-11-15'),
(2, 'expense', 'labor', 6000.0, 'أجور عمال نوفمبر', '2024-11-30'),
(2, 'expense', 'equipment', 3500.0, 'شراء شبكات ري تنقيط', '2024-11-01');

-- December 2024
INSERT INTO transactions (farm_id, type, category, amount, description, date) VALUES
(2, 'expense', 'irrigation', 2200.0, 'تكاليف ري ديسمبر', '2024-12-01'),
(2, 'expense', 'labor', 5800.0, 'أجور عمال ديسمبر', '2024-12-31'),
(2, 'expense', 'fertilizer', 4200.0, 'أسمدة شتوية', '2024-12-15'),
(2, 'income', 'sales', 28000.0, 'بيع خيار وفلفل', '2024-12-20');


-- ============================================
-- Farm 3: مزرعة بني سويف (ذرة)
-- ============================================

-- July 2024
INSERT INTO transactions (farm_id, type, category, amount, description, date) VALUES
(3, 'expense', 'irrigation', 3000.0, 'تكاليف ري يوليو', '2024-07-15'),
(3, 'expense', 'labor', 6000.0, 'أجور عمال يوليو', '2024-07-31'),
(3, 'expense', 'fertilizer', 4500.0, 'أسمدة نيتروجينية', '2024-07-10');

-- August 2024
INSERT INTO transactions (farm_id, type, category, amount, description, date) VALUES
(3, 'expense', 'irrigation', 3500.0, 'تكاليف ري أغسطس', '2024-08-15'),
(3, 'expense', 'labor', 6500.0, 'أجور عمال أغسطس', '2024-08-31'),
(3, 'expense', 'pesticide', 3000.0, 'مبيدات حشرية للذرة', '2024-08-20'),
(3, 'income', 'sales', 60000.0, 'بيع ذرة صيفي مبكر', '2024-08-25');

-- September 2024
INSERT INTO transactions (farm_id, type, category, amount, description, date) VALUES
(3, 'income', 'sales', 48000.0, 'بيع ذرة صيفي', '2024-09-30'),
(3, 'expense', 'labor', 7000.0, 'أجور عمال سبتمبر', '2024-09-30'),
(3, 'expense', 'equipment', 8000.0, 'شراء جرار جديد', '2024-09-15');

-- October 2024
INSERT INTO transactions (farm_id, type, category, amount, description, date) VALUES
(3, 'expense', 'seeds', 4500.0, 'شراء تقاوي ذرة وفول', '2024-10-01'),
(3, 'expense', 'fertilizer', 5200.0, 'أسمدة شتوية', '2024-10-10'),
(3, 'expense', 'labor', 6500.0, 'أجور عمال أكتوبر', '2024-10-31');

-- November 2024
INSERT INTO transactions (farm_id, type, category, amount, description, date) VALUES
(3, 'expense', 'fertilizer', 7200.0, 'أسمدة فوسفاتية', '2024-11-05'),
(3, 'expense', 'labor', 8500.0, 'أجور عمال نوفمبر', '2024-11-30'),
(3, 'expense', 'irrigation', 2800.0, 'تكاليف ري نوفمبر', '2024-11-15');

-- December 2024
INSERT INTO transactions (farm_id, type, category, amount, description, date) VALUES
(3, 'expense', 'irrigation', 2400.0, 'تكاليف ري ديسمبر', '2024-12-01'),
(3, 'expense', 'labor', 8000.0, 'أجور عمال ديسمبر', '2024-12-31'),
(3, 'expense', 'pesticide', 2500.0, 'مبيدات فطرية', '2024-12-15');
