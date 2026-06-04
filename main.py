from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///hotel_reservation.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app, origins=os.environ.get('CORS_ORIGINS', '*').split(','))


class Hotel(db.Model):

    __tablename__ = 'hotel'

    hotel_id = db.Column(db.Integer, primary_key=True)

    hotel_name = db.Column(db.String(100))

    location = db.Column(db.String(100))

    phone = db.Column(db.String(15))



class Room(db.Model):

    __tablename__ = 'room'

    room_id = db.Column(db.Integer, primary_key=True)

    room_number = db.Column(db.Integer)

    room_type = db.Column(db.String(50))

    price = db.Column(db.Float)

    
    status = db.Column(db.String(20), default="Available")

    hotel_id = db.Column(
        db.Integer,
        db.ForeignKey('hotel.hotel_id')
    )


class Customer(db.Model):

    __tablename__ = 'customer'

    customer_id = db.Column(db.Integer, primary_key=True)

    customer_name = db.Column(db.String(100))

    phone = db.Column(db.String(15))

    email = db.Column(db.String(100))

    address = db.Column(db.String(200))



class Reservation(db.Model):

    __tablename__ = 'reservation'

    reservation_id = db.Column(db.Integer, primary_key=True)

    check_in_date = db.Column(db.Date)

    check_out_date = db.Column(db.Date)

    reservation_date = db.Column(db.Date)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey('customer.customer_id')
    )

    room_id = db.Column(
        db.Integer,
        db.ForeignKey('room.room_id')
    )



class Payment(db.Model):

    __tablename__ = 'payment'

    payment_id = db.Column(db.Integer, primary_key=True)

    amount = db.Column(db.Float)

    payment_date = db.Column(db.Date)

    payment_method = db.Column(db.String(50))

    reservation_id = db.Column(
        db.Integer,
        db.ForeignKey('reservation.reservation_id')
    )



@app.route('/')
def home():

    return render_template('index.html')



@app.route('/add_hotel', methods=['POST'])
def add_hotel():

    data = request.json

    hotel = Hotel(
        hotel_name=data['hotel_name'],
        location=data['location'],
        phone=data['phone']
    )

    db.session.add(hotel)
    db.session.commit()

    return jsonify({
        "message": "Hotel Added Successfully"
    })


@app.route('/add_customer', methods=['POST'])
def add_customer():

    data = request.json

    customer = Customer(
        customer_name=data['customer_name'],
        phone=data['phone'],
        email=data['email'],
        address=data['address']
    )

    db.session.add(customer)

    db.session.commit()

    return jsonify({
        "message": "Customer Added",
        "customer_id": customer.customer_id
    })

@app.route('/customers', methods=['GET'])
def get_customers():

    customers = Customer.query.all()

    result = []

    for c in customers:

        result.append({
            "customer_id": c.customer_id,
            "customer_name": c.customer_name,
            "phone": c.phone,
            "email": c.email,
            "address": c.address
        })

    return jsonify(result)



@app.route('/add_room', methods=['POST'])
def add_room():

    data = request.json

    room = Room(
        room_number=data['room_number'],
        room_type=data['room_type'],
        price=data['price'],
        status="Available",
        hotel_id=data['hotel_id']
    )

    db.session.add(room)
    db.session.commit()

    return jsonify({
        "message": "Room Added Successfully"
    })



@app.route('/rooms', methods=['GET'])
def get_rooms():

    rooms = Room.query.all()

    result = []

    for r in rooms:

        result.append({
            "room_id": r.room_id,
            "room_number": r.room_number,
            "room_type": r.room_type,
            "price": r.price,
            "status": r.status
        })

    return jsonify(result)



@app.route('/available_rooms', methods=['GET'])
def available_rooms():

    count = Room.query.filter_by(
        status="Available"
    ).count()

    return jsonify({
        "available_rooms": count
    })



@app.route('/available_rooms_details', methods=['GET'])
def available_rooms_details():

    rooms = Room.query.filter_by(
        status="Available"
    ).all()

    result = []

    for r in rooms:

        result.append({
            "room_id": r.room_id,
            "room_number": r.room_number,
            "room_type": r.room_type,
            "price": r.price,
            "status": r.status
        })

    return jsonify(result)



