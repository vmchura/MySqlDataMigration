CREATE TABLE main_products_table (
    main_product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL
);
CREATE TABLE variation_products_table(
    variation_product_id INT AUTO_INCREMENT PRIMARY KEY,
    main_product_id INT NOT NULL,
    variation_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (main_product_id) REFERENCES main_products_table(main_product_id));

-- INSERT INTO main_products_table VALUES (1, 'cafe especial'), (2, 'queso');
-- INSERT INTO variation_products_table VALUES (1, 1, '1kg'), (2, 1, '3kg');