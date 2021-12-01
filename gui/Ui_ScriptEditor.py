# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ScriptEditor.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ScriptEdior(object):
    def setupUi(self, ScriptEdior):
        ScriptEdior.setObjectName("ScriptEdior")
        ScriptEdior.resize(682, 640)
        self.verticalLayout = QtWidgets.QVBoxLayout(ScriptEdior)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_2 = QtWidgets.QFrame(ScriptEdior)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.frame_2)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.lineEdit = QtWidgets.QLineEdit(self.frame_2)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lineEdit.setFont(font)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_2.addWidget(self.lineEdit)
        spacerItem = QtWidgets.QSpacerItem(261, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addWidget(self.frame_2)
        self.frame_3 = QtWidgets.QFrame(ScriptEdior)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.gridLayout = QtWidgets.QGridLayout(self.frame_3)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtWidgets.QSplitter(self.frame_3)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.scriptEdit = QtWidgets.QPlainTextEdit(self.splitter)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.scriptEdit.setFont(font)
        self.scriptEdit.setObjectName("scriptEdit")
        self.messages = QtWidgets.QTextBrowser(self.splitter)
        self.messages.setObjectName("messages")
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.frame_3)
        self.frame = QtWidgets.QFrame(ScriptEdior)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.testScriptButton = QtWidgets.QPushButton(self.frame)
        self.testScriptButton.setObjectName("testScriptButton")
        self.horizontalLayout.addWidget(self.testScriptButton)
        self.clearButton = QtWidgets.QPushButton(self.frame)
        self.clearButton.setObjectName("clearButton")
        self.horizontalLayout.addWidget(self.clearButton)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.frame)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(ScriptEdior)
        self.buttonBox.accepted.connect(ScriptEdior.accept)
        self.buttonBox.rejected.connect(ScriptEdior.reject)
        self.testScriptButton.clicked.connect(ScriptEdior.test_script)
        self.clearButton.clicked.connect(ScriptEdior.clear_message)
        QtCore.QMetaObject.connectSlotsByName(ScriptEdior)

    def retranslateUi(self, ScriptEdior):
        _translate = QtCore.QCoreApplication.translate
        ScriptEdior.setWindowTitle(_translate("ScriptEdior", "Dialog"))
        self.label.setText(_translate("ScriptEdior", "Script Name"))
        self.testScriptButton.setText(_translate("ScriptEdior", "Test Script"))
        self.clearButton.setText(_translate("ScriptEdior", "PushButton"))

