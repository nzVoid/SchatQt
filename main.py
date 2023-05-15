import sys
import typing 
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from ui import server
import socket
from threading import Thread

class ServerThread(QThread):
    '''
    пропишем конструктор, чтоюы при инициализации класса можно было забрать данные айпи, порта 
    и ссылку на экземпляр главного класса, чтобы можно было контролировать textBrowser и вписывать
    туда данные при выполнении логики этого потока
    '''
    def __init__(self, IP_HOST, PORT,main):
        super().__init__()
        self.IP_HOST = IP_HOST
        self.PORT = int(PORT)
        self.main = main

    '''
    метод создаёт сокет 
    '''    
    def run(self):
        separator_token = "<SEP>" # мы будем использовать его для разделения имени клиента и сообщения
        # инициализация списка/множества всех подключенных клиентских сокетов
        client_sockets = set()
        # создание TCP-сокета
        s = socket.socket()
        # привязка сокета к указанному адресу
        s.bind((self.IP_HOST, self.PORT))
        self.main.textBrowser.append(f"[*] Слушаем {self.IP_HOST}:{self.PORT}")
        # ожидание новых подключений
        s.listen()
        

        def listen_for_client(cs):
            """
            Эта функция продолжает прослушивать сообщения от сокета cs
            Когда сообщение получено, широковещает его всем подключенным клиентам
            """
            while True:
                try:
                    # продолжаем прослушивать сообщения от сокета cs
                    msg = cs.recv(512).decode()
                except Exception as e:
                    self.main.textBrowser.append(f"[!] Ошибка: {e}")
                    client_sockets.remove(cs)
                else:
                    '''
                    если мы получили сообщение, заменяем токен <SEP> 
                    двоеточием и пробелом для красивого вывода
                    '''      
                    msg = msg.replace(separator_token, ": ")
                # перебираем все подключенные сокеты
                for client_socket in client_sockets:
                    # и отправляем сообщение
                    client_socket.send(msg.encode())


        while True:
            # продолжаем прослушивать новые подключения все время
            client_socket, client_address = s.accept()
            self.main.textBrowser.append(f"[+] {client_address} подключился.")
            # добавляем нового подключенного клиента в список подключенных сокетов
            client_sockets.add(client_socket)
            # запускаем новый поток, который прослушивает сообщения от каждого клиента
            t = Thread(target=listen_for_client, args=(client_socket,))
            # делаем поток демоном
            t.daemon = True
            # запускаем поток
            t.start()

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
    
    def start(self):
        self.pushButton.setEnabled(False)
        self.thread = ServerThread(self.lineEdit.text(), self.lineEdit_2.text(), self)
        self.thread.start()    
    
        
def main():
    app = QtWidgets.QApplication(sys.argv)  
    window = ExampleApp() 
    window.show()  
    app.exec_() 
    
    
if __name__ == '__main__':  
    main()  