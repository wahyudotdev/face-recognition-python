from ui.MainWindow import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
from core.Enroll import Enroll
from core.PreviewCamera import PreviewCamera
import sys
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
# PyQt5 window class defined here
app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
DialogWindow = QtWidgets.QInputDialog()
ui = Ui_MainWindow()
pv = PreviewCamera(2)


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        while self._run_flag:
            self.change_pixmap_signal.emit(pv.begin())
        pv.stop()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

class MainApp(QtWidgets.QWidget):

    def dialog(self):
        text, okPressed = DialogWindow.getText(None, "Specify User Name",
                                                "Enter name :",
                                                QtWidgets.QLineEdit.Normal)
        if(okPressed):
            print('p')
            self.closeEvent()

    @pyqtSlot(np.ndarray)
    def showVideo(self, cv_image):
        ui.camera.setPixmap(QtGui.QPixmap.fromImage(self.convertCvToPixmap(cv_image)))

    def convertCvToPixmap(self,img):
        return QtGui.QImage(img, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()

    def setupWindow(self):
        ui.setupUi(MainWindow)
        ui.pbAddUser.clicked.connect(self.dialog)
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.showVideo)
        self.thread.start()
        MainWindow.show()
    def closeEvent(self):
        self.thread.stop()

if __name__ == "__main__":
    window = MainApp()
    window.setupWindow()
    sys.exit(app.exec_())