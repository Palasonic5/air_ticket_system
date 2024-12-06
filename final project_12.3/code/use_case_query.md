# Use Cases and Queries

## Welcome Page

1. **View Public Info**: All users, whether logged in or not, can search for upcoming flights based on source city/airport name, destination city/airport name, date. The user will be able to see the flight's status based on flight number, arrival/departure date.

- The default query is to get the upcoming 30 day's flight information:

``` sql
SELECT * 
FROM flight 
WHERE True 
AND departure_time BETWEEN NOW() AND ADDTIME(NOW(), '30 0:0:0');
```

- If user specifies only part of the selections from "departure date start, departure date end, departure city and airport, and arrival city and airport" (i.e., vague search):

``` sql
SELECT *
FROM flight
WHERE True 
AND arrival_airport IN ('PVG', 'JFK')
AND DATE(departure_time) >= '2022-03-01' 
ORDER BY departure_time, arrival_time;
```

- If user specifies all the selections:

``` sql
SELECT *     
FROM flight 
WHERE True 
AND departure_airport IN ('La Guardia') 
AND arrival_airport IN ('Louisville SDF', 'PVG') 
AND DATE(departure_time) BETWEEN '2022-03-01' AND '2022-07-05' 
ORDER BY departure_time, arrival_time;
```

2. **Register**: 3 types of user registrations (Customer, Booking agent, Airline staff) option via forms.

- Customer:

``` sql
-- Parameter order: email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth
INSERT INTO customer 
VALUES('test_email', 'test_name', MD5('pwd'), 123, 'test_street', 'ny', 'ny', 12345678, 'Passport123', '2025-05-01', 'China', '1980-01-01');
```

- Booking Agent:

``` sql
-- Parameter order: email, password, booking_agent_id
INSERT INTO booking_agent 
VALUES('test_email', MD5('pwd'), 111);
```

- Airline Staff:

``` sql
-- Parameter order: username, password, first_name, last_name, date_of_birth, airline_name
INSERT INTO airline_staff 
VALUES('test_username', MD5('pwd'), 'firstname', 'lastname', '1980-01-01', 'Jet Blue');
```

3. **Login**: 3 types of user login (Customer, Booking agent, Airline Staff). User enters their username (email address will be used as username), x, and password, y, via forms on login page. This data is sent as POST parameters to the login-authentication component, which checks whether there is a tuple in the Person table with username=x and the password = md5(y).

- Customer:

``` sql
SELECT * 
FROM customer 
WHERE email = 'test_email' AND password = MD5('pwd');
```

- Booking Agent:

``` sql
SELECT * 
FROM booking_agent 
WHERE email = 'test_email' AND password = MD5('pwd');
```

- Airline Staff:

``` sql
SELECT * 
FROM airline_staff 
WHERE username = 'test_username' AND password = MD5('pwd');
```

## Customer

1. **View My flights**: Provide various ways for the user to see flights information which he/she purchased. The default should be showing for the upcoming flights. The user can vaguely specify a range of dates, specify destination and/or source airport name or city name.

- The default query is to get the upcoming 30 day's flight information:

``` sql
SELECT ticket_id, airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, airplane_id 
FROM flight NATURAL JOIN (ticket NATURAL JOIN purchases) 
WHERE customer_email = "test"
AND departure_time BETWEEN NOW() AND ADDTIME(NOW(), '30 0:0:0')
ORDER BY departure_time, arrival_time;
```

- If user specifies only part of the selections from "departure date start, departure date end, departure city and airport, and arrival city and airport" (i.e., vague search):

``` sql
SELECT ticket_id, airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, airplane_id 
FROM flight NATURAL JOIN (ticket NATURAL JOIN purchases) 
WHERE customer_email = "test"
AND arrival_airport IN ('PVG', 'JFK')
AND DATE(departure_time) >= '2022-05-01' 
ORDER BY departure_time, arrival_time;
```

- If user specifies all the selections:

``` sql
SELECT ticket_id, airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, airplane_id 
FROM flight NATURAL JOIN (ticket NATURAL JOIN purchases) 
WHERE customer_email = "test"
AND departure_airport IN ('La Guardia') 
AND arrival_airport IN ('Louisville SDF', 'PVG') 
AND DATE(departure_time) BETWEEN '2022-05-01' AND '2022-07-13' 
ORDER BY departure_time, arrival_time;
```

2. **Purchase tickets**: Customer chooses a flight and purchase ticket for this flight.

- Check if there is ticket left

