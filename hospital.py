from PyQt5.QtWidgets import *
from PyQt5 import uic,QtCore, QtGui, QtWidgets
import sys
import requests
from bs4 import BeautifulSoup
import csv
import time
import background


class Hospital(QMainWindow):
    def __init__(self):
        super(Hospital, self).__init__()

        # Load the ui file
        uic.loadUi("ui_file/hospital.ui", self)

        # Do something
        self.seekButton.clicked.connect(self.seek)
        self.clrButton.clicked.connect(self.clrline)
        self.csvButton.clicked.connect(self.savecsvdata)

        # Show The App
        #self.show()



    def seek(self):
       # self.textBrowser.append("开始查找数据……")
        #self.note12()
        # position = "山西省"
        #position = input("请输入查询地点：")
        position = str(self.lineEdit.text())
        city = (self.cityEdit.text())
        url = f"https://www.zgylbx.com/index.php?m=content&c=index&a=lists&catid=106&steps=&search=1&pc_hash=&k1={position}&k2=0&k3=0&title="
        page = requests.get(url).text
        doc = BeautifulSoup(page, "html.parser")

        page_text_text = doc.find(class_="dpgpages2-m1")
        page_text = page_text_text.find_all('a')
        page_num = page_text_text.find(class_='a1').text
        pagestext = (page_text[-2])

        pages = int(str(pagestext).split("/")[-2].split(">")[-1][:-1])

        self.textBrowser.clear()
        rows = [["医院名称", '省份', '城市', "医院等级", '擅长病症', '医院地址', '医院电话', '医院邮箱', '医院网站']]

        self.textBrowser.append(f"{position}共{page_num}医院数据")
        self.textBrowser.append("----------------------------------------------------")


        for page in range(1, pages + 1):
            url = f"https://www.zgylbx.com/index.php?m=content&c=index&a=lists&page={page}&catid=106&steps=&search=1&pc_hash=&k1={position}&k2=0&k3=0&title="
            page = requests.get(url).text
            doc = BeautifulSoup(page, "html.parser")

            message = doc.find_all('tr')
            # print(message)

            rows.extend(self.get_rows(message,city))
            self.rows = rows
        self.textBrowser.append("查询结束")

    def get_rows(self,msg,city):
        row_list = []
        row = []
        sub_row = False
        i = 0
        for line in msg[1:]:
            data = line.find_all('td')
            if not sub_row:
                prov_city = data[1].text.strip().split('-')
                row = [
                    data[0].text,
                    prov_city[0],
                    prov_city[1],
                    data[2].text,
                    data[3].text
                ]
                name = data[0].text
                rank = data[2].text
                advantage = data[3].text
                sub_row = True
            else:
                data = str(data[0]).split('<br/>')
                add = data[0].strip().split('医院地址:')[-1]
                tel = data[1].strip().split('医院电话:')[-1]
                mail = data[2].strip().split('医院邮箱:')[-1]
                site = data[3].strip().split('医院网站:')[-1][:-5]
                row.extend([add, tel, mail, site])
                row_list.append(row)
                sub_row = False


                if city :
                    if prov_city[1]==str(city):

                        self.textBrowser.append(f"医院名称:{name}")
                        self.textBrowser.append(f"省份:{prov_city[0]}")
                        self.textBrowser.append(f"城市:{prov_city[1]}")
                        self.textBrowser.append(f"医院等级:{rank}")
                        self.textBrowser.append(f"擅长病症:{advantage}")
                        self.textBrowser.append(f"医院地址:{add}")
                        self.textBrowser.append(f"医院电话:{tel}")
                        self.textBrowser.append(f"医院邮箱:{mail}")
                        self.textBrowser.append(f"医院网站:{site}\n")
                        self.textBrowser.append("----------------------------------------------------")

                else:

                    self.textBrowser.append(f"医院名称:{name}")
                    self.textBrowser.append(f"省份:{prov_city[0]}")
                    self.textBrowser.append(f"城市:{prov_city[1]}")
                    self.textBrowser.append(f"医院等级:{rank}")
                    self.textBrowser.append(f"擅长病症:{advantage}")
                    self.textBrowser.append(f"医院地址:{add}")
                    self.textBrowser.append(f"医院电话:{tel}")
                    self.textBrowser.append(f"医院邮箱:{mail}")
                    self.textBrowser.append(f"医院网站:{site}\n")
                    self.textBrowser.append("----------------------------------------------------")

        #if i:
            #self.textBrowser.append(f"{city}共{i}条医院数据")

        self.row_list = row_list
        return self.row_list

    def clrline(self):
        self.lineEdit.setText('')
        self.textBrowser.setText('')
        self.cityEdit.setText('')

    def savecsvdata(self):
        date = str(time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()))
        name = "hospital_" + date + ".csv"
        with open(name, 'w') as f:
            write = csv.writer(f)
            write.writerows(self.rows)
            msg = QMessageBox()
            msg.setWindowTitle("提示：")
            msg.setText("保存成功!")
            msg.setIcon(QMessageBox.Information)
            x = msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Hospital()
    window.show()
    sys.exit(app.exec())


'''
        # Define Our Widgets
        self.seekButton = self.findChild(QPushButton, "seekButton")
        self.clrButton = self.findChild(QPushButton, "clrButton")
        self.csvButton = self.findChild(QPushButton, "csvButton")
        self.lineEdit = self.findChild(QLineEdit, "lineEdit")
        self.textBrowser = self.findChild(QTextBrowser, "textBrowser")
        self.calendarWidget = self.findChild(QCalendarWidget, "calendarWidget")
        self.cityEdit = self.findChild(QLineEdit, "cityEdit")

'''