@app.route('/add_reservation', methods=['POST'])
def add_reservation():

    data = request.json

    check_in = datetime.strptime(
        data['check_in_date'],
        '%Y-%m-%d'
    ).date()

    check_out = datetime.strptime(
        data['check_out_date'],
        '%Y-%m-%d'
    ).date()

    today = datetime.today().date()

   

    if check_out <= check_in:

        return jsonify({
            "error": "Check-out date must be after check-in date"
        }), 400

   

    if check_in < today:

        return jsonify({
            "error": "Check-in date cannot be in the past"
        }), 400

    

    room = Room.query.get(data['room_id'])

    if not room:

        return jsonify({
            "error": "Room not found"
        }), 404

 

    if room.status != "Available":

        return jsonify({
            "error": "Room is not available"
        }), 400

    

    existing = Reservation.query.filter(
        Reservation.room_id == data['room_id'],
        Reservation.check_out_date > check_in,
        Reservation.check_in_date < check_out
    ).first()

    if existing:

        return jsonify({
            "error": "Room already booked for selected dates"
        }), 400


    reservation = Reservation(
        check_in_date=check_in,
        check_out_date=check_out,
        reservation_date=today,
        customer_id=data['customer_id'],
        room_id=data['room_id']
    )

    db.session.add(reservation)

    

    room.status = "Booked"

    db.session.commit()

    return jsonify({
        "message": "Reservation Added Successfully"
    })



@app.route('/checkout', methods=['POST'])
def checkout():

    data = request.json

    room = Room.query.get(data['room_id'])

    if not room:

        return jsonify({
            "error": "Room not found"
        }), 404

    # change room status
    room.status = "Available"

    db.session.commit()

    return jsonify({
        "message": "Checkout Successful"
    })



@app.route('/reservations', methods=['GET'])
def get_reservations():

    reservations = Reservation.query.all()

    result = []

    for r in reservations:

        result.append({
            "reservation_id": r.reservation_id,
            "check_in_date": str(r.check_in_date),
            "check_out_date": str(r.check_out_date),
            "customer_id": r.customer_id,
            "room_id": r.room_id
        })

    return jsonify(result)




@app.route('/add_payment', methods=['POST'])
def add_payment():

    data = request.json

    payment = Payment(
        amount=data['amount'],
        payment_date=datetime.today().date(),
        payment_method=data['payment_method'],
        reservation_id=data['reservation_id']
    )

    db.session.add(payment)
    db.session.commit()

    return jsonify({
        "message": "Payment Added Successfully"
    })



@app.route('/payments', methods=['GET'])
def get_payments():

    payments = Payment.query.all()

    result = []

    for p in payments:

        result.append({
            "payment_id": p.payment_id,
            "amount": p.amount,
            "payment_method": p.payment_method,
            "reservation_id": p.reservation_id
        })

    return jsonify(result)



