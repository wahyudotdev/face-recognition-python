from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox
class Ui_ConfirmDialog(QWidget):

    def __init__(self, title, content):
        super().__init__()
        self.title = title
        self.left = 100
        self.top = 100
        self.width = 320
        self.height = 200
        self.content = content
        self.initUI()
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.buttonReply = QMessageBox.question(self, self.title, self.content, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if self.buttonReply == QMessageBox.Yes:
            self.isAccepted = True
        else:
            self.isAccepted = False

        self.show()