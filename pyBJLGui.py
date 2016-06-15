#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import pybjagent
from itertools import cycle

#Gui
class Window(QtGui.QMainWindow):

    def __init__(self):
        super(Window, self).__init__() # Initialise the parent class, (QMainWindow obeject)
        self.agent = pybjagent.Agent()
        self.setGeometry(50,50,1000,600)
        self.setWindowTitle("Blackjack Learn")
        self.suitCycle = cycle(["♣","♦", "♥", "♠"])

        # Code main menu here since it's the same throughout the whole application (though it is possible to change)
        quitAction = QtGui.QAction("&Close Application",self)
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

        self.home()
    

    # Views (Home Page)
    def home(self):

        # Stop button
        self.haltBtn = QtGui.QPushButton("Halt", self)
        self.learnBtn = QtGui.QPushButton("Learn",self)



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
        
        # Dial behaviour
        self.dial1.valueChanged.connect(lambda value=self.dial1.value(): self.dial1Label.setText("Epsilon = %s" % (self.dial1.value()/100)))
        self.dial2.valueChanged.connect(lambda value=self.dial2.value(): self.dial2Label.setText("Gamma = %s" % (self.dial2.value()/100)))
        self.dial3.valueChanged.connect(lambda value=self.dial3.value(): self.dial3Label.setText("Mu = %s" % (self.dial3.value()/100)))
        
        # Line Edit (number of games)
        self.line = QtGui.QLineEdit()
        self.line.setValidator(QtGui.QIntValidator())
        self.line.setMaxLength(6)
        self.line.setAlignment(QtCore.Qt.AlignRight)
        self.flo = QtGui.QFormLayout()
        self.flo.addRow("Number of Games", self.line)

        # Percentage Display
        self.percentageDisplay = QtGui.QLabel()
        self.percentageDisplay.setAlignment(QtCore.Qt.AlignCenter)
        self.percentageDisplay.setText("")
        newfont = QtGui.QFont("Times", 50, QtGui.QFont.Bold) 
        self.percentageDisplay.setFont(newfont)
        self.percentageDisplay.setStyleSheet("border: 1px solid #E2E2E2");

        self.plotWidget = pg.PlotWidget(title="Learning Progress",labels={'left': "Percentage Won / Drawn", 'bottom': "Number of Games"})
        self.data = np.zeros(50)
        self.plotPos = 0
        self.plotWidget.plot(self.data)

        # Layout
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

        buttonLayout = QtGui.QHBoxLayout()
        buttonLayout.addWidget(self.haltBtn)
        buttonLayout.addWidget(self.learnBtn)

        rightPanel = QtGui.QVBoxLayout()
        rightPanel.addWidget(self.percentageDisplay)
        rightPanel.addLayout(dialsLayout)
        rightPanel.addLayout(self.flo)
        rightPanel.addLayout(buttonLayout)

        grid = QtGui.QGridLayout()
        grid.addWidget(self.plotWidget,1,1,4,12)
        grid.addLayout(rightPanel,1,13,4,4)

        # central widget
        self.centralWidget = QtGui.QWidget()
        self.centralWidget.setAutoFillBackground(True)
        palette = self.centralWidget.palette()
        # palette.setColor(self.centralWidget.backgroundRole(), QtGui.QColor(0,0,0))
        self.centralWidget.setPalette(palette)
        self.centralWidget.setLayout(grid) 
        self.setCentralWidget(self.centralWidget)


        self.show()

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
            self.setGeometry(50,50,1000,600)
        else:
            self.setGeometry(50,50,500,300)

    def learnButton(self):
        self.agent.learn(mu=self.mu,gamma=self.gamma,epsilon=self.epsilon,nGames=self.nGames,plots=True)  # mu=0.75,gamma=0.15,epsilon=0.1,nGames=10000,plots=True

    def update(self):
        self.percentageDisplay.setText(next(self.suitCycle))

    def plot_update(self):
        self.data[:-1] = self.data[1:]  # shift data in the array one sample left
        self.data[-1] = np.random.normal()
        self.plotPos += 1
        self.plotWidget.plot(self.data)
        
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setStyleSheet('QLabel{color: #E2E2E2} QMainWindow{background-color: #000} QWidget{background-color: #000} QPushButton{background-color: #E2E2E2} QLineEdit{color: #E2E2E2}')
    GUI = Window()
    timer = QtCore.QTimer()
    timer.timeout.connect(GUI.update)
    timer.timeout.connect(GUI.plot_update)
    timer.start(600)
    sys.exit(app.exec_())


