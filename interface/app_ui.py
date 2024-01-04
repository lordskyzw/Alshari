from flask import Flask, render_template, request, redirect, url_for, Response
from flask_socketio import SocketIO
from models import db, Entry, Plate  # Importing the models from models.py
import cv2

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Adjust as per your database file
app.config['SECRET_KEY'] = 'secret'
db.init_app(app)
socketio = SocketIO(app)

def gen_frames():  
    # Connect to the RTSP stream
    cap = cv2.VideoCapture('rtsp://your_camera_ip:554/live/main/av_stream')

    while True:
        success, frame = cap.read()  # read the camera frame
        if not success:
            break
        else:
            # Optional: Apply any processing on the frame here
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('base.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/feed')
def feed():
    return render_template('feed.html')


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
