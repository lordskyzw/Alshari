from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO
from models import db, Entry, Plate  # Importing the models from models.py

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Adjust as per your database file
app.config['SECRET_KEY'] = 'secret'
db.init_app(app)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/register', methods=['GET', 'POST'])
def register_plate():
    if request.method == 'POST':
        number_plate = request.form['number_plate']
        owner = request.form['owner']
        new_plate = Plate(number_plate=number_plate, owner=owner)
        db.session.add(new_plate)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logs')
def view_logs():
    entries = Entry.query.all()
    return render_template('logs.html', entries=entries)

@socketio.on('new_entry')
def handle_new_entry(data):
    plate = data['plate']
    new_entry = Entry(plate=plate)
    db.session.add(new_entry)
    db.session.commit()
    socketio.emit('update_entries', {'plate': plate, 'timestamp': new_entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}, broadcast=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure the database tables are created
    socketio.run(app, debug=True)
