import mysql.connector
from datetime import datetime
import requests
from multiprocessing import Process
class Report(object):
    def __init__(self, chat_id, bot_token, db_ip, db_user, db_password):
        self.lastname = None
        self.bot_token = bot_token
        self.chat_id = chat_id
        try:
            self.db = mysql.connector.connect(
                host = db_ip,
                user = db_user,
                passwd = db_password,
                database = "db_absen"
            )
            self.cursor = self.db.cursor()
            print('=== Database connected ===')
        except:
            print('=== Failed connect to database ===')
    def __isAvailable(self,name):
        time = datetime.now().strftime("%d/%m/%Y")
        self.cursor.execute(f'SELECT * FROM tb_absen WHERE waktu REGEXP "{time}" AND nama="{name}"')
        if(self.cursor.fetchall() == []):
            return True
        else:
            return False
        
    def insert(self, name, temperature):
        if(self.__isAvailable(name) and name != 'unknown'):
            time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            sql = 'INSERT INTO tb_absen (nama, suhu, waktu) values (%s, %s, %s)'
            val = (str(name), str(temperature), str(time))
            self.cursor.execute(sql,val)
            self.db.commit()      
            p = Process(target=self.send, args=(name, temperature, time))
            p.start()
            return True
        else:
            # print("Telah absen")
            return False
    def send(self, name, temperature, time):
        url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
        message = f'Nama : {name}\nSuhu : {temperature}°C\nWaktu : {time}'
        obj = {f'chat_id': self.chat_id,'caption':message}
        files = {'photo': ('person.jpg', open('db/person.jpg', 'rb'), {'Expires': '0'})}
        r = requests.post(url=url, data=obj, files=files)

# r = Report("1123810574", "1096181817:AAFAdvG8exQgYiF6q6s3g2pWGwNBwLsUHa4",'localhost','root','raspberry')
# print(r.insert("Wahyu", "33"))