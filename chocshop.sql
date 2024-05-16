/*
This is chocshop.sql, a script for setting up and populating a database for a chocolate shop.

Author: Jason Fearnall
Date: 5/16/2024
Filename: chocshop.sql
*/

-- Create and use the chocshop database
CREATE DATABASE IF NOT EXISTS chocshop;
USE chocshop;


----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------- Create Tables and Populate with sample data----------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS customer (
    cust_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address VARCHAR(250),
    zip_code VARCHAR(5)
);

INSERT INTO customer (name, email, phone, address, zip_code) 
VALUES 
    ('Jack B Nimble', 'jack.nimble@example.com', '123-456-7890', '123 Jump Street', '12345'),
    ('Jack B Quick', 'jack.quick@example.com', '234-567-8901', '456 Dash Avenue', '23456'),
    ('Kandelle Stik', 'Kandelle.stik@example.com', '345-678-9012', '789 Flame Boulevard', '34567'),
    ('Jumpin J Flash', 'jumpin.flash@example.com', '456-789-1234', '012 Lightning Lane', '45678');

CREATE TABLE IF NOT EXISTS chocolate (
    choc_id INT PRIMARY KEY AUTO_INCREMENT,
    type VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    inventory_count INT 
);
INSERT INTO chocolate (type, price, inventory_count) 
VALUES 
    ('Dark Chocolate', 2.50, 100),
    ('Milk Chocolate', 2.00, 150),
    ('White Chocolate', 2.25, 120),
    ('Almond Choc Bar', 2.25, 120),
    ('Turtles', 2.25, 120),
    ('Swiss Imported', 3.25, 220);

CREATE TABLE IF NOT EXISTS orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    cust_id INT,
    order_date DATE,
    subtotal DECIMAL(10, 2),
    FOREIGN KEY (cust_id) REFERENCES customer(cust_id)
);
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    choc_id INT,
    quantity INT,
    price DECIMAL(10, 2),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (choc_id) REFERENCES chocolate(choc_id)
);



----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------- Create Triggers for functionality-------------------------------------------------------------------------------------------------

DELIMITER //

-- Trigger to set the price of an order item based on the chocolate price
CREATE TRIGGER set_price_before_insert
BEFORE INSERT ON order_items
FOR EACH ROW
BEGIN
    DECLARE chocolate_price DECIMAL(10, 2);

    SELECT price INTO chocolate_price FROM chocolate WHERE choc_id = NEW.choc_id;

    IF chocolate_price IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No chocolate with the given choc_id exists';
    ELSE
        SET NEW.price = chocolate_price * NEW.quantity;
    END IF;
END;//


-- Trigger to update the inventory count of a chocolate after an order item is inserted
CREATE TRIGGER decrease_inventory_after_insert
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
    UPDATE chocolate
    SET inventory_count = inventory_count - NEW.quantity
    WHERE choc_id = NEW.choc_id;
END;//


-- Trigger to update the subtotal of an order after an order item is inserted
CREATE TRIGGER email_check_before_insert BEFORE INSERT ON customer
FOR EACH ROW
BEGIN
    IF NEW.email NOT REGEXP '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,4}$' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid email format';
    END IF;
END;//


-- Trigger to validate the phone number format before inserting a new customer
CREATE TRIGGER validate_phone_before_insert
BEFORE INSERT ON customer
FOR EACH ROW
BEGIN
    IF NOT NEW.phone REGEXP '^[0-9]{3}-[0-9]{3}-[0-9]{4}$' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid phone format';
    END IF;
END;//


-- Trigger to validate the zip code format before inserting a new customer
CREATE TRIGGER validate_zip_code_before_insert
BEFORE INSERT ON customer
FOR EACH ROW
BEGIN
    IF NOT NEW.zip_code REGEXP '^[0-9]{5}$' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid zip code format';
    END IF;
END;//
DELIMITER ;


----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------- Create Views----------------------------------------------------------------------------------------------------------------------

-- View to display customer orders
CREATE VIEW customer_orders AS
SELECT customer.cust_id, customer.name, COUNT(`orders`.order_id) AS total_orders
FROM customer
JOIN `orders` ON customer.cust_id = `orders`.cust_id
GROUP BY customer.cust_id;


