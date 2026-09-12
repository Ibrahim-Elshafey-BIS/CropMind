--
-- CropMind Database Schema
-- PostgreSQL
--
-- Author: CropMind Team
-- Date: 2026
--

-- ============================================
-- 1. Farms Table
-- ============================================

CREATE TABLE farms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(500),
    area FLOAT NOT NULL DEFAULT 0.0,
    crop_type VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_farms_id ON farms (id);
CREATE INDEX ix_farms_name ON farms (name);
CREATE INDEX ix_farms_is_active ON farms (is_active);
CREATE INDEX ix_farms_crop_type ON farms (crop_type);


-- ============================================
-- 2. Users Table
-- ============================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'worker',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    farm_id INTEGER REFERENCES farms(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_users_role CHECK (role IN ('manager', 'worker'))
);

CREATE INDEX ix_users_id ON users (id);
CREATE INDEX ix_users_email ON users (email);
CREATE INDEX ix_users_role ON users (role);
CREATE INDEX ix_users_farm_id ON users (farm_id);
CREATE INDEX ix_users_is_active ON users (is_active);


-- ============================================
-- 3. Workers Table
-- ============================================

CREATE TABLE workers (
    id SERIAL PRIMARY KEY,
    farm_id INTEGER NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'laborer',
    daily_wage FLOAT NOT NULL DEFAULT 0.0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    hire_date DATE NOT NULL,
    notes VARCHAR(1000),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_workers_role CHECK (role IN ('laborer', 'supervisor', 'irrigation_specialist')),
    CONSTRAINT ck_workers_daily_wage CHECK (daily_wage >= 0)
);

CREATE INDEX ix_workers_id ON workers (id);
CREATE INDEX ix_workers_farm_id ON workers (farm_id);
CREATE INDEX ix_workers_full_name ON workers (full_name);
CREATE INDEX ix_workers_role ON workers (role);
CREATE INDEX ix_workers_is_active ON workers (is_active);


-- ============================================
-- 4. Crops Table
-- ============================================

CREATE TABLE crops (
    id SERIAL PRIMARY KEY,
    farm_id INTEGER NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    variety VARCHAR(255),
    area FLOAT NOT NULL,
    planting_date DATE NOT NULL,
    expected_harvest_date DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'growing',
    health_score FLOAT,
    notes VARCHAR(1000),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_crops_status CHECK (status IN ('growing', 'harvested', 'failed')),
    CONSTRAINT ck_crops_health_score CHECK (health_score >= 0 AND health_score <= 100)
);

CREATE INDEX ix_crops_id ON crops (id);
CREATE INDEX ix_crops_farm_id ON crops (farm_id);
CREATE INDEX ix_crops_name ON crops (name);
CREATE INDEX ix_crops_status ON crops (status);
CREATE INDEX ix_crops_planting_date ON crops (planting_date);


-- ============================================
-- 5. Transactions Table
-- ============================================

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    farm_id INTEGER NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    category VARCHAR(255) NOT NULL,
    amount FLOAT NOT NULL,
    description VARCHAR(1000),
    date DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_transactions_type CHECK (type IN ('income', 'expense')),
    CONSTRAINT ck_transactions_amount CHECK (amount >= 0)
);

CREATE INDEX ix_transactions_id ON transactions (id);
CREATE INDEX ix_transactions_farm_id ON transactions (farm_id);
CREATE INDEX ix_transactions_type ON transactions (type);
CREATE INDEX ix_transactions_category ON transactions (category);
CREATE INDEX ix_transactions_date ON transactions (date);


-- ============================================
-- 6. Inventory Items Table
-- ============================================

CREATE TABLE inventory_items (
    id SERIAL PRIMARY KEY,
    farm_id INTEGER NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL DEFAULT 'other',
    quantity FLOAT NOT NULL DEFAULT 0.0,
    unit VARCHAR(50) NOT NULL DEFAULT 'piece',
    min_quantity FLOAT NOT NULL DEFAULT 0.0,
    price_per_unit FLOAT NOT NULL DEFAULT 0.0,
    notes VARCHAR(1000),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_inventory_items_category CHECK (category IN ('seeds', 'fertilizer', 'pesticide', 'equipment', 'other')),
    CONSTRAINT ck_inventory_items_quantity CHECK (quantity >= 0),
    CONSTRAINT ck_inventory_items_min_quantity CHECK (min_quantity >= 0),
    CONSTRAINT ck_inventory_items_price_per_unit CHECK (price_per_unit >= 0)
);

CREATE INDEX ix_inventory_items_id ON inventory_items (id);
CREATE INDEX ix_inventory_items_farm_id ON inventory_items (farm_id);
CREATE INDEX ix_inventory_items_name ON inventory_items (name);
CREATE INDEX ix_inventory_items_category ON inventory_items (category);


-- ============================================
-- 7. Sensor Readings Table
-- ============================================

CREATE TABLE sensor_readings (
    id SERIAL PRIMARY KEY,
    farm_id INTEGER NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    sensor_id VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    value FLOAT NOT NULL,
    unit VARCHAR(50) NOT NULL,
    is_anomaly BOOLEAN NOT NULL DEFAULT FALSE,
    timestamp TIMESTAMPTZ NOT NULL,
    CONSTRAINT ck_sensor_readings_type CHECK (type IN ('temperature', 'humidity', 'soil_moisture', 'ph', 'light'))
);

CREATE INDEX ix_sensor_readings_id ON sensor_readings (id);
CREATE INDEX ix_sensor_readings_farm_id ON sensor_readings (farm_id);
CREATE INDEX ix_sensor_readings_sensor_id ON sensor_readings (sensor_id);
CREATE INDEX ix_sensor_readings_type ON sensor_readings (type);
CREATE INDEX ix_sensor_readings_timestamp ON sensor_readings (timestamp);
CREATE INDEX ix_sensor_readings_is_anomaly ON sensor_readings (is_anomaly);


-- ============================================
-- 8. Market Prices Table
-- ============================================

CREATE TABLE market_prices (
    id SERIAL PRIMARY KEY,
    commodity VARCHAR(255) NOT NULL,
    price FLOAT NOT NULL,
    min_price FLOAT,
    max_price FLOAT,
    unit VARCHAR(50) NOT NULL DEFAULT 'EGP/kg',
    market_name VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_market_prices_price CHECK (price >= 0),
    CONSTRAINT ck_market_prices_min_price CHECK (min_price >= 0 OR min_price IS NULL),
    CONSTRAINT ck_market_prices_max_price CHECK (max_price >= 0 OR max_price IS NULL),
    CONSTRAINT ck_market_prices_price_range CHECK (max_price >= min_price OR min_price IS NULL OR max_price IS NULL)
);

CREATE INDEX ix_market_prices_id ON market_prices (id);
CREATE INDEX ix_market_prices_commodity ON market_prices (commodity);
CREATE INDEX ix_market_prices_market_name ON market_prices (market_name);
CREATE INDEX ix_market_prices_date ON market_prices (date);


-- ============================================
-- Optional: Auto-update updated_at trigger
-- ============================================

-- Create a function to update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to tables with updated_at
CREATE TRIGGER update_farms_updated_at
    BEFORE UPDATE ON farms
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workers_updated_at
    BEFORE UPDATE ON workers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_crops_updated_at
    BEFORE UPDATE ON crops
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at
    BEFORE UPDATE ON transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inventory_items_updated_at
    BEFORE UPDATE ON inventory_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
