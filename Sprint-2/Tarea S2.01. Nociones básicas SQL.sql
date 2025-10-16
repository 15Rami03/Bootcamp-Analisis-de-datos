#NIVEL 1
#Ejercicio 2
#Listado de los países que están generando ventas.
SELECT DISTINCT country 
FROM company c
JOIN transaction t
ON c.id = company_id
WHERE declined = 0		-- Aqui tenia amount>0 pero me dijeron que utilizara declined
ORDER BY country ASC;

#Desde cuántos países se generan las ventas.
SELECT COUNT(DISTINCT country) AS cantidad_paises_con_ventas
FROM company c
JOIN transaction
ON c.id = company_id
WHERE declined = 0;   -- Aqui tenia amount>0 pero me dijeron que utilizara declined

# Identifica la compañía con la mayor media de ventas
SELECT company_name, ROUND(AVG(amount), 2) AS max_average_sale
FROM company c
JOIN transaction
  ON c.id = company_id
WHERE declined = 0
GROUP BY company_name
ORDER BY max_average_sale DESC
LIMIT 1;

#Ejercicio 3
#Muestra todas las transacciones realizadas por empresas de Alemania.
SELECT t.*,
       (SELECT company_name
        FROM company c
        WHERE c.id = company_id) AS company_name,
        (SELECT country
        FROM company c
        WHERE c.id = company_id) AS country
FROM transaction t
WHERE company_id IN (
    SELECT id
    FROM company
    WHERE country = 'Germany'
);

#Lista las empresas que han realizado transacciones por un amount superior a la media de todas las transacciones.
SELECT company_name
FROM company
WHERE id = ANY (				-- Aqui me pidieron utilizar any o exist en lugar de in, mas eficiente
	SELECT company_id
	FROM transaction
	WHERE amount > (SELECT AVG(amount) FROM transaction ));


#Eliminarán del sistema las empresas que carecen de transacciones registradas, entrega el listado de estas empresas.
SELECT company_name
FROM company c
WHERE NOT EXISTS (
    SELECT 1			-- dentro del subquery es una práctica común: no importa qué selecciones, solo interesa si existe al menos una fila.
    FROM transaction
    WHERE company_id = c.id
);

#NIVEL 2
#Ejercicio 1
#Identifica los cinco días que se generó la mayor cantidad de ingresos en la empresa por ventas. 
#Muestra la fecha de cada transacción junto con el total de las ventas.

SELECT DATE(timestamp) AS date, SUM(amount) AS total_sales
FROM transaction
GROUP BY DATE(timestamp)
ORDER BY total_sales DESC
LIMIT 5;

#Ejercicio 2
#¿Cuál es la media de ventas por país? Presenta los resultados ordenados de mayor a menor medio.
SELECT country, ROUND(AVG(amount), 2) AS avg_sales
FROM company c
JOIN transaction
ON c.id = company_id
GROUP BY country
ORDER BY avg_sales DESC;


#Ejercicio 3
#En tu empresa, se plantea un nuevo proyecto para lanzar algunas campañas publicitarias para hacer competencia a la compañía “Non Institute”. 
#Para ello, te piden la lista de todas las transacciones realizadas por empresas que están ubicadas en el mismo país que esta compañía.

#Muestra el listado aplicando solo subconsultas.
SELECT t.id, amount, timestamp, company_name, country
FROM company c, transaction t
WHERE c.id = company_id AND c.country IN (
										SELECT country
										FROM company c				-- tanto en la consuta inicial como en las subconsultas puedo utilizar el mismo alias para la tabla
										WHERE company_name = 'Non Institute'
);

#Muestra el listado aplicando JOIN y subconsultas.       
SELECT t.id, amount, timestamp, company_name, country
FROM transaction t 
JOIN company c
ON c.id = company_id
WHERE country IN (
	SELECT country
    FROM company
    WHERE company_name = 'Non Institute');
    
#Nivel 3
#Ejercicio 1
#Presenta el nombre, teléfono, país, fecha y amount, de aquellas empresas que realizaron transacciones con un valor comprendido entre 350 y 400 euros 
#y en alguna de estas fechas: 29 de abril de 2015, 20 de julio de 2018 y 13 de marzo de 2024. Ordena los resultados de mayor a menor cantidad.

SELECT company_name, phone, country, DATE(timestamp), amount
FROM company c
JOIN transaction 
ON c.id = company_id
WHERE (amount BETWEEN 350 AND 400) AND (DATE(timestamp) IN ( '2015-04-29', '2018-07-20', '2024-03-13' ))
ORDER BY amount DESC;

#Ejercicio 2
#Necesitamos optimizar la asignación de los recursos y dependerá de la capacidad operativa que se requiera, 
#por lo que te piden la información sobre la cantidad de transacciones que realizan las empresas, pero el departamento de recursos humanos es exigente 
#y quiere un listado de las empresas en las que especifiques si tienen más de 400 transacciones o menos.

SELECT company_name, COUNT(c.id) AS total_transactions,
CASE
	WHEN COUNT(c.id) > 400 THEN "More than 400"
    ELSE "400 or less"
END AS transaction_category
FROM transaction
JOIN company c ON company_id = c.id
GROUP BY c.id
ORDER BY company_name;