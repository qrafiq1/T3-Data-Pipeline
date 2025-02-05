-- Set the default schema for the session
SET search_path TO qasim_rafiq_schema;

-- Drops to ensure reusability
DROP TABLE IF EXISTS DIM_Payment_Method CASCADE;
DROP TABLE IF EXISTS DIM_Truck CASCADE;
DROP TABLE IF EXISTS FACT_Transaction CASCADE;

-- Create DIM_Payment_Method table with "cash" and "card" options enforced through foreign key reference or application logic
CREATE TABLE DIM_Payment_Method (
    payment_method_id SMALLINT PRIMARY KEY,
    payment_method VARCHAR(10) NOT NULL
);

-- Create DIM_Truck table without CHECK constraints (enforce fsa_rating range in the application layer)
CREATE TABLE DIM_Truck (
    truck_id SMALLINT PRIMARY KEY,
    truck_name TEXT NOT NULL,
    truck_description TEXT NOT NULL,
    has_card_reader BOOLEAN NOT NULL,
    fsa_rating SMALLINT NOT NULL
);

-- Create FACT_Transaction table without CHECK constraints (enforce date logic in application layer)
CREATE TABLE FACT_Transaction (
    transaction_id BIGINT IDENTITY(1, 1) PRIMARY KEY,
    truck_id SMALLINT REFERENCES DIM_Truck(truck_id),
    payment_method_id SMALLINT REFERENCES DIM_Payment_Method(payment_method_id),
    total FLOAT NOT NULL,
    at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (truck_id) REFERENCES DIM_Truck(truck_id),
    FOREIGN KEY (payment_method_id) REFERENCES DIM_Payment_Method(payment_method_id)
);

-- Seed data for DIM_Payment_Method, restricting to "cash" and "card" in data
INSERT INTO DIM_Payment_Method (payment_method_id, payment_method) VALUES
(1, 'cash'),
(2, 'card');

-- Seed data for DIM_Truck
INSERT INTO DIM_Truck (truck_id, truck_name, truck_description, has_card_reader, fsa_rating) VALUES
(1, 'Burrito Madness', 'An authentic taste of Mexico.', TRUE, 4),
(2, 'Kings of Kebabs', 'Locally-sourced meat cooked over a charcoal grill.', TRUE, 2),
(3, 'Cupcakes by Michelle', 'Handcrafted cupcakes made with high-quality, organic ingredients.', TRUE, 5),
(4, 'Hartmann''s Jellied Eels', 'A taste of history with this classic English dish.', TRUE, 4),
(5, 'Yoghurt Heaven', 'All the great tastes, but only some of the calories!', TRUE, 4),
(6, 'SuperSmoothie', 'Pick any fruit or vegetable, and we''ll make you a delicious, healthy, multi-vitamin shake. Live well; live wild.', FALSE, 3);
