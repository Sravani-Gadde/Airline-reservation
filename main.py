from bson import ObjectId
from flask import Flask,request,render_template,redirect,session
from pyexpat.errors import messages
import datetime
app=Flask(__name__)
import pymongo
import os
App=os.path.dirname(os.path.abspath(__file__))
profiles=App+"/static/profiles"
myclient=pymongo.MongoClient("mongodb://localhost:27017")
mydatabase=myclient["airline"]
locations_collection=mydatabase["locations"]
airports_collection=mydatabase["airports"]
airlines_collection=mydatabase["airlines"]
airplanes_collection=mydatabase["airplanes"]
schedules_collection=mydatabase["schedules"]
boarding_pass_collection=mydatabase["boarding_pass"]
bookings_collection=mydatabase["bookings"]
payments_collection=mydatabase["payments"]
customers_collection=mydatabase["customers"]
app.secret_key="sravani"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin_login")
def admin():
    return render_template("admin_login.html")

@app.route("/admin_login_action", methods=['post'])
def admin_login_action():
    username=request.form.get("username")
    password = request.form.get("password")
    if username=="admin" and password == "admin":
        session["role"]="admin"
        return redirect("/admin_home")
    else:
        return render_template("message.html", message="Invalid Login")

@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")

@app.route("/customer_login")
def customer_login():
    return render_template("customer_login.html")

@app.route("/customer_login_action",methods=['post'])
def customer_login_action():
    email=request.form.get("email")
    password=request.form.get("password")
    query={"email":email,"password":password}
    count=customers_collection.count_documents(query)
    if count>0:
        customer=customers_collection.find_one(query)
        session['customer_id']=str(customer['_id'])
        session['role']="customer"
        return redirect("/customer_home")
    return render_template("message.html",message="invalid details")

@app.route("/customer_registration")
def customer_registration():
    return render_template("customer_registration.html")

@app.route("/customer_registration_action",methods=['post'])
def customer_registration_action():
    name=request.form.get("name")
    first_name=request.form.get("first_name")
    last_name=request.form.get("last_name")
    email=request.form.get("email")
    phone=request.form.get("phone")
    password=request.form.get("password")
    address=request.form.get("address")
    state=request.form.get("state")
    city=request.form.get("city")
    zipcode=request.form.get("zipcode")
    query={"email":email}
    count=customers_collection.count_documents(query)
    if count>0:
        return render_template("message.html",message="Duplicate Email Address")
    query={"phone":phone}
    count=customers_collection.count_documents(query)
    if count>0:
        return render_template("message.html",message="Duplicate Phone Number")
    query={"name":name,"first_name":first_name,"last_name":last_name,"email":email,"password":password,"address":address,"state":state,"city":city,"zipcode":zipcode}
    customers_collection.insert_one(query)
    return render_template("message.html",message="Customer Registration Successful")

@app.route("/customer_home")
def customer_home():
    return render_template("customer_home.html")

@app.route("/airline_login")
def airline_login():
    return render_template("airline_login.html")

@app.route("/airline_login_action",methods=['post'])
def airline_login_action():
    email=request.form.get("email")
    password=request.form.get("password")
    query={"email":email,"password":password}
    count=airlines_collection.count_documents(query)
    if count>0:
        airline=airlines_collection.find_one(query)
        session['airline_id']=str(airline['_id'])
        session['role']="airline"
        return redirect("/airline_home")
    return render_template("message.html",message="invalid details")

@app.route("/airline_registration")
def airline_registration():
    query = {}
    airlines = airlines_collection.find(query)
    airlines = list(airlines)
    message=request.args.get("message")
    return render_template("airline_registration.html",airlines=airlines,message=message)

@app.route("/airline_registration_action",methods=['post'])
def airline_registration_action():
    airline=request.form.get("airline")
    email=request.form.get("email")
    phone=request.form.get("phone")
    password=request.form.get("password")
    established_year=request.form.get("established_year")
    address=request.form.get("address")
    about=request.form.get("about")
    query = {"email": email}
    count = customers_collection.count_documents(query)
    if count > 0:
        return redirect("/airline_registration?message=Duplicate Email Number")
    query = {"phone": phone}
    count = customers_collection.count_documents(query)
    if count > 0:
        return redirect("/airline_registration?message=Duplicate Phone Number")
    query={"airline":airline,"email":email,"phone":phone,"password":password,"established_year":established_year,"address":address,"about":about}
    airlines_collection.insert_one(query)
    return redirect("/airline_registration?message=Airline Added Successfully")

@app.route("/airline_home")
def airline_home():
    return render_template("airline_home.html")

@app.route("/logout")
def logout():
    return redirect("/")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/pricing")
def pricing():
    return render_template("pricing.html")

@app.route("/locations")
def locations():
    query={}
    locations=locations_collection.find(query)
    locations=list(locations)
    message=request.args.get("message")
    return render_template("locations.html",locations=locations,message=message)

