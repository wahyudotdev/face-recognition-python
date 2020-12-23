from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox
class Ui_ConfirmDialog(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Re-Train dataset'
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 200
        self.initUI()
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.buttonReply = QMessageBox.question(self, 'Re-Train dataset', "Do you want to re-train dataset?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if self.buttonReply == QMessageBox.Yes:
            self.isAccepted = True
        else:
            self.isAccepted = False

        self.show()