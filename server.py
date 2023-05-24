import os
import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread
from ui import server
import socket
from threading import Thread
from pyngrok import ngrok, conf


class ServerThread(QThread):
    '''
    пропишем конструктор, чтобы при инициализации класса можно было забрать данные айпи, порта 
    и ссылку на экземпляр главного класса, чтобы можно было контролировать textBrowser и вписывать
    туда данные при выполнении логики этого потока
    '''
    def __init__(self, IP_HOST, PORT,main):
        super().__init__()
        self.IP_HOST = IP_HOST
        self.PORT = int(PORT)
        self.main = main
        self.Stop = False

    
    #метод который и будет выполняться в потоке
    def run(self):
            separator_token = "<SEP>" # мы будем использовать его для разделения имени клиента и сообщения
            client_sockets = set() #в этом множестве будем хранить сокеты подключенных клиентов
            # создание TCP-сокета
            s = socket.socket()
            s.bind((self.IP_HOST, self.PORT)) # привязка сокета к указанному адресу
            #тут думаю всё понятно будет 
            self.main.textBrowser.append(f"[*] Слушаем {self.IP_HOST}:{self.PORT}") 
            # ожидание новых подключений
            s.listen()
            

            def listen_for_client(cs):
                """
                тут функция слушает сообщения от клиентов
                в цикле получаем сообщения от сокета cs если ошибка выводим и удаляем этот сокет
                из множества client_sockets
                """
                while True:
                    try:
                        # продолжаем прослушивать сообщения от сокета cs
                        msg = cs.recv(512).decode()
                    except Exception as e:
                        self.main.textBrowser.append(f"[!] Ошибка: {e}")
                        client_sockets.remove(cs)
                    else:
                        #в сообщении заменяем сепаратор на двоеточие чтобы было по типу (name: HELLO)     
                        msg = msg.replace(separator_token, ": ")
                    '''
                    перебераем в цикле каждый сокет из множества
                    отправляем полученное сообщение
                    итого каждый клиент получает сообщение принимаемое сервером
                    '''
                    for client_socket in client_sockets:                  
                        client_socket.send(msg.encode())
                        
                        
            while True:
                client_socket, client_address = s.accept()#серверный сокет возращает кортеж (сокет, адрес)
                self.main.textBrowser.append(f"[+] {client_address} подключился.")
                # добавляем нового подключенного клиента в список подключенных сокетов
                client_sockets.add(client_socket)
                '''
                запускаем новый поток, который прослушивает сообщения от каждого клиента
                делаем экземпляр класса Thread в таргет положим функцию которая слушает msg от клиентов
                в качество аргумента будет клиентский сокет. см аргумент cs в listen_for_client
                '''
                t = Thread(target=listen_for_client, args=(client_socket,))        
                t.daemon = True # делаем поток демоном        
                t.start() # запускаем поток

            # закрываем клиентские сокеты
            for cs in client_sockets:
                cs.close()
            # закрываем серверный сокет
            s.close()
  

class ExampleApp(QtWidgets.QMainWindow, server.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.start)
        self.pushButton_2.clicked.connect(self.tunel)     
        self.pushButton_3.clicked.connect(self.restart)    
        conf.get_default().region = 'eu'
        conf.get_default().ngrok_path = 'ngrok.exe'
        self.lineEdit.setText(socket.gethostbyname(socket.gethostname()))
        self.lineEdit_2.setFocus()
        self.ip.setText('IP tunel')
        self.port.setText('PORT tunel')
        self.setWindowIcon(QtGui.QIcon('./icon/server.ico'))
     
    def closeEvent(self,event):
        ngrok.kill()
                   
    def start(self):
        self.pushButton.setEnabled(False)       
        self.thread = ServerThread(self.lineEdit.text(), self.lineEdit_2.text(), self)
        self.thread.start()
    
    def tunel(self):
        ngrok.set_auth_token(self.lineEdit_3.text())
        try:
            self.tunnel = ngrok.connect(f'{self.lineEdit.text()}:{self.lineEdit_2.text()}', "tcp")
            self.pushButton_2.setEnabled(False)      
            # self.ip.setText(str(self.tunnel.public_url)[str(self.tunnel.public_url).find('//')+2:str(self.tunnel.public_url).find(':',5)])
            ip_ngrok = str(self.tunnel.public_url)[str(self.tunnel.public_url).find('//')+2:str(self.tunnel.public_url).find(':',5)]
            self.ip.setText(socket.gethostbyname(ip_ngrok))
            self.port.setText(str(self.tunnel.public_url)[str(self.tunnel.public_url).find(':',5)+1:])
        except Exception as e:
            QMessageBox.about(self, "Error", f'{e}')
    
    def restart(self):
        try:
            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            QMessageBox.about(self, "Error", f'{e}')
        
         
def main():
    app = QtWidgets.QApplication(sys.argv)  
    window = ExampleApp() 
    window.show()  
    app.exec_() 
    
    
if __name__ == '__main__':  
    main()  