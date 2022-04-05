import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5.Qt import QKeyEvent, QMouseEvent
from PyQt5 import Qt
import qdarkstyle, pyaudio, sys, time, threading, wave, os
from BACKEND import client, clientAudio
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:toor@localhost:5432/Baras')
db = scoped_session(sessionmaker(bind=engine))

class Main(qtw.QWidget):

    ONLINE_COUNTER = 4

    def __init__(self, USER):
        super(Main, self).__init__()

        self.user = client.Client(USER)

        self.resize(1500, 800)

        #Display Screen
        self.formLayout = qtw.QFormLayout()
        self.groupBox = qtw.QFrame()
        self.groupBox.setLayout(self.formLayout)
        self.scroll = qtw.QScrollArea()
        self.scroll.setWidget(self.groupBox)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(self.height()/1.2)
        self.scroll.setFixedWidth(self.width() / 1.5)
        self.scroll.verticalScrollBar().rangeChanged.connect(lambda x, y: self.scroll.verticalScrollBar().setValue(y))
        # self.scroll = qtw.QTextEdit()
        # self.scroll.setReadOnly(True)
        # self.scroll.setMaximumWidth(self.width()/1.5)
        # self.scroll.setMaximumHeight(self.height()/1.2)

        #Text input from the user
        self.textInput = TextEdit()
        self.textInput.setPlaceholderText("Enter your message here")
        self.textInput.setMaximumHeight(50)
        self.textInput.setMaximumWidth(self.width()/1.5)
        self.textInput.returnPressed.connect(self.updateScreen)

        #Settings Layout
        #TODO add settings wheel and profile pic
        self.settings = qtw.QHBoxLayout()

        #Layout for voice connectivity
        self.audioBox = qtw.QVBoxLayout()
        self.voiceLabel = QLabelClickable("VOICE CHAT")
        self.voiceLabel.setMaximumHeight(50)
        self.voiceLabel.setStyleSheet("background-color: blue")
        self.voiceLabel.setAlignment(qtc.Qt.AlignCenter)
        self.voiceLabel.clicked.connect(self.connectVoiceChat)
        self.audioBox.addWidget(self.voiceLabel)
        self.audioBox.addStretch()
        self.disconnectButton = qtw.QPushButton("DISCONNECT")
        self.disconnectButton.setEnabled(False)
        self.disconnectButton.clicked.connect(self.disconnectVoiceChat)
        self.audioBox.addWidget(self.disconnectButton)

        self.box2 = qtw.QVBoxLayout()
        self.onlineLabel = qtw.QLabel(f"ONLINE - {Main.ONLINE_COUNTER}")
        self.onlineLabel.setStyleSheet("background-color: green")
        self.onlineLabel.setAlignment(qtc.Qt.AlignCenter)
        self.box2.addWidget(self.onlineLabel)
        self.box2.addStretch()

        self.grid = qtw.QGridLayout()
        self.grid.addWidget(self.scroll, 1, 1)
        self.grid.addWidget(self.textInput, 3, 1)
        self.grid.addLayout(self.audioBox, 0, 0, -1, 1)
        self.grid.addLayout(self.box2, 0, 2, -1, 1)

        self.setLayout(self.grid)
        self.show()

        self.worker = Worker(self)
        self.worker.updateDisplay.connect(self.updateDisplay)
        self.worker.updateOnline.connect(self.updateOnline)
        self.worker.start()

        self.audioChat = WorkerAudio()

    def updateOnline(self, msg):
        query = "SELECT * FROM members"
        table = db.execute(query).fetchall()
        db.commit()
        for users in table:
            if users[3]:
                if not self.ifExist(users[2]):
                    label = qtw.QLabel(users[2])
                    label.setObjectName(users[2])
                    self.box2.insertWidget(self.box2.count()-1, label)
                else:
                    continue
            else:
                self.deleteWidget(users[2])
        # if table['status']:
        #     self.box2.insertWidget(self.box2.count()-1, qtw.QLabel(table['username']))

    def deleteWidget(self, name):
        for i in range(self.box2.count()):
            if self.box2.itemAt(i).widget() is not None:
                if name == self.box2.itemAt(i).widget().objectName():
                    self.box2.itemAt(i).widget().close()

    def ifExist(self, name):
        print(self.box2.count())
        for i in range(self.box2.count()):
            if self.box2.itemAt(i).widget() is not None:
                if name == self.box2.itemAt(i).widget().objectName():
                    print(name)
                    return True
        return False

    def updateDisplay(self, msg):
        label = qtw.QLabel(msg)
        label.setFont(qtg.QFont("Arial", 12))
        # self.formLayout.addRow(label)
        self.formLayout.addWidget(label)

    def connectVoiceChat(self):
        #TODO create an object of audio server
        print("Hello")
        self.audioChat.start()
        self.userJoined = qtw.QLabel("Baras")
        self.audioBox.insertWidget(1, self.userJoined)
        self.disconnectButton.setEnabled(True)
        #TODO notify rest of clients and add widget

    def disconnectVoiceChat(self):
        print("Bye")
        self.audioChat.terminate()
        clientAudio.Client.receiveServerData = False
        self.disconnectButton.setEnabled(False)
        self.audioBox.itemAt(1).widget().close()
        self.audioBox.removeWidget(self.userJoined)
        #TODO destroy the audio server object created


    def updateScreen(self):
        textMsg = self.textInput.toPlainText().strip()
        self.user.send_message(textMsg)
        self.textInput.setText("")

    # def appendMessage(self, msg, vbox):
    #     if len(msg.split(" ")) == 6 and msg.split(" ")[2] == 'connected':
    #         print(msg.split(" ")[0])
    #         vbox.insertWidget(self.box2.count()-1, qtw.QLabel("GG"))
    #         time.sleep(0.1)
    #     self.scroll.append(msg)


