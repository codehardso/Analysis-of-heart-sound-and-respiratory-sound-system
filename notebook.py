from PyQt5.QtWidgets import *
from PyQt5 import uic,QtCore, QtGui, QtWidgets
import sys
import sqlite3


db = sqlite3.connect("userdata.db")
cursor = db.cursor()
cursor.execute("""CREATE TABLE if not exists tasks (userID INTEGER, task Text , completed Text, date Text, FOREIGN KEY (userID) REFERENCES login_info(ID))""")
db.commit()
db.close()

class Window(QMainWindow):
    def __init__(self,userid):
        super(Window, self).__init__()

        # Load the ui file
        uic.loadUi("ui_file/notebook.ui", self)
        self.userid = userid
        #self.userid = userid


        # Do something
        self.calendarWidget.selectionChanged.connect(self.calendarDateChanged)
        self.calendarDateChanged()
        self.saveButton.clicked.connect(self.saveChanges)
        self.addButton.clicked.connect(self.addNewTask)
        self.deleteButton.clicked.connect(self.delete_it)

        # Show The App
        self.show()



    def calendarDateChanged(self):
        print("The calendar date was changed.")
        dateSelected = self.calendarWidget.selectedDate().toPyDate()
        print("Date selected:", dateSelected)
        self.updateTaskList(dateSelected)

    def updateTaskList(self, date):
        self.tasksListWidget.clear()

        db = sqlite3.connect("userdata.db")
        cursor = db.cursor()
        userid = self.userid
        query = "SELECT task, completed FROM tasks WHERE date = ? AND userid = ?"
        row = (date, userid, )
        results = cursor.execute(query, row).fetchall()
        for result in results:
            item = QListWidgetItem(str(result[0]))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            if result[1] == "YES":
                item.setCheckState(QtCore.Qt.Checked)
            elif result[1] == "NO":
                item.setCheckState(QtCore.Qt.Unchecked)
            self.tasksListWidget.addItem(item)

    def saveChanges(self):
        db = sqlite3.connect("userdata.db")
        cursor = db.cursor()
        date = self.calendarWidget.selectedDate().toPyDate()

        for i in range(self.tasksListWidget.count()):
            item = self.tasksListWidget.item(i)
            task = item.text()
            if item.checkState() == QtCore.Qt.Checked:
                query = "UPDATE tasks SET completed = 'YES' WHERE task = ? AND date = ?"
            else:
                query = "UPDATE tasks SET completed = 'NO' WHERE task = ? AND date = ?"
            row = (task, date,)
            cursor.execute(query, row)
        db.commit()

        messageBox = QMessageBox()
        messageBox.setText("保存成功！")
        messageBox.setStandardButtons(QMessageBox.Ok)
        messageBox.exec()

    def addNewTask(self):
        db = sqlite3.connect("userdata.db")
        cursor = db.cursor()

        newTask = str(self.taskLineEdit.text())
        date = self.calendarWidget.selectedDate().toPyDate()
        userID = int(self.userid)
        query = "INSERT INTO tasks(userID, task, completed, date) VALUES (?,?,?,?)"
        row = (userID, newTask, "NO", date,)

        cursor.execute(query, row)
        db.commit()
        self.updateTaskList(date)
        self.taskLineEdit.clear()

    def delete_it(self):
        # Grab the selected row or current row
        clicked = self.tasksListWidget.currentRow()
        # Delete selected row
        self.tasksListWidget.takeItem(clicked)

        db = sqlite3.connect("userdata.db")
        cursor = db.cursor()
        date = self.calendarWidget.selectedDate().toPyDate()

        query = "DELETE FROM tasks WHERE  date = ?"
        row = (date,)
        cursor.execute(query, row)
        db.commit()
        self.updateTaskList(date)
        self.taskLineEdit.clear()
        messageBox = QMessageBox()
        messageBox.setText("删除成功！")
        messageBox.setStandardButtons(QMessageBox.Ok)
        messageBox.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())

    '''
            # Define Our Widgets
        self.saveButton = self.findChild(QPushButton, "saveButton")
        self.addButton = self.findChild(QPushButton, "addButton")
        self.taskLineEdit = self.findChild(QLineEdit, "taskLineEdit")
        self.tasksListWidget = self.findChild(QListWidget, "tasksListWidget")
        self.calendarWidget = self.findChild(QCalendarWidget, "calendarWidget")
        self.deleteButton = self.findChild(QPushButton, "deleteButton")
    '''