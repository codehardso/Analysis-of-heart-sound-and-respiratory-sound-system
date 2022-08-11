import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QMessageBox
from sysmenu import UI
import sqlite3


class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("ui_file/welcomescreen.ui",self)
        self.login.clicked.connect(self.gotologin)
        self.create.clicked.connect(self.gotocreate)
        self.quit.clicked.connect(self.quitprogram)

    def quitprogram(self):
        exit()

    def gotologin(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotocreate(self):
        create = CreateAccScreen()
        widget.addWidget(create)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("ui_file/login.ui",self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginfunction)
        self.back.clicked.connect(self.backmain)
        #self.userID = []

    def loginfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()

        if len(user)==0 or len(password)==0:
            self.error.setText("Please input all fields.")

        else:
            conn = sqlite3.connect("userdata.db")
            cur = conn.cursor()
            query = 'SELECT password, ID FROM login_info WHERE username =\''+user+"\'"
            queryid = 'SELECT ID FROM login_info WHERE username =\''+user+"\'"
            cur.execute(query)
            resu = cur.fetchone()
            print('resuinfo:',resu)
            result_pass =  resu[0]
            if result_pass == password:
                print("Successfully logged in.")
                #cur.execute(queryid)
                userid = resu[1]
                self.userid =  resu[1]
                print("username:", user)
                print("id:", self.userid)
                print("result_pass:", result_pass)
                #self.userID.append(self.userid)
                #print("idd:",self.userID)
                self.error.setText("")
                # Pop up box
                msg = QMessageBox()
                msg.setWindowTitle("提示：")
                msg.setText("登陆成功!")
                msg.setIcon(QMessageBox.Information)
                x = msg.exec_()

                #login.hide()
                login = LoginScreen()
                widget.addWidget(login)
                widget.hide()

                self.window = QtWidgets.QMainWindow()
                self.ui = UI(userid,user)

                #旧的连接方式
                #self.window = QtWidgets.QMainWindow()
                #self.ui = UI(userid)

                print("ok!")
                #self.ui.setupUi(self.window)
                #self.window.show()
                #self.ui.userID = self.userid
                #return self.userid
            else:
                self.error.setText("Invalid username or password")


    def backmain(self):
        mainwidow = WelcomeScreen()
        widget.addWidget(mainwidow)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class CreateAccScreen(QDialog):
    def __init__(self):
        super(CreateAccScreen, self).__init__()
        loadUi("ui_file/createacc.ui",self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpasswordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup.clicked.connect(self.signupfunction)
        self.back.clicked.connect(self.backmain)

    def signupfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()
        confirmpassword = self.confirmpasswordfield.text()

        if len(user)==0 or len(password)==0 or len(confirmpassword)==0:
            self.error.setText("Please fill in all inputs.")

        elif password!=confirmpassword:
            self.error.setText("Passwords do not match.")
        else:
            conn = sqlite3.connect("userdata.db")
            cur = conn.cursor()

            cur.execute("""CREATE TABLE if not exists login_info( ID INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password TEXT NOT NULL)""")

            user_info = [user, password]
            cur.execute('INSERT INTO login_info (username, password) VALUES (?,?)', user_info)

            conn.commit()
            conn.close()
            print("Successfully sign up.")
            # Pop up box
            msg = QMessageBox()
            msg.setWindowTitle("提示：")
            msg.setText("注册成功!请返回菜单登录！")
            msg.setIcon(QMessageBox.Information)
            x = msg.exec_()
            #fillprofile = FillProfileScreen()
            #widget.addWidget(fillprofile)
            #widget.setCurrentIndex(widget.currentIndex()+1)

    def backmain(self):
        mainwidow = WelcomeScreen()
        widget.addWidget(mainwidow)
        widget.setCurrentIndex(widget.currentIndex() + 1)

# main
app = QApplication(sys.argv)
welcome = WelcomeScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(welcome)
widget.setFixedHeight(800)
widget.setFixedWidth(1200)
widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")
