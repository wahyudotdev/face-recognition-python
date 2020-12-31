# import the necessary packages
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from imutils import paths
import numpy as np
import imutils
import pickle
import cv2
import os
 
class TrainModel(object):
    def __init__(self):
        print("[INFO] loading face self.detector...")
        self.protoPath = os.path.sep.join(["core/face_detection_model", "deploy.prototxt"])
        self.modelPath = os.path.sep.join(["core/face_detection_model",
            "res10_300x300_ssd_iter_140000.caffemodel"])
        self.detector = cv2.dnn.readNetFromCaffe(self.protoPath, self.modelPath)
        
        # load our serialized face embedding model from disk
        print("[INFO] loading face recognizer...")
        self.embedder = cv2.dnn.readNetFromTorch("core/openface_nn4.small2.v1.t7")
        # grab the paths to the input images in our dataset
        print("[INFO] quantifying faces...")
        self.imagePaths = list(paths.list_images("core/dataset"))
        
        # initialize our lists of extracted facial embeddings and
        # corresponding people names
        self.knownEmbeddings = []
        self.knownNames = []
        self.threshold = 0.99
        # initialize the self.total number of faces processed
        self.total = 0
    
    def extractEmbedding(self):
        # loop over the image paths
        for (i, imagePath) in enumerate(self.imagePaths):
            # extract the person name from the image path
            print("[INFO] processing image {}/{}".format(i + 1,
                len(self.imagePaths)))
            name = imagePath.split(os.path.sep)[-2]
        
            # load the image, resize it to have a width of 600 pixels (while
            # maintaining the aspect ratio), and then grab the image
            # dimensions
            image = cv2.imread(imagePath)
            image = imutils.resize(image, width=600)
            (h, w) = image.shape[:2]
            # construct a blob from the image
            imageBlob = cv2.dnn.blobFromImage(
                cv2.resize(image, (300, 300)), 1.0, (300, 300),
                (104.0, 177.0, 123.0), swapRB=False, crop=False)
        
            # apply OpenCV's deep learning-based face self.detector to localize
            # faces in the input image
            self.detector.setInput(imageBlob)
            detections = self.detector.forward()
                # ensure at least one face was found
            if len(detections) > 0:
                # we're making the assumption that each image has only ONE
                # face, so find the bounding box with the largest probability
                i = np.argmax(detections[0, 0, :, 2])
                confidence = detections[0, 0, i, 2]

                # ensure that the detection with the largest probability also
                # means our minimum probability test (thus helping filter out
                # weak detections)
                if confidence > self.threshold:
                    # compute the (x, y)-coordinates of the bounding box for
                    # the face
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                    # extract the face ROI and grab the ROI dimensions
                    face = image[startY:endY, startX:endX]
                    (fH, fW) = face.shape[:2]

                    # ensure the face width and height are sufficiently large
                    if fW < 20 or fH < 20:
                        continue
                                    # construct a blob for the face ROI, then pass the blob
                    # through our face embedding model to obtain the 128-d
                    # quantification of the face
                    faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255,
                        (96, 96), (0, 0, 0), swapRB=True, crop=False)
                    self.embedder.setInput(faceBlob)
                    vec = self.embedder.forward()

                    # add the name of the person + corresponding face
                    # embedding to their respective lists
                    self.knownNames.append(name)
                    self.knownEmbeddings.append(vec.flatten())
                    self.total += 1
                    # dump the facial embeddings + names to disk
        print("[INFO] serializing {} encodings...".format(self.total))
        data = {"embeddings": self.knownEmbeddings, "names": self.knownNames}
        f = open("core/output/embeddings.pickle", "wb")
        f.write(pickle.dumps(data))
        f.close()
        return True

    def beginTraining(self):
        data = pickle.loads(open("core/output/embeddings.pickle", "rb").read())
        print("[INFO] encoding labels...")
        le = LabelEncoder()
        labels = le.fit_transform(data["names"])
        sk_recognizer = SVC(C=1.0, kernel="linear", probability=True)
        sk_recognizer.fit(data["embeddings"], labels)
        f = open("core/output/recognizer.pickle", "wb")
        f.write(pickle.dumps(sk_recognizer))
        f.close()
        # write the label encoder to disk
        f = open("core/output/le.pickle", "wb")
        f.write(pickle.dumps(le))
        f.close()
        print("[INFO] Training finished...")
        return True