class WorkerAudio(qtc.QThread):

    def __init__(self):
        super(WorkerAudio, self).__init__()

    def run(self):
        print("AYYY")
        clientAudio.Client()


class Worker(qtc.QThread):

    updateDisplay = qtc.pyqtSignal(str)
    updateOnline = qtc.pyqtSignal(str)

    def __init__(self, obj):
        super(Worker, self).__init__()
        self.obj = obj

    def run(self):
        msgs = []
        run = True
        while run:
            new_messages = self.obj.user.get_messages()  # get any new messages from client
            msgs.extend(new_messages)  # add to local list of messages
            for msg in new_messages:  # display new messages
                print(msg)
                # self.scroll.append(msg)
                self.appendMessage(msg)
                if msg == "/quit":
                    run = False
                    sys.exit(0)
            time.sleep(0.1)

    def appendMessage(self, msg):
        if msg == 'PERFORM UPDATE TABLE ACTION':
            self.updateOnline.emit(msg)
            time.sleep(0.1)
        else:
            self.updateDisplay.emit(msg)


class TextEdit(qtw.QTextEdit):
    returnPressed = qtc.pyqtSignal()
    val = qtc.Qt.Key_Shift

    def keyPressEvent(self, e: QKeyEvent):
        if TextEdit.val == e.key():
            TextEdit.val += qtc.Qt.Key_Return
        if TextEdit.val == (qtc.Qt.Key_Shift + e.key()):
            TextEdit.val = qtc.Qt.Key_Shift
            self.returnPressed.emit()
        else:
            return super().keyPressEvent(e)


class QLabelClickable(qtw.QLabel):
    clicked = qtc.pyqtSignal()

    def mousePressEvent(self, e: QMouseEvent):
        self.clicked.emit()



def main():
    app = qtw.QApplication(sys.argv)
    ex = Main()
    # app.installEventFilter(app)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    sys.exit(app.exec_())

# main("BARas")