-- Nivell 1
-- Exercici 1
-- La teva tasca és dissenyar i crear una taula anomenada "credit_card" que emmagatzemi detalls crucials sobre 
-- les targetes de crèdit. La nova taula ha de ser capaç d'identificar de manera única cada targeta i establir 
-- una relació adequada amb les altres dues taules ("transaction" i "company"). Després de crear la taula 
-- serà necessari que ingressis la informació del document denominat "dades_introduir_credit". 
-- Recorda mostrar el diagrama i realitzar una breu descripció d'aquest.

USE transactions;
CREATE TABLE credit_card (
	id VARCHAR(20), 
    iban VARCHAR(50), 
    pan VARCHAR(50), 
    pin VARCHAR(4), 
    cvv INT, 
    expiring_date VARCHAR(20)
);

ALTER TABLE credit_card
ADD PRIMARY KEY (ID);

ALTER TABLE transaction
ADD FOREIGN KEY (credit_card_id) REFERENCES credit_card(id);


-- Exercici 2
-- El departament de Recursos Humans ha identificat un error en el número de compte associat a 
-- la targeta de crèdit amb ID CcU-2938. La informació que ha de mostrar-se per a aquest registre és: 
-- TR323456312213576817699999. Recorda mostrar que el canvi es va realitzar.

UPDATE credit_card
SET iban = "TR323456312213576817699999"
WHERE id = "CcU-2938";

select * FROM credit_card
WHERE id = "CcU-2938";

-- Exercici 3
-- En la taula "transaction" ingressa una nova transacció amb la següent informació:

/*Id	108B1D1D-5B23-A76C-55EF-C568E49A99DD
credit_card_id	CcU-9999
company_id	b-9999
user_id	9999
lat	829.999
longitude	-117.999
amount	111.11
declined	0*/

INSERT INTO company (id) VALUES ("b-9999");
INSERT INTO credit_card (id) VALUES ("CcU-9999");
INSERT INTO transaction (id, credit_card_id, company_id, user_id, lat, longitude, amount, declined) VALUES ("108B1D1D-5B23-A76C-55EF-C568E49A99DD", "CcU-9999", "b-9999", "9999", 829.999, -117.999, 111.11, 0);

-- Exercici 4
-- Des de recursos humans et sol·liciten eliminar la columna "pan" de la taula credit_card. Recorda mostrar el canvi realitzat.

ALTER TABLE credit_card DROP COLUMN pan; 
SELECT * FROM credit_card;

-- Nivell 2
-- Exercici 1
-- Elimina de la taula transaction el registre amb ID 000447FE-B650-4DCF-85DE-C7ED0EE1CAAD de la base de dades.

DELETE FROM transaction WHERE id='000447FE-B650-4DCF-85DE-C7ED0EE1CAAD';
SELECT * FROM transaction
WHERE id='000447FE-B650-4DCF-85DE-C7ED0EE1CAAD';

-- Exercici 2
-- La secció de màrqueting desitja tenir accés a informació específica per a realitzar anàlisi i estratègies efectives. 
-- S'ha sol·licitat crear una vista que proporcioni detalls clau sobre les companyies i les seves transaccions. 
-- Serà necessària que creïs una vista anomenada VistaMarketing que contingui la següent informació: 
-- Nom de la companyia. Telèfon de contacte. País de residència. Mitjana de compra realitzat per cada companyia. 
-- Presenta la vista creada, ordenant les dades de major a menor mitjana de compra.

CREATE OR REPLACE VIEW VistaMarketing AS
SELECT c.company_name, c.phone, c.country, ROUND(AVG(t.amount), 2) AS mitja_amount
FROM company c 
JOIN transaction t ON t.company_id=c.id
GROUP BY c.id
ORDER BY AVG(amount) DESC;

SELECT * FROM VistaMarketing;

-- Exercici 3
-- Filtra la vista VistaMarketing per a mostrar només les companyies que tenen el seu país de residència en "Germany"

SELECT * FROM VistaMarketing
WHERE country = 'germany';

-- Nivell 3
-- Exercici 1
-- La setmana vinent tindràs una nova reunió amb els gerents de màrqueting. 
-- Un company del teu equip va realitzar modificacions en la base de dades, però no recorda com les va realitzar. 
-- Et demana que l'ajudis a deixar els comandos executats per a obtenir el següent diagrama:
-- En aquesta activitat, és necessari que descriguis el "pas a pas" de les tasques realitzades. 
-- És important realitzar descripcions senzilles, simples i fàcils de comprendre. 
-- Per a realitzar aquesta activitat hauràs de treballar amb els arxius denominats "estructura_dades_user" i 
-- "dades_introduir_user"
-- Recorda continuar treballant sobre el model i les taules amb les quals ja has treballat fins ara.

ALTER TABLE transaction
MODIFY user_id INT;

ALTER TABLE user
MODIFY id INT;

INSERT INTO user (id) VALUES (9999);

ALTER TABLE transaction
ADD FOREIGN KEY (user_id) REFERENCES user(id);

SELECT * FROM transaction t
LEFT JOIN user u ON u.id = t.user_id;


-- A la taula company, s’ha eliminat el camp “website”
ALTER TABLE company DROP COLUMN website; 
-- La taula “user” ha canviat el nom a “data_user”
RENAME TABLE user TO data_user;
-- El camp “email” a canviat a “personal_email”
ALTER TABLE data_user RENAME COLUMN email TO personal_email;
-- El camp “credit_card_id” te un format de VARCHAR (20) en comptes de 15
ALTER TABLE transaction
MODIFY credit_card_id VARCHAR(20);
-- Hi ha un camp nou a la taula “credit_card”, “fecha_actual” DATE, que haurem de crear.
ALTER TABLE credit_card
ADD COLUMN fecha_actual DATE DEFAULT (CURDATE());

-- Exercici 2
-- L'empresa també us demana crear una vista anomenada "InformeTecnico" que contingui la següent informació:

/*ID de la transacció
Nom de l'usuari/ària
Cognom de l'usuari/ària
IBAN de la targeta de crèdit usada.
Nom de la companyia de la transacció realitzada.
Assegureu-vos d'incloure informació rellevant de les taules que coneixereu 
i utilitzeu àlies per canviar de nom columnes segons calgui.
Mostra els resultats de la vista, ordena els resultats de forma descendent en funció de la variable ID de transacció. */

CREATE OR REPLACE VIEW InformeTecnico AS
SELECT t.id Id_Transaccio, 
	name Nom, 
	surname Cognom, 
	iban IBAN, 
	company_name Nom_companyia, 
	timestamp Data_transaccio, 
	co.country pais,
    amount Import,
    s.Mitja_Companyia,
    s.Total_Companyia
FROM transaction t 
JOIN data_user du ON du.id = t.user_id
JOIN credit_card cc ON cc.id = t.credit_card_id
JOIN company co ON co.id = t.company_id
JOIN (
    SELECT company_id, ROUND(AVG(amount),2) AS Mitja_Companyia, SUM(amount) AS Total_Companyia
    FROM transaction
    GROUP BY company_id
) s ON s.company_id = t.company_id
ORDER BY t.id DESC;

SELECT * FROM InformeTecnico;

