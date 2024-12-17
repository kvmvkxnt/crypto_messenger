import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


class Ui_BlockChain(object):
    """
    App`s class: class of app
    """

    def setupUi(self, BlockChain):
        """
        Sets up the user interface for the main window.

        :param Blockchain: The main window object where the UI will be loaded.
        :type Blockchain: QMainWindow
        """
        
        BlockChain.setObjectName("BlockChain")
        BlockChain.setMinimumSize(800, 600)
        BlockChain.resize(800, 600)
        BlockChain.setAutoFillBackground(False)

        self.centralwidget = QtWidgets.QWidget(BlockChain)
        self.centralwidget.setMinimumSize(QtCore.QSize(200, 200))
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        self.allelementsgrid = QtWidgets.QGridLayout()
        self.allelementsgrid.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.allelementsgrid.setContentsMargins(0, 0, 0, 0)
        self.allelementsgrid.setSpacing(2)
        self.allelementsgrid.setObjectName("allelementsgrid")

        self.chatsLayout = QtWidgets.QVBoxLayout()
        self.chatsLayout.setObjectName("chatsLayout")

        self.chat_Search = QtWidgets.QLineEdit(self.centralwidget)
        self.chat_Search.setText("")
        self.chat_Search.setObjectName("lineEdit")
        self.chatsLayout.addWidget(self.chat_Search)

        self.chatList = QtWidgets.QListWidget(self.centralwidget)
        self.chatList.setObjectName("chatList")
        self.chatsLayout.addWidget(self.chatList)

        self.allelementsgrid.addLayout(self.chatsLayout, 0, 0, 1, 1)

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        self.currentChatLabel = QtWidgets.QLabel(self.centralwidget)
        self.currentChatLabel.setObjectName("currentChatLabel")
        self.currentChatLabel.setText("Select chat")
        self.currentChatLabel.setAlignment(Qt.AlignCenter)
        self.verticalLayout.addWidget(self.currentChatLabel)

        self.message_area = QtWidgets.QTextBrowser(self.centralwidget)
        self.message_area.setObjectName("message_area")
        self.verticalLayout.addWidget(self.message_area)

        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setObjectName("frame")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.messagePrint_area = QtWidgets.QLineEdit(self.frame)
        self.messagePrint_area.setText("")
        self.messagePrint_area.setObjectName("messagePrint")
        self.horizontalLayout.addWidget(self.messagePrint_area)

        self.sendMessage_button = QtWidgets.QPushButton(self.centralwidget)
        self.sendMessage_button.setObjectName("sendMessage_button")
        self.sendMessage_button.setIcon(QIcon("./icons/sendMessage_Button.png"))
        self.sendMessage_button.setIconSize(self.sendMessage_button.size())
        self.horizontalLayout.addWidget(self.sendMessage_button)

        self.verticalLayout.addWidget(self.frame)
        self.allelementsgrid.addLayout(self.verticalLayout, 0, 1, 1, 1)

        self.gridLayout.addLayout(self.allelementsgrid, 2, 0, 1, 1)

        self.up_stroke = QtWidgets.QFrame(self.centralwidget)
        self.up_stroke.setObjectName("up_stroke")

        self.optionsButtonsArea = QtWidgets.QHBoxLayout(self.up_stroke)
        self.optionsButtonsArea.setContentsMargins(0, 0, 0, 0)
        self.optionsButtonsArea.setObjectName("optionsButtonsArea")
        self.optionsButtonsArea.addStretch(1)

        self.options_Button = QtWidgets.QPushButton(self.up_stroke)
        self.options_Button.setObjectName("options_Button")
        self.optionsButtonsArea.addWidget(self.options_Button)
        self.options_Button.setFixedSize(32, 32)

        self.optionsMenu = QtWidgets.QMenu(self.centralwidget)

        self.addChatAction = QtWidgets.QAction("Add chat", self.centralwidget)
        self.renameChatAction = QtWidgets.QAction("Rename chat", self.centralwidget)
        self.deleteChatAction = QtWidgets.QAction("Delete chat", self.centralwidget)
        self.changeNicknameAction = QtWidgets.QAction("Change username", self.centralwidget)

        self.optionsMenu.addAction(self.addChatAction)
        self.optionsMenu.addAction(self.renameChatAction)
        self.optionsMenu.addAction(self.deleteChatAction)
        self.optionsMenu.addAction(self.changeNicknameAction)

        self.options_Button.setMenu(self.optionsMenu)

        self.minimize_button = QtWidgets.QPushButton(self.up_stroke)
        self.minimize_button.setObjectName("minimize_button")
        self.optionsButtonsArea.addWidget(self.minimize_button)
        self.minimize_button.setFixedSize(32, 32)

        self.maximize_button = QtWidgets.QPushButton(self.up_stroke)
        self.maximize_button.setObjectName("maximize_button")
        self.optionsButtonsArea.addWidget(self.maximize_button)
        self.maximize_button.setFixedSize(32, 32)

        self.close_button = QtWidgets.QPushButton(self.up_stroke)
        self.close_button.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.close_button.sizePolicy().hasHeightForWidth())
        self.close_button.setSizePolicy(sizePolicy)
        self.close_button.resize(16, 16)
        self.close_button.setObjectName("close_button")
        self.optionsButtonsArea.addWidget(self.close_button)

        self.gridLayout.addWidget(self.up_stroke, 1, 0, 1, 1)
        BlockChain.setCentralWidget(self.centralwidget)

        self.retranslateUi(BlockChain)
        QtCore.QMetaObject.connectSlotsByName(BlockChain)

    def retranslateUi(self, BlockChain):
        """
        Translates the UI components of MainWindow.

        :param MainWindow: The main window object to apply translations.
        :type MainWindow: QMainWindow
        """
        _translate = QtCore.QCoreApplication.translate
        BlockChain.setWindowTitle(_translate("BlockChain", "Blockchain mess"))
        self.chat_Search.setPlaceholderText(_translate("BlockChain", "Search..."))
        self.messagePrint_area.setPlaceholderText(_translate("BlockChain", "Write a message..."))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    with open("styles.qss", "r") as file:
        style_sheet = file.read()
        app.setStyleSheet(style_sheet)

    BlockChain = QtWidgets.QMainWindow()
    ui = Ui_BlockChain()
    ui.setupUi(BlockChain)
    BlockChain.show()
    sys.exit(app.exec_())