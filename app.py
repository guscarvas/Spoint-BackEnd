from datetime import datetime

from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin

import os
import sqlite3


app = Flask(__name__)
app.config['SECRET_KEY'] = 'sssdhgclshfsh;shd;jshjhsjhjhsjldchljk'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///website.db'

#Initialize database
db = SQLAlchemy(app)

#Initialize marshmallow for jsonnifying queries
ma = Marshmallow(app)

#Initialize Bcrypt for password encryption
bcrypt = Bcrypt(app)

#Initialize CORS for supporting Cross-origin resource sharing, and receive requests from front end
cors = CORS(app, resources={r"/*": {"origins": "*"}}, headers="Content-Type", methods=['GET', 'HEAD', 'POST', 'OPTIONS', 'PUT', 'PATCH', 'DELETE'])

#Importing all models and Marshmallow Schemas
from models import User, Performer, Customer, UserSchema, PerformerSchema, CustomerSchema, Job, JobSchema, Message, MessageSchema, Transaction, TransactionSchema, Report, ReportSchema


#creating database
db.create_all()
db.session.commit()


@app.route('/', methods=['GET'])  # Root of your web platform
def home():
    return '<h1>Hello! Welcome to the Spoint BackEnd!</h1>'


#############
#### USERS

@app.route('/user/', methods=['POST'])
@cross_origin(allow_headers=['Content-Type'])
def users():

    email = request.json.get('email')
    user = User.query.filter_by(email=email).first()
    if user:
        return "This email is already registered"

    password_hash = bcrypt.generate_password_hash(request.json.get('password')).encode('utf-8')
    role = request.json.get('role')
    name = request.json.get('name')
    fiscal_code = request.json.get('fiscal_code')
    address = request.json.get('address')
    profile_pic_url = "ABC"

    if request.json.get('profile_pic_url'):
        profile_pic_url = request.json.get('profile_pic_url')

    newuser = User(email=email, password=password_hash, role=role)
    db.session.add(newuser)
    db.session.commit()

    if role == 'Performer':
        category = request.json.get('category')
        genre = "None"
        if request.json.get('genre'):
            genre = request.json.get('genre')
        cost_per_hour = request.json.get('cost_per_hour')
        birthday = request.json.get('birthday')
        birthday = datetime.strptime(birthday, '%d-%m-%Y')
        search_city = request.json.get('search_city')
        newperformer = Performer(email=email, user=newuser, name=name, category=category, genre=genre, birthday=birthday,
                                 cost_per_hour=cost_per_hour, fiscal_code=fiscal_code, address=address, search_city=search_city,
                                 profile_pic_url=profile_pic_url)
        db.session.add(newperformer)
        performer_schema = PerformerSchema()
        output = performer_schema.dump(newperformer).data
    if role == 'Customer':
        newcustomer = Customer(email=email, user=newuser, name=name,
                               fiscal_code=fiscal_code, address=address, profile_pic_url=profile_pic_url)
        db.session.add(newcustomer)
        customer_schema = CustomerSchema()
        output = customer_schema.dump(newcustomer).data
    db.session.commit()
    return jsonify(output)

@app.route('/performer/', methods=['GET'])
def performers():
    performers_query = Performer.query.all()
    performer_schema = PerformerSchema(many=True)
    performers_output = performer_schema.dump(performers_query).data
    return jsonify(performers_output)

@app.route('/performer/<int:id_performer>', methods=['GET', 'PUT', 'DEL'])
def performer(id_performer):
    performer_query = Performer.query.get(id_performer)
    performer_schema = PerformerSchema()
    if request.method == 'GET':
        performer_output = performer_schema.dump(performer_query).data
    elif request.method == 'PUT':
        performer_query.update(request.json)
        performer_output = performer_schema.dump(performer_query).data
    elif request.method == 'DEL':
        performer_output = performer_schema.dump(performer_query).data
        performer_query.delete()
        db.session.commit()
    return jsonify(performer_output)

@app.route('/search/', methods=['POST'])
def search():
    performers_query = Performer.query
    if request.json.get('city'):
        city = request.json.get('city')
        performers_query = performers_query.filter_by(search_city=city)
    if request.json.get('category'):
        category = request.json.get('category')
        performers_query = performers_query.filter_by(category=category)
    if request.json.get('genre'):
        genre = request.json.get('genre')
        performers_query = performers_query.filter_by(genre=genre)
    if request.json.get('cost_minimum'):
        cost_minimum = request.json.get('cost_minimum')
        performers_query = performers_query.filter(Performer.cost_per_hour >= cost_minimum)
    if request.json.get('cost_max'):
        cost_max = request.json.get('cost_max')
        performers_query = performers_query.filter(Performer.cost_per_hour <= cost_max)

    performer_schema = PerformerSchema(many=True)
    performers_output = performer_schema.dump(performers_query).data
    return jsonify({'performers': performers_output})



@app.route('/customer/', methods=['GET'])
def customers():
    customers_query = Customer.query.all()
    customer_schema = CustomerSchema(many=True)
    customers_output = customer_schema.dump(customers_query).data
    return jsonify(customers_output)


