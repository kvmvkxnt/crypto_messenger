from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
import unittest
from unittest.mock import patch
from messenger_window import MessengerApp
import sys

app = QApplication(sys.argv)

class TestMessengerApp(unittest.TestCase):
    def setUp(self):
        """Настройка для каждого теста"""
        self.window = MessengerApp()
        self.window.show()

    def tearDown(self):
        """Закрытие окна после теста"""
        self.window.close()

    @patch('PyQt5.QtWidgets.QInputDialog.getText', return_value=("NewChat", True))
    def test_add_chat(self, mock_input):
        """Тест добавления чата"""
        initial_count = len(self.window.chat_names)
        self.window.addChatAction.trigger()
        self.assertEqual(len(self.window.chat_names), initial_count + 1)
        self.assertIn("NewChat", self.window.chat_names)

    @patch('PyQt5.QtWidgets.QInputDialog.getText', return_value=("RenamedChat", True))
    def test_rename_chat(self, mock_input):
        """Тест переименования чата"""
        self.window.chat_names = ["OldChat"]
        self.window.load_chats()
        self.window.chatList.setCurrentRow(0)
        self.window.renameChatAction.trigger()
        self.assertIn("RenamedChat", self.window.chat_names)
        self.assertNotIn("OldChat", self.window.chat_names)

    def test_delete_chat(self):
        """Тест удаления чата"""
        self.window.chat_names = ["Chat1", "Chat2"]
        self.window.load_chats()
        self.window.chatList.setCurrentRow(0)
        self.window.deleteChatAction.trigger()
        self.assertNotIn("Chat1", self.window.chat_names)
        self.assertEqual(len(self.window.chat_names), 1)

    def test_close_window(self):
        """Тест закрытия окна"""
        self.assertTrue(self.window.isVisible())
        self.window.close_window()
        self.assertFalse(self.window.isVisible())

    def test_minimize_window(self):
        """Тест сворачивания окна"""
        self.window.minimize_window()
        self.assertEqual(self.window.windowState(), Qt.WindowMinimized)

    def test_maximize_window(self):
        """Тест разворачивания окна"""
        self.window.maximize_window()
        self.assertTrue(self.window.isMaximized())
        self.window.maximize_window()
        self.assertFalse(self.window.isMaximized())

    def test_send_message(self):
        """Тест отправки сообщений"""
        self.window.username = "TestUser"
        test_message = "Test message"
        self.window.messagePrint_area.setText(test_message)
        self.window.send_message()
        message_html = self.window.message_area.toHtml()
        self.assertIn(test_message, message_html)
        self.assertIn("TestUser", message_html)

if __name__ == "__main__":
    unittest.main()