def insert_rooms():

    if Room.query.count() == 0:

        rooms = [

            # -------------------------
            # STANDARD ROOMS
            # -------------------------

            Room(room_number=101, room_type="Standard", price=1800, status="Available", hotel_id=1),
            Room(room_number=102, room_type="Standard", price=1800, status="Available", hotel_id=1),
            Room(room_number=103, room_type="Standard", price=1800, status="Booked", hotel_id=1),
            Room(room_number=104, room_type="Standard", price=1800, status="Available", hotel_id=1),
            Room(room_number=105, room_type="Standard", price=1800, status="Maintenance", hotel_id=1),
            Room(room_number=106, room_type="Standard", price=1800, status="Available", hotel_id=1),
            Room(room_number=107, room_type="Standard", price=1800, status="Booked", hotel_id=1),
            Room(room_number=108, room_type="Standard", price=1800, status="Available", hotel_id=1),
            Room(room_number=109, room_type="Standard", price=1800, status="Available", hotel_id=1),
            Room(room_number=110, room_type="Standard", price=1800, status="Available", hotel_id=1),

            # -------------------------
            # DELUXE ROOMS
            # -------------------------

            Room(room_number=201, room_type="Deluxe", price=2500, status="Available", hotel_id=1),
            Room(room_number=202, room_type="Deluxe", price=2500, status="Available", hotel_id=1),
            Room(room_number=203, room_type="Deluxe", price=2500, status="Booked", hotel_id=1),
            Room(room_number=204, room_type="Deluxe", price=2500, status="Available", hotel_id=1),
            Room(room_number=205, room_type="Deluxe", price=2500, status="Maintenance", hotel_id=1),
            Room(room_number=206, room_type="Deluxe", price=2500, status="Available", hotel_id=1),
            Room(room_number=207, room_type="Deluxe", price=2500, status="Booked", hotel_id=1),
            Room(room_number=208, room_type="Deluxe", price=2500, status="Available", hotel_id=1),
            Room(room_number=209, room_type="Deluxe", price=2500, status="Available", hotel_id=1),
            Room(room_number=210, room_type="Deluxe", price=2500, status="Available", hotel_id=1),

            # -------------------------
            # SUITE ROOMS
            # -------------------------

            Room(room_number=301, room_type="Suite", price=5000, status="Available", hotel_id=1),
            Room(room_number=302, room_type="Suite", price=5000, status="Booked", hotel_id=1),
            Room(room_number=303, room_type="Suite", price=5000, status="Available", hotel_id=1),
            Room(room_number=304, room_type="Suite", price=5000, status="Available", hotel_id=1),
            Room(room_number=305, room_type="Suite", price=5000, status="Maintenance", hotel_id=1),
            Room(room_number=306, room_type="Suite", price=5000, status="Available", hotel_id=1),
            Room(room_number=307, room_type="Suite", price=5000, status="Booked", hotel_id=1),
            Room(room_number=308, room_type="Suite", price=5000, status="Available", hotel_id=1),
            Room(room_number=309, room_type="Suite", price=5000, status="Available", hotel_id=1),
            Room(room_number=310, room_type="Suite", price=5000, status="Available", hotel_id=1),

            # -------------------------
            # PREMIUM ROOMS
            # -------------------------

            Room(room_number=401, room_type="Premium", price=7000, status="Available", hotel_id=1),
            Room(room_number=402, room_type="Premium", price=7000, status="Booked", hotel_id=1),
            Room(room_number=403, room_type="Premium", price=7000, status="Available", hotel_id=1),
            Room(room_number=404, room_type="Premium", price=7000, status="Available", hotel_id=1),
            Room(room_number=405, room_type="Premium", price=7000, status="Maintenance", hotel_id=1),
            Room(room_number=406, room_type="Premium", price=7000, status="Available", hotel_id=1),
            Room(room_number=407, room_type="Premium", price=7000, status="Booked", hotel_id=1),
            Room(room_number=408, room_type="Premium", price=7000, status="Available", hotel_id=1),
            Room(room_number=409, room_type="Premium", price=7000, status="Available", hotel_id=1),
            Room(room_number=410, room_type="Premium", price=7000, status="Available", hotel_id=1),

            # -------------------------
            # EXECUTIVE ROOMS
            # -------------------------

            Room(room_number=501, room_type="Executive", price=9000, status="Available", hotel_id=1),
            Room(room_number=502, room_type="Executive", price=9000, status="Booked", hotel_id=1),
            Room(room_number=503, room_type="Executive", price=9000, status="Available", hotel_id=1),
            Room(room_number=504, room_type="Executive", price=9000, status="Available", hotel_id=1),
            Room(room_number=505, room_type="Executive", price=9000, status="Maintenance", hotel_id=1),
            Room(room_number=506, room_type="Executive", price=9000, status="Available", hotel_id=1),
            Room(room_number=507, room_type="Executive", price=9000, status="Booked", hotel_id=1),
            Room(room_number=508, room_type="Executive", price=9000, status="Available", hotel_id=1),
            Room(room_number=509, room_type="Executive", price=9000, status="Available", hotel_id=1),
            Room(room_number=510, room_type="Executive", price=9000, status="Available", hotel_id=1),

        ]

        db.session.add_all(rooms)

        db.session.commit()

        print("50 Rooms Inserted Successfully")

with app.app_context():
 db.create_all()
 if  Room.query.count() == 0:
  insert_rooms()


if __name__ == '__main__':

    
    app.run(
        debug=os.environ.get('FLASK_DEBUG', 'False') == 'True',
        port=int(os.environ.get('FLASK_PORT', 5000))
    )