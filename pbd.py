import socket
import time
import sys
from datetime import datetime
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication
from UI import Ui_MainWindow

HOST_IP = "192.168.56.1"
HOST_PORT = 1234
global stop_logic
stop_logic = 0

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__() 
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_control()

    def setup_control(self):
        self.ui.button_start.clicked.connect(self.start_buttonClicked)
        self.ui.button_reset.clicked.connect(self.reset_buttonClicked)
        self.ui.button_connect.clicked.connect(self.connect_buttonClicked)

        self.qthread = ThreadTask()
        self.qthread.qthread_signal.connect(self.text_update) 
        

    def connect_buttonClicked(self):
        self.qthread.tcp_server()

    def start_buttonClicked(self):
        global stop_logic
        stop_logic = 0

    def reset_buttonClicked(self):
        global stop_logic
        stop_logic = 1
        
    def text_update(self, value):
        global stop_logic
        QApplication.processEvents()
        print(value)
        currentDateTime= datetime.now()
        currentTime= currentDateTime.strftime("%Y-%m-%d %H:%M:%S")
        if stop_logic == 0:
            if value <5:
                self.ui.alert_label.setStyleSheet("background-color: rgb(87, 255, 49)")
                self.ui.alert_label.setText("L")    
            elif value >= 5: 
                if value <= 25:
                    self.ui.alert_label.setStyleSheet("background-color: rgb(255, 195, 0)")
                    self.ui.alert_label.setText("M")
                    self.ui.textBrowser.append(currentTime+ "-Medium %d" %(value))
                elif value >25:
                    self.ui.alert_label.setStyleSheet("background-color: rgb(255, 9, 0)")
                    self.ui.alert_label.setText("H")
                    self.ui.textBrowser.append(currentTime+ "-High %d" %(value))
        elif stop_logic == 1: 
            self.ui.textBrowser.setText("Date-degree")
                

class ThreadTask(QThread):
    qthread_signal = pyqtSignal(int)

    #tcp_server
    def tcp_server(self):
        logic = 0

        print("Starting socket: TCP...")
        host_addr = (HOST_IP, HOST_PORT)
        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("TCP server listen @ %s:%d!" %(HOST_IP, HOST_PORT) )
        socket_tcp.bind(host_addr)
        socket_tcp.listen(1)

        socket_con, (client_ip, client_port) = socket_tcp.accept()
        print("Connection accepted from %s." %client_ip)
        socket_con.send(str.encode("start"))

        print("Receiving package...")
        while True:
            data=0
            data_x=0
            data_y=0

            #try:
            if logic== 0:
                data = socket_con.recv(512)  
                data_x = int.from_bytes(data, "big")
                if data_x!=-1: 

                    print("diff x: %d " %data_x)
                    self.qthread_signal.emit(data_x)

                    socket_con.send(str.encode("Y?"))
                    logic= 1
                    time.sleep(0.5)

                    continue     
            if logic== 1:
                data = socket_con.recv(512)  
                data_y = int.from_bytes(data, "big")
                if data_y!=-1: 

                    print("diff y: %d " %data_y)
                    self.qthread_signal.emit(data_y)

                    socket_con.send(str.encode("X?"))

                    logic= 0

                    time.sleep(0.5)

                    continue   


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())