``` sql
SELECT ticket_id 
FROM ticket WHERE airline_name = 'Jet Blue' 
AND flight_num = 9999
AND ticket_id NOT IN 
(SELECT ticket_id FROM purchases);
```

- Get the ticket id for this purchase

``` sql
SELECT min(ticket_id) AS min_ticket_id 
FROM ticket WHERE airline_name = 'Jet Blue' 
AND flight_num = 9999
AND ticket_id NOT IN 
(SELECT ticket_id FROM purchases);
```

- Purchase the ticket

``` sql
-- Parameter order: ticket_id, customer_email, booking_agent_id, purchase_date
INSERT INTO purchases 
VALUES (101, 'test@nyu.edu', null, '2022-05-01');
```

3. **Search for flights**: Search for upcoming flights based on source city/airport name, destination city/airport name, date.

- The default query is to get the upcoming 30 day's flight information:

``` sql
SELECT * 
FROM flight 
WHERE True 
AND departure_time BETWEEN NOW() AND ADDTIME(NOW(), '30 0:0:0')
ORDER BY departure_time, arrival_time;
```

- If user specifies only part of the selections from "departure date start, departure date end, departure city and airport, and arrival city and airport" (i.e., vague search):

``` sql
SELECT * 
FROM flight 
WHERE True 
AND arrival_airport IN ('PVG', 'JFK')
AND DATE(departure_time) >= '2022-05-01' 
ORDER BY departure_time, arrival_time;
```

- If user specifies all the selections:

``` sql
SELECT * 
FROM flight 
WHERE True 
AND departure_airport IN ('La Guardia') 
AND arrival_airport IN ('Louisville SDF', 'PVG') 
AND DATE(departure_time) BETWEEN '2022-05-01' AND '2022-07-13' 
ORDER BY departure_time, arrival_time;
```

4. **Track My Spending**: Default view will be total amount of money spent in the past year and a bar chart showing month wise money spent for last 6 months. He/she will also have option to specify a range of dates to view total amount of money spent within that range and a bar chart showing month wise money spent within that range.

- The default query is to get last 6 months' information:

``` sql
SELECT YEAR(purchase_date) AS purchase_year, MONTH(purchase_date) AS purchase_month, SUM(price) AS month_spent 
FROM flight NATURAL JOIN ticket NATURAL JOIN purchases
WHERE customer_email = 'test@nyu.edu' 
AND purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 6 MONTH) AND NOW()
GROUP BY purchase_year, purchase_month 
ORDER BY purchase_year, purchase_month;
```

- If user specifies a range of dates:

``` sql
SELECT YEAR(purchase_date) AS purchase_year, MONTH(purchase_date) AS purchase_month, SUM(price) AS month_spent 
FROM flight NATURAL JOIN ticket NATURAL JOIN purchases
WHERE customer_email = 'test@nyu.edu' 
AND purchase_date BETWEEN '2022-05-01' AND '2022-07-13' 
GROUP BY purchase_year, purchase_month 
ORDER BY purchase_year, purchase_month;
```

## Booking Agent

1. **View My flights**: Provide various ways for the booking agents to see flights information for which he/she purchased on behalf of customers. The default should be showing for the upcoming flights. The user can specify a range of dates, specify destination and/or source airport name and/or city name etc to show all the flights for which he/she purchased tickets.

- The default query is to get the upcoming 30 day's flight information:

``` sql
SELECT customer_email, name as customer_name, ticket_id, airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, airplane_id 
FROM flight NATURAL JOIN (ticket NATURAL JOIN (purchases JOIN customer ON customer_email=email )) 
WHERE booking_agent_id = 777
AND departure_time BETWEEN NOW() AND ADDTIME(NOW(), '30 0:0:0')
ORDER BY departure_time, arrival_time;
```

- If user specifies only part of the selections from "departure date start, departure date end, departure city and airport, and arrival city and airport" (i.e., vague search):

``` sql
SELECT customer_email, name as customer_name, ticket_id, airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, airplane_id 
FROM flight NATURAL JOIN (ticket NATURAL JOIN (purchases JOIN customer ON customer_email=email )) 
WHERE booking_agent_id = 777
AND arrival_airport IN ('PVG', 'JFK')
AND DATE(departure_time) >= '2022-05-01' 
ORDER BY departure_time, arrival_time;
```

- If user specifies all the selections:

