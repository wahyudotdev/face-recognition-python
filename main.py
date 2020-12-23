from ui.MainWindow import Ui_MainWindow
from ui.EnrollWindow import Ui_EnrollWindow
from PyQt5 import QtCore, QtGui, QtWidgets
from core.Enroll import Enroll
from core.WebcamVideoStream import WebcamVideoStream
from core.PreviewCamera import PreviewCamera
from core.FaceRecognition import FaceRecognitionVideo
from core.Enroll import Enroll
import sys
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
from time import sleep
# PyQt5 window class defined here
app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
DialogWindow = QtWidgets.QInputDialog()
EnrollWindow = QtWidgets.QMainWindow()

ui = Ui_MainWindow()
enroll = Ui_EnrollWindow()

class EnrollVideoThread(QThread):
    enroll_pixmap = pyqtSignal(np.ndarray)
    def __init__(self, camera, username):
        super().__init__()
        self.camera = camera
        self.username = username

    def run(self):
        webcam = WebcamVideoStream(src=self.camera).start()
        self.enr = Enroll(webcam, self.username)
        self._run_flag = True
        while self._run_flag:
            self.enroll_pixmap.emit(self.enr.begin())
        self.enr.stop()
    
    def again(self):
        self._run_flag = True
    def capture(self):
        self.enr.capture()
    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    def __init__(self, camera):
        super().__init__()
        self.camera = camera

    def run(self):
        webcam = WebcamVideoStream(src=self.camera).start()
        self.pv = FaceRecognitionVideo(webcam)
        self._run_flag = True
        while self._run_flag:
            self.change_pixmap_signal.emit(self.pv.begin())
        self.pv.stop()
    
    def again(self):
        self._run_flag = True

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

class TesThread(QThread):
    def run(self):
        for i in range(10):
            print(i)
            sleep(0.5)
        print('tes thread finished')


class MainApp(QtWidgets.QApplication):
    def __init__(self, *args):
        super(MainApp, self).__init__(*args)
        self.setQuitOnLastWindowClosed(True)
        self.aboutToQuit.connect(self.onLastClosed)
        self.lastWindowClosed.connect(self.destroyInstance)

    def destroyInstance(self):
        try:
            self.enrollVideoThread.stop()
        except:
            print('destroy error')
            pass
        finally:
            print('destroy instance')

    def onLastClosed(self):
        print("exiting ...")
        self.exit()
    
    @pyqtSlot(np.ndarray)
    def showEnrollVideo(self, cv_image):
        enroll.camera.setPixmap(QtGui.QPixmap.fromImage(self.convertCvToPixmap(cv_image)))

    def destroyEnrollWindows(self):
        print('destroyed')

    def enrollUserWindow(self, name):
        enroll.setupUi(EnrollWindow)
        EnrollWindow.setWindowTitle(f'Registering {name}')
        self.enrollVideoThread = EnrollVideoThread(2, name)
        self.enrollVideoThread.enroll_pixmap.connect(self.showEnrollVideo)
        self.enrollVideoThread.start()
        enroll.pbCapture.clicked.connect(self.enrollVideoThread.capture)
        EnrollWindow.show()


    def dialog(self):
        text, okPressed = DialogWindow.getText(None, "Specify User Name",
                                                "Enter name :",
                                                QtWidgets.QLineEdit.Normal)
        if(okPressed):
            try:
                self.videothread.stop()
            except:
                print('Skip Error')
            finally:
                self.enrollUserWindow(text)
    @pyqtSlot(np.ndarray)
    def showVideo(self, cv_image):
        ui.camera.setPixmap(QtGui.QPixmap.fromImage(self.convertCvToPixmap(cv_image)))

    def convertCvToPixmap(self,img):
        return QtGui.QImage(img, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()

    def runVideoThread(self):
        self.videothread = VideoThread(2)
        if(self.videothread.isFinished):
            self.videothread.change_pixmap_signal.connect(self.showVideo)
            self.videothread.start()

    def setupWindow(self):
        ui.setupUi(MainWindow)
        ui.pbAddUser.clicked.connect(self.dialog)
        ui.pbStart.clicked.connect(self.runVideoThread)
        MainWindow.show()
    def closeEvent(self):
        pv.stop()
        self.videothread.stop()
    def beforeQuit(self):
        print('Quit')
        self.exit()

if __name__ == "__main__":
    window = MainApp([])
    window.setupWindow()
    sys.exit(app.exec_())