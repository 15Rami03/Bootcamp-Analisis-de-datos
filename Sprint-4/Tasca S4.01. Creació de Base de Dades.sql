#SPRINT 4
#NIVEL 1
#EJERCICIO 0
--  1- Creo la base de datos y las tablas (no las definitivas)
CREATE DATABASE ecommerce
CHARACTER SET utf8mb4 -- Soporta todos los caracteres unicode (incluidos emojis 😃, caracteres chinos, árabes, etc.)
COLLATE utf8mb4_unicode_ci; -- Usa reglas de ordenamiento y comparación unicode (no distingue entre mayúsculas y minúsculas A=a, no distingue tildes á=a)

USE ecommerce;
-- companies_temporal
CREATE TABLE companies_temporal (
  company_id VARCHAR(255),
  company_name VARCHAR(500),
  phone VARCHAR(255),
  email VARCHAR(500),
  country VARCHAR(255),
  website VARCHAR(1000)
);
-- credit_card_temporal
CREATE TABLE credit_card_temporal (
  id VARCHAR(255),
  user_id VARCHAR(255),
  iban VARCHAR(255),
  pan VARCHAR(255), -- Hay que arreglarlo quitando los espacios para poder hacer un char(16)
  pin VARCHAR(255),
  cvv VARCHAR(255),
  track1 VARCHAR(2000),
  track2 VARCHAR(2000),
  expiring_date VARCHAR(255) -- Hay que modificar del formato mm-dd-yyy al formato yyyy-mm-dd para darle valor DATE
);
-- products_temporal
CREATE TABLE products_temporal (
  id VARCHAR(255),
  product_name VARCHAR(1000),
  price VARCHAR(255), -- Hay que quitar $ despues de importar datos para usar DECIMAL(10,2)
  colour VARCHAR(255),
  weight VARCHAR(255),
  warehouse_id VARCHAR(255)
);
-- users_temporal
CREATE TABLE users_temporal (
  id VARCHAR(255),
  name VARCHAR(255),
  surname VARCHAR(255),
  phone VARCHAR(255),
  email VARCHAR(500),
  birth_date VARCHAR(255), -- Hay que modificar de mm dd, yyyy a yyyy-mm-dd para pasar a DATE
  country VARCHAR(255),
  city VARCHAR(255),
  postal_code VARCHAR(255), -- Una vez subido los datos comprobar para pasar a un char(5)
  address VARCHAR(1000)
);
-- transactions_temporal
CREATE TABLE transactions_temporal (
  id VARCHAR(255),
  card_id VARCHAR(255),
  business_id VARCHAR(255), -- Hay que cambiar el nombre de la columna a company_id una vez se carguen los datos
  timestamp VARCHAR(255), -- Hay que modificar este campo a not null y default current timestamp
  amount VARCHAR(255),
  declined VARCHAR(255), -- Commprobar si puedo poner BOOL poruqe solo tendré 0 y 1
  product_ids VARCHAR(2000), -- Aqui hay varios id de productos, hay que hacer una tabla extra que contenga esta relacion de muchos a muchos
  user_id VARCHAR(255),
  lat VARCHAR(255),
  longitude VARCHAR(255)
);

-- 2- Preparo MySQL y los archivos CSV para la carga de datos
-- Activar local_infile en el servidor
SHOW VARIABLES LIKE 'local_infile';
-- Si la consulta anterior no da OFF ejecutamos este comando
SET GLOBAL local_infile = 1;
-- Comprobamos si ahora nos sale ON
SHOW VARIABLES LIKE 'local_infile';
-- Visualizo cual es la carpeta desde donde se importa y hacia donde se exporta datos de MySQL
SHOW VARIABLES LIKE "secure_file_priv";

-- 3- Cargo los datos desde los arcivos CSV ubicados en la ruta de acceso: C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\Sprint-4\\companies.csv
-- a) companies_temporal
LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\Sprint-4\\companies.csv'
INTO TABLE companies_temporal
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(company_id, company_name, phone, email, country, website);

-- b) credit_card_temporal
LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\Sprint-4\\credit_cards.csv'
INTO TABLE credit_card_temporal
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, user_id, iban, pan, pin, cvv, track1, track2, expiring_date);

-- c) products_temporal
LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\Sprint-4\\products.csv'
INTO TABLE products_temporal
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, product_name, price, colour, weight, warehouse_id);

-- d) users_temporal (american_users)
LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\Sprint-4\\american_users.csv'
INTO TABLE users_temporal
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, name, surname, phone, email, birth_date, country, city, postal_code, address);

