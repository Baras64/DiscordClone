from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5.Qt import QKeyEvent
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from passlib.hash import pbkdf2_sha256
import qdarkstyle
import sys
import threading
import time
# from GUI import MainWindow
import MainWindow
import base64

engine = create_engine('postgresql://postgres:toor@localhost:5432/Baras')
db = scoped_session(sessionmaker(bind=engine))


class Login(qtw.QWidget):

    METHOD = "$pbkdf2-sha256$"
    ROUNDS = "100"
    KEY = "$QmFyYXM$"
    TABLE_NAME = 'members'
    # SALT = b"Baras"

    def __init__(self):
        super(Login, self).__init__()
        # self.resize(1500, 800)
        self.email = qtw.QLabel("Email")
        self.emailInput = qtw.QLineEdit()
        self.password = qtw.QLabel("Password")
        self.passwordInput = qtw.QLineEdit()
        self.passwordInput.setEchoMode(qtw.QLineEdit.Password)
        self.submit = qtw.QPushButton("Submit")
        self.submit.clicked.connect(self.verifyUser)

        self.container = qtw.QFormLayout()
        self.container.addRow(self.email, self.emailInput)
        self.container.addRow(self.password, self.passwordInput)
        self.container.addWidget(self.submit)

        self.setLayout(self.container)

        self.show()

    def verifyUser(self):
        print(pbkdf2_sha256.hash("charizard"))
        query = f'''SELECT * FROM {Login.TABLE_NAME} WHERE email_id='{self.emailInput.text()}';'''
        print(query)
        users = db.execute(query).fetchone()
        print('flag')
        if users == None:
            print("NO USER FOUND")
        else:
            # original_hash = Login.METHOD+Login.ROUNDS+Login.KEY+users.password
            original_hash = users.password
            print(type(original_hash), type(self.passwordInput.text()))
            if pbkdf2_sha256.verify(self.passwordInput.text(), original_hash):
                print(users.username)
                self.close()
                self.dialog = MainWindow.Main(users.username)
                self.dialog.show()

            else:
                print("WE ARE OUT")


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    ex = Login()
    app.installEventFilter(app)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    sys.exit(app.exec_())
