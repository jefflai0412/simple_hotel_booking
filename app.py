from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0000@localhost:5433/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)

# Database Model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)

# Initialize the database
@app.cli.command('init-db')
def init_db():
    """Initialize the database."""
    db.create_all()
    print("Database initialized!")

# Home Page: Display all bookings
@app.route('/')
def index():
    bookings = Booking.query.all()
    return render_template('index.html', bookings=bookings)

# Add a new booking
@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        try:
            check_in = datetime.strptime(request.form['check_in'], '%Y-%m-%d')
            check_out = datetime.strptime(request.form['check_out'], '%Y-%m-%d')
            if check_out <= check_in:
                flash('Check-out date must be later than check-in date', 'error')
                return redirect(url_for('book'))
            new_booking = Booking(
                check_in=check_in,
                check_out=check_out,
                room_type=request.form['room_type'],
                user_name=request.form['user_name']
            )
            db.session.add(new_booking)
            db.session.commit()
            flash('Booking successful!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", 'error')
    return render_template('booking.html')

# Delete a booking
@app.route('/delete/<int:id>', methods=['POST'])
def delete_booking(id):
    booking = Booking.query.get_or_404(id)
    try:
        db.session.delete(booking)
        db.session.commit()
        flash('Booking deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting booking: {str(e)}", 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
