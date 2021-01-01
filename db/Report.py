import mysql.connector
from datetime import datetime
import requests
from multiprocessing import Process
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
from time import sleep
from gpiozero import LED

red = LED(17) # Pin 11
yellow = LED(27) # Pin 13
blue = LED(22) # Pin 15
class LedStatus(QThread):
    status = pyqtSignal(int)
    def run(self):
        while True:
            # red.off()
            # yellow.off()
            # blue.off()
            sleep(15)

    @pyqtSlot(int)
    def recv(self, value):
        if(value == 0):
            print('LED merah')
            red.on()
        if(value == 1):
            yellow.on()
            red.on()
            print('LED kuning')
        if(value == 2):
            print('LED biru')
            blue.on()
            red.off()
            yellow.off()
            sleep(10)
            red.on()

led_status = LedStatus()
led_status.status.connect(led_status.recv)
led_status.start()

class Report(object):
    def __init__(self, chat_id, bot_token, db_ip, db_user, db_password):
        led_status.status.emit(0)
        self.lastname = None
        self.count = 0
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
        try:
            self.cursor.execute(f'SELECT * FROM tb_absen WHERE waktu REGEXP "{time}" AND nama="{name}"')
            if(self.cursor.fetchall() == []):
                return True
            else:
                return False
        except:
            print('check your database setting')
            pass
        
    def insert(self, name, temperature):
        print(f'count : {self.count}')
        if(name != 'unknown' and name != None):
            if(name == self.lastname):
                self.count = self.count+1
            else:
                self.count = 0
            self.lastname = name
            if(self.count >= 3):
                led_status.status.emit(2)
                self.count = 0
                if(self.__isAvailable(name)):
                        print(f"sending . .")
                        time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        sql = 'INSERT INTO tb_absen (nama, suhu, waktu) values (%s, %s, %s)'
                        val = (str(name), str(temperature), str(time))
                        try:
                            self.cursor.execute(sql,val)
                            self.db.commit()    
                        except:
                            print('check your db setting')
                            pass
                        p = Process(target=self.send, args=(name, temperature, time))
                        p.start()
                        led_status.status.emit(2)
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