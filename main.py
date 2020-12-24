from ui.MainWindow import Ui_MainWindow
from ui.EnrollWindow import Ui_EnrollWindow
from ui.ConfirmDialog import Ui_ConfirmDialog
from ui.UserListWindow import Ui_UserList

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread



from core.Enroll import Enroll
from core.WebcamVideoStream import WebcamVideoStream
from core.FaceRecognition import FaceRecognitionVideo
from core.Enroll import Enroll
from core.TrainModel import TrainModel

import sys
import numpy as np
from time import sleep
import pickle
import os
import shutil
# PyQt5 window class defined here
app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
DialogWindow = QtWidgets.QInputDialog()
EnrollWindow = QtWidgets.QMainWindow()
UserListWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
enroll = Ui_EnrollWindow()
userlist = Ui_UserList()
class EnrollVideoThread(QThread):
    enroll_pixmap = pyqtSignal(np.ndarray)
    enroll_count = pyqtSignal(int)
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
        # self.enr.capture()
        self.enroll_count.emit(self.enr.capture())

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    detected_person = pyqtSignal(str)
    def __init__(self, camera):
        super().__init__()
        self.camera = camera
    def run(self):
        webcam = WebcamVideoStream(src=self.camera).start()
        self.pv = FaceRecognitionVideo(webcam)
        self._run_flag = True
        while self._run_flag:
            self.change_pixmap_signal.emit(self.pv.begin())
            self.detected_person.emit('Nama : '+self.pv.getinfo()+'\nSuhu : 30 C')
        self.pv.stop()
    
    def again(self):
        self._run_flag = True

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

class TrainingThread(QThread):

    train_signal = pyqtSignal(bool, name='trainingfinished')
    def run(self):
        t = TrainModel()
        if(t.extractEmbedding()):
            self.train_signal.emit(t.beginTraining())

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

    def enrollUserWindow(self, name):
        enroll.setupUi(EnrollWindow)
        EnrollWindow.setWindowTitle(f'Registering {name}')
        self.enrollVideoThread = EnrollVideoThread(2, name)
        self.enrollVideoThread.enroll_pixmap.connect(self.showEnrollVideo)
        self.enrollVideoThread.enroll_count.connect(self.changeCountEnroll)
        self.enrollVideoThread.start()
        enroll.pbCapture.clicked.connect(self.enrollVideoThread.capture)
        EnrollWindow.show()

    @pyqtSlot(int)
    def changeCountEnroll(self, value):
        enroll.pbCapture.setText(f'{value} Captured')

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

    @pyqtSlot(str)
    def setInfo(self, info):
        ui.label_info.setText(info)

    def runVideoThread(self):
        self.videothread = VideoThread(2)
        if(self.videothread.isFinished):
            self.videothread.change_pixmap_signal.connect(self.showVideo)
            self.videothread.detected_person.connect(self.setInfo)
            self.videothread.start()

    def confirmDialog(self):
        confirm = Ui_ConfirmDialog('Re-Train Dataset','Do you want to re-train your dataset?')
        confirm.show()
        if(confirm.isAccepted):
            print('gassss training')
            if(self.trainingThread.isFinished):
                self.trainingThread.start()
            if(self.trainingThread.isRunning):
                print('already running')

    def isTrainingFinished(self):
        print('[INFO] Training Finished with code 0')


    def selectItem(self, item):
        self.selected_user = str(item.data(0))
        print(item.data(0))

    def refreshUser(self):
        files = []
        for dirname, dirnames, filenames in os.walk('core/dataset'):
                    for subdirname in dirnames:
                        files.append(os.path.join(dirname, subdirname))
        userlist.listWidget.addItems(files)

    def deleteUser(self):
        if(self.selected_user is not None):
            confirm = Ui_ConfirmDialog('Delete User','Are you sure?')
            confirm.show()
            if(confirm.isAccepted):
                try:
                    shutil.rmtree(self.selected_user)
                    print('deleted : '+self.selected_user)
                except OSError as e:
                    print("Error: %s : %s" % (self.selected_user, e.strerror))
                
                userlist.listWidget.takeItem(userlist.listWidget.currentRow())
    
    def userList(self):
        userlist.setupUi(UserListWindow)
        userlist.listWidget.itemClicked.connect(self.selectItem)
        userlist.pbDeleteUser.clicked.connect(self.deleteUser)
        self.selected_user = None
        self.refreshUser()
        UserListWindow.show()
        

    def setupWindow(self):
        ui.setupUi(MainWindow)
        ui.pbAddUser.clicked.connect(self.dialog)
        ui.pbStart.clicked.connect(self.runVideoThread)
        ui.pbTrain.clicked.connect(self.confirmDialog)
        ui.pbListUser.clicked.connect(self.userList)
        self.trainingThread = TrainingThread()
        self.trainingThread.train_signal.connect(self.isTrainingFinished)

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