@app.route("/locations_action",methods=['post'])
def locations_action():
    location=request.form.get("location")
    query={"location":location}
    count=locations_collection.count_documents(query)
    if count>0:
        return redirect("/locations?message=duplicate location")
    query = {"location": location}
    locations_collection.insert_one(query)
    return redirect("/locations?message=location added successfully")

@app.route("/airports")
def airports():
    query = {}
    locations = locations_collection.find(query)
    locations = list(locations)
    query={}
    airports=airports_collection.find(query)
    airports=list(airports)
    message=request.args.get("message")
    return render_template("airports.html",locations=locations,airports=airports,message=message,get_airports_by_location_id=get_airports_by_location_id)

@app.route("/airport_action",methods=['post'])
def airport_action():
    airport=request.form.get("airport")
    airport_type=request.form.get("airport_type")
    location_id=request.form.get("location_id")
    query={"airport":airport}
    count=airports_collection.count_documents(query)
    if count>0:
        return redirect("/airports?message=duplicate airport name")
    query={"airport":airport,"airport_type":airport_type,"location_id":ObjectId(location_id)}
    airports_collection.insert_one(query)
    return redirect("/airports?message=airport added successfully")

def get_airports_by_location_id(location_id):
    query={"location_id":ObjectId(location_id)}
    airports=airports_collection.find(query)
    airports=list(airports)
    return airports

@app.route("/add_airplane")
def add_airplane():
    query = {}
    airplanes = airplanes_collection.find(query)
    airplanes = list(airplanes)
    return render_template("add_airplane.html",airplanes=airplanes,get_airline_by_airline_id=get_airline_by_airline_id)

@app.route("/add_airplane_action",methods=['post'])
def add_airplane_action():
    airplane_name=request.form.get("airplane_name")
    airplane_number=request.form.get("airplane_number")
    description=request.form.get("description")
    economy_class_available_seats=request.form.get("economy_class_available_seats")
    business_class_available_seats=request.form.get("business_class_available_seats")
    first_class_available_seats=request.form.get("first_class_available_seats")
    airline_id= session['airline_id']
    image=request.files.get("image")
    path=profiles+"/"+image.filename
    image.save(path)
    query={"airplane_name":airplane_name,"airplane_number":airplane_number,"image":image.filename,"description":description,"economy_class_available_seats":economy_class_available_seats,"business_class_available_seats":business_class_available_seats,"first_class_available_seats":first_class_available_seats,"airline_id":ObjectId(airline_id)}
    airplanes_collection.insert(query)
    return render_template("apmessage.html",message="airplane added successfully")

def get_airline_by_airline_id(airline_id):
    query={"_id":airline_id}
    airline=airlines_collection.find_one(query)
    return airline

@app.route("/add_schedule")
def add_schedule():
    airplane_id=request.args.get("airplane_id")
    airports=airports_collection.find({})
    airports=list(airports)
    message=request.args.get("message")
    today = datetime.datetime.now()
    today = today.strftime("%Y-%m-%dT%H:%M")
    return render_template("add_schedule.html",airplane_id=airplane_id,airports=airports,message=message,today=today)

@app.route("/schedules_action",methods=['post'])
def schedules_action():
    airplane_id=request.form.get("airplane_id")
    arrival_date_time=request.form.get("arrival_date_time")
    departure_date_time=request.form.get("departure_date_time")
    business_class_price=request.form.get("business_class_price")
    economic_class_price=request.form.get("economic_class_price")
    first_class_price=request.form.get("first_class_price")
    source_airport_id=request.form.get("source_airport_id")
    destination_airport_id=request.form.get("destination_airport_id")
    departure_date_time=datetime.datetime.strptime(departure_date_time,"%Y-%m-%dT%H:%M")
    arrival_date_time = datetime.datetime.strptime(arrival_date_time, "%Y-%m-%dT%H:%M")
    today=datetime.datetime.now()
    if departure_date_time<today:
        return redirect("/add_schedule?message=you can not add schedule for past dates")
    if arrival_date_time<departure_date_time:
        return redirect("/add_schedule?message=departure date should be greater than arrival date")
    duration=departure_date_time-arrival_date_time
    seconds=duration.seconds
    hours=int(seconds/3600)
    minutes=int(seconds%3600/60)
    if hours == 0:
        duration = str(minutes) + ' Minutes'
    else:
        if minutes == 0:
            duration = str(hours) + ' Hours'
        else:
            duration = str(hours) + ' Hours '+str(minutes)+ ' Minutes'
    departure_date=departure_date_time.strftime("%Y-%m-%d")
    departure_date=datetime.datetime.strptime(departure_date,"%Y-%m-%d")
    query={"arrival_date_time":arrival_date_time,"departure_date_time":departure_date_time,"business_class_price":business_class_price,"economic_class_price":economic_class_price,"first_class_price":first_class_price,"duration":str(duration),"source_airport_id":ObjectId(source_airport_id),"destination_airport_id":ObjectId(destination_airport_id),"airplane_id":ObjectId(airplane_id),"departure_date":departure_date}
    schedules_collection.insert(query)
    return render_template("apmessage.html",message="schedule added successfully")

