# import the necessary packages
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import os


class Enroll(object):
	def __init__(self, camera, username):
		self.username = "core/dataset/"+username
		self.detector = cv2.CascadeClassifier('core/haarcascade_frontalface_default.xml')
		if not os.path.exists(self.username):
			os.makedirs(self.username)
		self.vs = VideoStream(src=camera).start()
		time.sleep(2.0)
		self.total = 0
		# self.begin()

	def begin(self):
		frame = self.vs.read()
		orig = frame.copy()
		frame = imutils.resize(frame, width=400)
		# detect faces in the grayscale frame
		rects = self.detector.detectMultiScale(
			cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), scaleFactor=1.1, 
			minNeighbors=5, minSize=(30, 30))
		# loop over the face detections and draw them on the frame
		for (x, y, w, h) in rects:
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		# show the output frame
		# cv2.imshow("Tekan K untuk capture, Q untuk keluar", frame)
		key = cv2.waitKey(1) & 0xFF
	
		# if the `k` key was pressed, write the *original* frame to disk
		# so we can later process it and use it for face recognition
		if key == ord("k"):
			p = os.path.sep.join([self.username, "{}.png".format(
				str(self.total).zfill(5))])
			cv2.imwrite(p, orig)
			self.total += 1
		# if the `q` key was pressed, break from the loop
		# elif key == ord("q"):
		# 	self.stop()
		# 	break

	def stop(self):
		print("[INFO] {} face images stored".format(self.total))
		print("[INFO] cleaning up...")
		cv2.destroyAllWindows()
		self.vs.stop()
