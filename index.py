from flask import Flask, render_template, request, flash, redirect,\
 url_for, flash, make_response, session
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import sched, time
import threading
import argparse
import datetime
import imutils
import time
#import cv2

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apscheduler.schedulers.background import BackgroundScheduler
from flask_socketio import SocketIO, emit
'''
outputFrame = None
lock = threading.Lock()
vs = VideoStream(src=0).start()

def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock
	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue
			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
			# ensure the frame was successfully encoded
			if not flag:
				continue
		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

def detect_motion(frameCount=32):
	# grab global references to the video stream, output frame, and
	# lock variables
	global vs, outputFrame, lock
	# initialize the motion detector and the total number of frames
	# read thus far
	total = 0
    # loop over frames from the video stream
	while True:
		# read the next frame from the video stream, resize it,
		# convert the frame to grayscale, and blur it
		frame = vs.read()
		frame = imutils.resize(frame, width=400)
		timestamp = datetime.datetime.now()
		with lock:
			outputFrame = frame.copy()

'''
from database import init_db

init_db()

from database import db_session
from models import User, Queue
# sqlalchemy config
engine = create_engine('sqlite:///:memory:', echo=True)
# Session = sessionmaker(bind=engine)
# session = Session()
app = Flask(__name__)
app.secret_key = 'super secret key'
app.permanent_session_lifetime = datetime.timedelta(days=365)
socketio = SocketIO(app)

@app.route('/')

def index():
    if 'username' in session:
        username = session['username']
    else:
        username = False
    return render_template('index.html', username = username)

@app.route('/login', methods=['GET', 'POST', 'DESTROY']) 
def login():
    username = request.form.get('username')
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        p = User.query.filter_by(username=username).first()
        print(p)
        password = request.form.get('password')
        if p and (p.password == request.form.get('password')):
            flash('Successful Login')
            return redirect(url_for('index'))
        elif p:
            flash('Username Already Exists')
            render_template('login.html')
        else:
            db_session.add(User(username=username,password=request.form.get('password')))
            db_session.commit()
            session['username'] = username
            flash('User Registered')
            return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('index'))

@app.route('/queue', methods=["POST"])
def queue():
    p = User.query.filter_by(username=session['username']).first()
    q = Queue.query.filter_by(id=p.id).first()
    print(request.form.get("link"))
    if not q:
        db_session.add(Queue(p.id, request.form.get("link")))
        db_session.commit()
        flash('Added to queue')
    else:
        flash('Already in queue')
    return redirect(url_for('index'))


'''

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")
'''
@app.route("/viewer")
def viewer():
	# return the response generated along with the specific media
	# type (mime type)
	return render_template("viewer.html")


# socketio = SocketIO(app)
# import sched, time
import time

# @socketio.on('connect')
# @celery.task()
def change_link():
    q = Queue.query.first()
    if q:
        db_session.delete(q)
        db_session.commit()
        with app.test_request_context('/'):
            socketio.emit('change', {'link': q.video})
            print(q.video)
    else:
        with app.test_request_context('/'):
            socketio.emit('change', {'link': 'nothing'})
            print('Nothing')
    # sc.enter(2, 1, change_link, (sc,))

sched = BackgroundScheduler(daemon=True)
sched.add_job(change_link,'interval',minutes=1)
sched.start()

if __name__ == '__main__':
     '''
     ap = argparse.ArgumentParser()
     ap.add_argument("-i", "--ip", type=str, required=False, help="ip address of the device")
     ap.add_argument("-o", "--port", type=int, required=False, help="ephemeral port number of the server (1024 to 65535)")
     ap.add_argument("-f", "--frame-count", type=int, default=32, help="# of frames used to construct the background model")
     args = vars(ap.parse_args())
     '''
     # s = sched.scheduler(time.time, time.sleep)
     # s.enter(60, 1, change_link, (s,))
     # s.run()
     
     # t1 = threading.Thread(target=detect_motion)
     # t1.daemon = True
     # t1.start()

     socketio.run(app)
     # app.run(threaded=True)
     # change_link()