``` sql
SELECT customer_email, name as customer_name, ticket_id, airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, airplane_id 
FROM flight NATURAL JOIN (ticket NATURAL JOIN (purchases JOIN customer ON customer_email=email )) 
WHERE booking_agent_id = 777
AND departure_airport IN ('La Guardia') 
AND arrival_airport IN ('Louisville SDF', 'PVG') 
AND DATE(departure_time) BETWEEN '2022-05-01' AND '2022-07-13' 
ORDER BY departure_time, arrival_time;
```

2. **Purchase tickets**: Booking agent chooses a flight and purchases tickets for other customers giving customer information. The booking agent may only purchase tickets from airlines they work for.

- Check if there is ticket left

``` sql
SELECT ticket_id 
FROM ticket WHERE airline_name = 'Jet Blue' 
AND flight_num = 9999
AND ticket_id NOT IN 
(SELECT ticket_id FROM purchases);
```

- Get the ticket id for this purchase

``` sql
SELECT min(ticket_id) AS min_ticket_id 
FROM ticket WHERE airline_name = 'Jet Blue' 
AND flight_num = 9999
AND ticket_id NOT IN 
(SELECT ticket_id FROM purchases);
```

- Purchase the ticket

``` sql
-- Parameter order: ticket_id, customer_email, booking_agent_id, purchase_date
INSERT INTO purchases 
VALUES (101, 'test@nyu.edu', 777, '2022-05-01');
```

3. **Search for flights**: Search for upcoming flights based on source city/airport name, destination city/airport name, date.

- The default query is to get the upcoming 30 day's flight information:

``` sql
SELECT * 
FROM flight 
WHERE True 
AND departure_time BETWEEN NOW() AND ADDTIME(NOW(), '30 0:0:0')
ORDER BY departure_time, arrival_time;
```

- If user specifies only part of the selections from "departure date start, departure date end, departure city and airport, and arrival city and airport" (i.e., vague search):

``` sql
SELECT * 
FROM flight 
WHERE True 
AND arrival_airport IN ('PVG', 'JFK')
AND DATE(departure_time) >= '2022-05-01' 
ORDER BY departure_time, arrival_time;
```

- If user specifies all the selections:

``` sql
SELECT * 
FROM flight 
WHERE True 
AND departure_airport IN ('La Guardia') 
AND arrival_airport IN ('Louisville SDF', 'PVG') 
AND DATE(departure_time) BETWEEN '2022-05-01' AND '2022-07-13' 
ORDER BY departure_time, arrival_time;
```

4. **View my commission**: Default view will be total amount of commission received in the past 30 days and the average commission he/she received per ticket booked in the past 30 days and total number of tickets sold by him in the past 30 days. He/she will also have option to specify a range of dates to view total amount of commission received and total numbers of tickets sold.

- The default query is to get last 30 days' information:

``` sql
SELECT SUM(price)/10 AS total_commission, COUNT(*) AS ticket_num, AVG(price)/10 AS avg_commission 
FROM flight NATURAL JOIN (ticket NATURAL JOIN purchases) 
WHERE booking_agent_id = 777
AND purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 MONTH) AND NOW();
```

- If user specifies a range of dates vaguely:

``` sql
SELECT SUM(price)/10 AS total_commission, COUNT(*) AS ticket_num, AVG(price)/10 AS avg_commission 
FROM flight NATURAL JOIN (ticket NATURAL JOIN purchases) 
WHERE booking_agent_id = 777
AND purchase_date >= '2022-05-01';
```

- If user specifies a range of dates:

``` sql
SELECT SUM(price)/10 AS total_commission, COUNT(*) AS ticket_num, AVG(price)/10 AS avg_commission 
FROM flight NATURAL JOIN (ticket NATURAL JOIN purchases) 
WHERE booking_agent_id = 777
AND purchase_date BETWEEN '2022-05-01' AND '2022-07-13';
```
		
5. **View Top Customers**: Top 5 customers based on number of tickets bought from the booking agent in the past 6 months and top 5 customers based on amount of commission received in the last year. Show a bar chart showing each of these 5 customers in x-axis and number of tickets bought in y-axis. Show another bar chart showing each of these 5 customers in x-axis and amount commission received in y- axis.

- The result in the past 6 months:

``` sql
SELECT customer_email, COUNT(ticket_id) AS ticket_num 
FROM purchases 
WHERE booking_agent_id = 777 
AND purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 6 MONTH) AND NOW()
GROUP BY customer_email 
ORDER BY ticket_num DESC LIMIT 5;
```

- The result in the last year:

