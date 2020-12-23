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
		# self.vs = VideoStream(src=camera).start()
		self.vs = camera
		time.sleep(0.5)
		self.total = 0
		# self.begin()
		print('[INFO] Enroll Started')

	def begin(self):
		self.frame = self.vs.read()
		self.orig = self.frame.copy()
		self.frame = imutils.resize(self.frame, width=300)
		# detect faces in the grayscale self.frame
		rects = self.detector.detectMultiScale(
			cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY), scaleFactor=1.1, 
			minNeighbors=5, minSize=(30, 30))
		# loop over the face detections and draw them on the self.frame
		for (x, y, w, h) in rects:
			cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		# show the output self.frame
		# cv2.imshow("Tekan K untuk capture, Q untuk keluar", self.frame)
		# key = cv2.waitKey(1) & 0xFF
	
		# # if the `k` key was pressed, write the *self.original* self.frame to disk
		# # so we can later process it and use it for face recognition
		# if key == ord("k"):
		# 	p = os.path.sep.join([self.username, "{}.png".format(
		# 		str(self.total).zfill(5))])
		# 	cv2.imwrite(p, self.orig)
		# 	self.total += 1
		return self.frame
		# if the `q` key was pressed, break from the loop
		# elif key == ord("q"):
		# 	self.stop()
		# 	break

	def capture(self):
		p = os.path.sep.join([self.username, "{}.png".format(
			str(self.total).zfill(5))])
		cv2.imwrite(p, self.orig)
		self.total += 1
		return self.total
	
	def stop(self):
		print("[INFO] {} face images stored".format(self.total))
		print("[INFO] cleaning up...")
		cv2.destroyAllWindows()
		self.vs.stop()
