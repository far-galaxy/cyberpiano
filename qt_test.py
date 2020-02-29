#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QToolTip, QPushButton, QMessageBox, QLabel
from PyQt5.QtGui import QIcon, QFont

def error():
    QMessageBox.critical(w, "Title", "Message")

app = QApplication(sys.argv)

w = QWidget()
w.resize(250, 150)
w.move(300, 300)
w.setWindowTitle('CyberPiano')
w.setWindowIcon(QIcon('icon.png'))

QToolTip.setFont(QFont('SansSerif', 10))
btn = QPushButton('Connect', w)
lbl = QLabel("COM", w)
lbl.move(15, 25)
btn.clicked.connect(error)
btn.move(100, 25)
btn.resize(75,20)

w.show()

sys.exit(app.exec_())