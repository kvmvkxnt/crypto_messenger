import sys
import os
from datetime import datetime
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QInputDialog
from PyQt5.QtCore import Qt

from new_design import Ui_BlockChain  

class MessengerApp(QMainWindow, Ui_BlockChain):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.username = "Guest"

        bubbles_file = "formats.html"
        self.load_stylesheet()
        self.templates = self.load_message_bubbles(bubbles_file)

        self.border_width = 5
        self.is_resizing = False
        self.resize_direction = None
        

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
            bubble = self.templates["Sender Bubble"].format(time=time, username=self.username, text=text)
            
            current_html = self.message_area.toHtml()
            new_html = current_html + bubble
            self.message_area.setHtml(new_html)
            self.messagePrint_area.clear()

    def receive_message(self, sender, text):
        if text:
            time = datetime.now().strftime("%H:%M")
            bubble = self.templates["Receiver Bubble"].format(time=time, username=sender, text=text)

            current_html = self.message_area.toHtml()
            new_html = current_html + bubble
            self.message_area.setHtml(new_html)

    def load_message_bubbles(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        
        templates = {}
        sections = content.split("<!-- TEMPLATE:")
        for section in sections[1:]:
            marker, html = section.split("-->", 1)
            templates[marker.strip()] = html.strip()
        
        print(f"Loaded templates: {templates}")
        return templates
    
    def load_stylesheet(self):
        with open("messages.qss", "r") as file:
            style_sheet = file.read()
        self.setStyleSheet(style_sheet)

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
        if event.button() == QtCore.Qt.LeftButton:
            if self.up_stroke.geometry().contains(event.pos()):
                self.is_dragging = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            else:
                self.is_resizing = True
                self.resize_direction = self.get_resize_direction(event.pos())
            event.accept()
        

    def mouseMoveEvent(self, event):
        if getattr(self, "is_dragging", False):
            self.move(event.globalPos() - self.drag_position)
            event.accept()

        elif getattr(self, "is_resizing", False):
            self.resize_window(event.globalPos())
            event.accept()
        else:
            direction = self.get_resize_direction(event.pos())


    
    def mouseReleaseEvent(self, event):
        self.is_dragging = False
        self.is_resizing = False
        self.resize_direction = None

    
    def get_resize_direction(self, pos):
        rect = self.rect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        mx, my = pos.x(), pos.y()

        directions = {
        "top": my <= self.border_width, 
        "bottom": my >= h - self.border_width,
        "left": mx <= self.border_width, 
        "right": mx >= w - self.border_width,
    }
        direction = None
        if directions["top"] and directions["left"]:
            direction = "top_left"
        elif directions["top"] and directions["right"]:
            direction = "top_right"
        elif directions["bottom"] and directions["left"]:
            direction = "bottom_left"
        elif directions["bottom"] and directions["right"]:
            direction = "bottom_right"
        elif directions["top"]:
            direction = "top"
        elif directions["bottom"]:
            direction = "bottom"
        elif directions["left"]:
            direction = "left"
        elif directions["right"]:
            direction = "right"
        
        #print(f"Direction: {direction}")
        return direction
    

    def resize_window(self, global_pos):
        self.is_resizing = True
        rect = self.frameGeometry()
        diff = global_pos - rect.topLeft()
        if self.resize_direction == "top":
            rect.setTop(global_pos.y())
        elif self.resize_direction == "bottom":
            rect.setBottom(global_pos.y())
        elif self.resize_direction == "left":
            rect.setLeft(global_pos.x())
        elif self.resize_direction == "right":
            rect.setRight(global_pos.x())
        elif self.resize_direction == "top_left":
            rect.setTopLeft(global_pos)
        elif self.resize_direction == "top_right":
            rect.setTopRight(global_pos)
        elif self.resize_direction == "bottom_left":
            rect.setBottomLeft(global_pos)
        elif self.resize_direction == "bottom_right":
            rect.setBottomRight(global_pos)
        self.setGeometry(rect)

    def test_receive_message(self):
        sender = "Campot"
        text = "PUT UR PHONE DOWN!!!"
        print(f"Testing receive message: sender={sender}, text={text}")
        self.receive_message(sender, text)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_V:
            print("Key V pressed")
            self.test_receive_message()
            event.accept()
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open("styles.qss", "r") as file:
        style_sheet = file.read()
        app.setStyleSheet(style_sheet)
    
    window = MessengerApp()
    window.show()
    sys.exit(app.exec_())