-- e) users_temporal (european_users)
LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\Sprint-4\\european_users.csv'
INTO TABLE users_temporal
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, name, surname, phone, email, birth_date, country, city, postal_code, address);

-- f) transactions_temporal (usa ';' como separador)
LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\Sprint-4\\transactions.csv'
INTO TABLE transactions_temporal
FIELDS TERMINATED BY ';' 
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(id, card_id, business_id, timestamp, amount, declined, product_ids, user_id, lat, longitude);

-- 4- Creo las tablas definitivas, con los tipos de valor adecuados para cada columna
USE ecommerce;
-- Companies
CREATE TABLE companies (
    company_id VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(50),
    country VARCHAR(30),
    website VARCHAR(50)
);

-- Credit Card
CREATE TABLE credit_card (
    id VARCHAR(10) PRIMARY KEY,
    user_id INT,
    iban VARCHAR(30),
    pan CHAR(16),
    pin CHAR(5),
    cvv CHAR(3),
    track1 VARCHAR(50),
    track2 VARCHAR(50),
    expiring_date DATE
);

-- Products
CREATE TABLE products (
    id INT PRIMARY KEY,
    product_name VARCHAR(50),
    price DECIMAL(10,2),
    colour VARCHAR(15),
    weight FLOAT,
    warehouse_id VARCHAR(10)
);

-- Users
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    surname VARCHAR(50),
    phone VARCHAR(30),
    email VARCHAR(50),
    birth_date DATE,
    country VARCHAR(30),
    city VARCHAR(30),
    postal_code VARCHAR(10),
    address VARCHAR(100)
);

-- Transactions
CREATE TABLE transactions (
    id VARCHAR(50) PRIMARY KEY,
    card_id VARCHAR(10),
    company_id VARCHAR(10),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(10,2),
    declined BOOLEAN,
    user_id INT,
    lat VARCHAR(100),
    longitude VARCHAR(100)
);

-- 5- Transformo e inserto los datos en cada una de las tablas
-- Insertar y transformar datos de companies
INSERT INTO companies (company_id, company_name, phone, email, country, website)
SELECT company_id, company_name, phone, email, country, website
FROM companies_temporal;

-- Insertar y transformar datos de credit_card
INSERT INTO credit_card (id, user_id, iban, pan, pin, cvv, track1, track2, expiring_date)
SELECT 
	id,
    user_id,
    iban,
    REPLACE(pan, ' ', '') AS pan, -- quitar espacios entre numeros
    pin,
    cvv,
    track1,
    track2,
    STR_TO_DATE(expiring_date, '%m/%d/%y') AS expiring_date -- modificar el formato de string a date
FROM credit_card_temporal;

-- Insertar y transformar datos de products
INSERT INTO products (id, product_name, price, colour, weight, warehouse_id)
SELECT 
    id,
    product_name,
    REPLACE(price, '$','') AS price, -- quitar '$'
    colour,
    weight,
    warehouse_id
FROM products_temporal;

-- Insertar y transformar datos de users
INSERT INTO users (id, name, surname, phone, email, birth_date, country, city, postal_code, address)
SELECT 
    id,
    name,
    surname,
    phone,
    email,
    STR_TO_DATE(birth_date, '%b %d, %Y') AS birth_date, -- Modificar de string a date ejemplo: "Nov 17, 1985" a DATE
    country,
    city,
    postal_code,
    address
FROM users_temporal;

-- Insertar y transformar datos de transactions
-- Insertar datos de transactions sin product_ids
INSERT INTO transactions (id, card_id, company_id, timestamp, amount, declined, user_id, lat, longitude)
SELECT 
    id,
    card_id,
    business_id AS company_id,
    timestamp,
    amount,
    declined,
    user_id,
    lat,
    longitude
FROM transactions_temporal;

-- Creo las constraints
ALTER TABLE transactions
ADD CONSTRAINT fk_transactions_credit_card
FOREIGN KEY (card_id) REFERENCES credit_card(id),
ADD CONSTRAINT fk_transactions_company
FOREIGN KEY (company_id) REFERENCES companies(id),
ADD CONSTRAINT fk_transactions_user
FOREIGN KEY (user_id) REFERENCES users(id);

#EJERCICIO 1
-- Realiza una subconsulta que muestre a todos los usuarios con más de 80 transacciones utilizando al menos 2 tablas.
SELECT * 
FROM users u
WHERE EXISTS (
    SELECT user_id, COUNT(id) AS number_of_transactions
    FROM transactions t
    WHERE t.user_id = u.id
    GROUP BY t.user_id
    HAVING COUNT(t.id) > 80
);