-- View to display total amount spent by each customer
CREATE VIEW customers_total_spent AS
SELECT customer.cust_id, customer.name, SUM(orders.subtotal) AS total_spend
FROM customer
JOIN orders ON customer.cust_id = orders.cust_id
GROUP BY customer.cust_id;


----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------Window Functions-------------------------------------------------------------------------------------------------------------------

-- window function to calculate the average total spend across all customers
SELECT cust_id, name, total_spend, AVG(total_spend) OVER () as avg_spend
FROM customers_total_spent;

-- window funtion to calculate the running total of quantity ordered for each chocolate type
SELECT chocolate.type, order_items.quantity,
       SUM(order_items.quantity) OVER (PARTITION BY chocolate.type ORDER BY orders.order_date) as running_total
FROM order_items
JOIN orders ON order_items.order_id = orders.order_id
JOIN chocolate ON order_items.choc_id = chocolate.choc_id;

-- window function to calculate the average quantity ordered for each chocolate type within each order
SELECT orders.order_id, chocolate.type, AVG(order_items.quantity) OVER (PARTITION BY orders.order_id, chocolate.type) as avg_quantity
FROM order_items
JOIN orders ON order_items.order_id = orders.order_id
JOIN chocolate ON order_items.choc_id = chocolate.choc_id;


----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------Create User/Permissions-----------------------------------------------------------------------------------------------------------

-- Create a new users
CREATE USER 'fearnall@hotmail.com' IDENTIFIED BY '11111111';
CREATE USER 'admin.jfear@chocshop.com' IDENTIFIED BY 'password';
CREATE USER 'first_cust@chocshop.com' IDENTIFIED BY 'password';


-- Grant privileges to the new user
GRANT ALL PRIVILEGES ON chocshop.* TO 'fearnall@hotmail.com' WITH ADMIN OPTION;

-- Create Role
CREATE ROLE 'manager';

--Greant Privileges to the Role
GRANT SELECT, UPDATE ON chocshop.customer TO 'manager';

-- Grant the role to the user
GRANT 'manager' TO 'admin,jfear@chocshop.com' WITH ADMIN OPTION;


CREATE ROLE 'customer';

GRANT SELECT ON chocshop.chocolate TO 'customer';
GRANT SELECT, INSERT ON chocshop.orders TO 'customer';
GRANT SELECT, INSERT ON chocshop.order_items TO 'customer';
GRANT SELECT ON chocshop.customer TO 'customer';

CREATE USER 'jack.frost@example.com';
GRANT 'customer' TO 'jack.frost@example.com';


----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------Queries---------------------------------------------------------------------------------------------------------------------------


-- Query to retrieve the highest selling chocolate type
SELECT chocolate.type, SUM(order_items.quantity) as total_sales
FROM order_items
JOIN chocolate ON order_items.choc_id = chocolate.choc_id
GROUP BY chocolate.type
ORDER BY total_sales DESC
LIMIT 1;

-- Query to retrieve the top 5 customers by total order amount
SELECT customer.name, SUM(orders.subtotal) as total_order_amount
FROM orders
JOIN customer ON orders.cust_id = customer.cust_id
GROUP BY customer.name
ORDER BY total_order_amount DESC
LIMIT 5;


-- Query to retrieve chocolates with inventory count less than 100
SELECT type, inventory_count
FROM chocolate
WHERE inventory_count < 100;


-- Complex query using subquery to find the top selling chocolate and the customers who bought it
SELECT customer.name, chocolate.type, SUM(order_items.quantity) as total_quantity
FROM order_items
JOIN orders ON order_items.order_id = orders.order_id
JOIN customer ON orders.cust_id = customer.cust_id
JOIN chocolate ON order_items.choc_id = chocolate.choc_id
WHERE order_items.choc_id = (
    SELECT choc_id
    FROM (
        SELECT choc_id, SUM(quantity) as total_quantity
        FROM order_items
        GROUP BY choc_id
        ORDER BY total_quantity DESC
        LIMIT 1
    ) as top_selling_chocolate
)
GROUP BY customer.name, chocolate.type
ORDER BY total_quantity DESC;