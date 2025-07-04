from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson.objectid import ObjectId
from bson.errors import InvalidId

app = Flask(__name__)
# IMPORTANT: Replace with a strong, random key in production
# This key is used for secure session management.
app.secret_key = 'f229b60b0dcb35c39f0fe90fe4487ee9323eaf809669642d83f3be170954f330' # Consider generating a new one

# MongoDB connection
client = MongoClient('mongodb+srv://upendra23:123up@cluster0.ac3auf8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['travel_booking_db']

# Collections
users_collection = db['users']
flights_collection = db['flights']
trains_collection = db['trains']
bookings_collection = db['bookings']
hotels_collection = db['hotels']

# --- Sample Data Insertion Functions ---
def insert_sample_train_data():
    """Inserts sample train data into the MongoDB collection if it's empty."""
    if trains_collection.count_documents({}) == 0:
        sample_trains = [
            {"_id": ObjectId(), "name": "Duronto Express", "train_number": "12285", "source": "Hyderabad", "destination": "Delhi", "departure_time": "07:00 AM", "arrival_time": "05:00 AM (next day)", "price": 1800, "date": "2025-07-10"},
            {"_id": ObjectId(), "name": "AP Express", "train_number": "12723", "source": "Hyderabad", "destination": "Vijayawada", "departure_time": "09:00 AM", "arrival_time": "03:00 PM", "price": 450, "date": "2025-07-10"},
            {"_id": ObjectId(), "name": "Gouthami Express", "train_number": "12737", "source": "Guntur", "destination": "Hyderabad", "departure_time": "08:00 PM", "arrival_time": "06:00 AM (next day)", "price": 600, "date": "2025-07-10"},
            {"_id": ObjectId(), "name": "Chennai Express", "train_number": "12839", "source": "Bengaluru", "destination": "Chennai", "departure_time": "10:30 AM", "arrival_time": "05:30 PM", "price": 750, "date": "2025-07-11"},
            {"_id": ObjectId(), "name": "Mumbai Mail", "train_number": "12101", "source": "Hyderabad", "destination": "Mumbai", "departure_time": "06:00 PM", "arrival_time": "09:00 AM (next day)", "price": 1200, "date": "2025-07-10"},
            {"_id": ObjectId(), "name": "Godavari Express", "train_number": "12720", "source": "Vijayawada", "destination": "Hyderabad", "departure_time": "05:00 PM", "arrival_time": "11:00 PM", "price": 400, "date": "2025-07-10"},
        ]
        trains_collection.insert_many(sample_trains)
        print("Sample train data inserted into MongoDB.")

def insert_sample_flight_data():
    """Inserts sample flight data into the MongoDB collection if it's empty."""
    if flights_collection.count_documents({}) == 0:
        sample_flights = [
            {"_id": ObjectId(), "airline": "IndiGo", "flight_number": "6E 2345", "source": "Delhi", "destination": "Mumbai", "departure_time": "10:00 AM", "arrival_time": "12:00 PM", "price": 5000, "date": "2025-07-15"},
            {"_id": ObjectId(), "airline": "Air India", "flight_number": "AI 400", "source": "Mumbai", "destination": "Bengaluru", "departure_time": "03:00 PM", "arrival_time": "05:00 PM", "price": 6500, "date": "2025-07-15"},
        ]
        flights_collection.insert_many(sample_flights)
        print("Sample flight data inserted into MongoDB.")

def insert_sample_hotel_data():
    """Inserts sample hotel data into the MongoDB collection if it's empty."""
    if hotels_collection.count_documents({}) == 0:
        sample_hotels = [
            {"_id": ObjectId(), "name": "The Grand Hotel", "location": "Mumbai", "price_per_night": 4000},
            {"_id": ObjectId(), "name": "City Centre Inn", "location": "Delhi", "price_per_night": 2500},
        ]
        hotels_collection.insert_many(sample_hotels)
        print("Sample hotel data inserted into MongoDB.")

def insert_default_user():
    """Inserts a default user if one does not already exist."""
    default_email = "upendrakonari2107@gmail.com"
    default_password = "123up"
    if not users_collection.find_one({'email': default_email}):
        hashed_password = generate_password_hash(default_password)
        users_collection.insert_one({'fullname': 'uprendra', 'email': default_email, 'password': hashed_password})
        print("Default user inserted.")

# --- Routes ---

@app.route('/')
def index():
    """Renders the home page."""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            print("Register: Passwords do not match.")
            return render_template('register.html', error='Passwords do not match!')
        if users_collection.find_one({'email': email}):
            print(f"Register: Email {email} already exists.")
            return render_template('register.html', error='Email already exists!')
        
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({'fullname': fullname, 'email': email, 'password': hashed_password})
        print(f"Register: User {email} registered successfully. Redirecting to login.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({'email': email})

        print(f"Login attempt for email: {email}") # Debug print

        if user and check_password_hash(user['password'], password):
            session['email'] = email
            session['fullname'] = user.get('fullname', email)
            print(f"Login successful for {email}. Session email: {session.get('email')}. Redirecting to dashboard.") # Debug print
            return redirect(url_for('dashboard'))
        else:
            print(f"Login failed for {email}. Invalid credentials.") # Debug print
            # FIX: Changed 'message' to 'error' to match the template's expected variable
            return render_template('login.html', error='Invalid email or password!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logs out the user by clearing the session."""
    email_logged_out = session.get('email', 'N/A')
    session.pop('email', None)
    session.pop('fullname', None)
    print(f"User {email_logged_out} logged out. Redirecting to index.") # Debug print
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Displays the user dashboard with their bookings."""
    print(f"Dashboard access attempt. Session email: {session.get('email')}") # Debug print
    if 'email' not in session:
        print("Dashboard: User not in session. Redirecting to login.") # Debug print
        return redirect(url_for('login'))

    user_email = session['email']
    user_fullname = session.get('fullname', user_email)
    user_bookings = list(bookings_collection.find({'user_email': user_email}).sort('booking_date', -1))

    # Process bookings to include 'date' for display consistency if not already present
    for booking in user_bookings:
        if '_id' in booking and isinstance(booking['_id'], ObjectId):
            booking['booking_id'] = str(booking['_id'])
        else:
            booking['booking_id'] = None
        
        # Ensure 'date' key is present for consistent display in the template
        # You might need to adjust this based on how dates are stored for different booking types
        if booking.get('booking_type') == 'bus':
            booking['type'] = 'Bus'
            booking['details'] = f"{booking.get('name', 'N/A')} from {booking.get('source', 'N/A')} to {booking.get('destination', 'N/A')}"
            booking['date'] = booking.get('travel_date', 'N/A') # Use travel_date for consistency
        elif booking.get('booking_type') == 'train':
            booking['type'] = 'Train'
            booking['details'] = f"{booking.get('name', 'N/A')} ({booking.get('train_number', 'N/A')}) from {booking.get('source', 'N/A')} to {booking.get('destination', 'N/A')}"
            booking['date'] = booking.get('travel_date', 'N/A') # Use travel_date for consistency
        elif booking.get('booking_type') == 'flight':
            booking['type'] = 'Flight'
            booking['details'] = f"{booking.get('airline', 'N/A')} ({booking.get('flight_number', 'N/A')}) from {booking.get('source', 'N/A')} to {booking.get('destination', 'N/A')}"
            booking['date'] = booking.get('travel_date', 'N/A') # Use travel_date for consistency
        elif booking.get('booking_type') == 'hotel':
            booking['type'] = 'Hotel'
            booking['details'] = f"{booking.get('hotel_name', 'N/A')} in {booking.get('location', 'N/A')}"
            booking['date'] = booking.get('check_in_date', 'N/A') # Use check_in_date for consistency
        else:
            booking['type'] = 'N/A'
            booking['details'] = 'Booking details not available.'
            booking['date'] = 'N/A'

    print(f"Dashboard: Rendering for user {user_email} with {len(user_bookings)} bookings.") # Debug print
    return render_template('dashboard.html', name=user_fullname, bookings=user_bookings)

# --- Bus Search and Booking Flow ---

@app.route('/bus')
def bus():
    """Renders the bus search page."""
    print(f"Bus page access attempt. Session email: {session.get('email')}")
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('bus.html')

@app.route('/confirm_bus_booking', methods=['POST'])
def confirm_bus_booking():
    print(f"Confirm Bus Booking attempt. Session email: {session.get('email')}")
    if 'email' not in session:
        return redirect(url_for('login'))

    name = request.form.get('name')
    source = request.form.get('source')
    destination = request.form.get('destination')
    time = request.form.get('time')
    bus_type = request.form.get('type')
    travel_date = request.form.get('date')
    
    try:
        price_per_person = float(request.form.get('price'))
        num_persons = int(request.form.get('persons'))
    except (TypeError, ValueError):
        print("Error: Invalid price or number of persons provided for bus booking.")
        return redirect(url_for('bus'))

    total_price = price_per_person * num_persons

    booking_details = {
        'name': name,
        'source': source,
        'destination': destination,
        'time': time,
        'type': bus_type,
        'price_per_person': price_per_person,
        'travel_date': travel_date,
        'num_persons': num_persons,
        'total_price': total_price,
        'booking_type': 'bus',
        'user_email': session['email']
    }
    session['pending_booking'] = booking_details
    print(f"Bus booking details stored in session for confirmation.")
    return render_template('confirm.html', booking=booking_details, booking_type='bus')

@app.route('/final_confirm_booking', methods=['POST'])
def final_confirm_booking():
    print(f"Final Confirm Bus Booking attempt. Session email: {session.get('email')}")
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'User not logged in', 'redirect': url_for('login')}), 401

    booking_data = session.pop('pending_booking', None)
    if not booking_data:
        print("No pending bus booking found in session.")
        return jsonify({'success': False, 'message': 'No pending booking to confirm.'}), 400

    try:
        booking_data['booking_date'] = datetime.now().isoformat()
        bookings_collection.insert_one(booking_data)
        print(f"Bus booking for {booking_data.get('user_email')} confirmed and saved.")
        return jsonify({
            'success': True,
            'message': 'Bus booking confirmed successfully!'
        })
    except Exception as e:
        print(f"Error saving bus booking to DB: {e}")
        return jsonify({'success': False, 'message': f'Failed to confirm booking: {str(e)}'}), 500

# --- Train Search and Booking Flow ---

@app.route('/train')
def train():
    print(f"Train page access attempt. Session email: {session.get('email')}")
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('train.html')

@app.route('/confirm_train_booking', methods=['POST'])
def confirm_train_booking():
    print(f"Confirm Train Booking attempt. Session email: {session.get('email')}")
    if 'email' not in session:
        return redirect(url_for('login'))

    name = request.form.get('name')
    train_number = request.form.get('trainNumber')
    source = request.form.get('source')
    destination = request.form.get('destination')
    departure_time = request.form.get('departureTime')
    arrival_time = request.form.get('arrivalTime')
    travel_date = request.form.get('date')

    try:
        price_per_person = float(request.form.get('price'))
        num_persons = int(request.form.get('persons'))
    except (TypeError, ValueError):
        print("Error: Invalid price or number of persons provided for train booking.")
        return redirect(url_for('train'))

    total_price = price_per_person * num_persons

    booking_details = {
        'name': name,
        'train_number': train_number,
        'source': source,
        'destination': destination,
        'departure_time': departure_time,
        'arrival_time': arrival_time,
        'price_per_person': price_per_person,
        'travel_date': travel_date,
        'num_persons': num_persons,
        'total_price': total_price,
        'booking_type': 'train',
        'user_email': session['email']
    }
    session['pending_booking'] = booking_details
    print(f"Train booking details stored in session for confirmation.")
    return render_template('confirmtrain.html', booking=booking_details)

@app.route('/final_confirm_train_booking', methods=['POST'])
def final_confirm_train_booking():
    print(f"Final Confirm Train Booking attempt. Session email: {session.get('email')}")
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'User not logged in', 'redirect': url_for('login')}), 401

    booking_data = session.pop('pending_booking', None)
    if not booking_data:
        print("No pending train booking found in session.")
        return jsonify({'success': False, 'message': 'No pending booking to confirm.'}), 400

    try:
        booking_data['booking_date'] = datetime.now().isoformat()
        bookings_collection.insert_one(booking_data)
        print(f"Train booking for {booking_data.get('user_email')} confirmed and saved.")
        return jsonify({
            'success': True,
            'message': 'Train booking confirmed successfully!'
        })
    except Exception as e:
        print(f"Error saving train booking to DB: {e}")
        return jsonify({'success': False, 'message': f'Failed to confirm train booking: {str(e)}'}), 500

# --- Flight Search and Booking Flow ---

@app.route('/flight', methods=['GET', 'POST'])
def flight():
    print(f"Flight page access attempt. Session email: {session.get('email')}")
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('flight.html')

@app.route('/confirm_flight_booking', methods=['POST'])
def confirm_flight_booking():
    print(f"Confirm Flight Booking attempt. Session email: {session.get('email')}")
    if 'email' not in session:
        return redirect(url_for('login'))

    airline = request.form.get('airline')
    flight_number = request.form.get('flightNumber')
    source = request.form.get('source')
    destination = request.form.get('destination')
    departure_time = request.form.get('departureTime')
    arrival_time = request.form.get('arrivalTime')
    travel_date = request.form.get('date')

    try:
        price_per_person = float(request.form.get('price'))
        num_persons = int(request.form.get('persons'))
    except (TypeError, ValueError):
        print("Error: Invalid price or number of persons provided for flight booking.")
        return redirect(url_for('flight'))

    total_price = price_per_person * num_persons

    booking_details = {
        'airline': airline,
        'flight_number': flight_number,
        'source': source,
        'destination': destination,
        'departure_time': departure_time,
        'arrival_time': arrival_time,
        'price_per_person': price_per_person,
        'travel_date': travel_date,
        'num_persons': num_persons,
        'total_price': total_price,
        'booking_type': 'flight',
        'user_email': session['email']
    }
    session['pending_booking'] = booking_details
    print(f"Flight booking details stored in session for confirmation.")
    return render_template('confirmflight.html', booking=booking_details)

@app.route('/final_confirm_flight_booking', methods=['POST'])
def final_confirm_flight_booking():
    print(f"Final Confirm Flight Booking attempt. Session email: {session.get('email')}")
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'User not logged in', 'redirect': url_for('login')}), 401

    booking_data = session.pop('pending_booking', None)
    if not booking_data:
        print("No pending flight booking found in session.")
        return jsonify({'success': False, 'message': 'No pending booking to confirm.'}), 400

    try:
        booking_data['booking_date'] = datetime.now().isoformat()
        bookings_collection.insert_one(booking_data)
        print(f"Flight booking for {booking_data.get('user_email')} confirmed and saved.")
        return jsonify({
            'success': True,
            'message': 'Flight booking confirmed successfully!'
        })
    except Exception as e:
        print(f"Error saving flight booking to DB: {e}")
        return jsonify({'success': False, 'message': f'Failed to confirm flight booking: {str(e)}'}), 500

# --- Hotel Search and Booking Flow ---

@app.route('/hostel')
def hotel():
    print(f"Hotel page access attempt. Session email: {session.get('email')}")
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('hotel.html')

@app.route('/confirm_hotel_booking', methods=['POST'])
def confirm_hotel_booking():
    print(f"Confirm Hotel Booking attempt. Session email: {session.get('email')}")
    if 'email' not in session:
        return redirect(url_for('login'))

    hotel_name = request.form.get('hotelName')
    location = request.form.get('location')
    check_in_date = request.form.get('checkInDate')
    check_out_date = request.form.get('checkOutDate')
    
    try:
        num_rooms = int(request.form.get('numRooms'))
        num_guests = int(request.form.get('numGuests'))
        price_per_night = float(request.form.get('pricePerNight'))
        
        # FIX: Calculate num_nights based on check-in and check-out dates
        check_in_dt = datetime.strptime(check_in_date, '%Y-%m-%d')
        check_out_dt = datetime.strptime(check_out_date, '%Y-%m-%d')
        num_nights = (check_out_dt - check_in_dt).days
        
        if num_nights < 1:
            print("Error: Check-out date must be after check-in date for hotel booking.")
            # Redirect with an error or display a message to the user
            return redirect(url_for('hostel', error='Check-out date must be after check-in date.')) 

    except (TypeError, ValueError) as e:
        print(f"Error: Invalid numeric or date data provided for hotel booking: {e}")
        return redirect(url_for('hostel', error='Invalid input for hotel booking.'))

    total_price = price_per_night * num_rooms * num_nights

    booking_details = {
        'hotel_name': hotel_name,
        'location': location,
        'check_in_date': check_in_date,
        'check_out_date': check_out_date,
        'num_rooms': num_rooms,
        'num_guests': num_guests,
        'price_per_night': price_per_night,
        'num_nights': num_nights, # FIX: Added num_nights to booking details
        'total_price': total_price,
        'booking_type': 'hotel',
        'user_email': session['email']
    }
    session['pending_booking'] = booking_details
    print(f"Hotel booking details stored in session for confirmation.")
    return render_template('confirmhotel.html', booking=booking_details)

@app.route('/final_confirm_hotel_booking', methods=['POST'])
def final_confirm_hotel_booking():
    print(f"Final Confirm Hotel Booking attempt. Session email: {session.get('email')}")
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'User not logged in', 'redirect': url_for('login')}), 401

    booking_data = session.pop('pending_booking', None)
    if not booking_data:
        print("No pending hotel booking found in session.")
        return jsonify({'success': False, 'message': 'No pending booking to confirm.'}), 400

    try:
        booking_data['booking_date'] = datetime.now().isoformat()
        bookings_collection.insert_one(booking_data)
        print(f"Hotel booking for {booking_data.get('user_email')} confirmed and saved.")
        return jsonify({
            'success': True,
            'message': 'Hotel booking confirmed successfully!'
        })
    except Exception as e:
        print(f"Error saving hotel booking to DB: {e}")
        return jsonify({'success': False, 'message': f'Failed to confirm hotel booking: {str(e)}'}), 500

# --- Cancel Booking Route ---
@app.route('/cancel', methods=['POST'])
def cancel():
    """
    Handles cancellation of a booking.
    """
    print(f"Cancel booking attempt. Session email: {session.get('email')}")
    if 'email' not in session:
        return redirect(url_for('login'))

    booking_id = request.form.get('booking_id')
    user_email = session['email']

    if not booking_id:
        print("Error: booking_id is missing for cancellation.")
        return redirect(url_for('dashboard'))

    try:
        object_id_to_delete = ObjectId(booking_id)
        query = {'_id': object_id_to_delete, 'user_email': user_email}
        result = bookings_collection.delete_one(query)
        if result.deleted_count == 1:
            print(f"Booking {booking_id} cancelled by {user_email}")
        else:
            print(f"Booking {booking_id} not found or not owned by {user_email}. Deleted count: {result.deleted_count}")
    except InvalidId:
        print(f"Booking ID '{booking_id}' is not a valid ObjectId.")
    except Exception as e:
        print(f"Error cancelling booking {booking_id}: {e}")

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    # Insert sample data and default user when the app starts
    insert_sample_train_data()
    insert_sample_flight_data()
    insert_sample_hotel_data()
    insert_default_user()
    app.run(host='0.0.0.0', port=8000, debug=True)