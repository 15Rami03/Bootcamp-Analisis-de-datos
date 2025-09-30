#NIVEL 1
#Ejercicio 1
-- Creacion de la tabla credit_card
USE transactions;

CREATE TABLE credit_card (
id VARCHAR(15) PRIMARY KEY,
iban VARCHAR(34),
pan CHAR(30),
pin CHAR(4),
cvv CHAR(3),
expiring_date VARCHAR(10)
);

-- Modificacion de columnas pan y expiration_date
-- eliminar espacios de pan y convertir expiration_date a DATE
-- Desactivar temporalmente safe updates
SET SQL_SAFE_UPDATES = 0;

-- Ejecutar el UPDATE de toda la tabla
UPDATE credit_card
SET 
    pan = REPLACE(pan, ' ', ''),
    expiring_date = STR_TO_DATE(expiring_date, '%m/%d/%y');

-- Volver a activar safe updates
SET SQL_SAFE_UPDATES = 1;

-- cambiar tipos de las dos columnas
ALTER TABLE credit_card
MODIFY COLUMN pan CHAR(16),
MODIFY COLUMN expiring_date DATE;

-- Agregar relacion entre tabla transaction y credit_card
ALTER TABLE transaction
ADD CONSTRAINT fk_transaction_credit_card
FOREIGN KEY (credit_card_id) REFERENCES credit_card(id);

#Ejercicio 2
-- Modificar este registro: tarjeta de crédito con ID CcU-2938. La información que debe mostrarse para este registro es: TR323456312213576817699999
-- Visualizo el registro con error
SELECT *
FROM credit_card
WHERE id = 'CcU-2938';

-- Modifico el campo iban y corrijo el error
UPDATE credit_card
SET iban = 'TR323456312213576817699999'
WHERE id = 'CcU-2938';

-- Ejercicio 3
-- Ingresar nuevos datos a la tabla transaction

-- Ingreso un nuevo registro en la tabla company
INSERT INTO company (id, company_name, phone, email, country, website) VALUES ('b-9999', 'Ibesdrola', '06 01 02 70 48', 'mique@protonmail.net', 'Spain', 'https://ibesdrola.es');
-- compruebo que el registro se realizó correctamente
SELECT *
FROM company
WHERE id = 'b-9999';

-- Ingreso un nuevo registro a la tabla credit_card
INSERT INTO credit_card (id, iban, pin, cvv, expiring_date) VALUES ( 'CcU-9999', 'XX4857592035292505850771', 5776, 217, '2032-07-27');
-- Compruebo que el registro fue ingresado de manera correcta
SELECT *
FROM credit_card
WHERE id = 'Ccu-9999';

