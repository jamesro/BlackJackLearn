#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import pybjagent
from itertools import cycle


class Window(QtGui.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.agent = pybjagent.Agent()
        self.update_step = 200 # Games played before updating GUI (very CPU intensive to update)
        self.setGeometry(50, 50, 1000, 600)
        self.setWindowTitle("Blackjack Learn")
        self.suitCycle = cycle(["♣", "♦", "♥", "♠"])

        # Code main menu here since it's the same throughout the whole application (though it is possible to change)
        quitAction = QtGui.QAction("&Close Application", self)
        quitAction.setShortcut("Ctrl+Q")
        quitAction.setStatusTip("Leave The App")
        quitAction.triggered.connect(self.close_application)

        resAction = QtGui.QAction("&Resize window", self)
        resAction.setShortcut("Ctrl+R")
        resAction.setStatusTip("Resizes The Window")
        resAction.triggered.connect(self.resize_application)

        # This is an assigned object because we're going to modify it
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu("&File")
        fileMenu.addAction(quitAction)

        editMenu = mainMenu.addMenu("&Edit")
        editMenu.addAction(resAction)

        # Calls the status bar (bottom bar)
        self.statusBar()

        # Stop button
        self.haltBtn = QtGui.QPushButton("Halt", self)
        self.learnBtn = QtGui.QPushButton("Learn", self)
        self.learnBtn.clicked.connect(self.learn_button)
        self.loadBtn = QtGui.QPushButton("Load", self)
        self.saveBtn = QtGui.QPushButton("Save", self)

        # Dial 1
        self.dial1 = QtGui.QDial()
        self.dial1.setNotchesVisible(True)
        self.dial1.setValue(10)
        self.dial1Label = QtGui.QLabel()
        self.dial1Label.setAlignment(QtCore.Qt.AlignCenter)
        self.dial1Label.setText("Epsilon = %s" % (self.dial1.value()/100))
        
        # Dial 2
        self.dial2 = QtGui.QDial()
        self.dial2.setNotchesVisible(True)
        self.dial2.setValue(15)
        self.dial2Label = QtGui.QLabel()
        self.dial2Label.setAlignment(QtCore.Qt.AlignCenter)
        self.dial2Label.setText("Gamma = %s" % (self.dial2.value()/100))
        
        # Dial 3 
        self.dial3 = QtGui.QDial()
        self.dial3.setNotchesVisible(True)
        self.dial3.setValue(75)
        self.dial3Label = QtGui.QLabel()
        self.dial3Label.setAlignment(QtCore.Qt.AlignCenter)
        self.dial3Label.setText("Mu = %s" % (self.dial3.value()/100))

        self.mu = self.dial3.value()/100
        self.gamma = self.dial2.value()/100
        self.epsilon = self.dial1.value()/100

        # Dial behaviour
        self.dial1.valueChanged.connect(lambda value=self.dial1.value():
                                        self.dial1Label.setText("Epsilon = %s" % (self.dial1.value()/100)))
        self.dial2.valueChanged.connect(lambda value=self.dial2.value():
                                        self.dial2Label.setText("Gamma = %s" % (self.dial2.value()/100)))
        self.dial3.valueChanged.connect(lambda value=self.dial3.value():
                                        self.dial3Label.setText("Mu = %s" % (self.dial3.value() / 100)))

        # Line Edit (number of games)
        self.line = QtGui.QLineEdit()
        self.line.setValidator(QtGui.QIntValidator())
        self.line.setMaxLength(6)
        self.line.setAlignment(QtCore.Qt.AlignRight)
        self.flo = QtGui.QFormLayout()
        self.flo.addRow("Number of Games", self.line)

        self.textDisplay = QtGui.QLabel()
        self.textDisplay.setAlignment(QtCore.Qt.AlignCenter)
        self.textDisplay.setText("")
        newfont = QtGui.QFont("Times", 50, QtGui.QFont.Bold)
        self.textDisplay.setFont(newfont)
        self.textDisplay.setStyleSheet("border: 2px solid #E2E2E2")

        self.plotWidget = pg.PlotWidget(title="Learning Progress",
                                        labels={'left': "Percentage Won / Drawn", 'bottom': "Number of Games"})
        self.data = np.zeros(100)
        self.xAxis = np.array(range(1, 101))
        self.plotPos = 0
        self.plotWidget.plot(self.data)

        grid = self.set_layout()

        # Enclose everything in a QWidget and set it as the Central Widget in the Main Window
        self.centralWidget = QtGui.QWidget()
        self.centralWidget.setAutoFillBackground(True)
        self.centralWidget.setLayout(grid)
        self.setCentralWidget(self.centralWidget)

        self.show()

    def set_layout(self):
        dial1Layout = QtGui.QVBoxLayout()
        dial1Layout.addWidget(self.dial1Label)
        dial1Layout.addWidget(self.dial1)
        dial2Layout = QtGui.QVBoxLayout()
        dial2Layout.addWidget(self.dial2Label)
        dial2Layout.addWidget(self.dial2)
        dial3Layout = QtGui.QVBoxLayout()
        dial3Layout.addWidget(self.dial3Label)
        dial3Layout.addWidget(self.dial3)

        dialsLayout = QtGui.QHBoxLayout()
        dialsLayout.addLayout(dial1Layout)
        dialsLayout.addLayout(dial2Layout)
        dialsLayout.addLayout(dial3Layout)

        buttonLayout = QtGui.QGridLayout()
        buttonLayout.addWidget(self.haltBtn, 1, 1, 2, 1)
        buttonLayout.addWidget(self.learnBtn, 1, 2, 2, 1)
        buttonLayout.addWidget(self.loadBtn, 3, 1, 2, 1)
        buttonLayout.addWidget(self.saveBtn, 3, 2, 2, 1)

        rightPanel = QtGui.QVBoxLayout()
        rightPanel.addWidget(self.textDisplay)
        rightPanel.addLayout(dialsLayout)
        rightPanel.addLayout(self.flo)
        rightPanel.addLayout(buttonLayout)

        grid = QtGui.QGridLayout()
        grid.addWidget(self.plotWidget, 1, 1, 4, 12)
        grid.addLayout(rightPanel, 1, 13, 4, 4)
        return grid

    def close_application(self):
        choice = QtGui.QMessageBox.question(self, "quit!",
                                            "Are you sure?",
                                            QtGui.QMessageBox.Yes |
                                            QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            sys.exit()
        else:
            pass

    def resize_application(self, state):
        if state == QtCore.Qt.Checked:
            self.setGeometry(50, 50, 1000, 600)
        else:
            self.setGeometry(50, 50, 500, 300)

    def learn_button(self):
        mu = self.dial3.value() / 100
        gamma = self.dial2.value() / 100
        epsilon = self.dial1.value() / 100
        nGames = int(self.line.text())
        # default values: mu=0.75   gamma=0.15    epsilon=0.1
        learning_steps = self.agent.learn(mu, gamma, epsilon, nGames, plots=True)
        for count, step in enumerate(learning_steps):
            if count % self.update_step == 0:
                self.plot_update(step)
            if count % 800 == 0:
                self.update()
            QtCore.QCoreApplication.processEvents()

    def update(self):
        self.textDisplay.setText(next(self.suitCycle))

    def plot_update(self, data_item):
        self.data[:-1] = self.data[1:]  # shift data in the array one sample left
        self.xAxis[:-1] = self.xAxis[1:]
        self.data[-1] = data_item
        self.plotPos += self.update_step
        self.xAxis[-1] = self.plotPos
        self.plotWidget.plot(self.xAxis, self.data, clear=True)
        
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setStyleSheet("""
                      QLabel{color: #E2E2E2} QMainWindow{background-color: #000}
                      QWidget{background-color: #000}
                      QPushButton{background-color: #E2E2E2}
                      QLineEdit{color: #E2E2E2}
                      """)
    GUI = Window()
    sys.exit(app.exec_())

