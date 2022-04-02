from flask import Flask, render_template, request
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import cv2

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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

app = Flask(__name__)

# sqlalchemy config
engine = create_engine('sqlite:///:memory:', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

@app.route('/')
def index():
    return render_template('index.html', text='')

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

if __name__ == '__main__':
     '''
     ap = argparse.ArgumentParser()
     ap.add_argument("-i", "--ip", type=str, required=False, help="ip address of the device")
     ap.add_argument("-o", "--port", type=int, required=False, help="ephemeral port number of the server (1024 to 65535)")
     ap.add_argument("-f", "--frame-count", type=int, default=32, help="# of frames used to construct the background model")
     args = vars(ap.parse_args())
     '''
     t = threading.Thread(target=detect_motion)
     t.daemon = True
     t.start()
     app.run(threaded=True)
