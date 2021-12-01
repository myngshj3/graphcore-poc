# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ConsoleWidget.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ConsoleForm(object):
    def setupUi(self, ConsoleForm):
        ConsoleForm.setObjectName("ConsoleForm")
        ConsoleForm.resize(787, 338)
        self.gridLayout = QtWidgets.QGridLayout(ConsoleForm)
        self.gridLayout.setObjectName("gridLayout")
        self.frame = GeometrySerializableFrame(ConsoleForm)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.textBrowser = ConsoleWidget(self.frame)
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout_2.addWidget(self.textBrowser, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)

        self.retranslateUi(ConsoleForm)
        QtCore.QMetaObject.connectSlotsByName(ConsoleForm)

    def retranslateUi(self, ConsoleForm):
        _translate = QtCore.QCoreApplication.translate
        ConsoleForm.setWindowTitle(_translate("ConsoleForm", "Form"))

from gui.ConsoleWidget import ConsoleWidget
from gui.geomserializable import GeometrySerializableFrame
