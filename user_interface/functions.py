import sys
import os
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
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
        
        self.chat_names = []
        self.load_chats()
       
        self.chatList.itemClicked.connect(self.select_chat)

        self.sendMessage_button.clicked.connect(self.send_message)
        self.messagePrint_area.returnPressed.connect(self.send_message)
        self.close_button.clicked.connect(self.close_window) 
        self.minimize_button.clicked.connect(self.minimize_window)
        self.maximize_button.clicked.connect(self.maximize_window)
        self.addChatAction.triggered.connect(self.add_chat)
        self.renameChatAction.triggered.connect(self.rename_chat)
        self.deleteChatAction.triggered.connect(self.delete_chat)
        self.changeNicknameAction.triggered.connect(self.change_nickname)


    def add_chat(self):
        text, ok = QtWidgets.QInputDialog.getText(
            self.centralwidget, "Add Chat", "Enter chat name:"
        )
        if ok and text.strip():
            self.chat_names.append(text.strip()) 
            self.load_chats()


    def delete_chat(self):
        selected_items = self.chatList.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(
                self.centralwidget, "No Selection", "Please select a chat to delete."
            )
            return
        for item in selected_items:
            self.chat_names.remove(item.text())
        self.load_chats()


    def rename_chat(self):
        selected_items = self.chatList.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(
                self.centralwidget, "No Selection", "Please select a chat to rename."
            )
            return

        current_name = selected_items[0].text()
        new_name, ok = QtWidgets.QInputDialog.getText(
            self.centralwidget, "Rename Chat", f"Rename '{current_name}' to:"
        )
        if ok and new_name.strip():
            index = self.chat_names.index(current_name)
            self.chat_names[index] = new_name.strip()
            self.load_chats()

    def load_chats(self):
        self.chatList.clear()
        for chat_name in self.chat_names:
            item = QListWidgetItem(chat_name)
            self.chatList.addItem(item)

    def select_chat(self, item):
        chat_name = item.text()
        self.currentChatLabel.setText(chat_name)
        self.message_area.clear()

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
        
        #print(f"Loaded templates: {templates}")
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
        else:
            self.showMaximized()

    
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