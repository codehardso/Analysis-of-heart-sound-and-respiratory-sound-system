import sqlite3

db = sqlite3.connect("userdata.db")
cursor = db.cursor()
cursor.execute("SELECT * FROM login_info")
#cursor.execute("SELECT * FROM tasks")
records = cursor.fetchall()

re = cursor.fetchone()
db.commit()
db.close()
for record in records:
    print("infomation:"+str(record))
    #print("id = "+str(record[0]))
    #print("username:"+str(record[1]))
    #print("password: "+str(record[2]))