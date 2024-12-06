# Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect, flash
import pymysql.cursors
import logging

import matplotlib.pyplot as plt
from io import BytesIO
import base64

from datetime import datetime
import numpy as np
import matplotlib


# Initialize the app from Flask
app = Flask(__name__)

# Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='mysql',
                       db='airline',
                       cursorclass=pymysql.cursors.DictCursor)


###################################
# chart functions
###################################

# helps to generate a bar chart based on two given lists: one is the x-axis values, another is the y-axis values
def gen_bar_chart(x_values, x_labels, y_values, x_axis_name, y_axis_name):
	img = BytesIO()
	plt.clf()
	plt.xlabel(x_axis_name)
	plt.ylabel(y_axis_name)
	plt.bar(x_values, height=y_values, width= 0.4, alpha=0.5)
	plt.xticks(x_values, x_labels)
	plt.savefig(img, format='png', dpi=100)
	plt.close()
	img.seek(0)
	chart_url = base64.b64encode(img.getvalue()).decode('utf8')
	return chart_url

# helps to generate a pie chart
def gen_pie_chart(labels, values):
	img = BytesIO()
	fig1, ax1 = plt.subplots()
	ax1.pie(values, explode=(0, 0.1), labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
	ax1.axis('equal')
	fig1.savefig(img, format='png', dpi=1000)
	img.seek(0)
	pie_url = base64.b64encode(img.getvalue()).decode('utf8')
	return pie_url

# a helper function to check the airline staff's permission
def check_permission(username, perm_to_check):
	# the perm_to_check is either 'admin' or 'operator'
	cursor = conn.cursor()
	query = 'SELECT username, permission_type FROM permission WHERE username = %s AND permission_type = %s;'
	cursor.execute(query, (username, perm_to_check))
	data = cursor.fetchall()
	cursor.close()
	if (data):
		return True
	else:
		return False


############################
# public interface
############################
@app.route('/', methods=['GET', 'POST'])
def default():
	cursor = conn.cursor()
	# default: get the upcoming flights of the airline for the next 30 days
	query_1 = "SELECT * \
		FROM flight \
	    WHERE True "
	cursor.execute(query_1)
	flights = cursor.fetchall()
	cursor.close()
	return render_template('index.html', flights=flights)
	# departure_airport_city=departure_airport_city, arrival_airport_city=arrival_airport_city

############################
# Login
############################

@app.route('/login')
def login():
	return render_template('login.html')

# Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
	# grabs information from the forms
	usertype = request.form.get('usertype')
	# app.logger.info(usertype)
	logname = request.form['logname'] # the logname means email (for customer, agent) or username (for airline staff)
	password = request.form['password']

	# cursor used to send queries
	cursor = conn.cursor()
	# executes query
	if (str(usertype) == "customer"):
		# customer uses email to log in
		query = 'SELECT * FROM customer WHERE email = %s and password = MD5(%s);'
	elif (str(usertype) == "airline_staff"):
		# airline staff uses username to log in
		query = 'SELECT * FROM airline_staff WHERE username = %s and password = MD5(%s);'
	elif (str(usertype) == "booking_agent"):
		# booking agent uses email to log in
		query = 'SELECT * FROM booking_agent WHERE email = %s and password = MD5(%s);'
	cursor.execute(query, (logname, password))
	# stores the results in a variable
	data = cursor.fetchone()
	# use fetchall() if you are expecting more than 1 data row
	cursor.close()
	if (data):
		session['logname'] = logname
		session['usertype'] = usertype
		return redirect(url_for('home'))
	else:
		# returns an error message to the html page
		flash("Invalid username or password")
		return redirect(url_for("login"))


############################
# register for new users 
############################

@app.route('/register')
def register():
	return render_template('register.html')

@app.route('/registerCustomer')
def registerCustomer():
	return render_template('cregister.html')

@app.route('/registerBookingAgent')
def registerBookingAgent():
	return render_template('bregister.html')

@app.route('/registerAirlineStaff')
def registerAirlineStaff():
	return render_template('sregister.html')

# Authenticates the register for customer
@app.route('/registerCustomerAuth', methods=['GET', 'POST'])
def registerCustomerAuth():
	# grabs information from the forms
	email = request.form['email']
	name = request.form['name']
	password = request.form['password']
	building_number = request.form['building_number']
	street = request.form['street']
	city = request.form['city']
	state = request.form['state']
	phone_number = request.form['phone_number']
	passport_number = request.form['passport_number']
	passport_expiration = request.form['passport_expiration']
	passport_country = request.form['passport_country']
	date_of_birth = request.form['date_of_birth']
	# cursor used to send queries
	cursor = conn.cursor()
	# executes query
	query = 'SELECT * FROM customer WHERE email = %s;'
	cursor.execute(query, (email))
	# stores the results in a variable
	data = cursor.fetchone()
	# use fetchall() if you are expecting more than 1 data row
	if int(phone_number) < 0:
		flash("Your phone number should not be negative")
		return render_template('cregister.html')
	elif (passport_expiration<=date_of_birth):
		flash("Your passport expiration date should be later than your date of birth")
		return render_template('cregister.html')
	elif (data):
		# If the previous query returns data, then user exists
		flash("This email has been used")
		return render_template('cregister.html')
	else:
		ins = 'INSERT INTO customer VALUES(%s, %s, MD5(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s);'
		cursor.execute(ins, (email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth))
		conn.commit()
		cursor.close()
		return render_template('index.html')

# Authenticates the register for booking agent
@app.route('/registerBookingAgentAuth', methods=['GET', 'POST'])
def registerBookingAgentAuth():
	#grabs information from the forms
	email = request.form['email']
	password = request.form['password']
	booking_agent_id = request.form['booking_agent_id']
	#cursor used to send queries
	cursor = conn.cursor()
	query_1 = 'SELECT * FROM booking_agent WHERE email = %s;'
	cursor.execute(query_1, (email))
	#stores the results in a variable
	data_1 = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	query_2 = 'SELECT * FROM booking_agent WHERE booking_agent_id = %s;'
	cursor.execute(query_2, (booking_agent_id))
	# stores the results in a variable
	data_2 = cursor.fetchone()
	# use fetchall() if you are expecting more than 1 data row
	if int(booking_agent_id) < 0:
		#If the previous query returns data, then user exists
		flash("Booking agent id should not be negative")
		return render_template('bregister.html')
	elif (data_1):
		#If the previous query returns data, then user exists
		flash("This email has been used")
		return render_template('bregister.html')
	elif (data_2):
		#If the previous query returns data, then user exists
		flash("This booking agent id has been used")
		return render_template('bregister.html')
	else:
		ins = 'INSERT INTO booking_agent VALUES(%s, MD5(%s), %s);'
		cursor.execute(ins, (email, password, booking_agent_id))
		conn.commit()
		cursor.close()
		return render_template('index.html')

# Authenticates the register for airline staff
@app.route('/registerAirlineStaffAuth', methods=['GET', 'POST'])
def registerAirlineStaffAuth():
	# grabs information from the forms
	username = request.form['username']
	password = request.form['password']
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	date_of_birth = request.form['date_of_birth']
	airline_name = request.form['airline_name']
	cursor = conn.cursor()
	query_1 = 'SELECT * FROM airline_staff WHERE username = %s;'
	cursor.execute(query_1, (username))
	# stores the results in a variable
	data_1 = cursor.fetchone()
	# use fetchall() if you are expecting more than 1 data row
	# executes query
	query_2 = 'SELECT * FROM airline WHERE airline_name = %s;'
	cursor.execute(query_2, (airline_name))
	data_2 = cursor.fetchone()
	if (data_1):
		# If the previous query returns data, then user exists
		flash("This username has been used")
		return render_template('sregister.html')
	elif (not data_2):
		flash("No such airline")
		return render_template('sregister.html')
	else:
		ins = 'INSERT INTO airline_staff VALUES(%s, MD5(%s), %s, %s, %s, %s);'
		cursor.execute(ins, (username, password, first_name, last_name, date_of_birth, airline_name))
		conn.commit()
		cursor.close()
		return render_template('index.html')

############################
# home interface after logged in
############################

@app.route('/home')
def home():
	logname = session['logname']
	usertype = session['usertype']

	# get the customer's information and enter the customer's home page
	if (usertype == "customer"):
		# app.logger.info("Customer: %s", logname)
		cursor = conn.cursor()
		query = 'SELECT * FROM customer WHERE email = %s;'
		cursor.execute(query, (logname))
		customer_data = cursor.fetchone()
		cursor.close()
		customer_name = customer_data["name"]
		return render_template('home_customer.html', name=customer_name, data=customer_data)
	# get the airline staff's information and enter the airlie staff's home page
	elif (usertype == "airline_staff"):
		# app.logger.info("Airline staff: %s", logname)
		cursor = conn.cursor()
		query = 'SELECT first_name, last_name FROM airline_staff WHERE username = %s;'
		cursor.execute(query, (logname))
		airline_staff_data = cursor.fetchone()
		cursor.close()
		staff_name = airline_staff_data["first_name"] + " " + airline_staff_data["last_name"]
		return render_template('home_airline_staff.html', name=staff_name)
	# get the booking agent's information and enter the booking agent's home page
	elif (usertype == "booking_agent"):
		# app.logger.info("Booking agent: %s", logname)
		return render_template('home_booking_agent.html', name=logname)
	else:
		return redirect('/')


############################
# customer applications
############################

@app.route("/home/customer_view_my_flights", methods=['GET', 'POST'])
def customer_view_my_flights():
	# Defaults will be showing all the upcoming flights operated by the airline he/she works for the next 30 days.
	# He/she will be able to see all the current/future/past flights operated by the airline he/she works for based on range of dates,
	# source/destination airports/city etc.
	# He/she will be able to see all the customers of a particular flight.
	customer_email = session['logname']
	cursor = conn.cursor()

	# default: get the upcoming flights of the airline for the next 30 days
	query_1 = "SELECT ticket_id, airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, airplane_id \
		FROM flight NATURAL JOIN (ticket NATURAL JOIN purchases) \
		WHERE customer_email = %s "
	time_range_statement = "AND (departure_time BETWEEN NOW() AND ADDTIME(NOW(), '30 0:0:0')) "

	# get source/destination airports/city, for customized selections
	query_2 = "SELECT DISTINCT f.departure_airport AS depart_airport, a.airport_city AS departure_city FROM flight f JOIN airport a ON (f.departure_airport = a.airport_name)"
	cursor.execute(query_2)
	departure_airport_city = cursor.fetchall()
	query_3 = "SELECT DISTINCT f.arrival_airport AS arr_airport, a.airport_city AS arrival_city FROM flight f JOIN airport a ON (f.arrival_airport = a.airport_name)"
	cursor.execute(query_3)
	arrival_airport_city = cursor.fetchall()

	if request.method == "POST":
		# get from the form result: the range of dates that the staff wants to check
		start_date = request.form["range_start"]
		end_date = request.form["range_end"]

		# get from the form result: the departure and arrival city/ airport
		departure = []
		for i in range(len(departure_airport_city)):
			try:
				data = request.form["departure: " + str(i)]
				departure.append(departure_airport_city[i])
			except:
				pass
		arrival = []
		for j in range(len(arrival_airport_city)):
			try:
				data = request.form["arrival: " + str(j)]
				arrival.append(arrival_airport_city[j])
			except:
				pass

		# prepare the query for filtered search
		# the departure date range selection
		if start_date and end_date:
			time_range_statement = "AND DATE(departure_time) BETWEEN \'{}\' AND \'{}\' ".format(start_date, end_date)
		elif start_date:
			time_range_statement = "AND DATE(departure_time) >= \'{}\' ".format(start_date)
		elif end_date:
			time_range_statement = "AND DATE(departure_time) <= \'{}\' ".format(end_date)
		else:
			time_range_statement = " "

		# the departure/arrival airport selection
		if departure:
			departure_statement = ""
			for d in departure:
				departure_statement += "\'" + d["depart_airport"].replace("\'", "\\\'") + "\'" + ", "
			departure_statement = departure_statement.strip(", ")
			departure_statement = "(" + departure_statement + ") "
			query_1 += "AND departure_airport IN " + departure_statement
		if arrival:
			arrival_statement = ""
			for a in arrival:
				arrival_statement += "\'" + a["arr_airport"].replace("\'", "\\\'") + "\'" + ", "
			arrival_statement = arrival_statement.strip(", ")
			arrival_statement = "(" + arrival_statement + ") "
			query_1 += "AND arrival_airport IN " + arrival_statement

	# now execute the flight search query to get the filtered (if applicable) search result
	query_1 += time_range_statement
	query_1 += "ORDER BY departure_time, arrival_time;"
	cursor.execute(query_1, (customer_email))
	flights = cursor.fetchall()
	cursor.close()
	return render_template("customer_view_my_flights.html", flights=flights, departure_airport_city=departure_airport_city, arrival_airport_city=arrival_airport_city)

# customer search for flights
@app.route("/home/customer_search_for_flights", methods=['GET', 'POST'])
def customer_search_for_flights():
	# Defaults will be showing all the upcoming flights operated by the airline he/she works for the next 30 days.
	# He/she will be able to see all the current/future/past flights operated by the airline he/she works for based on range of dates,
	# source/destination airports/city etc.
	# He/she will be able to see all the customers of a particular flight.
	cursor = conn.cursor()
	# default: get the upcoming flights of the airline for the next 30 days
	query_1 = "SELECT * \
		FROM flight \
	    WHERE True "
	time_range_statement = "AND departure_time BETWEEN NOW() AND ADDTIME(NOW(), '30 0:0:0') "

	# get source/destination airports/city, for customized selections
	query_2 = "SELECT DISTINCT f.departure_airport AS depart_airport, a.airport_city AS departure_city FROM flight f JOIN airport a ON (f.departure_airport = a.airport_name)"
	cursor.execute(query_2)
	departure_airport_city = cursor.fetchall()
	query_3 = "SELECT DISTINCT f.arrival_airport AS arr_airport, a.airport_city AS arrival_city FROM flight f JOIN airport a ON (f.arrival_airport = a.airport_name)"
	cursor.execute(query_3)
	arrival_airport_city = cursor.fetchall()

	if request.method == "POST":
		# get from the form result: the range of dates that the staff wants to check
		start_date = request.form["range_start"]
		end_date = request.form["range_end"]

		# get from the form result: the departure and arrival city/ airport
		departure = []
		for i in range(len(departure_airport_city)):
			try:
				data = request.form["departure: " + str(i)]
				departure.append(departure_airport_city[i])
			except:
				pass
		arrival = []
		for j in range(len(arrival_airport_city)):
			try:
				data = request.form["arrival: " + str(j)]
				arrival.append(arrival_airport_city[j])
			except:
				pass

		# prepare the query for filtered search
		# the departure date range selection
		if start_date and end_date:
			time_range_statement = "AND DATE(departure_time) BETWEEN \'{}\' AND \'{}\' ".format(start_date, end_date)
		elif start_date:
			time_range_statement = "AND DATE(departure_time) >= \'{}\' ".format(start_date)
		elif end_date:
			time_range_statement = "AND DATE(departure_time) <= \'{}\' ".format(end_date)
		else:
			time_range_statement = " "

		# the departure/arrival airport selection
		if departure:
			departure_statement = ""
			for d in departure:
				departure_statement += "\'" + d["depart_airport"].replace("\'", "\\\'") + "\'" + ", "
			departure_statement = departure_statement.strip(", ")
			departure_statement = "(" + departure_statement + ") "
			query_1 += "AND departure_airport IN " + departure_statement
		if arrival:
			arrival_statement = ""
			for a in arrival:
				arrival_statement += "\'" + a["arr_airport"].replace("\'", "\\\'") + "\'" + ", "
			arrival_statement = arrival_statement.strip(", ")
			arrival_statement = "(" + arrival_statement + ") "
			query_1 += "AND arrival_airport IN " + arrival_statement

	# now execute the flight search query to get the filtered (if applicable) search result
	query_1 += time_range_statement
	query_1 += "ORDER BY departure_time, arrival_time;"
	cursor.execute(query_1)
	flights = cursor.fetchall()
	cursor.close()
	return render_template("customer_search_for_flights.html", flights=flights, departure_airport_city=departure_airport_city, arrival_airport_city=arrival_airport_city)

# purchase tickets
@app.route("/home/customer_purchase_tickets", methods=['GET', 'POST'])
def customer_purchase_tickets():
	username = session['logname']
	cursor = conn.cursor()
	error = None
	# receive the inputs of purchasing tickets
	if request.method == "POST":
		airline_name = request.form["airline_name"]
		flight_num = request.form["flight_num"]

		# first check if there the given flight_num already exists
		query_1 = "SELECT * FROM flight WHERE airline_name = %s AND flight_num = %s"
		# then check if there are seats left
		query_2 = "SELECT ticket_id FROM ticket WHERE airline_name = %s AND flight_num = %s AND ticket_id NOT IN (SELECT ticket_id FROM purchases)"
		cursor.execute(query_1, (airline_name, flight_num))
		data_1 = cursor.fetchone()
		cursor.execute(query_2, (airline_name, flight_num))
		data_2 = cursor.fetchone()

		if (not data_1):
			# If the previous query returns data, then the flight exists
			flash("This flight does not exist!")
			error = True
		elif (not data_2):
			# If the previous query returns data, then the flight exists
			flash("Sorry! This flight has no seat left!")
			error = True

		# if there is no detected error
		if (not error):
			# get the ticket_id to be purchased
			query_3 = "SELECT min(ticket_id) AS min_ticket_id FROM ticket WHERE airline_name = %s AND flight_num = %s AND ticket_id NOT IN (SELECT ticket_id FROM purchases)"
			cursor.execute(query_3, (airline_name, flight_num))
			ticket_id_data = cursor.fetchone()
			ticket_id = ticket_id_data["min_ticket_id"]
			# get the current date as purchase_date
			cur_time = str(datetime.now())
			cur_date = cur_time.split()[0]
			# add the purchase to database
			ins = "INSERT INTO purchases VALUES (%s, %s, NULL, %s);"
			cursor.execute(ins, (ticket_id, username, cur_date))
			conn.commit()
			flash("You have purchased the ticket! The ticket ID is " + str(ticket_id) + "!")

		# default: get the upcoming flights of the airline for the next 30 days
		query_4 = "SELECT * \
				FROM flight \
			    WHERE True "
		time_range_statement = "AND departure_time BETWEEN NOW() AND ADDTIME(NOW(), '30 0:0:0') "
		query_4 += time_range_statement
		query_4 += "ORDER BY departure_time, arrival_time;"
		cursor.execute(query_4)
		flights = cursor.fetchall()
		# get source/destination airports/city, for customized selections
		query_5 = "SELECT DISTINCT f.departure_airport AS depart_airport, a.airport_city AS departure_city FROM flight f JOIN airport a ON (f.departure_airport = a.airport_name)"
		cursor.execute(query_5)
		departure_airport_city = cursor.fetchall()
		query_6 = "SELECT DISTINCT f.arrival_airport AS arr_airport, a.airport_city AS arrival_city FROM flight f JOIN airport a ON (f.arrival_airport = a.airport_name)"
		cursor.execute(query_6)
		arrival_airport_city = cursor.fetchall()

	cursor.close()
	return render_template("customer_search_for_flights.html", flights=flights, departure_airport_city=departure_airport_city, arrival_airport_city=arrival_airport_city, error=error)

# track spending
@app.route("/home/customer_track_my_spending", methods=['GET', 'POST'])
def customer_track_my_spending():
	email = session['logname']
	cursor = conn.cursor()

	# period is for sql query, period_string is for front-end display
	method = "default"
	period_string = "for Last 6 Months"
	period_statement = "(purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 6 MONTH) AND NOW())"
	if request.method == "POST":
		method = request.form["method_select"]
		range_start = request.form["range_start"]
		range_end = request.form["range_end"]

		# if the period is recent month or recent year
		if (method == "customize"):
			start_string = range_start if range_start else "Today"
			end_string = range_end if range_end else "Today"
			period_string = "from {} up to {}".format(start_string, end_string)
			start_period = "\'" + range_start + "\'" if range_start else "NOW()"
			end_period = "\'" + range_end + "\'" if range_end else "NOW()"
			period_statement = "(purchase_date BETWEEN {} AND {})".format(start_period, end_period)

	empty = None
	plot_url = None
	# display the monthly ticket selling statistics based on the given period (customized range, or last year, or last month)
	# by the number of tickets sold and by the amout of profit earned
	query = "SELECT YEAR(purchase_date) AS purchase_year, MONTH(purchase_date) AS purchase_month, SUM(price) AS month_spent \
		FROM flight NATURAL JOIN ticket NATURAL JOIN purchases\
		WHERE customer_email = %s AND {} \
		GROUP BY purchase_year, purchase_month \
		ORDER BY purchase_year, purchase_month;".format(period_statement)
	cursor.execute(query, (email))
	month_spent_data = cursor.fetchall()
	cursor.close()

	# process the fetched dictionary
	if (not month_spent_data):
		flash("The Period You Selected Has NO Data, NO Bar Chart Available!")
		empty = True
	else:
		year_months = []
		month_spent = []
		for data in month_spent_data:
			cur_year_month = str(data["purchase_year"]) + "-" + str(data["purchase_month"])
			year_months.append(cur_year_month)
			month_spent.append(data["month_spent"])
			x_pos = np.arange(len(year_months))
		plot_url = gen_bar_chart(x_pos, year_months, month_spent, "Year and Month", "Money Spent")

	return render_template("customer_track_my_spending.html", period_string=period_string, plot_url=plot_url, empty=empty)


############################
# booking agent functions
############################

@app.route("/home/booking_agent_view_my_flights", methods=['GET', 'POST'])
def booking_agent_view_my_flights():
	# Defaults will be showing all the upcoming flights operated by the airline he/she works for the next 30 days.
	# He/she will be able to see all the current/future/past flights operated by the airline he/she works for based on range of dates,
	# source/destination airports/city etc.
	# He/she will be able to see all the customers of a particular flight.
	booking_agent_email = session['logname']
	cursor = conn.cursor()

	query_0 = 'SELECT booking_agent_id FROM booking_agent WHERE email = %s;'
	cursor.execute(query_0, (booking_agent_email))
	booking_agent_id_data = cursor.fetchone()
	booking_agent_id = booking_agent_id_data["booking_agent_id"]

	# default: get the upcoming flights of the airline for the next 30 days
	query_1 = "SELECT customer_email, name as customer_name, ticket_id, airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, airplane_id \
		FROM flight NATURAL JOIN (ticket NATURAL JOIN (purchases JOIN customer ON customer_email=email )) \
		WHERE booking_agent_id = %s "
	time_range_statement = "AND (departure_time BETWEEN NOW() AND ADDTIME(NOW(), '30 0:0:0')) "

	# get source/destination airports/city, for customized selections
	query_2 = "SELECT DISTINCT f.departure_airport AS depart_airport, a.airport_city AS departure_city FROM flight f JOIN airport a ON (f.departure_airport = a.airport_name)"
	cursor.execute(query_2)
	departure_airport_city = cursor.fetchall()
	query_3 = "SELECT DISTINCT f.arrival_airport AS arr_airport, a.airport_city AS arrival_city FROM flight f JOIN airport a ON (f.arrival_airport = a.airport_name)"
	cursor.execute(query_3)
	arrival_airport_city = cursor.fetchall()

	if request.method == "POST":
		# get from the form result: the range of dates that the staff wants to check
		start_date = request.form["range_start"]
		end_date = request.form["range_end"]

		# get from the form result: the departure and arrival city/ airport
		departure = []
		for i in range(len(departure_airport_city)):
			try:
				data = request.form["departure: " + str(i)]
				departure.append(departure_airport_city[i])
			except:
				pass
		arrival = []
		for j in range(len(arrival_airport_city)):
			try:
				data = request.form["arrival: " + str(j)]
				arrival.append(arrival_airport_city[j])
			except:
				pass

		# prepare the query for filtered search
		# the departure date range selection
		if start_date and end_date:
			time_range_statement = "AND DATE(departure_time) BETWEEN \'{}\' AND \'{}\' ".format(start_date, end_date)
		elif start_date:
			time_range_statement = "AND DATE(departure_time) >= \'{}\' ".format(start_date)
		elif end_date:
			time_range_statement = "AND DATE(departure_time) <= \'{}\' ".format(end_date)
		else:
			time_range_statement = " "

		# the departure/arrival airport selection
		if departure:
			departure_statement = ""
			for d in departure:
				departure_statement += "\'" + d["depart_airport"].replace("\'", "\\\'") + "\'" + ", "
			departure_statement = departure_statement.strip(", ")
			departure_statement = "(" + departure_statement + ") "
			query_1 += "AND departure_airport IN " + departure_statement
		if arrival:
			arrival_statement = ""
			for a in arrival:
				arrival_statement += "\'" + a["arr_airport"].replace("\'", "\\\'") + "\'" + ", "
			arrival_statement = arrival_statement.strip(", ")
			arrival_statement = "(" + arrival_statement + ") "
			query_1 += "AND arrival_airport IN " + arrival_statement

	# now execute the flight search query to get the filtered (if applicable) search result
	query_1 += time_range_statement
	query_1 += "ORDER BY departure_time, arrival_time;"
	cursor.execute(query_1, (booking_agent_id))
	flights = cursor.fetchall()
	cursor.close()
	return render_template("booking_agent_view_my_flights.html", flights=flights, departure_airport_city=departure_airport_city, arrival_airport_city=arrival_airport_city)

#search for flights
@app.route("/home/booking_agent_search_for_flights", methods=['GET', 'POST'])
def booking_agent_search_for_flights():
	# Defaults will be showing all the upcoming flights operated by the airline he/she works for the next 30 days.
	# He/she will be able to see all the current/future/past flights operated by the airline he/she works for based on range of dates,
	# source/destination airports/city etc.
	# He/she will be able to see all the customers of a particular flight.
	cursor = conn.cursor()
	# default: get the upcoming flights of the airline for the next 30 days
	query_1 = "SELECT * \
		FROM flight \
		WHERE True "
	time_range_statement = "AND departure_time BETWEEN NOW() AND ADDTIME(NOW(), '30 0:0:0') "

	# get source/destination airports/city, for customized selections
	query_2 = "SELECT DISTINCT f.departure_airport AS depart_airport, a.airport_city AS departure_city FROM flight f JOIN airport a ON (f.departure_airport = a.airport_name)"
	cursor.execute(query_2)
	departure_airport_city = cursor.fetchall()
	query_3 = "SELECT DISTINCT f.arrival_airport AS arr_airport, a.airport_city AS arrival_city FROM flight f JOIN airport a ON (f.arrival_airport = a.airport_name)"
	cursor.execute(query_3)
	arrival_airport_city = cursor.fetchall()

	if request.method == "POST":
		# get from the form result: the range of dates that the staff wants to check
		start_date = request.form["range_start"]
		end_date = request.form["range_end"]

		# get from the form result: the departure and arrival city/ airport
		departure = []
		for i in range(len(departure_airport_city)):
			try:
				data = request.form["departure: " + str(i)]
				departure.append(departure_airport_city[i])
			except:
				pass
		arrival = []
		for j in range(len(arrival_airport_city)):
			try:
				data = request.form["arrival: " + str(j)]
				arrival.append(arrival_airport_city[j])
			except:
				pass

		# prepare the query for filtered search
		# the departure date range selection
		if start_date and end_date:
			time_range_statement = "AND DATE(departure_time) BETWEEN \'{}\' AND \'{}\' ".format(start_date, end_date)
		elif start_date:
			time_range_statement = "AND DATE(departure_time) >= \'{}\' ".format(start_date)
		elif end_date:
			time_range_statement = "AND DATE(departure_time) <= \'{}\' ".format(end_date)
		else:
			time_range_statement = " "

		# the departure/arrival airport selection
		if departure:
			departure_statement = ""
			for d in departure:
				departure_statement += "\'" + d["depart_airport"].replace("\'", "\\\'") + "\'" + ", "
			departure_statement = departure_statement.strip(", ")
			departure_statement = "(" + departure_statement + ") "
			query_1 += "AND departure_airport IN " + departure_statement
		if arrival:
			arrival_statement = ""
			for a in arrival:
				arrival_statement += "\'" + a["arr_airport"].replace("\'", "\\\'") + "\'" + ", "
			arrival_statement = arrival_statement.strip(", ")
			arrival_statement = "(" + arrival_statement + ") "
			query_1 += "AND arrival_airport IN " + arrival_statement

	# now execute the flight search query to get the filtered (if applicable) search result
	query_1 += time_range_statement
	query_1 += "ORDER BY departure_time, arrival_time;"
	cursor.execute(query_1)
	flights = cursor.fetchall()
	cursor.close()
	return render_template("booking_agent_search_for_flights.html", flights=flights, departure_airport_city=departure_airport_city, arrival_airport_city=arrival_airport_city)

# purchase tickets
@app.route("/home/booking_agent_purchase_tickets", methods=['GET', 'POST'])
def booking_agent_purchase_tickets():
	username = session['logname']
	cursor = conn.cursor()
	error = None
	# receive the inputs of purchasing tickets
	if request.method == "POST":
		airline_name = request.form["airline_name"]
		flight_num = request.form["flight_num"]
		email = request.form["email"]
		# get the booking agent id
		query_0 = "SELECT booking_agent_id FROM booking_agent WHERE email = %s"
		cursor.execute(query_0, (username))
		booking_agent_id_data = cursor.fetchone()
		booking_agent_id = booking_agent_id_data["booking_agent_id"]
		# first check if there the given flight_num already exists
		query_1 = "SELECT ticket_id FROM ticket WHERE airline_name = %s AND flight_num = %s"
		# then check if there are seats left
		query_2 = "SELECT ticket_id FROM ticket WHERE airline_name = %s AND flight_num = %s AND ticket_id NOT IN (SELECT ticket_id FROM purchases)"
		cursor.execute(query_1, (airline_name, flight_num))
		data_1 = cursor.fetchone()
		cursor.execute(query_2, (airline_name, flight_num))
		data_2 = cursor.fetchone()
		# check if the customer exists
		query = "SELECT * FROM customer WHERE email = %s"
		cursor.execute(query, (email))
		data_3 = cursor.fetchone()

		if (not data_1):
			# If the previous query returns data, then the flight exists
			flash("This flight does not exist!")
			error = True
		elif (not data_2):
			# If the previous query returns data, then the flight exists
			flash("Sorry! This flight has no seat left!")
			error = True
		elif (not data_3):
			# If the previous query returns data, then the flight exists
			flash("Sorry! This customer email is invalid!")
			error = True

		# if there is no detected error
		if (not error):
			# get the ticket_id to be purchased
			query_3 = "SELECT min(ticket_id) AS min_ticket_id FROM ticket WHERE airline_name = %s AND flight_num = %s AND ticket_id NOT IN (SELECT ticket_id FROM purchases)"
			cursor.execute(query_3, (airline_name, flight_num))
			ticket_id_data = cursor.fetchone()
			ticket_id = ticket_id_data["min_ticket_id"]
			# get the current date as purchase_date
			cur_time = str(datetime.now())
			cur_date = cur_time.split()[0]
			# add the purchase to database
			ins = "INSERT INTO purchases VALUES (%s, %s, %s, %s);"
			cursor.execute(ins, (ticket_id, email, booking_agent_id, cur_date))
			conn.commit()
			flash("You have purchased the ticket! The ticket ID is " + str(ticket_id) + "!")

		# default: get the upcoming flights of the airline for the next 30 days
		query_4 = "SELECT * \
				FROM flight \
			    WHERE True "
		time_range_statement = "AND departure_time BETWEEN NOW() AND ADDTIME(NOW(), '30 0:0:0') "
		query_4 += time_range_statement
		query_4 += "ORDER BY departure_time, arrival_time;"
		cursor.execute(query_4)
		flights = cursor.fetchall()
		# get source/destination airports/city, for customized selections
		query_5 = "SELECT DISTINCT f.departure_airport AS depart_airport, a.airport_city AS departure_city FROM flight f JOIN airport a ON (f.departure_airport = a.airport_name)"
		cursor.execute(query_5)
		departure_airport_city = cursor.fetchall()
		query_6 = "SELECT DISTINCT f.arrival_airport AS arr_airport, a.airport_city AS arrival_city FROM flight f JOIN airport a ON (f.arrival_airport = a.airport_name)"
		cursor.execute(query_6)
		arrival_airport_city = cursor.fetchall()

	cursor.close()
	return render_template("booking_agent_search_for_flights.html", flights=flights, departure_airport_city=departure_airport_city, arrival_airport_city=arrival_airport_city, error=error)


# view commission
@app.route("/home/booking_agent_view_my_commission", methods=['GET', 'POST'])
def booking_agent_view_my_commission():
	# Defaults will be showing all the upcoming flights operated by the airline he/she works for the next 30 days.
	# He/she will be able to see all the current/future/past flights operated by the airline he/she works for based on range of dates,
	# source/destination airports/city etc.
	# He/she will be able to see all the customers of a particular flight.
	booking_agent_email = session['logname']
	cursor = conn.cursor()

	query_0 = 'SELECT booking_agent_id FROM booking_agent WHERE email = %s;'
	cursor.execute(query_0, (booking_agent_email))
	booking_agent_id_data = cursor.fetchone()
	booking_agent_id = booking_agent_id_data["booking_agent_id"]
	# default: get the upcoming purchased flights for the next 30 days
	query_1 = "SELECT SUM(price)/10 AS total_commission, COUNT(*) AS ticket_num, AVG(price)/10 AS avg_commission \
		FROM flight NATURAL JOIN (ticket NATURAL JOIN purchases) \
		WHERE booking_agent_id = %s "
	time_range_statement = "AND (purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 MONTH) AND NOW()) "


	if request.method == "POST":
		# get from the form result: the range of dates that the staff wants to check
		start_date = request.form["range_start"]
		end_date = request.form["range_end"]

		# prepare the query for filtered search
		# the departure date range selection
		if start_date and end_date:
			time_range_statement = "AND purchase_date BETWEEN \'{}\' AND \'{}\' ".format(start_date, end_date)
		elif start_date:
			time_range_statement = "AND purchase_date >= \'{}\' ".format(start_date)
		elif end_date:
			time_range_statement = "AND purchase_date <= \'{}\' ".format(end_date)

	# now execute the flight search query to get the filtered (if applicable) search result
	query_1 += time_range_statement
	cursor.execute(query_1, (booking_agent_id))
	commission_data = cursor.fetchall()
	cursor.close()
	total_commission = commission_data[0]["total_commission"]
	ticket_num = commission_data[0]["ticket_num"]
	avg_commission = commission_data[0]["avg_commission"]
	if (total_commission == None):
		total_commission = 0
		ticket_num = 0
		avg_commission = 0

	return render_template("booking_agent_view_my_commission.html", total_commission=total_commission, ticket_num = ticket_num, avg_commission = avg_commission)


#track  spending
@app.route("/home/booking_agent_view_top_customers", methods=['GET', 'POST'])
def booking_agent_view_top_customers():
	# get the airline name that the staff belongs to
	booking_agent_email = session['logname']
	cursor = conn.cursor()
	query_0 = 'SELECT booking_agent_id FROM booking_agent WHERE email = %s;'
	cursor.execute(query_0, (booking_agent_email))
	booking_agent_id_data = cursor.fetchone()
	booking_agent_id = booking_agent_id_data["booking_agent_id"]

	period_statement_1 = "(purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 6 MONTH) AND NOW())"
	period_statement_2 = "(purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 YEAR) AND NOW())"

	empty_1 = None
	empty_2 = None
	plot_url_1 = None
	plot_url_2 = None
	# display the monthly ticket selling statistics based on the given period (customized range, or last year, or last month)
	# by the number of tickets sold and by the amout of profit earned
	query_1 = "SELECT customer_email, COUNT(ticket_id) AS ticket_num \
		FROM purchases \
		WHERE booking_agent_id = %s \
		AND {}\
		GROUP BY customer_email \
		ORDER BY ticket_num DESC LIMIT 5;".format(period_statement_1)
	cursor.execute(query_1, (booking_agent_id))
	ticket_num_data = cursor.fetchall()
	query_2 = "SELECT customer_email, SUM(price) AS total_commission\
		FROM flight NATURAL JOIN ticket NATURAL JOIN purchases \
		WHERE booking_agent_id = %s \
		AND {}\
		GROUP BY customer_email \
		ORDER BY total_commission DESC LIMIT 5;".format(period_statement_2)
	cursor.execute(query_2, (booking_agent_id))
	total_commission_data = cursor.fetchall()
	cursor.close()

	# process the fetched dictionary
	if (not ticket_num_data):
		empty_1 = True
	else:
		ticket_num = []
		customer_1 = []
		for data in ticket_num_data:
			customer_1.append(data["customer_email"])
			ticket_num.append(data["ticket_num"])
			x_pos = np.arange(len(customer_1))
		plot_url_1 = gen_bar_chart(x_pos, customer_1, ticket_num, "Customer Email", "Number of Tickets")
	
	if (not total_commission_data):
		empty_2 = True
	else:
		total_commission = []
		customer_2 = []
		for data in total_commission_data:
			customer_2.append(data["customer_email"])
			total_commission.append(data["total_commission"])
			x_pos = np.arange(len(customer_2))
		plot_url_2 = gen_bar_chart(x_pos, customer_2, total_commission, "Customer Email", "Total Commission")

	return render_template("booking_agent_view_top_customers.html", plot_url_1=plot_url_1, plot_url_2=plot_url_2, empty_1=empty_1, empty_2=empty_2)


############################
# airline staff applications
############################
@app.route("/home/airline_staff_view_my_flights", methods=['GET','POST'])
def airline_staff_view_my_flights():
	# Defaults will be showing all the upcoming flights operated by the airline he/she works for the next 30 days. 
	# He/she will be able to see all the current/future/past flights operated by the airline he/she works for based on range of dates, 
	# source/destination airports/city etc. 
	# He/she will be able to see all the customers of a particular flight.
	username = session['logname']
	cursor = conn.cursor()

	# get the airline name that the staff belongs to
	query_1 = "SELECT airline_name FROM airline_staff WHERE username = %s;"
	cursor.execute(query_1, (username))
	airline_name_data = cursor.fetchone()
	airline_name = airline_name_data["airline_name"]

	# default: get the upcoming flights of the airline for the next 30 days
	query_2 = "SELECT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, airplane_id, GROUP_CONCAT(customer_email SEPARATOR ', ') as customers \
		FROM flight NATURAL LEFT OUTER JOIN (ticket NATURAL JOIN purchases) \
		WHERE airline_name = %s "
	time_range_statement = "AND (departure_time BETWEEN NOW() AND ADDTIME(NOW(), '30 0:0:0')) "

	# get source/destination airports/city, for customized selections
	query_3 = "SELECT DISTINCT f.departure_airport AS depart_airport, a.airport_city AS departure_city FROM flight f JOIN airport a ON (f.departure_airport = a.airport_name)"
	cursor.execute(query_3)
	departure_airport_city = cursor.fetchall()
	query_4 = "SELECT DISTINCT f.arrival_airport AS arr_airport, a.airport_city AS arrival_city FROM flight f JOIN airport a ON (f.arrival_airport = a.airport_name)"
	cursor.execute(query_4)
	arrival_airport_city = cursor.fetchall()

	if request.method == "POST":
		# get from the form result: the range of dates that the staff wants to check
		start_date = request.form["range_start"]
		end_date = request.form["range_end"]
		
		# get from the form result: the departure and arrival city/ airport
		departure = []
		for i in range(len(departure_airport_city)):
			try:
				data = request.form["departure: "+str(i)]
				departure.append(departure_airport_city[i])
			except:
				pass
		arrival = []
		for j in range(len(arrival_airport_city)):
			try:
				data = request.form["arrival: "+str(j)]
				arrival.append(arrival_airport_city[j])
			except:
				pass

		# prepare the query for filtered search
		# the departure date range selection
		if start_date and end_date:
			time_range_statement = "AND DATE(departure_time) BETWEEN \'{}\' AND \'{}\' ".format(start_date, end_date)
		elif start_date:
			time_range_statement = "AND DATE(departure_time) >= \'{}\' ".format(start_date)
		elif end_date:
			time_range_statement = "AND DATE(departure_time) <= \'{}\' ".format(end_date)
		else:
			time_range_statement = " "
		
		# the departure/arrival airport selection
		if departure:
			departure_statement = ""
			for d in departure:
				departure_statement += "\'" + d["depart_airport"].replace("\'", "\\\'") + "\'" + ", "
			departure_statement = departure_statement.strip(", ")
			departure_statement = "(" + departure_statement + ") "
			query_2 += "AND departure_airport IN " + departure_statement
		if arrival:
			arrival_statement = ""
			for a in arrival:
				arrival_statement += "\'" + a["arr_airport"].replace("\'", "\\\'") + "\'" + ", "
			arrival_statement = arrival_statement.strip(", ")
			arrival_statement = "(" + arrival_statement + ") "
			query_2 += "AND arrival_airport IN " + arrival_statement
				
	# now execute the flight search query to get the filtered (if applicable) search result
	query_2 += time_range_statement
	query_2 += "GROUP BY airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, airplane_id\
		ORDER BY departure_time, arrival_time;"
	cursor.execute(query_2, (airline_name))
	flights = cursor.fetchall()
	cursor.close()

	return render_template("airline_staff_view_my_flights.html", flights=flights, departure_airport_city=departure_airport_city, arrival_airport_city=arrival_airport_city)

# create new flights: for admin staff
@app.route("/home/airline_staff_create_new_flight", methods=['GET', 'POST'])
def airline_staff_create_new_flight():
	username = session['logname']
	is_admin = check_permission(username, 'admin')
	# if not admin, then refuse to do this
	if (not is_admin):
		flash("Unauthorized Operation: You do not have Admin Permission!")
		return redirect(url_for("home"))

	# display the existing flight information
	# get the airline name that the staff belongs to
	cursor = conn.cursor()
	query_1 = "SELECT airline_name FROM airline_staff WHERE username = %s;"
	cursor.execute(query_1, (username))
	airline_name_data = cursor.fetchone()
	airline_name = airline_name_data["airline_name"]

	error = None
	# receive the inputs of creating a new flight
	if request.method == "POST":
		flight_num = request.form["flight_num"]
		airplane_id = request.form["airplane_id"]
		departure_airport = request.form["departure_airport"]
		departure_time = request.form["departure_time"]
		arrival_airport = request.form["arrival_airport"]
		arrival_time = request.form["arrival_time"]
		price = request.form["price"]
		status = request.form["status"]

		# first check if there the given flight_num already exists
		q1 = "SELECT airline_name, flight_num FROM flight WHERE airline_name = %s AND flight_num = %s;"
		cursor.execute(q1, (airline_name, flight_num))
		d1 = cursor.fetchone()
		if (d1):
			# If the previous query returns data, then the flight exists
			flash("This flight already exists!")
			error = True
		
		# then check if this airline really has this airplane (id)
		q2 = "SELECT * FROM airplane WHERE airline_name = %s AND airplane_id = %s;"
		cursor.execute(q2, (airline_name, airplane_id))
		d2 = cursor.fetchone()
		if (not d2):
			# If the previous query returns nothing, then the airplane is invalid
			flash("Your Airline DOES NOT have this Airplane!")
			error = True
		
		# then check if the departure airport and arrival airport exist, and not the same
		if departure_airport == arrival_airport:
			flash("Departure airport CANNOT be the same as Arrival airport!")
			error = True
		q3 = "SELECT * FROM airport WHERE airport_name = %s"
		cursor.execute(q3, (departure_airport))
		d3_d = cursor.fetchone()
		cursor.execute(q3, (arrival_airport))
		d3_a = cursor.fetchone()
		# only if both queries have result, it means the airports are valid
		if (not d3_d):
			flash("The Departure Airport Code is Invalid!")
			error = True
		if (not d3_a):
			flash("The Arrival Airport Code is Invalid!")
			error = True

		# then check if departure time is ahead of arrival time
		if (departure_time >= arrival_time):
			flash("The Departure Time CANNOT be Later than the Arrival Time!")
			error = True
		
		# then check if the price is positive
		if (int(price) <= 0):
			flash("The Price MUST be Positive numbers!")
			error = True
	
		# if there is no detected error
		if (not error):
			# add the new flight to database
			ins = "INSERT INTO flight VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
			cursor.execute(ins, (airline_name, flight_num, departure_airport, departure_time.replace("T", " "), arrival_airport, arrival_time.replace("T", " "), price, status, airplane_id))
			conn.commit()

			# also, need to add the corresponding tickets into the "ticket" table
			# the number of tickets is the number of seats
			# first, get the max_ticket id in the ticket table, so that we can increment from that
			q_cur_max_ticket_id = "SELECT MAX(ticket_id) AS max_tid FROM ticket;"
			cursor.execute(q_cur_max_ticket_id)
			cur_max_ticket_id_dict = cursor.fetchone()
			cur_max_ticket_id = cur_max_ticket_id_dict["max_tid"]
			if (not cur_max_ticket_id):
				ticket_id_counter = 1
			else:
				ticket_id_counter = cur_max_ticket_id + 1
			# then, get the number of seats of that airplane, to serve as ticket number
			q_seats = "SELECT seats FROM airplane WHERE airline_name = %s AND airplane_id = %s;"
			cursor.execute(q_seats, (airline_name, airplane_id))
			seats_dict = cursor.fetchone()
			seats = seats_dict["seats"]
			# finally, add tickets to the ticket table
			ins_ticket = "INSERT INTO ticket VALUES (%s, %s, %s);"
			for i in range(ticket_id_counter, ticket_id_counter+seats):
				cursor.execute(ins_ticket, (i, airline_name, flight_num))
			conn.commit()
			flash("You have added the Flight into the System!")
			flash("Also, the corresponding Tickets have been added!")
	
	# default: get the upcoming flights of the airline for the next 30 days
	query_2 = "SELECT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, airplane_id, GROUP_CONCAT(customer_email SEPARATOR ', ') as customers \
		FROM flight NATURAL LEFT OUTER JOIN (ticket NATURAL JOIN purchases) \
		WHERE airline_name = %s AND (departure_time BETWEEN NOW() AND ADDTIME(NOW(), '30 0:0:0')) \
		GROUP BY airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, airplane_id\
		ORDER BY departure_time, arrival_time;"
	cursor.execute(query_2, (airline_name))
	flights = cursor.fetchall()
	cursor.close()
	return render_template("airline_staff_create_new_flight.html", flights=flights, error=error)

# change flight status: for operator staff
@app.route("/home/airline_staff_change_flight_status", methods=['GET', 'POST'])
def airline_staff_change_flight_status():
	username = session['logname']
	is_op = check_permission(username, 'operator')
	# if not operator, then refuse to do this
	if (not is_op):
		flash("Unauthorized Operation: You do not have Operator Permission!")
		return redirect(url_for("home"))
	
	# display the existing flight information
	# get the airline name that the staff belongs to
	cursor = conn.cursor()
	query_1 = "SELECT airline_name FROM airline_staff WHERE username = %s;"
	cursor.execute(query_1, (username))
	airline_name_data = cursor.fetchone()
	airline_name = airline_name_data["airline_name"]

	error = None
	# receive the inputs of updating a flight status
	if request.method == "POST":
		flight_num = request.form["flight_num"]
		status = request.form["status"]

		# first check if the flight number is valid
		q1 = "SELECT airline_name, flight_num FROM flight WHERE airline_name = %s AND flight_num = %s;"
		cursor.execute(q1, (airline_name, flight_num))
		d1 = cursor.fetchone()
		if (not d1):
			flash("Invalid Flight Number!")
			error = True

		# then check if the status is duplicated as before
		q2 = "SELECT status FROM flight WHERE airline_name = %s AND flight_num = %s;"
		cursor.execute(q2, (airline_name, flight_num))
		d2 = cursor.fetchone()
		if d2 and d2["status"] == status:
			flash("This Flight #{} already has status {}, NO need to change!".format(flight_num, status))
			error = True

		# if there is no detected error, then add the new flight to database
		if (not error):
			update = "UPDATE flight SET status = %s WHERE flight_num = %s;"
			cursor.execute(update, (status, flight_num))
			conn.commit()
			flash("You have updated the status of Flight #{} as {}!".format(flight_num, status))

	# get all the upcoming, in-progress and delayed flights and list them
	query_2_upcoming = "SELECT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, airplane_id, GROUP_CONCAT(customer_email SEPARATOR ', ') as customers \
		FROM flight NATURAL LEFT OUTER JOIN (ticket NATURAL JOIN purchases) \
		WHERE airline_name = %s AND status = \'Upcoming\' \
		GROUP BY airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, airplane_id\
		ORDER BY departure_time, arrival_time;"
	cursor.execute(query_2_upcoming, (airline_name))
	upcoming_flights = cursor.fetchall()

	query_2_progress = "SELECT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, airplane_id, GROUP_CONCAT(customer_email SEPARATOR ', ') as customers \
		FROM flight NATURAL LEFT OUTER JOIN (ticket NATURAL JOIN purchases) \
		WHERE airline_name = %s AND status = \'In-progress\' \
		GROUP BY airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, airplane_id\
		ORDER BY departure_time, arrival_time;"
	cursor.execute(query_2_progress, (airline_name))
	progress_flights = cursor.fetchall()

	query_2_delayed = "SELECT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, airplane_id, GROUP_CONCAT(customer_email SEPARATOR ', ') as customers \
		FROM flight NATURAL LEFT OUTER JOIN (ticket NATURAL JOIN purchases) \
		WHERE airline_name = %s AND status = \'Delayed\' \
		GROUP BY airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, airplane_id\
		ORDER BY departure_time, arrival_time;"
	cursor.execute(query_2_delayed, (airline_name))
	delayed_flights = cursor.fetchall()
	cursor.close()
	return render_template("airline_staff_change_flight_status.html", upcoming_flights=upcoming_flights, progress_flights=progress_flights, delayed_flights=delayed_flights, error=error)

# add airplane: for admin staff
@app.route("/home/airline_staff_add_airplane", methods=['GET', 'POST'])
def airline_staff_add_airplane():
	username = session['logname']
	is_admin = check_permission(username, 'admin')
	# if not admin, then refuse to do this
	if (not is_admin):
		flash("Unauthorized Operation: You do not have Admin Permission!")
		return redirect(url_for("home"))

	# get the airline name that the staff belongs to
	cursor = conn.cursor()
	query_1 = "SELECT airline_name FROM airline_staff WHERE username = %s;"
	cursor.execute(query_1, (username))
	airline_name_data = cursor.fetchone()
	airline_name = airline_name_data["airline_name"]

	error = None
	# receive the inputs of creating a new plane
	if request.method == "POST":
		airplane_id = request.form["airplane_id"]
		seats = request.form["seats"]

		# first check if the airplane id already exists
		q1 = "SELECT * FROM airplane WHERE airplane_id = %s;"
		cursor.execute(q1, (airplane_id))
		d1 = cursor.fetchone()
		if (d1):
			flash("This airplane already exists!")
			error = True
		
		# then check if the airplane id is valid number
		if (int(airplane_id) < 0):
			flash("The Airplane ID MUST be Non-Negative numbers!")
			error = True

		# then check if the number of seats is valid number
		if (int(seats) < 0):
			flash("The Number of Seats MUST be Non-Negative numbers!")
			error = True

		# if there is no detected error, then add the new plane to database
		if (not error):
			ins = "INSERT INTO airplane VALUES(%s, %s, %s);"
			cursor.execute(ins, (airline_name, airplane_id, seats))
			conn.commit()
			flash("You have added the Airplane into the System!")
	
	# display all the existing planes in the airline that the staff belongs to
	query_2 = "SELECT * FROM airplane WHERE airline_name = %s ORDER BY airplane_id;"
	cursor.execute(query_2, (airline_name))
	airplane = cursor.fetchall()
	cursor.close()
	return render_template("airline_staff_add_airplane.html", airline_name=airline_name, airplane=airplane, error=error)

# add airport: for admin staff
@app.route("/home/airline_staff_add_airport", methods=['GET', 'POST'])
def airline_staff_add_airport():
	username = session['logname']
	is_admin = check_permission(username, 'admin')
	# if not admin, then refuse to do this
	if (not is_admin):
		flash("Unauthorized Operation: You do not have Admin Permission!")
		return redirect(url_for("home"))

	error = None
	cursor = conn.cursor()
	# receive the inputs of creating a new airport
	if request.method == "POST":
		airport_name = request.form["airport_name"]
		airport_city = request.form["airport_city"]

		# first check if the airport name already exists
		q1 = "SELECT * FROM airport WHERE airport_name = %s;"
		cursor.execute(q1, (airport_name))
		d1 = cursor.fetchone()
		if (d1):
			flash("This airport already exists!")
			error = True

		# if there is no detected error, then add the new airport to database
		if (not error):
			ins = "INSERT INTO airport VALUES(%s, %s);"
			cursor.execute(ins, (airport_name, airport_city))
			conn.commit()
			flash("You have added the Airport into the System!")
	
	# display all the existing planes in the airline that the staff belongs to
	query_1 = "SELECT * FROM airport ORDER BY airport_name;"
	cursor.execute(query_1)
	airport = cursor.fetchall()
	cursor.close()
	return render_template("airline_staff_add_airport.html", airport=airport, error=error)

# view booking agent
@app.route("/home/airline_staff_view_booking_agent", methods=['GET', 'POST'])
def airline_staff_view_booking_agent():
	# get the airline name that the staff belongs to
	username = session['logname']
	cursor = conn.cursor()
	query_1 = "SELECT airline_name FROM airline_staff WHERE username = %s;"
	cursor.execute(query_1, (username))
	airline_name_data = cursor.fetchone()
	airline_name = airline_name_data["airline_name"]

	period = "YEAR"
	if request.method == "POST":
		period = request.form["period"]
	
	# display the top 5 booking agents in the recent year, and in the recent month
	# by the number of tickets sold and by the amout of commission received
	query_2 = "SELECT b.email AS booking_agent_email, p.booking_agent_id AS booking_agent_id, COUNT(t.ticket_id) AS number_of_tickets \
		FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p NATURAL JOIN booking_agent b \
		WHERE airline_name = %s AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 {}) AND NOW()) \
		GROUP BY booking_agent_email ORDER BY number_of_tickets DESC LIMIT 5;".format(period)
	cursor.execute(query_2, (airline_name))
	top_5_agent_ticket = cursor.fetchall()
	query_3 = "SELECT b.email AS booking_agent_email, p.booking_agent_id AS booking_agent_id, SUM(f.price)*0.1 AS commission_earned \
		FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p NATURAL JOIN booking_agent b \
		WHERE airline_name = %s AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 {}) AND NOW()) \
		GROUP BY booking_agent_email ORDER BY commission_earned DESC LIMIT 5;".format(period)
	cursor.execute(query_3, (airline_name))
	top_5_agent_money = cursor.fetchall()

	cursor.close()
	return render_template("airline_staff_view_booking_agent.html", top_5_agent_ticket=top_5_agent_ticket, top_5_agent_money=top_5_agent_money, period=period)

# view frequent customers, and customers' purchased tickets
@app.route("/home/airline_staff_view_frequent_customer", methods=['GET','POST'])
def airline_staff_view_frequent_customer():
	# get the airline name that the staff belongs to
	username = session['logname']
	cursor = conn.cursor()
	query_1 = "SELECT airline_name FROM airline_staff WHERE username = %s;"
	cursor.execute(query_1, (username))
	airline_name_data = cursor.fetchone()
	airline_name = airline_name_data["airline_name"]

	# display the top 5 customers in the recent year
	# by the number of tickets purchased and by the amout of money spent
	query_2 = "SELECT p.customer_email AS customer_email, COUNT(t.ticket_id) AS number_of_tickets \
		FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p \
		WHERE airline_name = %s AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 YEAR) AND NOW()) \
		GROUP BY customer_email ORDER BY number_of_tickets DESC LIMIT 5;"
	cursor.execute(query_2, (airline_name))
	top_5_customer_num_ticket = cursor.fetchall()
	query_3 = "SELECT p.customer_email AS customer_email, SUM(f.price) AS money_spent \
		FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p \
		WHERE airline_name = %s AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 YEAR) AND NOW()) \
		GROUP BY customer_email ORDER BY money_spent DESC LIMIT 5;"
	cursor.execute(query_3, (airline_name))
	top_5_customer_money = cursor.fetchall()
	# select all the customers who have purchased a ticket, for the staff to select and view all tickets
	query_4 = "SELECT DISTINCT customer_email FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE airline_name = %s ORDER BY customer_email;"
	cursor.execute(query_4, (airline_name))
	customers = cursor.fetchall()

	info = None
	customer_email = None
	# receive the inputs of what customer the staff wants to check
	if request.method == "POST":
		selected_customer_idx = request.form["selected_customer"]
		selected_customer_dict = customers[int(selected_customer_idx)]
		customer_email = selected_customer_dict["customer_email"]
		# get all the purchased tickets of that customer
		q1 = "SELECT purchase_date, flight_num, airplane_id, departure_airport, arrival_airport, departure_time, arrival_time, price, status \
			FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE customer_email = %s ORDER BY purchase_date;"
		cursor.execute(q1, (customer_email))
		info = cursor.fetchall()

	cursor.close()
	return render_template("airline_staff_view_frequent_customer.html", top_5_customer_num_ticket=top_5_customer_num_ticket, top_5_customer_money=top_5_customer_money, customers=customers, info=info, customer_email=customer_email)

# view reports and bar chart
@app.route("/home/airline_staff_view_reports", methods=['GET','POST'])
def airline_staff_view_reports():
	# get the airline name that the staff belongs to
	username = session['logname']
	cursor = conn.cursor()
	query_1 = "SELECT airline_name FROM airline_staff WHERE username = %s;"
	cursor.execute(query_1, (username))
	airline_name_data = cursor.fetchone()
	airline_name = airline_name_data["airline_name"]

	# period is for sql query, period_string is for front-end display
	period = "MONTH"
	period_string = "for the Recent Month"
	period_statement = "(p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 {}) AND NOW())".format(period)
	if request.method == "POST":
		period = request.form["period_select"]
		range_start = request.form["range_start"]
		range_end = request.form["range_end"]
		
		# if the period is recent month or recent year
		if (period == "MONTH" or period == "YEAR"):
			if period == "YEAR":
				period_string = "for the Recent Year"
			period_statement = "(p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 {}) AND NOW())".format(period)
		# if the period is a customized time range
		else:
			start_string = range_start if range_start else "Today"
			end_string = range_end if range_end else "Today"
			period_string = "from {} up to {}".format(start_string, end_string)
			start_period = "\'" + range_start + "\'" if range_start else "NOW()"
			end_period = "\'" + range_end + "\'" if range_end else "NOW()"
			period_statement = "(p.purchase_date BETWEEN {} AND {})".format(start_period, end_period)
	
	empty = None
	plot_url_1 = None
	plot_url_2 = None
	# display the monthly ticket selling statistics based on the given period (customized range, or last year, or last month)
	# by the number of tickets sold and by the amout of profit earned
	query_2 = "SELECT YEAR(p.purchase_date) AS purchase_year, MONTH(p.purchase_date) AS purchase_month, COUNT(t.ticket_id) AS number_ticket_sold \
		FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p \
		WHERE f.airline_name = %s AND {} \
		GROUP BY purchase_year, purchase_month \
		ORDER BY purchase_year, purchase_month;".format(period_statement)
	cursor.execute(query_2, (airline_name))
	num_ticket_sold = cursor.fetchall()
	query_3 = "SELECT YEAR(p.purchase_date) AS purchase_year, MONTH(p.purchase_date) AS purchase_month, SUM(f.price) AS profit_earned \
		FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p \
		WHERE f.airline_name = %s AND {} \
		GROUP BY purchase_year, purchase_month \
		ORDER BY purchase_year, purchase_month;".format(period_statement)
	cursor.execute(query_3, (airline_name))
	profit_earned = cursor.fetchall()
	cursor.close()

	# process the fetched dictionary
	if (not num_ticket_sold) and (not profit_earned):
		flash("The Period You Selected Has NO Data, NO Bar Chart Available!")
		empty = True
	else:
		year_months = []
		monthly_num_ticket_sold = []
		for data in num_ticket_sold:
			cur_year_month = str(data["purchase_year"]) + "-" + str(data["purchase_month"])
			year_months.append(cur_year_month)
			monthly_num_ticket_sold.append(data["number_ticket_sold"])
			x_pos = np.arange(len(year_months))
		plot_url_1 = gen_bar_chart(x_pos, year_months, monthly_num_ticket_sold, "Year and Month", "Number of Tickets Sold")
	
		year_months_2 = []
		monthly_ticket_profit = []
		for data in profit_earned:
			cur_year_month = str(data["purchase_year"]) + "-" + str(data["purchase_month"])
			year_months_2.append(cur_year_month)
			monthly_ticket_profit.append(data["profit_earned"])
			x_pos_2 = np.arange(len(year_months_2))
		plot_url_2 = gen_bar_chart(x_pos_2, year_months_2, monthly_ticket_profit, "Year and Month", "Ticket Profits")

	return render_template("airline_staff_view_reports.html", period_string=period_string, plot_url_1=plot_url_1, plot_url_2=plot_url_2, empty=empty)

# compare the revenues earned
@app.route("/home/airline_staff_compare_revenue", methods=['GET','POST'])
def airline_staff_compare_revenue():
	# get the airline name that the staff belongs to
	username = session['logname']
	cursor = conn.cursor()
	query_1 = "SELECT airline_name FROM airline_staff WHERE username = %s;"
	cursor.execute(query_1, (username))
	airline_name_data = cursor.fetchone()
	airline_name = airline_name_data["airline_name"]

	period = "YEAR"
	if request.method == "POST":
		period = request.form["period"]

	# get: total amount of revenue earned from direct sales (when customer bought tickets without using a booking agent) 
	# and total amount of revenue earned from indirect sales (when customer bought tickets using booking agents)
	query_2 = "SELECT SUM(f.price) AS revenue FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p \
		WHERE airline_name = %s AND p.booking_agent_id IS NULL \
		AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 {}) AND NOW());".format(period)
	cursor.execute(query_2, (airline_name))
	direct_revenue_info = cursor.fetchone()
	
	query_3 = "SELECT SUM(f.price) AS revenue FROM flight f NATURAL JOIN ticket t NATURAL JOIN purchases p \
		WHERE airline_name = %s AND p.booking_agent_id IS NOT NULL \
		AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 {}) AND NOW());".format(period)
	cursor.execute(query_3, (airline_name))
	indirect_revenue_info = cursor.fetchone()
	cursor.close()

	# edge case: direct revenue or/and indirect revenue is/are zero
	if (not direct_revenue_info):
		direct_revenue = 0
	else:
		direct_revenue = int(direct_revenue_info["revenue"])
	if (not indirect_revenue_info):
		indirect_revenue = 0
	else:
		indirect_revenue = int(indirect_revenue_info["revenue"])

	# generate the pie chart
	pie_url = None
	empty = True
	pie_labels = ["Direct Revenue: " + str(direct_revenue), "Indirect Revenue: " + str(indirect_revenue)]
	if direct_revenue == 0 and indirect_revenue == 0:
		flash("The Period You Selected Has NO Data, NO Pie Chart Available!")
	else:
		percentage_direct_rev = int(direct_revenue*100 / (direct_revenue+indirect_revenue))
		pie_values = [percentage_direct_rev, 100-percentage_direct_rev]
		pie_url = gen_pie_chart(pie_labels, pie_values)
		empty = None
	return render_template("airline_staff_compare_revenue.html", period=period, pie_url=pie_url, empty=empty)

# view top 3 destinations
@app.route("/home/airline_staff_view_top_destination", methods=['GET','POST'])
def airline_staff_view_top_destination():
	# get the airline name that the staff belongs to
	username = session['logname']
	cursor = conn.cursor()
	query_1 = "SELECT airline_name FROM airline_staff WHERE username = %s;"
	cursor.execute(query_1, (username))
	airline_name_data = cursor.fetchone()
	airline_name = airline_name_data["airline_name"]

	period = "1 YEAR"
	if request.method == "POST":
		period = request.form["period"]
	
	# search for the top 3 destinations according to the purchased tickets that depart from that airport
	query_2 = "SELECT a.airport_city AS city_name, a.airport_name AS airport_name, COUNT(t.ticket_id) AS num_ticket \
		FROM (flight f NATURAL JOIN ticket t NATURAL JOIN purchases p) JOIN airport a ON (f.departure_airport = a.airport_name) \
		WHERE airline_name = %s AND (p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL {}) AND NOW()) \
		GROUP BY city_name, airport_name ORDER BY num_ticket DESC LIMIT 3;".format(period)
	cursor.execute(query_2, (airline_name))
	top_3_destination = cursor.fetchall()
	cursor.close()
	return render_template("airline_staff_view_top_destination.html", top_3_destination=top_3_destination, period=period)

# grant new permissions: for admin staff
@app.route("/home/airline_staff_grant_new_permission", methods=['GET','POST'])
def airline_staff_grant_new_permission():
	username = session['logname']
	is_admin = check_permission(username, 'admin')
	# if not admin, then refuse to do this
	if (not is_admin):
		flash("Unauthorized Operation: You do not have Admin Permission!")
		return redirect(url_for("home"))
	
	# get the airline name that the staff belongs to
	cursor = conn.cursor()
	query_1 = "SELECT airline_name FROM airline_staff WHERE username = %s;"
	cursor.execute(query_1, (username))
	airline_name_data = cursor.fetchone()
	airline_name = airline_name_data["airline_name"]

	# select all the airline staff in this airline, so that the admin can choose
	query_2 = "SELECT DISTINCT username FROM airline_staff WHERE airline_name = %s ORDER BY username;"
	cursor.execute(query_2, (airline_name))
	staff_lst = cursor.fetchall()

	error = None
	# receive the inputs of updating a staff's permission
	if request.method == "POST":
		selected_staff_idx = request.form["selected_staff"]
		selected_staff_dict = staff_lst[int(selected_staff_idx)]
		staff_username = selected_staff_dict["username"]
		permission = request.form["permission"]
		op = request.form["op"]

		# operation 1: adding permission
		if op == "add":
			# first check if the selected staff already has such permission
			q1 = "SELECT * FROM permission p NATURAL JOIN airline_staff a \
				WHERE a.username = %s AND a.airline_name = %s AND p.permission_type = %s;"
			cursor.execute(q1, (staff_username, airline_name, permission))
			d1 = cursor.fetchone()
			if d1:
				flash("The Staff {} already has {} Permission!".format(staff_username, permission))
				error = True
			# if there is no error, then grant the staff the permission
			else:
				ins = "INSERT INTO permission VALUES (%s, %s);"
				cursor.execute(ins, (staff_username, permission))
				conn.commit()
				flash("You have Added {} Permission for Staff {}!".format(permission, staff_username))

		# operation 2: deleting permission
		elif op == "del":
			# first check if the selected staff has such a permission
			q1 = "SELECT * FROM permission p NATURAL JOIN airline_staff a \
				WHERE a.username = %s AND a.airline_name = %s AND p.permission_type = %s;"
			cursor.execute(q1, (staff_username, airline_name, permission))
			d1 = cursor.fetchone()
			if (not d1):
				flash("The Staff {} DOES NOT have {} Permission, UNABLE to Delete Permission!".format(staff_username, permission))
				error = True
			# then check if this is the last admin to delete: if so, reject the deletion
			if permission == "admin":
				q2 = "SELECT COUNT(*) AS admin_count FROM permission p NATURAL JOIN airline_staff a \
					WHERE a.airline_name = %s AND p.permission_type = %s;"
				cursor.execute(q2, (airline_name, permission))
				d2 = cursor.fetchone()
				if d2["admin_count"] == 1:
					q3 = "SELECT * FROM permission p NATURAL JOIN airline_staff a \
						WHERE a.airline_name = %s AND a.username = %s AND p.permission_type = %s;"
					cursor.execute(q3, (airline_name, staff_username, permission))
					d3 = cursor.fetchone()
					if d3:
						flash("The Staff {} is the only ONE Admin in this Airline! UNABLE to Delete!".format(staff_username))
						error = True
			# then delete the permission from the staff
			if (not error):
				delete = "DELETE FROM permission WHERE username = %s AND permission_type = %s;"
				cursor.execute(delete, (staff_username, permission))
				conn.commit()
				flash("You have Deleted {} Permission from Staff {}!".format(permission, staff_username))

	# get all the admin and operator staff in the airline
	query_3_admin = "SELECT a.username AS staff_username, a.first_name AS staff_first, a.last_name AS staff_last \
		FROM airline_staff a NATURAL JOIN permission p \
		WHERE a.airline_name = %s AND p.permission_type = \'admin\';"
	cursor.execute(query_3_admin, (airline_name))
	admin_staff = cursor.fetchall()

	query_3_operator = "SELECT a.username AS staff_username, a.first_name AS staff_first, a.last_name AS staff_last \
		FROM airline_staff a NATURAL JOIN permission p \
		WHERE a.airline_name = %s AND p.permission_type = \'operator\';"
	cursor.execute(query_3_operator, (airline_name))
	operator_staff = cursor.fetchall()
	cursor.close()

	return render_template("airline_staff_grant_new_permission.html", staff_lst=staff_lst, admin_staff=admin_staff, operator_staff=operator_staff, error=error)

# add booking agents: for admin staff
@app.route("/home/airline_staff_add_booking_agent", methods=['GET','POST'])
def airline_staff_add_booking_agent():
	username = session['logname']
	is_admin = check_permission(username, 'admin')
	# if not admin, then refuse to do this
	if (not is_admin):
		flash("Unauthorized Operation: You do not have Admin Permission!")
		return redirect(url_for("home"))
	
	# get the airline name that the staff belongs to
	cursor = conn.cursor()
	query_1 = "SELECT airline_name FROM airline_staff WHERE username = %s;"
	cursor.execute(query_1, (username))
	airline_name_data = cursor.fetchone()
	airline_name = airline_name_data["airline_name"]

	# select all the booking agents in the system, for further making choices
	query_2 = "SELECT DISTINCT email FROM booking_agent ORDER BY email;"
	cursor.execute(query_2)
	booking_agent_lst = cursor.fetchall()

	error = None
	# receive the inputs of updating a booking agent to work for this airline
	if request.method == "POST":
		selected_agent_idx = request.form["selected_agent"]
		selected_agent_dict = booking_agent_lst[int(selected_agent_idx)]
		booking_agent_email = selected_agent_dict["email"]
		op = request.form["op"]

		# operation 1: adding the booking agent to work for this airline
		if op == "add":
			# first check if the current booking agent already works for the airline
			q1 = "SELECT * FROM booking_agent b NATURAL JOIN booking_agent_work_for w \
				WHERE b.email = %s AND w.airline_name = %s;"
			cursor.execute(q1, (booking_agent_email, airline_name))
			d1 = cursor.fetchone()
			if d1:
				flash("The Booking Agent {} already works for Your Airline!".format(booking_agent_email))
				error = True
			# if there is no error, then add the booking agent to work for the airline
			else:
				ins = "INSERT INTO booking_agent_work_for VALUES (%s, %s);"
				cursor.execute(ins, (booking_agent_email, airline_name))
				conn.commit()
				flash("You have Added Booking Agent {} to work for Your Airline!".format(booking_agent_email))

		# operation 2: remove this booking agent from working for this airline
		elif op == "del":
			# first check if the current booking agent is working for the airline
			q1 = "SELECT * FROM booking_agent b NATURAL JOIN booking_agent_work_for w \
				WHERE b.email = %s AND w.airline_name = %s;"
			cursor.execute(q1, (booking_agent_email, airline_name))
			d1 = cursor.fetchone()
			if (not d1):
				flash("The Booking Agent {} DOES NOT work for Your Airline! UNABLE to Delete!".format(booking_agent_email))
				error = True
			# if there is no error, then delete the booking agent from working for this airline
			else:
				delete = "DELETE FROM booking_agent_work_for WHERE email = %s AND airline_name = %s;"
				cursor.execute(delete, (booking_agent_email, airline_name))
				conn.commit()
				flash("You have Deleted {} from working for Your Airline!".format(booking_agent_email))

	# get all the booking agents currently working for this airline and display them on the webpage
	query_3 = "SELECT b.email AS agent_email, b.booking_agent_id AS agent_id \
		FROM booking_agent b NATURAL JOIN booking_agent_work_for w \
		WHERE w.airline_name = %s;"
	cursor.execute(query_3, (airline_name))
	work_agent = cursor.fetchall()
	cursor.close()

	return render_template("airline_staff_add_booking_agent.html", booking_agent_lst=booking_agent_lst, work_agent=work_agent, error=error)


### Logout Operation ###
@app.route('/logout')
def logout():
	session.pop('logname')
	session.pop('usertype')
	return redirect('/')
		
app.secret_key = 'some key that you will never guess'

############################
# run the app
############################
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
