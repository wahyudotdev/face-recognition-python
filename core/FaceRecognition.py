# from imutils.video import VideoStream
from core.WebcamVideoStream import WebcamVideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import pickle
import time
import cv2
import os
from multiprocessing import Process, Pool
from threading import Thread
class FaceRecognitionVideo(object):
	def __init__(self, camera):
		self.threshold = 0.99
		self.protoPath = "core/face_detection_model/deploy.prototxt"
		self.modelPath = "core/face_detection_model/res10_300x300_ssd_iter_140000.caffemodel"
		self.detector = cv2.dnn.readNetFromCaffe(self.protoPath, self.modelPath)
		self.name = ''
		# load our serialized face embedding model from disk
		print("[INFO] loading face recognizer...")
		self.embedder = cv2.dnn.readNetFromTorch('core/openface_nn4.small2.v1.t7')
		
		# load the actual face recognition model along with the label encoder
		self.recognizer = pickle.loads(open('core/output/recognizer.pickle', "rb").read())
		self.le = pickle.loads(open('core/output/le.pickle', "rb").read())
		# initialize the video stream, then allow the camera sensor to warm up
		print("[INFO] starting video stream...")
		# vs = VideoStream(src=2).start()
		# self.vs = WebcamVideoStream.WebcamVideoStream(src=camera).start()
		# self.vs = WebcamVideoStream(camera).start()
		self.vs = camera
		time.sleep(2.0)
		# start the FPS throughput estimator
		self.fps = FPS().start()

	def drawBondingBox(self, i):
		try:
			confidence = self.detections[0, 0, i, 2]
	
		# filter out weak detections
			if confidence > self.threshold:
				# compute the (x, y)-coordinates of the bounding box for
				# the face
				box = self.detections[0, 0, i, 3:7] * np.array([self.w, self.h, self.w, self.h])
				(startX, startY, endX, endY) = box.astype("int")

				# extract the face ROI
				face = self.frame[startY:endY, startX:endX]
				(fH, fW) = face.shape[:2]
				# construct a blob for the face ROI, then pass the blob
				# through our face embedding model to obtain the 128-d
				# quantification of the face
				faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255,
					(96, 96), (0, 0, 0), swapRB=True, crop=False)
				self.embedder.setInput(faceBlob)
				vec = self.embedder.forward()
				
				# perform classification to recognize the face
				preds = self.recognizer.predict_proba(vec)[0]
				j = np.argmax(preds)
				proba = preds[j]
				self.name = self.le.classes_[j]

				# draw the bounding box of the face along with the
				# associated probability
				text = "{}: {:.2f}%".format(self.name, proba * 100)
				y = startY - 10 if startY - 10 > 10 else startY + 10
				cv2.rectangle(self.frame, (startX, startY), (endX, endY),
					(0, 0, 255), 2)
				cv2.putText(self.frame, text, (startX, y),
							cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
		except:
			pass

	def begin(self):
		self.frame = self.vs.read()
		self.frame = imutils.resize(self.frame, width=300)
		(self.h, self.w) = self.frame.shape[:2]
	
		# construct a blob from the image
		imageBlob = cv2.dnn.blobFromImage(
			cv2.resize(self.frame, (300, 300)), 1.0, (300, 300),
			(104.0, 177.0, 123.0), swapRB=False, crop=False)
	
		# apply OpenCV's deep learning-based face detector to localize
		# faces in the input image
		self.detector.setInput(imageBlob)
		self.detections = self.detector.forward()
		Process(target=cv2.imwrite, args=('db/person.jpg',self.frame)).start()
		task = []
		for i in range(0, self.detections.shape[2]):
			task.append(Thread(target=self.drawBondingBox, args=[i]))
			task[i].start()
			# extract the confidence (i.e., probability) associated with
			# the prediction
		for i in range(0, self.detections.shape[2]):
			task[i].join()
		return self.frame
	def getinfo(self):
		return self.name
	def stop(self):
		# stop the timer and display FPS information
		self.fps.stop()
		cv2.destroyAllWindows()
		# do a bit of cleanup
		self.vs.stop()