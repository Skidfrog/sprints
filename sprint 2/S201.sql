-- Nivell 1
-- Exercici 1
-- A partir dels documents adjunts (estructura_dades i dades_introduir), importa les dues taules. Mostra les característiques principals de l'esquema creat i explica les diferents taules i variables que existeixen. Assegura't d'incloure un diagrama que il·lustri la relació entre les diferents taules i variables.
-- Archiu .pdf adjunt al zip.

    -- Creamos la base de datos
    CREATE DATABASE IF NOT EXISTS transactions;
    USE transactions;

    -- Creem la taula company
    CREATE TABLE IF NOT EXISTS company (
        id VARCHAR(15) PRIMARY KEY,
        company_name VARCHAR(255),
        phone VARCHAR(15),
        email VARCHAR(100),
        country VARCHAR(100),
        website VARCHAR(255)
    );

    -- Creem la taulaCreamos la tabla transaction
    CREATE TABLE IF NOT EXISTS transaction (
        id VARCHAR(255) PRIMARY KEY,
        credit_card_id VARCHAR(15) REFERENCES credit_card(id),
        company_id VARCHAR(20), 
        user_id INT REFERENCES user(id),
        lat FLOAT,
        longitude FLOAT,
        timestamp TIMESTAMP,
        amount DECIMAL(10, 2),
        declined BOOLEAN,
        FOREIGN KEY (company_id) REFERENCES company(id) 
    );

  -- Introduim les dades desde l'arxiu.

-- Exercici 2
-- Utilitzant JOIN realitzaràs les següents consultes:

-- Llistat dels països que estan generant vendes.

SELECT DISTINCT country FROM company co
JOIN transaction tr ON tr.company_id = co.id;


-- Des de quants països es generen les vendes.

SELECT COUNT(DISTINCT Country) AS RecomptePaisos FROM company co
JOIN transaction tr ON tr.company_id = co.id;

-- Identifica la companyia amb la mitjana més gran de vendes.

SELECT company_name, ROUND(AVG(amount), 2) AS MitjaCompanyia FROM company co
JOIN transaction tr ON tr.company_id = co.id
WHERE declined = 0
GROUP BY company_name
ORDER BY MitjaCompanyia DESC
LIMIT 1;


-- Exercici 3
-- Utilitzant només subconsultes (sense utilitzar JOIN):

-- Mostra totes les transaccions realitzades per empreses d'Alemanya.

SELECT tr.id FROM transaction tr  
WHERE EXISTS (
	SELECT co.id FROM company co
    WHERE co.country = 'Germany')
    ;

-- Llista les empreses que han realitzat transaccions per un amount superior a la mitjana de totes les transaccions.

SELECT co.company_name FROM company co 
WHERE EXISTS (
	SELECT company_id FROM transaction 
    WHERE amount > (SELECT AVG(amount) FROM transaction))
    ;

-- Eliminaran del sistema les empreses que no tenen transaccions registrades, entrega el llistat d'aquestes empreses.

SELECT co.company_name
FROM company co
WHERE NOT EXISTS (
    SELECT tr.company_id
    FROM transaction tr
    WHERE declined = 0)
;
-- Totes les companyies tenen transaccions registrades. 
-- El nombre de diferents companyies amb transaccions i companyies a la base de dades coincideix
SELECT DISTINCT company_id FROM transaction;  -- 100 companyies
SELECT DISTINCT id FROM company;     -- 100 companyies


-- Nivell 2
-- Exercici 1
-- Identifica els cinc dies que es va generar la quantitat més gran d'ingressos a l'empresa per vendes. Mostra la data de cada transacció juntament amb el total de les vendes.

SELECT SUM(amount) AS TotalVentesDiaries, DATE(timestamp) AS Data
FROM transaction tr 
GROUP BY Data
ORDER BY TotalVentesDiaries DESC
LIMIT 5;

-- Exercici 2
-- Quina és la mitjana de vendes per país? Presenta els resultats ordenats de major a menor mitjà.

SELECT co.country AS pais, ROUND(AVG(tr.amount), 2) AS MitjanaVendesXpais 
FROM company co
JOIN transaction tr on tr.company_id = co.id
WHERE declined = 0
GROUP BY co.country
ORDER BY MitjanaVendesXpais DESC;



-- Exercici 3
-- En la teva empresa, es planteja un nou projecte per a llançar algunes campanyes publicitàries ç
-- per a fer competència a la companyia "Non Institute". Per a això, et demanen la llista de totes 
-- les transaccions realitzades per empreses que estan situades en el mateix país que aquesta companyia.
-- Mostra el llistat aplicant JOIN i subconsultes.

SELECT * FROM transaction tr
JOIN company co ON co.id = tr.company_id
WHERE co.country = (
	SELECT country FROM company
    WHERE company_name = 'Non institute');

-- Mostra el llistat aplicant solament subconsultes.

SELECT t.*, 
	(SELECT company_name FROM company c WHERE c.id = t.company_id) AS Nom_companyia,
    (SELECT phone FROM company c WHERE c.id = t.company_id) AS telefon,
    (SELECT email FROM company c WHERE c.id = t.company_id) AS emailo,
    (SELECT country FROM company c WHERE c.id = t.company_id) AS pais,
    (SELECT website FROM company c WHERE c.id = t.company_id) AS website
FROM transaction t
WHERE company_id IN (
	SELECT id FROM company
    WHERE country = (
		SELECT country FROM company
        WHERE company_name = 'Non institute'
	)
);
 
 SELECT t.*, c.*
FROM (transaction t, company c)
WHERE company_id IN (
	SELECT id FROM company
    WHERE country = (
		SELECT country FROM company
        WHERE company_name = 'Non institute'
	)
)
AND t.company_id = c.id
;

-- Nivell 3
-- Exercici 1
-- Presenta el nom, telèfon, país, data i amount, d'aquelles empreses que van realitzar transaccions 
-- amb un valor comprès entre 350 i 400 euros 
-- i en alguna d'aquestes dates: 29 d'abril del 2015, 20 de juliol del 2018 i 13 de març del 2024. 
-- Ordena els resultats de major a menor quantitat.

SELECT company_name, phone, country, SUM(tr.amount) s_amount, DATE(tr.timestamp) data FROM company co
JOIN transaction tr ON tr.company_id = co.id
WHERE DATE(tr.timestamp) IN ("2015-04-29", "2018-07-20", "2024-03-13") 
GROUP BY tr.company_id, data
HAVING s_amount BETWEEN 350 AND 400
ORDER BY s_amount DESC
;

-- Exercici 2
-- Necessitem optimitzar l'assignació dels recursos i dependrà de la capacitat operativa que es requereixi, 
-- per la qual cosa et demanen la informació sobre la quantitat de transaccions que realitzen les empreses, ç
-- però el departament de recursos humans és exigent i vol un llistat de les empreses on especifiquis 
-- si tenen més de 400 transaccions o menys.

SELECT company_id, company_name as nom, COUNT(tr.id) AS total,
CASE
	WHEN COUNT(tr.id) < 400 THEN 'Menys de 400 transaccions'
    ELSE 'Mes de 400 transaccions'
END AS transaccions
FROM transaction tr
JOIN company co ON co.id = tr.company_id
WHERE declined = 0
GROUP BY company_id
ORDER BY total DESC
;