@app.route('/customer/<int:id_customer>', methods=['GET', 'PUT', 'DEL'])
def customer(id_customer):
    customer_query = Customer.query.get(id_customer)
    customer_schema = CustomerSchema()
    if request.method == 'GET':
        customer_output = customer_schema.dump(customer_query).data

    elif request.method == 'PUT':
        customer_query.update(request.json)
    elif request.method == 'DEL':
        customer_output = customer_schema.dump(customer_query).data
        customer_query.delete()
        db.session.commit()
    return jsonify(customer_output)


@app.route('/restartdb/', methods=['GET'])
def restart():
    User.query.delete()
    Performer.query.delete()
    Customer.query.delete()


@app.route('/login/', methods=['POST'])
@cross_origin(allow_headers=['Content-Type'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    user = User.query.filter_by(email=email).first()
    if user == None:
        return "Incorrect email"
    if bcrypt.check_password_hash(user.password, password):
        session["user_id"] = user.id
        session["role"] = user.role
        if user.performer:
            performer_schema = PerformerSchema()
            output = performer_schema.dump(user.performer).data
            user_jobs = Job.query.filter_by(performer=user.performer)
            job_schema = JobSchema(many=True)
            job_output = job_schema.dump(user_jobs).data
            for job in job_output:
                job['performer_name'] = user.performer.name
                job['performer_email'] = user.performer.email
                customer_query = Customer.query.get(job['customer'])
                job['customer_name'] = customer_query.name
                job['customer_email'] = customer_query.email

        else:
            customer_schema = CustomerSchema()
            output = customer_schema.dump(user.customer).data
            user_jobs = Job.query.filter_by(customer=user.customer)
            job_schema = JobSchema(many=True)
            job_output = job_schema.dump(user_jobs).data
            for job in job_output:
                job['customer_name'] = user.customer.name
                job['customer_email'] = user.customer.email
                performer_query = Performer.query.get(job['performer'])
                job['performer_name'] = performer_query.name
                job['performer_email'] = performer_query.email

        output['jobs'] = job_output
        return jsonify({'user': output})
    else:
        return "Log in failed"


@app.route('/job/', methods=["POST"])
@cross_origin(allow_headers=['Content-Type'])
def create_job():
    email = request.json.get('email')
    password = request.json.get('password')
    user = User.query.filter_by(email=email).first()
    if user == None:
        return "Incorrect email"

    if bcrypt.check_password_hash(user.password, password):
        if user.customer:
            customer_id = request.json.get('customer_id')
            customer_query = Customer.query.get(customer_id)
            performer_id = request.json.get('performer_id')
            performer_query = Performer.query.get(performer_id)

            title = request.json.get('title')
            start_time = request.json.get('start_time')
            start_time = datetime.strptime(start_time, '%Y-%m-%d,%H:%M')
            end_time = request.json.get('end_time')
            end_time = datetime.strptime(end_time, '%Y-%m-%d,%H:%M')

            address = request.json.get('address')
            price_per_hour = request.json.get('price_per_hour')


            addedjob = Job(customer=customer_query, performer=performer_query,
                           title=title, end_time=end_time,start_time=start_time, address=address, price_per_hour=price_per_hour)
            db.session.add(addedjob)
            db.session.commit()

            job_schema = JobSchema()
            output = job_schema.dump(addedjob).data
            return jsonify(output)


@app.route('/my_jobs/', methods=["POST"])
@cross_origin(allow_headers=['Content-Type'])
def list_jobs():

    email = request.json.get('email')
    password = request.json.get('password')
    user = User.query.filter_by(email=email).first()
    if user == None:
        return "Incorrect email"

    if bcrypt.check_password_hash(user.password, password):
        if user.performer:
            user_jobs = Job.query.filter_by(performer=user.performer)
            job_schema = JobSchema(many=True)
            job_output = job_schema.dump(user_jobs).data
        else:
            user_jobs = Job.query.filter_by(customer=user.customer)
            job_schema = JobSchema(many=True)
            job_output = job_schema.dump(user_jobs).data
    else:
        return "Invalid credentials"

    return jsonify({'your jobs are': job_output})

@app.route('/delete_job/', methods=["POST"])
@cross_origin(allow_headers=['Content-Type'])
def delete_job():
    id = request.json.get('id')
    job = Job.query.get(id)
    db.session.delete(job)
    db.session.commit()
    return "Job was deleted!"

@app.route('/update_job/', methods=["POST"])
@cross_origin(allow_headers=['Content-Type'])
def update_job():

    job_id = request.json.get('job_id')
    status = request.json.get('status')

    job_query = Job.query.get(job_id)
    job_query.status = status

    db.session.commit()
    return "Updated"

@app.route('/populate/', methods=['GET'])
def populate():
    x = [["giusto.aloia@gmail.com", "Giusto Aloia", "Singer", "acoustic", "Turin", "Via Volto San Luca 15",     "10020", 45, "https://spoint.s3-sa-east-1.amazonaws.com/photo-1460723237483-7a6dc9d0b212.jpeg"],
    ["paolo.selvaggio@gmail.com", "Paolo Selvaggio", "Singer", "pop", "Turin", "Via Giberti 101", "10080",     400, "https://spoint.s3-sa-east-1.amazonaws.com/photo-1463453091185-61582044d556.jpeg"],
    ["leontina.biancardi@gmail.com", "Leontina Biancardi", "Singer", "acoustic", "Turin", "Via Enrico Fermi 15",     "10027", 35, "https://spoint.s3-sa-east-1.amazonaws.com/photo-1474959783111-a0f551bdad25.jpeg"],
    ["giona.bellomo@gmail.com", "Giona Bellomo", "Singer", "acoustic", "Turin", "Via Adua 94", "10091", 30,     "https://spoint.s3-sa-east-1.amazonaws.com/photo-1492562080023-ab3db95bfbce.jpeg"],
    ["irma.pittaluga@gmail.com", "Irma Pittaluga",     "Stand-up Comedy",'', "Turin", "Via Volto San Luca 134", "10086", 100, "https://spoint.s3-sa-east-1.amazonaws.com/photo-1493666438817-866a91353ca9.jpeg"],
    ["susanna.farro@gmail.com", "Susanna Farro", "Singer", "rock", "Turin", "Via Giberti 25", "10080", 60,     "https://spoint.s3-sa-east-1.amazonaws.com/photo-1494790108377-be9c29b29330.jpeg"],
    ["pio.carnevale@gmail.com", "Pio Carnevale", "Singer", "acoustic", "Turin", "Via Volto San Luca 119", "10099",     39, "https://spoint.s3-sa-east-1.amazonaws.com/photo-1499996860823-5214fcc65f8f.jpeg"],
    ["floro.scordato@gmail.com", "Floro Scordato", "Singer", "jazz", "Turin", "Via del Pontiere 58", "10050",     70, "https://spoint.s3-sa-east-1.amazonaws.com/photo-1506794778202-cad84cf45f1d.jpeg"],
    ["sebastiana.airaldi@gmail.com", "Sebastiana Airaldi", "Singer", "rock", "Milan", "Via Nazario Sauro 140",     "20020", 20, "https://spoint.s3-sa-east-1.amazonaws.com/photo-1512310604669-443f26c35f52.jpeg"],
    ["andreina.sessa@gmail.com", "Andreina Sessa", "Singer", "rock", "Milan", "Via San Pietro Ad Aram 72",     "20080", 25, "https://spoint.s3-sa-east-1.amazonaws.com/photo-1524504388940-b1c1722653e1.jpeg"],
    ["orsola.natale@gmail.com", "Orsola Natale", "Singer", "pop", "Rome", "Via Longhena 75", "00047", 650,     "https://spoint.s3-sa-east-1.amazonaws.com/photo-1534751516642-a1af1ef26a56.jpeg"],
    ["giuseppina.padovano@gmail.com", "Giuseppina Padovano", "Stand-up Comedy", "pop", "Rome",     "Via Colonnello Galliano 5", "00020", 220,     "https://spoint.s3-sa-east-1.amazonaws.com/photo-1557555187-23d685287bc3.jpeg"],
    ["loretta.rocco@gmail.com", "Loretta Rocco", "Singer", "pop", "Rome", "Via Longhena 82", "00040", 120,     "https://spoint.s3-sa-east-1.amazonaws.com/photo-1593697821252-0c9137d9fc45.jpeg"]]

    for performer in x:
        password = '12345678'

        password_hash = bcrypt.generate_password_hash(password).encode('utf-8')
        newuser = User(email=performer[0], password=password_hash, role="Performer")

        db.session.add(newuser)
        db.session.commit()

        birthday = '20-02-1999'
        birthday = datetime.strptime(birthday, '%d-%m-%Y')

        newperformer = Performer(email=performer[0], user=newuser, name=performer[1], category=performer[2], genre=performer[3], birthday=birthday,
                                 cost_per_hour=performer[7], fiscal_code=performer[6], address=performer[5], search_city=performer[4], profile_pic_url=performer[8])

        db.session.add(newperformer)
        db.session.commit()

    password_hash = bcrypt.generate_password_hash(password).encode('utf-8')
    newuser = User(email='test@email.com', password=password_hash, role="Customer")

    db.session.add(newuser)
    db.session.commit()

    newcustomer = Customer(email='test@email.com', user=newuser, name='Professor',
                           fiscal_code="10129", address='Corso Duca degli Abruzzi, 24', profile_pic_url='https://scontent.fgru5-1.fna.fbcdn.net/v/t1.0-9/17309045_192522311236382_5190942424822553922_n.png?_nc_cat=109&ccb=3&_nc_sid=09cbfe&_nc_ohc=TYzPv6VGpxwAX9p0x4E&_nc_ht=scontent.fgru5-1.fna&oh=2157905807786214bfa4f02fa0bdf939&oe=605DBB98')

    db.session.add(newcustomer)
    db.session.commit()

    return "Everything populated"


if __name__ == '__main__':
    app.run()
