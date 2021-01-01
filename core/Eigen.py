import cv2
import numpy as np
class Eigen(object):
    def __init__(self):
        	# Number of EigenFaces
        NUM_EIGEN_FACES = 10

        # Maximum weight
        MAX_SLIDER_VALUE = 255

        # Directory containing images
        dirName = "core/dataset/"

        # Read images
        images = readImages(dirName)
        
        # Size of images
        sz = images[0].shape

        # Create data matrix for PCA.
        data = createDataMatrix(images)
        mean, eigenVectors = cv2.PCACompute(data, mean=None, maxComponents=NUM_EIGEN_FACES)
        averageFace = mean.reshape(sz)
        eigenFaces = []; 
        for eigenVector in eigenVectors:
            eigenFace = eigenVector.reshape(sz)
            eigenFaces.append(eigenFace)

        output = cv2.resize(averageFace, (0,0), fx=2, fy=2)
        return images