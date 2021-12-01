# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CoordinationFinderWidget.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CoordFinderForm(object):
    def setupUi(self, CoordFinderForm):
        CoordFinderForm.setObjectName("CoordFinderForm")
        CoordFinderForm.resize(673, 670)
        self.gridLayout_2 = QtWidgets.QGridLayout(CoordFinderForm)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.frame = QtWidgets.QFrame(CoordFinderForm)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_3 = QtWidgets.QFrame(self.frame)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.imageLabel = QtWidgets.QLabel(self.frame_3)
        self.imageLabel.setObjectName("imageLabel")
        self.horizontalLayout_2.addWidget(self.imageLabel)
        self.statusLabel = QtWidgets.QLabel(self.frame_3)
        self.statusLabel.setObjectName("statusLabel")
        self.horizontalLayout_2.addWidget(self.statusLabel)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addWidget(self.frame_3)
        self.frame_2 = QtWidgets.QFrame(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.searchButton = QtWidgets.QPushButton(self.frame_2)
        self.searchButton.setObjectName("searchButton")
        self.horizontalLayout.addWidget(self.searchButton)
        self.cancelButton = QtWidgets.QPushButton(self.frame_2)
        self.cancelButton.setEnabled(True)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.applyButton = QtWidgets.QPushButton(self.frame_2)
        self.applyButton.setObjectName("applyButton")
        self.horizontalLayout.addWidget(self.applyButton)
        spacerItem1 = QtWidgets.QSpacerItem(200, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.closeButton = QtWidgets.QPushButton(self.frame_2)
        self.closeButton.setObjectName("closeButton")
        self.horizontalLayout.addWidget(self.closeButton)
        self.verticalLayout.addWidget(self.frame_2)
        self.coordinationWidget = QtWidgets.QTableWidget(self.frame)
        self.coordinationWidget.setColumnCount(0)
        self.coordinationWidget.setObjectName("coordinationWidget")
        self.coordinationWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.coordinationWidget)
        self.gridLayout_2.addWidget(self.frame, 0, 0, 1, 1)

        self.retranslateUi(CoordFinderForm)
        self.searchButton.clicked.connect(CoordFinderForm.do_search)
        self.cancelButton.clicked.connect(CoordFinderForm.do_cancel)
        self.applyButton.clicked.connect(CoordFinderForm.do_apply)
        self.closeButton.clicked.connect(CoordFinderForm.do_close)
        QtCore.QMetaObject.connectSlotsByName(CoordFinderForm)

    def retranslateUi(self, CoordFinderForm):
        _translate = QtCore.QCoreApplication.translate
        CoordFinderForm.setWindowTitle(_translate("CoordFinderForm", "Form"))
        self.imageLabel.setText(_translate("CoordFinderForm", "image label"))
        self.statusLabel.setText(_translate("CoordFinderForm", "Stop"))
        self.searchButton.setText(_translate("CoordFinderForm", "Search"))
        self.cancelButton.setText(_translate("CoordFinderForm", "Cancel"))
        self.applyButton.setText(_translate("CoordFinderForm", "Apply"))
        self.closeButton.setText(_translate("CoordFinderForm", "Close"))

