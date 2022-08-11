from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QTextEdit, QPushButton,QGroupBox
from PyQt5 import uic
from chatapp_ui import Chat
from notebook import Window
from heartsound import HeartSound
from RespiratoryCare import Resp
from hospital import Hospital

import sys


class UI(QMainWindow):
    def __init__(self,userid,uername):
        super(UI, self).__init__()

        # Load the ui file
        uic.loadUi("ui_file/sysmenu.ui", self)

        self.userid = userid
        self.uername = uername
        #self.uername = "admin"

        # Click
        self.heartsound_Button.clicked.connect(self.heartsoundapp)
        self.respiratory_Button.clicked.connect(self.respiratoryapp)
        self.chat_Button.clicked.connect(self.chatapp)
        self.notebook_Button.clicked.connect(self.notebookapp)
        self.hospital_Button.clicked.connect(self.hospital)

        self.username.setText(f"欢迎 {self.uername}")
        # Show The App
        self.show()


    def heartsoundapp(self):
        self.window = HeartSound()
        self.window.show()

    def respiratoryapp(self):
        self.window = Resp()
        self.window.show()

    #def xray(self):
        #self.window = XRay()
        #self.window.show()

    #def tongueapp(self):
        #self.window = Tongue()
        #self.window.show()

    def chatapp(self):
        self.window = Chat()
        self.window.show()

    def notebookapp(self):
        userid = self.userid
        self.window = Window(userid)
        self.window.show()

    def hospital(self):
        self.window = Hospital()
        self.window.show()

# Initialize The App
if __name__ == "__main__":

    app = QApplication(sys.argv)
    UIWindow = UI()
    UIWindow.show()
    app.exec_()


'''
        self.groupBox= self.findChild(QGroupBox, "groupBox")
        self.heartsound_Button = self.findChild(QPushButton, "heartsound_Button")
        self.respiratory_Button = self.findChild(QPushButton, "respiratory_Button")
        self.tongue_Button = self.findChild(QPushButton, "tongue_Button")
        self.chat_Button = self.findChild(QPushButton, "chat_Button")
        self.notebook_Button = self.findChild(QPushButton, "notebook_Button")
        self.hospital_Button = self.findChild(QPushButton, "hospital_Button")
        self.xray_Button = self.findChild(QPushButton, "xray_Button")
        self.username = self.findChild(QLabel, "username")
'''