``` sql
SELECT customer_email, COUNT(ticket_id) AS ticket_num 
FROM purchases 
WHERE booking_agent_id = 777 
AND purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 YEAR) AND NOW()
GROUP BY customer_email 
ORDER BY ticket_num DESC LIMIT 5;
```
		
## Airline Staff

1. **View My flights**: Defaults will be showing all the upcoming flights operated by the airline he/she works for the next 30 days. He/she will be able to see all the current/future/past flights operated by the airline he/she works for based on range of dates, source/destination airports/city etc. He/she will be able to see all the customers of a particular flight.

- The default query is to get the upcoming 30 day's flight information:

``` sql
SELECT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, airplane_id, GROUP_CONCAT(customer_email SEPARATOR ', ') as customers
FROM flight NATURAL LEFT OUTER JOIN (ticket NATURAL JOIN purchases)
WHERE airline_name = 'Jet Blue'
AND (departure_time BETWEEN NOW() AND ADDTIME(NOW(), '30 0:0:0')) 
GROUP BY airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, airplane_id
ORDER BY departure_time, arrival_time;
```

- If user specifies only part of the selections from "departure date start, departure date end, departure city and airport, and arrival city and airport" (i.e., vague search):

``` sql
SELECT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, airplane_id, GROUP_CONCAT(customer_email SEPARATOR ', ') as customers
FROM flight NATURAL LEFT OUTER JOIN (ticket NATURAL JOIN purchases)
WHERE airline_name = 'Jet Blue'
AND arrival_airport IN ('PVG', 'JFK')
AND DATE(departure_time) >= '2022-03-01' 
GROUP BY airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, airplane_id
ORDER BY departure_time, arrival_time;
```

- If user specifies all the selections:

``` sql
SELECT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, airplane_id, GROUP_CONCAT(customer_email SEPARATOR ', ') as customers
FROM flight NATURAL LEFT OUTER JOIN (ticket NATURAL JOIN purchases)
WHERE airline_name = 'Jet Blue'
AND departure_airport IN ('La Guardia') 
AND arrival_airport IN ('Louisville SDF', 'PVG') 
AND DATE(departure_time) BETWEEN '2022-03-01' AND '2022-07-05' 
GROUP BY airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, airplane_id
ORDER BY departure_time, arrival_time;
```

2. **Create new flights**: He or she creates a new flight, providing all the needed data, via forms. The application should prevent unauthorized users or staffs without "Admin" permission from doing this action. This operation includes 2 parts: first, create the flight based on the given information in the `flight` table; then, create the corresponding number of tickets (based on the number of sears on that assigned airplane) in the `ticket` table.

``` sql
-- Parameter order: airline_name, flight_num, departure_airport, departure_time, arrival_airport, arrival_time, price, status, airplane_id
INSERT INTO flight VALUES ('Jet Blue', 111, 'La Guardia', '2022-05-20 07:20:00', 'SFO', '2022-05-21 15:20:00', 1600, 'Upcoming', 1);
-- Parameter order: t_id, airline_name, flight_num
INSERT INTO ticket VALUES (2, 'Jet Blue', 111);
INSERT INTO ticket VALUES (3, 'Jet Blue', 111);
INSERT INTO ticket VALUES (4, 'Jet Blue', 111);
```

3. **Change Status of flights**: He or she changes a flight status (from upcoming to in-progress, in-progress to delayed etc) via forms. The application should prevent unauthorized users or staffs without "Operator" permission from doing this action.

``` sql
UPDATE flight SET status = 'In-progress' WHERE flight_num = 123;
```

4. **Add airplane in the system**: He or she adds a new airplane, providing all the needed data, via forms. The application should prevent unauthorized users or staffs without "Admin" permission from doing this action. In the confirmation page, she/he will be able to see all the airplanes owned by the airline he/she works for.

``` sql
-- Parameter order: airline_name, airplane_id, seats
INSERT INTO airplane VALUES('Jet Blue', 11, 10);
```

5. **Add new airport in the system**: He or she adds a new airport, providing all the needed data, via forms. The application should prevent unauthorized users or staffs without "Admin" permission from doing this action.

``` sql
-- Parameter order: airport_name, airport_city
INSERT INTO airport VALUES('PVG', 'Shanghai');
```

6. **View all the booking agents**: Top 5 booking agents based on number of tickets sales for the past month and past year. Top 5 booking agents based on the amount of commission received for the last year.

- Get the top 5 booking agents in the recent year and in the recent month by the number of tickets sold