@app.route("/view_schedule")
def view_schedule():
    airplane_id=request.args.get("airplane_id")
    today=datetime.datetime.now()
    query={"airplane_id":ObjectId(airplane_id),"departure_date_time":{"$gte":today}}
    print(query)
    future_schedules=schedules_collection.find(query)
    future_schedules=list(future_schedules)
    query = {"airplane_id": ObjectId(airplane_id), "departure_date_time": {"$lte": today}}
    past_schedules=schedules_collection.find(query)
    past_schedules=list(past_schedules)
    message=request.args.get("message")
    return render_template("view_schedule.html",message=message,future_schedules=future_schedules,past_schedules=past_schedules,get_source_airport_name_by_airport_id=get_source_airport_name_by_airport_id,get_airplane_name_by_airplane_name=get_airplane_name_by_airplane_name,get_destination_airport_name_by_airport_id=get_destination_airport_name_by_airport_id,len=len)

def get_source_airport_name_by_airport_id(airport_id):
    query={"_id":airport_id}
    airport= airports_collection.find_one(query)
    print(airport)
    return airport

def get_destination_airport_name_by_airport_id(airport_id):
    query={"_id":airport_id}
    airport= airports_collection.find_one(query)
    print(airport)
    return airport

def get_airplane_name_by_airplane_name(airplane_id):
    query={"_id":airplane_id}
    airplane=airplanes_collection.find_one(query)
    print(airplane)
    return airplane

def get_source_location_by_airport_id(location_id):
    query={"_id":location_id}
    location=locations_collection.find_one(query)
    print(location)
    return location

def get_destination_location_by_airport_id(location_id):
    query={"_id":location_id}
    location=locations_collection.find_one(query)
    print(location)
    return location

def get_seats_by_airplane_id(airplane_id):
    query={"_id":airplane_id}
    airplane=airplanes_collection.find_one(query)
    return airplane

@app.route("/search_flights")
def search_flights():
    locations=locations_collection.find({})
    locations=list(locations)
    source_location_id = request.args.get("source_location_id")
    destination_location_id = request.args.get("destination_location_id")
    date = request.args.get("date")
    print(destination_location_id)
    if source_location_id == None:
        source_location_id == ""
    if destination_location_id == None:
        destination_location_id = ""
    if date == None:
        date = ""
    if source_location_id == "" or destination_location_id == "" or date == "":
        query = {"abc":"abc"}
    else:
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
        print(date)
        query = {"location_id": ObjectId(source_location_id)}
        source_airports = airports_collection.find(query)
        source_airports = list(source_airports)
        query = {"location_id": ObjectId(destination_location_id)}
        destination_airports = airports_collection.find(query)
        destination_airports = list(destination_airports)
        source_airport_ids = []
        for source_airport in source_airports:
            source_airport_ids.append(source_airport['_id'])
        destination_airport_ids = []
        for destination_airport in destination_airports:
            destination_airport_ids.append(destination_airport['_id'])
        query = {"departure_date": date, "source_airport_id": {"$in": source_airport_ids},
                 "destination_airport_id": {"$in": destination_airport_ids}}
    print(query)
    schedules = schedules_collection.find(query)
    schedules = list(schedules)
    print(schedules)
    return render_template("search_flights.html",locations=locations,schedules=schedules,get_source_airport_name_by_airport_id=get_source_airport_name_by_airport_id,get_destination_airport_name_by_airport_id=get_destination_airport_name_by_airport_id,get_airplane_name_by_airplane_name=get_airplane_name_by_airplane_name,get_source_location_by_airport_id=get_source_location_by_airport_id,get_destination_location_by_airport_id=get_destination_location_by_airport_id,get_seats_by_airplane_id=get_seats_by_airplane_id)

@app.route("/book_ticket")
def book_ticket():
    schedule_id=request.args.get("schedule_id")
    class_type=request.args.get("class_type")
    query={"_id":ObjectId(schedule_id)}
    schedule=schedules_collection.find_one(query)
    total_seats=request.args.get("total_seats")
    total_seats=int(total_seats)
    return render_template("book_ticket.html",schedule_id=schedule_id,schedule=schedule,class_type=class_type,get_source_airport_name_by_airport_id=get_source_airport_name_by_airport_id,get_destination_airport_name_by_airport_id=get_destination_airport_name_by_airport_id,get_airplane_name_by_airplane_name=get_airplane_name_by_airplane_name,get_source_location_by_airport_id=get_source_location_by_airport_id,get_destination_location_by_airport_id=get_destination_location_by_airport_id,get_seats_by_airplane_id=get_seats_by_airplane_id,total_seats=total_seats)

@app.route("/book_tickets2")
def book_tickets2():
    schedule_id = request.args.get("schedule_id")
    class_type = request.args.get("class_type")
    total_seats = request.args.get("total_seats")
    return render_template("book_tickets2.html",schedule_id=schedule_id,class_type=class_type,total_seats=total_seats)

app.run(debug=True)