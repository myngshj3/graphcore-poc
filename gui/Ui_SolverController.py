# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_SolverController.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SolverControllerForm(object):
    def setupUi(self, SolverControllerForm):
        SolverControllerForm.setObjectName("SolverControllerForm")
        SolverControllerForm.resize(1002, 833)
        self.verticalLayout = QtWidgets.QVBoxLayout(SolverControllerForm)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(SolverControllerForm)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.progressBar = QtWidgets.QProgressBar(self.frame)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.progressBar.setFont(font)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.horizontalLayout.addWidget(self.progressBar)
        self.progressLabel = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.progressLabel.setFont(font)
        self.progressLabel.setObjectName("progressLabel")
        self.horizontalLayout.addWidget(self.progressLabel)
        spacerItem = QtWidgets.QSpacerItem(432, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addWidget(self.frame)
        self.frame_2 = QtWidgets.QFrame(SolverControllerForm)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.frame_2)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.priorParallel = QtWidgets.QRadioButton(self.frame_2)
        self.priorParallel.setObjectName("priorParallel")
        self.horizontalLayout_2.addWidget(self.priorParallel)
        self.priorSerial = QtWidgets.QRadioButton(self.frame_2)
        self.priorSerial.setObjectName("priorSerial")
        self.horizontalLayout_2.addWidget(self.priorSerial)
        spacerItem1 = QtWidgets.QSpacerItem(534, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.startButton = QtWidgets.QPushButton(self.frame_2)
        self.startButton.setObjectName("startButton")
        self.horizontalLayout_2.addWidget(self.startButton)
        self.stopButton = QtWidgets.QPushButton(self.frame_2)
        self.stopButton.setObjectName("stopButton")
        self.horizontalLayout_2.addWidget(self.stopButton)
        self.verticalLayout.addWidget(self.frame_2)
        self.coordinateWidget = QtWidgets.QTableWidget(SolverControllerForm)
        self.coordinateWidget.setObjectName("coordinateWidget")
        self.coordinateWidget.setColumnCount(0)
        self.coordinateWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.coordinateWidget)
        self.frame_3 = QtWidgets.QFrame(SolverControllerForm)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.okButton = QtWidgets.QPushButton(self.frame_3)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout_3.addWidget(self.okButton)
        self.cancelButton = QtWidgets.QPushButton(self.frame_3)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout_3.addWidget(self.cancelButton)
        self.verticalLayout.addWidget(self.frame_3)

        self.retranslateUi(SolverControllerForm)
        self.cancelButton.clicked.connect(SolverControllerForm.cancel_clicked)
        self.okButton.clicked.connect(SolverControllerForm.ok_clicked)
        self.startButton.clicked.connect(SolverControllerForm.start_clicked)
        self.stopButton.clicked.connect(SolverControllerForm.stop_clicked)
        self.priorParallel.clicked.connect(SolverControllerForm.parallel_clicked)
        self.priorSerial.clicked.connect(SolverControllerForm.serial_clicked)
        self.coordinateWidget.customContextMenuRequested['QPoint'].connect(SolverControllerForm.context_menu_popup)
        QtCore.QMetaObject.connectSlotsByName(SolverControllerForm)

    def retranslateUi(self, SolverControllerForm):
        _translate = QtCore.QCoreApplication.translate
        SolverControllerForm.setWindowTitle(_translate("SolverControllerForm", "Form"))
        self.progressLabel.setText(_translate("SolverControllerForm", "TextLabel"))
        self.label.setText(_translate("SolverControllerForm", "Options: "))
        self.priorParallel.setText(_translate("SolverControllerForm", "Parallel"))
        self.priorSerial.setText(_translate("SolverControllerForm", "Serial"))
        self.startButton.setText(_translate("SolverControllerForm", "Start"))
        self.stopButton.setText(_translate("SolverControllerForm", "Stop"))
        self.okButton.setText(_translate("SolverControllerForm", "OK"))
        self.cancelButton.setText(_translate("SolverControllerForm", "Cancel"))

