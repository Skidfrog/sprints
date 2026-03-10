DROP DATABASE IF EXISTS sprint4;
CREATE DATABASE IF NOT EXISTS sprint4;

USE sprint4;

-- Creem una taula, on unificar els dos origen de dades d'usuaris

CREATE TABLE IF NOT EXISTS users (
id INT PRIMARY KEY NOT NULL,
name VARCHAR(255),
surname VARCHAR(255),
phone VARCHAR(255),
email VARCHAR(255),
birth_date VARCHAR(255),
country VARCHAR(255),
city VARCHAR(255),
postal_code VARCHAR(255),
address VARCHAR(255),
region ENUM('america', 'europa') -- creem un camp extra, per a difeneciar l'origen de les taules, amb dos possibles opcions
);

LOAD DATA INFILE "C:\\SQL_import\\american_users.csv"
INTO TABLE users
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
IGNORE 1 ROWS
(id,name,surname,phone,email,birth_date,country,city,postal_code,address) -- especifiquem els camps, i establim el valor del camp extra
SET region = 'america';

LOAD DATA INFILE "C:\\SQL_import\\european_users.csv"
INTO TABLE users
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
IGNORE 1 ROWS
(id,name,surname,phone,email,birth_date,country,city,postal_code,address)  -- especifiquem els camps, i establim el valor del camp extra
SET region = 'europa';

SELECT * FROM users;

-- creem i importem les dades de la taula companies
CREATE TABLE companies (
company_id VARCHAR(100) PRIMARY KEY NOT NULL,
company_name VARCHAR(100),
phone VARCHAR(50),
email VARCHAR(100),
country VARCHAR(50),
website VARCHAR(50)
);

LOAD DATA INFILE "C:\\SQL_import\\companies.csv"
INTO TABLE companies
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
IGNORE 1 ROWS;

-- creem i importem les dades de la taula credit_cards
CREATE TABLE credit_cards (
id VARCHAR(100) PRIMARY KEY NOT NULL,
user_id VARCHAR(100) NOT NULL,
iban VARCHAR(50),
pan VARCHAR(50),
pin VARCHAR(50),
cvv VARCHAR(50),
track1 VARCHAR(100),
track2 VARCHAR(100),
expiring_date VARCHAR(50)
);

LOAD DATA INFILE "C:\\SQL_import\\credit_cards.csv"
INTO TABLE credit_cards
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
IGNORE 1 ROWS;

-- creem i importem la taula transactions, relacionada amb les anteriors tres
CREATE TABLE transactions (
id VARCHAR(100) PRIMARY KEY NOT NULL,
card_id VARCHAR(100),
business_id VARCHAR(100),
timestamp TIMESTAMP,
amount DECIMAL,
declined TINYINT,
product_ids TEXT,
user_id INT,
lat FLOAT,
longitude FLOAT,
FOREIGN KEY (user_id) REFERENCES users(id),
FOREIGN KEY (card_id) REFERENCES credit_cards(id),
FOREIGN KEY (business_id) REFERENCES companies(company_id)
);

LOAD DATA INFILE "C:\\SQL_import\\transactions.csv"
INTO TABLE transactions
FIELDS TERMINATED BY ';'
IGNORE 1 ROWS;

SELECT * FROM transactions;


-- Nivell 1
-- Exercici 1
-- Realitza una subconsulta que mostri tots els usuaris amb més de 80 transaccions utilitzant almenys 2 taules.

SELECT *
FROM users u
WHERE u.id IN (
    SELECT t.user_id
    FROM transactions t
    GROUP BY t.user_id
    HAVING COUNT(*) > 80
);
               
-- Exercici 2
-- Mostra la mitjana d'amount per IBAN de les targetes de crèdit a la companyia Donec Ltd, utilitza almenys 2 taules.

SELECT company_name, ROUND(AVG(amount),2) average, iban FROM transactions t
JOIN credit_cards cc ON cc.id = t.card_id
JOIN companies co ON co.company_id = t.business_id
WHERE co.company_name = "Donec Ltd" AND declined = 0
GROUP BY iban;

-- Nivell 2
-- Crea una nova taula que reflecteixi l'estat de les targetes de crèdit basat en si 
-- les tres últimes transaccions han estat declinades aleshores és inactiu, 
-- si almenys una no és rebutjada aleshores és actiu. Partint d’aquesta taula respon:

DROP TABLE card_activity;
CREATE TABLE card_activity (
    id VARCHAR(100) PRIMARY KEY,
	estat_tarjeta VARCHAR (50)
)
AS
SELECT cc.id, user_id, iban,
    CASE
        WHEN SUM(ultimes.declined) = 3 THEN "tarjeta inactiva"
	    ELSE "Tarjeta activa"
    END AS estat_tarjeta
FROM credit_cards cc
JOIN (SELECT t.card_id, t.declined,
        ROW_NUMBER() OVER (
            PARTITION BY t.card_id
            ORDER BY t.timestamp DESC
        ) AS numerades
    FROM transactions t) ultimes 
    ON ultimes.card_id = cc.id
WHERE ultimes.numerades <= 3
GROUP BY cc.id, cc.user_id, cc.iban
ORDER BY cc.id;
;

SELECT * FROM card_activity;
ALTER TABLE card_activity
ADD FOREIGN KEY (id) REFERENCES credit_cards(id);

-- Exercici 1
-- Quantes targetes estan actives?
SELECT cc.id, cc.user_id, cc.iban, estat_tarjeta FROM card_activity ca
JOIN credit_cards cc ON cc.id = ca.id
WHERE estat_tarjeta = "tarjeta activa";


-- Nivell 3
-- Crea una taula amb la qual puguem unir les dades del nou arxiu products.csv amb la base de dades creada, 
-- tenint en compte que des de transaction tens product_ids. Genera la següent consulta:

CREATE TABLE products (
id VARCHAR(100) PRIMARY KEY NOT NULL,
product_name VARCHAR(100),
price VARCHAR (50),
colour VARCHAR(50),
weight VARCHAR(50),
warehouse_id VARCHAR(50)
);

LOAD DATA INFILE "C:\\SQL_import\\products.csv"
INTO TABLE products
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
IGNORE 1 ROWS;

SELECT * FROM products;
DROP TABLE transaction_products;
CREATE TABLE transaction_products (
    transaction_id VARCHAR (100),
    product_id VARCHAR (100),
    PRIMARY KEY (transaction_id, product_id),
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT INTO transaction_products (transaction_id, product_id)
SELECT
    t.id as transaction_id,
    p.id
FROM transactions t
JOIN JSON_TABLE(
        CONCAT('[', t.product_ids, ']'),
        '$[*]' COLUMNS (
            product_id INT PATH '$'
        )
    ) AS jt
JOIN products p
    ON p.id = jt.product_id;

SELECT * FROM transaction_products;
-- Exercici 1
-- Necessitem conèixer el nombre de vegades que s'ha venut cada producte.

SELECT product_id, product_name, COUNT(product_id) AS total_ventas FROM transaction_products tp
JOIN products p ON id = product_id
GROUP BY product_id, product_name;