``` sql
SELECT b.email AS booking_agent_email, p.booking_agent_id AS booking_agent_id, COUNT(t.ticket_id) AS number_of_tickets
FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p NATURAL JOIN booking_agent b
WHERE airline_name = 'Jet Blue' AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 YEAR) AND NOW())
GROUP BY booking_agent_email
ORDER BY number_of_tickets DESC LIMIT 5;
```

``` sql
SELECT b.email AS booking_agent_email, p.booking_agent_id AS booking_agent_id, COUNT(t.ticket_id) AS number_of_tickets
FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p NATURAL JOIN booking_agent b
WHERE airline_name = 'Jet Blue' AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 MONTH) AND NOW())
GROUP BY booking_agent_email
ORDER BY number_of_tickets DESC LIMIT 5;
```

- Get the top 5 booking agents in the recent year and in the recent month by the amout of commission received

``` sql
SELECT b.email AS booking_agent_email, p.booking_agent_id AS booking_agent_id, SUM(f.price)*0.1 AS commission_earned
FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p NATURAL JOIN booking_agent b
WHERE airline_name = 'Jet Blue' AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 YEAR) AND NOW())
GROUP BY booking_agent_email
ORDER BY commission_earned DESC LIMIT 5;
```

``` sql
SELECT b.email AS booking_agent_email, p.booking_agent_id AS booking_agent_id, SUM(f.price)*0.1 AS commission_earned
FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p NATURAL JOIN booking_agent b
WHERE airline_name = 'Jet Blue' AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 MONTH) AND NOW())
GROUP BY booking_agent_email
ORDER BY commission_earned DESC LIMIT 5;
```

7. **View frequent customers**: Airline Staff will also be able to see the most frequent customer within the last year. In addition, Airline Staff will be able to see a list of all flights a particular Customer has taken only on that particular airline.

- Get the top 5 customers in the recent year by the number of tickets purchased and by the amout of money spent

``` sql
SELECT p.customer_email AS customer_email, COUNT(t.ticket_id) AS number_of_tickets
FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p
WHERE airline_name = 'Jet Blue' AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 YEAR) AND NOW())
GROUP BY customer_email 
ORDER BY number_of_tickets DESC LIMIT 5;
```

``` sql
SELECT p.customer_email AS customer_email, SUM(f.price) AS money_spent
FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p
WHERE airline_name = 'Jet Blue' AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 YEAR) AND NOW())
GROUP BY customer_email 
ORDER BY money_spent DESC LIMIT 5;
```

- Get a particular customer's all purchased ticket information

``` sql
SELECT purchase_date, flight_num, airplane_id, departure_airport, arrival_airport, departure_time, arrival_time, price, status
FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE customer_email = 'test_email'
ORDER BY purchase_date;
```

8. **View reports**: Total amounts of ticket sold based on range of dates/last year/last month etc. Month-wise tickets sold in a bar chart.

- Get the monthly ticket selling statistics based on the given period (customized range, or last year, or last month), by the number of tickets sold

``` sql
SELECT YEAR(p.purchase_date) AS purchase_year, MONTH(p.purchase_date) AS purchase_month, COUNT(t.ticket_id) AS number_ticket_sold
FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p
WHERE f.airline_name = 'Jet Blue' AND (p.purchase_date BETWEEN '2022-01-01' AND NOW())
GROUP BY purchase_year, purchase_month
ORDER BY purchase_year, purchase_month;
```

``` sql
SELECT YEAR(p.purchase_date) AS purchase_year, MONTH(p.purchase_date) AS purchase_month, COUNT(t.ticket_id) AS number_ticket_sold
FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p
WHERE f.airline_name = 'Jet Blue' AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 YEAR) AND NOW())
GROUP BY purchase_year, purchase_month
ORDER BY purchase_year, purchase_month;
```

``` sql
SELECT YEAR(p.purchase_date) AS purchase_year, MONTH(p.purchase_date) AS purchase_month, COUNT(t.ticket_id) AS number_ticket_sold
FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p
WHERE f.airline_name = 'Jet Blue' AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 MONTH) AND NOW())
GROUP BY purchase_year, purchase_month
ORDER BY purchase_year, purchase_month;
```

- Get the monthly ticket selling statistics based on the given period (customized range, or last year, or last month), and by the amout of profit earned

``` sql
SELECT YEAR(p.purchase_date) AS purchase_year, MONTH(p.purchase_date) AS purchase_month, SUM(f.price) AS profit_earned
FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p
WHERE f.airline_name = 'Jet Blue' AND (p.purchase_date BETWEEN '2022-02-01' AND '2022-05-01')
GROUP BY purchase_year, purchase_month
ORDER BY purchase_year, purchase_month;
```

