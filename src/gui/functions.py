import sys
import os
from datetime import datetime
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QInputDialog
from PyQt5.QtCore import Qt

from new_design import Ui_BlockChain  

class MessengerApp(QMainWindow, Ui_BlockChain):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.username = "Guest"
        

        self.sendMessage_button.clicked.connect(self.send_message)
        self.messagePrint_area.returnPressed.connect(self.send_message)
        self.options_Button.clicked.connect(self.change_nickname)
        self.close_button.clicked.connect(self.close_window) 
        self.minimize_button.clicked.connect(self.minimize_window)
        self.maximize_button.clicked.connect(self.maximize_window)

    def send_message(self):
        text = self.messagePrint_area.text().strip()
        if text:
            time = datetime.now().strftime("%H:%M")
            
            sender_bubble_path = os.path.join(os.path.dirname(__file__), "formats.html")
            with open(sender_bubble_path, "r", encoding="utf-8") as file:
                bubble_template = file.read()
            
            bubble = bubble_template.format(time=time, username=self.username, text=text)
            self.message_area.append(bubble)
            self.messagePrint_area.clear()


    def change_nickname(self):
        new_username, ok = QInputDialog.getText(self, "Change Nickname", "Enter new nickname:")
        if ok and new_username.strip():
            self.username = new_username.strip()  
    
    def close_window(self):
        self.close()
    
    def minimize_window(self):
        self.showMinimized()

    def maximize_window(self):
        if self.isMaximized():
            self.showNormal()
            #self.maximize_button.setText("Maximize")
        else:
            self.showMaximized()
            #self.maximize_button.setText("Restore")
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.up_stroke.geometry().contains(event.pos()):
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_dragging = False
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open("styles.qss", "r") as file:
        style_sheet = file.read()
        app.setStyleSheet(style_sheet)
    
    window = MessengerApp()
    window.show()
    sys.exit(app.exec_())