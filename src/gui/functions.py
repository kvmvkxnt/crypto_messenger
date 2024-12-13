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
        if event.button() == QtCore.Qt.LeftButton:
            # Проверяем, перетаскивает ли пользователь окно
            if self.up_stroke.geometry().contains(event.pos()):
                self.is_dragging = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            else:
                # Проверяем, находится ли мышь в зоне изменения размеров
                self.is_resizing = True
                self.resize_direction = self.get_resize_direction(event.pos())
            event.accept()
        

    def mouseMoveEvent(self, event):
        if getattr(self, "is_dragging", False):
            self.move(event.globalPos() - self.drag_position)
            event.accept()

        # Если изменение размеров
        elif getattr(self, "is_resizing", False):
            self.resize_window(event.globalPos())
            event.accept()
        else:
            # Меняем курсор в зависимости от области
            direction = self.get_resize_direction(event.pos())
            cursor = self.get_cursor_shape(direction)
            if cursor:
                self.setCursor(cursor)
            else:
                self.unsetCursor()

    
    def mouseReleaseEvent(self, event):
        self.is_dragging = False
        self.is_resizing = False
        self.resize_direction = None

    
    def get_resize_direction(self, pos):
        """Определяет, в каком направлении пользователь изменяет размер окна"""
        rect = self.rect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        mx, my = pos.x(), pos.y()

        '''directions = {
            "top": y <= my <= y + self.border_width,
            "bottom": h - self.border_width <= my <= h,
            "left": x <= mx <= x + self.border_width,
            "right": w - self.border_width <= mx <= w,
        }'''
        directions = {
        "top": my <= self.border_width,  # Мышь в верхней зоне
        "bottom": my >= h - self.border_width,  # Мышь в нижней зоне
        "left": mx <= self.border_width,  # Мышь в левой зоне
        "right": mx >= w - self.border_width,  # Мышь в правой зоне
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
        
        print(f"Direction: {direction}")  # Отладочная печать
        return direction
    
    def get_cursor_shape(self, direction):
        """Возвращает подходящую форму курсора"""
        cursors = {
            "top": QtCore.Qt.SizeVerCursor,
            "bottom": QtCore.Qt.SizeVerCursor,
            "left": QtCore.Qt.SizeHorCursor,
            "right": QtCore.Qt.SizeHorCursor,
            "top_left": QtCore.Qt.SizeFDiagCursor,
            "bottom_right": QtCore.Qt.SizeFDiagCursor,
            "top_right": QtCore.Qt.SizeBDiagCursor,
            "bottom_left": QtCore.Qt.SizeBDiagCursor,
        }
        print(f"Cursor direction: {direction}")  # Для отладки
        return QtGui.QCursor(cursors.get(direction)) if direction else None
        
    def resize_window(self, global_pos):
        """Изменяет размер окна в зависимости от направления"""
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


if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open("styles.qss", "r") as file:
        style_sheet = file.read()
        app.setStyleSheet(style_sheet)
    
    window = MessengerApp()
    window.show()
    sys.exit(app.exec_())