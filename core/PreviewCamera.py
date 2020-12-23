# import the necessary packages
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import os

class PreviewCamera(object):
	def __init__(self, camera):
		# self.vs = vs
		self.detector = cv2.CascadeClassifier('core/haarcascade_frontalface_default.xml')
		self.vs = VideoStream(src=camera).start()
		# vs = VideoStream(usePiCamera=True).start()
		time.sleep(2.0)

	def begin(self):
		self.frame = self.vs.read()
		self.frame = imutils.resize(self.frame, width=300)
		# detect faces in the grayscale self.frame
		rects = self.detector.detectMultiScale(
			cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY), scaleFactor=1.1, 
			minNeighbors=5, minSize=(30, 30))
		# loop over the face detections and draw them on the self.frame
		for (x, y, w, h) in rects:
			cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		return self.frame
		# show the output self.frame
		# cv2.imshow("Q untuk keluar", self.frame)
		# key = cv2.waitKey(1) & 0xFF
		# if key == ord("q"):
		# 	break
	def stop(self):
		print("[INFO] cleaning up...")
		cv2.destroyAllWindows()
		self.vs.stop()
# pv = PreviewCamera(2)