-- Compruebo si la columna timestamp tiene o no un valor automatico
SHOW CREATE TABLE transaction;
-- Al ver que la collumna timsestamp permite NULL y no tiene un valor automatico, modifico la tabla para corregirlo
ALTER TABLE transaction
MODIFY COLUMN `timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;
-- Correjido este error, y tambien ingresados los correspondientes registros en las tablas
-- credit_card, commpany y user, ahora puedo ingresar los resgistros solicitados en la tabla transaction.
INSERT INTO transaction (id, credit_card_id, company_id, user_id, lat, longitude, amount, declined) 
VALUES ('108B1D1D-5B23-A76C-55EF-C568E49A99DD', 'CcU-9999', 'b-9999', '9999', 829.999, -117.999, 111.11, 0);
-- Compruebo si los registros fueron ingresados de manera correcta
SELECT *
FROM transaction
WHERE id = '108B1D1D-5B23-A76C-55EF-C568E49A99DD';

-- Ejercicio 4
-- Eliminar la columna "pan" de la tabla credit_card. Recuerda mostrar el cambio realizado.
ALTER TABLE credit_card
DROP COLUMN pan;

#NIVEL 2
#Ejercicio 1
-- Elimina de la tabla transacción el registro con ID 000447FE-B650-4DCF-85DE-C7ED0EE1CAAD de la base de datos.

#Ejercicio 2
-- La sección de marketing desea tener acceso a información específica para realizar análisis y estrategias efectivas. 
-- Se ha solicitado crear una vista que proporcione detalles clave sobre las compañías y sus transacciones. 
-- Será necesaria que crees una vista llamada VistaMarketing que contenga la siguiente información: 
-- Nombre de la compañía. Teléfono de contacto. País de residencia. Media de compra realizado por cada compañía. Presenta la vista creada, 
-- ordenando los datos de mayor a menor promedio de compra

CREATE OR REPLACE VIEW VistaMarketing AS
SELECT c.company_name, c.phone, c.country, ROUND(AVG(t.amount), 2) AS average_sales
FROM company c
JOIN transaction t ON c.id = t.company_id
GROUP BY c.company_name, c.phone, c.country
ORDER BY average_sales DESC;

#Ejercicio 3
-- Filtra la vista VistaMarketing para mostrar sólo las compañías que tienen su país de residencia en "Germany"

SELECT *
FROM vistamarketing vk
WHERE vk.country = 'Germany';

#NIVEL 3
#Ejercicio 1
-- La próxima semana tendrás una nueva reunión con los gerentes de marketing. 
-- Un compañero de tu equipo realizó modificaciones en la base de datos, pero no recuerda cómo las realizó. 
-- Te pide que le ayudes a dejar los comandos ejecutados para obtener el siguiente diagrama:
-- Creo el constraint que relaciona la tabla transaction con la tabla user
ALTER TABLE transaction
ADD CONSTRAINT fk_transaction_user
FOREIGN KEY (user_id) REFERENCES user(id);

-- Consulto como se llama el constraint entre las tablas company y transaction
SHOW CREATE TABLE transaction;

-- Elimino la FK que no tiene nombre adecuado para reemplazarlo posteriormente
ALTER TABLE transaction
DROP FOREIGN KEY transaction_ibfk_1;

-- Elimino el índice de esa FK
ALTER TABLE transaction
DROP INDEX company_id;

-- Genero una nueva FK con un nombre adecuado
ALTER TABLE transaction
ADD CONSTRAINT fk_transaction_company
FOREIGN KEY (company_id) REFERENCES company(id);

-- Cambios estructuras de las tablas
-- Compruebo la estructura actual de la tabla company
SELECT *
FROM company;
-- Elimino la columna website
ALTER TABLE company
DROP COLUMN website;
-- compruebo si se eliminó exitosamente
SELECT *
FROM company;

SELECT *
FROM credit_card;
-- Cambio los valores de las columnas y agrego la columna fecha_actual
ALTER TABLE credit_card
MODIFY id VARCHAR(20),
MODIFY iban VARCHAR(50),
MODIFY pin CHAR(4),
MODIFY cvv INT,			-- (Si lo dejo en INT, al tener un CVV como 012, se guardaría como 12, perdiendo el cero inicial).
MODIFY expiring_date VARCHAR(20),
ADD fecha_actual DATE NOT NULL DEFAULT (CURRENT_DATE);
-- Compruebo los cambios
SELECT *
FROM credit_card;

SELECT *
FROM user;
-- Renombro la tabla user por data_user
RENAME TABLE user TO data_user;
-- Modifico los valores de campos y renombro la columna email por personal_email
ALTER TABLE data_user
MODIFY name VARCHAR(100),
MODIFY surname VARCHAR(100),
MODIFY phone VARCHAR(150),
CHANGE email personal_email VARCHAR(150),
MODIFY birth_date VARCHAR(100),
MODIFY country VARCHAR(150),
MODIFY city VARCHAR(150),
MODIFY postal_code VARCHAR(100),
MODIFY address VARCHAR(255);
-- Compruebo los cambios
SELECT *
FROM data_user;
 
#EJERCICIO 2
-- La empresa también le pide crear una vista llamada "InformeTecnico" que contenga la siguiente información:
-- ID de la transacción
-- Nombre del usuario/a
-- Apellido del usuario/a
-- IBAN de la tarjeta de crédito usada.
-- Nombre de la compañía de la transacción realizada.
-- Asegúrese de incluir información relevante de las tablas que conocerá y utilice alias para cambiar de nombre columnas según sea necesario.
-- Muestra los resultados de la vista, ordena los resultados de forma descendente en función de la variable ID de transacción.


-- Creo la vista InformeTecnico
CREATE OR REPLACE VIEW InformeTecnico AS
SELECT 	t.id AS transaction_id, t.declined AS declined_transaction,
		u.name AS user_name, u.surname AS user_surname, u.country AS user_country, 
		cc.iban AS credit_card_iban, 
        c.company_name AS company_name, c.country AS company_country
FROM transaction t
JOIN data_user u ON t.user_id = u.id
JOIN credit_card cc ON t.credit_card_id = cc.id
JOIN company c ON t.company_id = c.id;
-- Compruebo que la vista se creó correctamente y la ordeno comp pide el enunciado
SELECT *
FROM informetecnico
ORDER BY transaction_id DESC ;

