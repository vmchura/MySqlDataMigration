CREATE TABLE PRODUCTS (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL
);

-- Optional: Insert some sample data to test the table
INSERT INTO PRODUCTS (product_name) VALUES
    ('Laptop'),
    ('Mouse'),
    ('Keyboard'),
    ('Monitor 20x20'),
    ('Monitor 40x40'),
    ('Headphones');

DELETE FROM PRODUCTS WHERE ID IN (1, 6);

SELECT * FROM PRODUCTS;

SELECT AUTO_INCREMENT
FROM information_schema.TABLES
WHERE TABLE_NAME = 'PRODUCTS';
