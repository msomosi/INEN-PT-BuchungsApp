-- Create extensions
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create tables
CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    room_number VARCHAR(50) NOT NULL,
    room_type VARCHAR(50) NOT NULL,
    capacity INT NOT NULL,
    price_per_night DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'available'
);

CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    room_id INT REFERENCES rooms(id),
    customer_id INT REFERENCES customers(id),
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO rooms (room_number, room_type, capacity, price_per_night) VALUES
    ('101', 'Standard', 2, 100.00),
    ('102', 'Deluxe', 2, 150.00),
    ('201', 'Suite', 4, 250.00);

INSERT INTO customers (first_name, last_name, email, phone) VALUES
    ('John', 'Doe', 'john.doe@example.com', '+1234567890'),
    ('Jane', 'Smith', 'jane.smith@example.com', '+0987654321');

INSERT INTO bookings (room_id, customer_id, check_in_date, check_out_date, total_price) VALUES
    (1, 1, '2024-02-01', '2024-02-03', 200.00),
    (2, 2, '2024-02-05', '2024-02-07', 300.00);