
-- online_sales (HW1 ile bağlantılı ETL için)
CREATE TABLE IF NOT EXISTS online_sales (
    id SERIAL PRIMARY KEY,
    product_id INT,
    quantity INT
);

INSERT INTO online_sales (product_id, quantity) VALUES
(1, 5),
(2, 3),
(1, 2),
(3, 7);

-- test_table (HW2 başlangıç tablosu)
CREATE TABLE IF NOT EXISTS test_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

INSERT INTO test_table (name) VALUES ('sde_gl'), ('Airflow'), ('Docker');
