import os
import sys 
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from ui import client 
import socket
from threading import Thread
from datetime import datetime

class ExampleApp(QtWidgets.QMainWindow, client.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.connect)
        self.pushButton_2.clicked.connect(self.send_msg)
        self.pushButton_3.clicked.connect(self.restart)
        self.s = socket.socket()
        self.pushButton_2.setShortcut("Return")
        self.setWindowIcon(QtGui.QIcon('./icon/chat.png'))
        
    
    def send_msg(self):
        NAME = self.lineEdit.text()
        if len(NAME) > 0:
            separator_token = "<SEP>" # мы будем использовать его для разделения имени клиента и сообщения
            # вводим сообщение, которое мы хотим отправить на сервер
            
            to_send = self.lineEdit_4.text()
            #получаем дату 
            date_now = datetime.now().strftime('%H:%M') 
            to_send = f"[{date_now}] {NAME}{separator_token}{to_send}"
            # наконец, отправляем сообщение
            self.s.send(to_send.encode())
            self.lineEdit_4.setText("")
        else:
            self.textBrowser.append('Введите имя')
        
               

    def connect(self):
        # IP-адрес сервера
        # если сервер не находится на этом компьютере, 
        # необходимо указать локальный (сетевой) IP-адрес (например, 192.168.1.2)
        IP_HOST = self.lineEdit_2.text()
        PORT = int(self.lineEdit_3.text())
        # инициализация TCP-сокета
        
        #print(f"[*] Подключаемся к {IP_HOST}:{PORT}...")
        self.textBrowser.append(f"[*] Подключаемся к {IP_HOST}:{PORT}...")
        #подключаемся к серверу     
        try:
            self.s.connect((IP_HOST, PORT))
            self.textBrowser.append("[+] Подключились")
            # запрашиваем у клиента имя
            #name = input("Введите ваше имя: ")

            def listen_for_messages():
                while True:
                    message = self.s.recv(512).decode()
                    self.textBrowser.append(message)

            # создаем поток, который слушает сообщения для этого клиента и выводит их
            # делаем поток демоном, чтобы он завершался, когда завершается основной поток
            # запускаем поток
            self.t = Thread(target=listen_for_messages)
            self.t.daemon = True
            self.t.start()      
        except:
            self.textBrowser.append("[-] Ошибка подключения")
            exit
    
    def restart(self):
        try:
            # app.exit(self.QMainWindow.EXIT_CODE_REBOOT )
            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            QMessageBox.about(self, "Error", f'{e}')
        
        
    

if __name__ == '__main__':  
    app = QtWidgets.QApplication(sys.argv)  
    window = ExampleApp() 
    window.show()  
    app.exec_() 