#EJERCICIO 2
-- Muestra la media de amount por IBAN de las tarjetas de crédito en la compañía Donec Ltd., utiliza por lo menos 2 tablas.
SELECT iban, ROUND(AVG(amount), 2) AS average_amount
FROM transactions t
JOIN credit_card cc
ON t.card_id = cc.id
WHERE EXISTS (
    SELECT c.id
    FROM companies c
    WHERE c.id = t.company_id AND c.company_name = 'Donec Ltd'
)
GROUP BY iban
ORDER BY average_amount DESC ;

#Nivel 2
-- Crea una nueva tabla que refleje el estado de las tarjetas de crédito basado en si las 
-- últimas tres transacciones fueron declinadas entonces inactivo si al menos 1 no es rechazada entonces activo y genera la siguiente consulta:
#Ejercicio 1
-- ¿Cuántas tarjetas están activas?
CREATE TABLE credit_card_status AS
SELECT 
    card_id,
    CASE 
        WHEN SUM(declined) = 3 THEN 'Inactive'
        ELSE 'Active'
    END AS status
FROM (
    SELECT card_id, declined, 
    ROW_NUMBER() OVER (PARTITION BY card_id ORDER BY timestamp DESC) AS row_num 
	-- Uso ROW_NUMBER() para enumerar las transacciones de cada tarjeta desde la más reciente (ORDER BY timestamp DESC).
    -- Así, row_num = 1 es la más reciente, row_num = 2 la segunda, y row_num = 3 la tercera.
    FROM transactions
) AS ordered_transactions
WHERE row_num <= 3 -- Tomo solo las últimas 3 transacciones (las 3 mas recientes)
GROUP BY card_id;
-- Hago la consulta para visualizar si existen tarjetas inactivas y cuantas son
SELECT *
FROM credit_card_status;

-- Genero las relaciones correspondientes
ALTER TABLE credit_card_status
ADD CONSTRAINT pk_card_status PRIMARY KEY (card_id),
ADD CONSTRAINT fk_card_status_credit_card 
FOREIGN KEY (card_id) REFERENCES credit_card(id);

#Nivel 3
-- Crea una tabla con la que podamos unir los datos del nuevo archivo products.csv con la base de datos creada, 
-- teniendo en cuenta que desde transaction tienes product_ids. Genera la siguiente consulta:
#Ejercicio 1
-- Necesitamos conocer el número de veces que se ha vendido cada producto.
-- Desactivo temporalmente la seguridad para realizar cambios
SET SQL_SAFE_UPDATES = 0;

-- Modifico la columna product_ids para eliminar los espacios y poder utilizar FIND IN SET
UPDATE transactions_temporal
SET product_ids = REPLACE(product_ids, ', ', ',');

-- Vuelvo a activar la seguridad para realizar cambios
SET SQL_SAFE_UPDATES = 1;

-- Compruebo que se eliminaron los espacios
SELECT *
FROM transactions_temporal;

-- Creo la tabla puente que contiene la relacion muchos a muchos
CREATE TABLE transactions_products (
    transaction_id VARCHAR(50),
    product_id CHAR(10),
    PRIMARY KEY (transaction_id, product_id),
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Inserto datos utilizando FIND IN SET
INSERT IGNORE INTO transactions_products (transaction_id, product_id)
-- INSERT IGNORE permite que si MySQL detecta duplicados, salte ese duplicado y continue ingresando datos
SELECT t.id AS transaction_id, p.id AS product_id
FROM transactions t
JOIN products p ON FIND_IN_SET(p.id, t.product_ids);  -- tuve que cambiar el tipo de valor de product.id a char

-- visualizar tabla
SELECT *
FROM transactions_products;

-- Realizo la consulta de cuantas transacciones tiene cada producto
SELECT product_id, COUNT(transaction_id) AS number_of_transactions
FROM transactions_products
GROUP BY product_id
ORDER BY product_id ASC;

-- Realizo correcciones de CHAR a INT en los ID's
ALTER TABLE transactions_products
DROP FOREIGN KEY transactions_products_ibfk_2;

ALTER TABLE products
MODIFY COLUMN id INT;

ALTER TABLE transactions_products
MODIFY COLUMN product_id INT;

ALTER TABLE transactions_products
ADD CONSTRAINT transactions_products_ibfk_2
FOREIGN KEY (product_id) REFERENCES products(id);

-- Vuelvo a generar la coonsulta hechos los cambios
SELECT product_id, COUNT(transaction_id) AS number_of_transactions
FROM transactions_products
GROUP BY product_id
ORDER BY product_id ASC;