``` sql
SELECT YEAR(p.purchase_date) AS purchase_year, MONTH(p.purchase_date) AS purchase_month, SUM(f.price) AS profit_earned
FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p
WHERE f.airline_name = 'Jet Blue' AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 YEAR) AND NOW())
GROUP BY purchase_year, purchase_month
ORDER BY purchase_year, purchase_month;
```

``` sql
SELECT YEAR(p.purchase_date) AS purchase_year, MONTH(p.purchase_date) AS purchase_month, SUM(f.price) AS profit_earned
FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p
WHERE f.airline_name = 'Jet Blue' AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 MONTH) AND NOW())
GROUP BY purchase_year, purchase_month
ORDER BY purchase_year, purchase_month;
```

9. **Comparison of Revenue earned**: Draw a pie chart for showing total amount of revenue earned from direct sales (when customer bought tickets without using a booking agent) and total amount of revenue earned from indirect sales (when customer bought tickets using booking agents) in the last month and last year.

- Get the total amount of revenue earned from direct sales, that is, when customer bought tickets without using a booking agent, for last month and last year

``` sql
SELECT SUM(f.price) AS revenue 
FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p
WHERE airline_name = 'Jet Blue' AND p.booking_agent_id IS NULL
AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 YEAR) AND NOW());
```

- Get the total amount of revenue earned from indirect sales, that is, when customer bought tickets using booking agents, for last month and last year

``` sql
SELECT SUM(f.price) AS revenue 
FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p
WHERE airline_name = 'Jet Blue' AND p.booking_agent_id IS NOT NULL
AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 MONTH) AND NOW());
```

10. **View Top destinations**: Find the top 3 most popular destinations for last month, last 3 months and last year.

``` sql
SELECT a.airport_city AS city_name, a.airport_name AS airport_name, COUNT(t.ticket_id) AS num_ticket
FROM (flight f NATURAL JOIN ticket t NATURAL JOIN purchases p) JOIN airport a ON (f.departure_airport = a.airport_name)
WHERE airline_name = 'Jet Blue' AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 MONTH) AND NOW())
GROUP BY city_name, airport_name 
ORDER BY num_ticket DESC LIMIT 3;
```

``` sql
SELECT a.airport_city AS city_name, a.airport_name AS airport_name, COUNT(t.ticket_id) AS num_ticket
FROM (flight f NATURAL JOIN ticket t NATURAL JOIN purchases p) JOIN airport a ON (f.departure_airport = a.airport_name)
WHERE airline_name = 'Jet Blue' AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 3 MONTH) AND NOW())
GROUP BY city_name, airport_name 
ORDER BY num_ticket DESC LIMIT 3;
```

``` sql
SELECT a.airport_city AS city_name, a.airport_name AS airport_name, COUNT(t.ticket_id) AS num_ticket
FROM (flight f NATURAL JOIN ticket t NATURAL JOIN purchases p) JOIN airport a ON (f.departure_airport = a.airport_name)
WHERE airline_name = 'Jet Blue' AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 YEAR) AND NOW())
GROUP BY city_name, airport_name 
ORDER BY num_ticket DESC LIMIT 3;
```

11. **Grant new permissions**: Grant new permissions to other staffs in the same airline. The application should prevent unauthorized users or staffs without "Admin" permission from doing this action. Initially there should be a staff with "Admin" permission in the database for each airline. Airline staffs registered through the application DO NOT have any permissions at beginning.

- Add a new permission to an airline staff

``` sql
-- Parameter order: staff_username, permission
INSERT INTO permission VALUES ('test_username', 'admin');
```

- Delete an existing permission from an airline staff

``` sql
DELETE FROM permission WHERE username = 'test_username' AND permission_type = 'admin';
```

12. **Add booking agents**: Add booking agents that can work for this airline, providing their email address. The application should prevent unauthorized users or staffs without "Admin" permission from doing this action. A booking agent cannot work for any airline (thus cannot purchase tickets) until any staff add them through this action.

- Add a booking agent to work for this airline

``` sql
-- Parameter order: booking_agent_email, airline_name
INSERT INTO booking_agent_work_for VALUES ('test_email', 'Jet Blue');
```

- Delete a booking agent from working for this airline

``` sql
DELETE FROM booking_agent_work_for WHERE email = 'test_email' AND airline_name = 'Jet Blue';
```
