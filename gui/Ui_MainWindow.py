# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1167, 804)
        font = QtGui.QFont()
        font.setFamily("メイリオ")
        font.setKerning(True)
        MainWindow.setFont(font)
        MainWindow.setAutoFillBackground(True)
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setStyleSheet("")
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.splitter_3 = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_3.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_3.setObjectName("splitter_3")
        self.left_pane = GeometrySerializableFrame(self.splitter_3)
        self.left_pane.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.left_pane.setFrameShadow(QtWidgets.QFrame.Plain)
        self.left_pane.setObjectName("left_pane")
        self.gridLayout = QtWidgets.QGridLayout(self.left_pane)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter_2 = QtWidgets.QSplitter(self.left_pane)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter_2.sizePolicy().hasHeightForWidth())
        self.splitter_2.setSizePolicy(sizePolicy)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName("splitter_2")
        self.frame_3 = QtWidgets.QFrame(self.splitter_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy)
        self.frame_3.setAutoFillBackground(False)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.frame_3)
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.splitter = QtWidgets.QSplitter(self.frame_3)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.left_top_pane = GeometrySerializableFrame(self.splitter)
        self.left_top_pane.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.left_top_pane.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.left_top_pane.setObjectName("left_top_pane")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.left_top_pane)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.left_top_pane)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.editorTabWidget = QtWidgets.QTabWidget(self.left_top_pane)
        self.editorTabWidget.setObjectName("editorTabWidget")
        self.tab_7 = QtWidgets.QWidget()
        self.tab_7.setObjectName("tab_7")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tab_7)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.propertyWidget = QtWidgets.QTableWidget(self.tab_7)
        self.propertyWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.propertyWidget.setObjectName("propertyWidget")
        self.propertyWidget.setColumnCount(0)
        self.propertyWidget.setRowCount(0)
        self.verticalLayout_4.addWidget(self.propertyWidget)
        self.editorTabWidget.addTab(self.tab_7, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.nodeTableWidget = QtWidgets.QTableWidget(self.tab)
        self.nodeTableWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.nodeTableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.nodeTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.nodeTableWidget.setColumnCount(4)
        self.nodeTableWidget.setObjectName("nodeTableWidget")
        self.nodeTableWidget.setRowCount(0)
        self.verticalLayout_3.addWidget(self.nodeTableWidget)
        self.editorTabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.tab_2)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.edgeTableWidget = QtWidgets.QTableWidget(self.tab_2)
        self.edgeTableWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.edgeTableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.edgeTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.edgeTableWidget.setColumnCount(4)
        self.edgeTableWidget.setObjectName("edgeTableWidget")
        self.edgeTableWidget.setRowCount(0)
        self.verticalLayout_6.addWidget(self.edgeTableWidget)
        self.horizontalLayout_8.addLayout(self.verticalLayout_6)
        self.editorTabWidget.addTab(self.tab_2, "")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab_5)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.frame_8 = QtWidgets.QFrame(self.tab_5)
        self.frame_8.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_8.setObjectName("frame_8")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.frame_8)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.splitter_4 = QtWidgets.QSplitter(self.frame_8)
        self.splitter_4.setOrientation(QtCore.Qt.Vertical)
        self.splitter_4.setObjectName("splitter_4")
        self.frame_9 = QtWidgets.QFrame(self.splitter_4)
        self.frame_9.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_9.setObjectName("frame_9")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.frame_9)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.frame_6 = QtWidgets.QFrame(self.frame_9)
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_4 = QtWidgets.QLabel(self.frame_6)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout.addWidget(self.label_4)
        self.verticalLayout_7.addWidget(self.frame_6)
        self.systemConstraintWidget = QtWidgets.QTableWidget(self.frame_9)
        self.systemConstraintWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.systemConstraintWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.systemConstraintWidget.setColumnCount(3)
        self.systemConstraintWidget.setObjectName("systemConstraintWidget")
        self.systemConstraintWidget.setRowCount(0)
        self.verticalLayout_7.addWidget(self.systemConstraintWidget)
        self.frame_10 = QtWidgets.QFrame(self.splitter_4)
        self.frame_10.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_10.setObjectName("frame_10")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.frame_10)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.frame_2 = QtWidgets.QFrame(self.frame_10)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_5 = QtWidgets.QLabel(self.frame_2)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_2.addWidget(self.label_5)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.addUserConstraintButton = QtWidgets.QPushButton(self.frame_2)
        self.addUserConstraintButton.setObjectName("addUserConstraintButton")
        self.horizontalLayout_2.addWidget(self.addUserConstraintButton)
        self.deleteUserConstraintButton = QtWidgets.QPushButton(self.frame_2)
        self.deleteUserConstraintButton.setObjectName("deleteUserConstraintButton")
        self.horizontalLayout_2.addWidget(self.deleteUserConstraintButton)
        self.verticalLayout_9.addWidget(self.frame_2)
        self.constraintWidget = QtWidgets.QTableWidget(self.frame_10)
        self.constraintWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.constraintWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.constraintWidget.setColumnCount(3)
        self.constraintWidget.setObjectName("constraintWidget")
        self.constraintWidget.setRowCount(0)
        self.verticalLayout_9.addWidget(self.constraintWidget)
        self.gridLayout_3.addWidget(self.splitter_4, 1, 0, 1, 1)
        self.gridLayout_2.addWidget(self.frame_8, 0, 0, 1, 1)
        self.editorTabWidget.addTab(self.tab_5, "")
        self.verticalLayout.addWidget(self.editorTabWidget)
        self.left_bottom_pane = QtWidgets.QFrame(self.splitter)
        self.left_bottom_pane.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.left_bottom_pane.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.left_bottom_pane.setObjectName("left_bottom_pane")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.left_bottom_pane)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.left_bottom_pane)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.errorWidget = QtWidgets.QTableWidget(self.left_bottom_pane)
        self.errorWidget.setStyleSheet("")
        self.errorWidget.setObjectName("errorWidget")
        self.errorWidget.setColumnCount(0)
        self.errorWidget.setRowCount(0)
        self.verticalLayout_2.addWidget(self.errorWidget)
        self.gridLayout_5.addWidget(self.splitter, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.splitter_2, 0, 0, 1, 1)
        self.right_pane = QtWidgets.QFrame(self.splitter_3)
        self.right_pane.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.right_pane.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.right_pane.setObjectName("right_pane")
        self.gridLayout_10 = QtWidgets.QGridLayout(self.right_pane)
        self.gridLayout_10.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.left_pane_2 = GeometrySerializableFrame(self.right_pane)
        self.left_pane_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.left_pane_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.left_pane_2.setObjectName("left_pane_2")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.left_pane_2)
        self.gridLayout_7.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.splitter_5 = QtWidgets.QSplitter(self.left_pane_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter_5.sizePolicy().hasHeightForWidth())
        self.splitter_5.setSizePolicy(sizePolicy)
        self.splitter_5.setOrientation(QtCore.Qt.Vertical)
        self.splitter_5.setObjectName("splitter_5")
        self.frame_4 = QtWidgets.QFrame(self.splitter_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_4.sizePolicy().hasHeightForWidth())
        self.frame_4.setSizePolicy(sizePolicy)
        self.frame_4.setAutoFillBackground(False)
        self.frame_4.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_4.setObjectName("frame_4")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.frame_4)
        self.gridLayout_8.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.splitter_6 = QtWidgets.QSplitter(self.frame_4)
        self.splitter_6.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.splitter_6.setFrameShadow(QtWidgets.QFrame.Plain)
        self.splitter_6.setLineWidth(1)
        self.splitter_6.setOrientation(QtCore.Qt.Vertical)
        self.splitter_6.setObjectName("splitter_6")
        self.right_top_pane = GeometrySerializableFrame(self.splitter_6)
        self.right_top_pane.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.right_top_pane.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.right_top_pane.setObjectName("right_top_pane")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.right_top_pane)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.tabWidget = QtWidgets.QTabWidget(self.right_top_pane)
        self.tabWidget.setObjectName("tabWidget")
        self.modelTab1 = QtWidgets.QWidget()
        self.modelTab1.setObjectName("modelTab1")
        self.tabWidget.addTab(self.modelTab1, "")
        self.noneed = QtWidgets.QWidget()
        self.noneed.setObjectName("noneed")
        self.tabWidget.addTab(self.noneed, "")
        self.verticalLayout_8.addWidget(self.tabWidget)
        self.right_bottom_pane = QtWidgets.QFrame(self.splitter_6)
        self.right_bottom_pane.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.right_bottom_pane.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.right_bottom_pane.setObjectName("right_bottom_pane")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.right_bottom_pane)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.label_3 = QtWidgets.QLabel(self.right_bottom_pane)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_12.addWidget(self.label_3)
        self.messages = QtWidgets.QTextBrowser(self.right_bottom_pane)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.messages.sizePolicy().hasHeightForWidth())
        self.messages.setSizePolicy(sizePolicy)
        self.messages.setObjectName("messages")
        self.verticalLayout_12.addWidget(self.messages)
        self.gridLayout_8.addWidget(self.splitter_6, 0, 0, 1, 1)
        self.gridLayout_7.addWidget(self.splitter_5, 0, 0, 1, 1)
        self.gridLayout_10.addWidget(self.left_pane_2, 0, 0, 1, 1)
        self.verticalLayout_5.addWidget(self.splitter_3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1167, 24))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuVersion = QtWidgets.QMenu(self.menubar)
        self.menuVersion.setObjectName("menuVersion")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuView_Scene = QtWidgets.QMenu(self.menubar)
        self.menuView_Scene.setObjectName("menuView_Scene")
        self.menuModel = QtWidgets.QMenu(self.menubar)
        self.menuModel.setObjectName("menuModel")
        self.menuLabel = QtWidgets.QMenu(self.menubar)
        self.menuLabel.setObjectName("menuLabel")
        self.menuSolver_Simulation = QtWidgets.QMenu(self.menubar)
        self.menuSolver_Simulation.setObjectName("menuSolver_Simulation")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionClose = QtWidgets.QAction(MainWindow)
        self.actionClose.setObjectName("actionClose")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setEnabled(False)
        self.actionSave.setObjectName("actionSave")
        self.actionSaveAs = QtWidgets.QAction(MainWindow)
        self.actionSaveAs.setEnabled(False)
        self.actionSaveAs.setObjectName("actionSaveAs")
        self.actionImport = QtWidgets.QAction(MainWindow)
        self.actionImport.setEnabled(False)
        self.actionImport.setObjectName("actionImport")
        self.actionExport = QtWidgets.QAction(MainWindow)
        self.actionExport.setEnabled(False)
        self.actionExport.setObjectName("actionExport")
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.actionVersion = QtWidgets.QAction(MainWindow)
        self.actionVersion.setEnabled(False)
        self.actionVersion.setObjectName("actionVersion")
        self.actionHelp = QtWidgets.QAction(MainWindow)
        self.actionHelp.setEnabled(False)
        self.actionHelp.setObjectName("actionHelp")
        self.actionFitToScene = QtWidgets.QAction(MainWindow)
        self.actionFitToScene.setEnabled(True)
        self.actionFitToScene.setObjectName("actionFitToScene")
        self.actionAddConstraint = QtWidgets.QAction(MainWindow)
        self.actionAddConstraint.setEnabled(False)
        self.actionAddConstraint.setObjectName("actionAddConstraint")
        self.actionDeleteConstraint = QtWidgets.QAction(MainWindow)
        self.actionDeleteConstraint.setEnabled(False)
        self.actionDeleteConstraint.setObjectName("actionDeleteConstraint")
        self.actionModelCheck = QtWidgets.QAction(MainWindow)
        self.actionModelCheck.setEnabled(False)
        self.actionModelCheck.setObjectName("actionModelCheck")
        self.actionChangeNodeLabel = QtWidgets.QAction(MainWindow)
        self.actionChangeNodeLabel.setObjectName("actionChangeNodeLabel")
        self.actionNode_Id_to_Label = QtWidgets.QAction(MainWindow)
        self.actionNode_Id_to_Label.setObjectName("actionNode_Id_to_Label")
        self.actionNode_Complexity_to_Label = QtWidgets.QAction(MainWindow)
        self.actionNode_Complexity_to_Label.setObjectName("actionNode_Complexity_to_Label")
        self.actionEdge_Id_to_Label = QtWidgets.QAction(MainWindow)
        self.actionEdge_Id_to_Label.setObjectName("actionEdge_Id_to_Label")
        self.actionEdge_Distance_to_Label = QtWidgets.QAction(MainWindow)
        self.actionEdge_Distance_to_Label.setObjectName("actionEdge_Distance_to_Label")
        self.actionEdge_Description_to_Label = QtWidgets.QAction(MainWindow)
        self.actionEdge_Description_to_Label.setObjectName("actionEdge_Description_to_Label")
        self.actionNode_Description_to_Label = QtWidgets.QAction(MainWindow)
        self.actionNode_Description_to_Label.setObjectName("actionNode_Description_to_Label")
        self.actionNode_Tooltips = QtWidgets.QAction(MainWindow)
        self.actionNode_Tooltips.setObjectName("actionNode_Tooltips")
        self.actionEdge_Tooltips = QtWidgets.QAction(MainWindow)
        self.actionEdge_Tooltips.setObjectName("actionEdge_Tooltips")
        self.actionLayout_Manager = QtWidgets.QAction(MainWindow)
        self.actionLayout_Manager.setEnabled(False)
        self.actionLayout_Manager.setObjectName("actionLayout_Manager")
        self.actionConsole = QtWidgets.QAction(MainWindow)
        self.actionConsole.setEnabled(True)
        self.actionConsole.setObjectName("actionConsole")
        self.actionScript_Editor = QtWidgets.QAction(MainWindow)
        self.actionScript_Editor.setEnabled(True)
        self.actionScript_Editor.setObjectName("actionScript_Editor")
        self.actionNew = QtWidgets.QAction(MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionStart_Solver = QtWidgets.QAction(MainWindow)
        self.actionStart_Solver.setEnabled(True)
        self.actionStart_Solver.setObjectName("actionStart_Solver")
        self.actionCut = QtWidgets.QAction(MainWindow)
        self.actionCut.setEnabled(False)
        self.actionCut.setObjectName("actionCut")
        self.actionCopy = QtWidgets.QAction(MainWindow)
        self.actionCopy.setEnabled(False)
        self.actionCopy.setObjectName("actionCopy")
        self.actionPaste = QtWidgets.QAction(MainWindow)
        self.actionPaste.setEnabled(False)
        self.actionPaste.setObjectName("actionPaste")
        self.actionVisualizer = QtWidgets.QAction(MainWindow)
        self.actionVisualizer.setEnabled(True)
        self.actionVisualizer.setObjectName("actionVisualizer")
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionClose)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionImport)
        self.menuFile.addAction(self.actionExport)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menuVersion.addAction(self.actionHelp)
        self.menuVersion.addAction(self.actionVersion)
        self.menuEdit.addAction(self.actionCut)
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)
        self.menuView_Scene.addAction(self.actionFitToScene)
        self.menuView_Scene.addAction(self.actionConsole)
        self.menuView_Scene.addAction(self.actionScript_Editor)
        self.menuModel.addAction(self.actionAddConstraint)
        self.menuModel.addAction(self.actionDeleteConstraint)
        self.menuModel.addSeparator()
        self.menuModel.addAction(self.actionModelCheck)
        self.menuModel.addAction(self.actionLayout_Manager)
        self.menuLabel.addAction(self.actionNode_Id_to_Label)
        self.menuLabel.addAction(self.actionNode_Complexity_to_Label)
        self.menuLabel.addAction(self.actionNode_Description_to_Label)
        self.menuLabel.addSeparator()
        self.menuLabel.addAction(self.actionEdge_Id_to_Label)
        self.menuLabel.addAction(self.actionEdge_Distance_to_Label)
        self.menuLabel.addAction(self.actionEdge_Description_to_Label)
        self.menuLabel.addSeparator()
        self.menuLabel.addAction(self.actionNode_Tooltips)
        self.menuLabel.addAction(self.actionEdge_Tooltips)
        self.menuSolver_Simulation.addAction(self.actionStart_Solver)
        self.menuSolver_Simulation.addAction(self.actionVisualizer)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView_Scene.menuAction())
        self.menubar.addAction(self.menuModel.menuAction())
        self.menubar.addAction(self.menuSolver_Simulation.menuAction())
        self.menubar.addAction(self.menuLabel.menuAction())
        self.menubar.addAction(self.menuVersion.menuAction())

        self.retranslateUi(MainWindow)
        self.editorTabWidget.setCurrentIndex(2)
        self.tabWidget.setCurrentIndex(0)
        self.actionOpen.triggered.connect(MainWindow.command_open)
        self.actionQuit.triggered.connect(MainWindow.command_quit)
        self.actionClose.triggered.connect(MainWindow.command_close)
        self.actionSave.triggered.connect(MainWindow.command_save)
        self.actionSaveAs.triggered.connect(MainWindow.command_saveAs)
        self.actionFitToScene.triggered.connect(MainWindow.command_fit_to_scene)
        self.actionDeleteConstraint.triggered.connect(MainWindow.command_delete_constraint)
        self.actionNode_Id_to_Label.triggered.connect(MainWindow.command_set_node_id_to_label)
        self.actionNode_Complexity_to_Label.triggered.connect(MainWindow.command_set_node_complexity_to_label)
        self.actionNode_Description_to_Label.triggered.connect(MainWindow.command_set_node_caption_to_label)
        self.actionEdge_Id_to_Label.triggered.connect(MainWindow.command_set_edge_id_to_label)
        self.actionEdge_Distance_to_Label.triggered.connect(MainWindow.command_set_edge_distance_to_label)
        self.actionEdge_Description_to_Label.triggered.connect(MainWindow.command_set_edge_caption_to_label)
        self.actionEdge_Tooltips.triggered.connect(MainWindow.command_change_edge_tooltips)
        self.actionNode_Tooltips.triggered.connect(MainWindow.command_change_node_tooltips)
        self.actionModelCheck.triggered.connect(MainWindow.command_model_check)
        self.actionLayout_Manager.triggered.connect(MainWindow.command_layout_manager)
        self.actionAddConstraint.triggered.connect(MainWindow.command_add_constraint)
        self.actionConsole.triggered.connect(MainWindow.command_console)
        self.actionScript_Editor.triggered.connect(MainWindow.command_script_editor)
        self.actionNew.triggered.connect(MainWindow.command_new_model)
        self.tabWidget.currentChanged['int'].connect(MainWindow.command_change_current)
        self.actionStart_Solver.triggered.connect(MainWindow.command_start_solver)
        self.actionVisualizer.triggered.connect(MainWindow.command_visualizer)
        self.addUserConstraintButton.clicked.connect(MainWindow.command_add_constraint)
        self.deleteUserConstraintButton.clicked.connect(MainWindow.command_delete_constraint)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Elements"))
        self.editorTabWidget.setTabText(self.editorTabWidget.indexOf(self.tab_7), _translate("MainWindow", "Property"))
        self.editorTabWidget.setTabText(self.editorTabWidget.indexOf(self.tab), _translate("MainWindow", "Nodes"))
        self.editorTabWidget.setTabText(self.editorTabWidget.indexOf(self.tab_2), _translate("MainWindow", "Edges"))
        self.label_4.setText(_translate("MainWindow", "System constraints"))
        self.label_5.setText(_translate("MainWindow", "User constraints"))
        self.addUserConstraintButton.setText(_translate("MainWindow", "Add"))
        self.deleteUserConstraintButton.setText(_translate("MainWindow", "Delete"))
        self.editorTabWidget.setTabText(self.editorTabWidget.indexOf(self.tab_5), _translate("MainWindow", "Constraints"))
        self.label_2.setText(_translate("MainWindow", "Errors"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.modelTab1), _translate("MainWindow", "Untitled"))
        self.label_3.setText(_translate("MainWindow", "Messages"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuVersion.setTitle(_translate("MainWindow", "Version"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuView_Scene.setTitle(_translate("MainWindow", "View/Scene"))
        self.menuModel.setTitle(_translate("MainWindow", "Model"))
        self.menuLabel.setTitle(_translate("MainWindow", "Label"))
        self.menuSolver_Simulation.setTitle(_translate("MainWindow", "Solver/Simulation"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionClose.setText(_translate("MainWindow", "Close"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSaveAs.setText(_translate("MainWindow", "SaveAs"))
        self.actionImport.setText(_translate("MainWindow", "Import"))
        self.actionExport.setText(_translate("MainWindow", "Export"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        self.actionVersion.setText(_translate("MainWindow", "Version"))
        self.actionHelp.setText(_translate("MainWindow", "Help"))
        self.actionFitToScene.setText(_translate("MainWindow", "Fit to Scene"))
        self.actionAddConstraint.setText(_translate("MainWindow", "Add Constraint"))
        self.actionDeleteConstraint.setText(_translate("MainWindow", "Delete Constraint"))
        self.actionModelCheck.setText(_translate("MainWindow", "Model Check"))
        self.actionChangeNodeLabel.setText(_translate("MainWindow", "Change Node Label"))
        self.actionNode_Id_to_Label.setText(_translate("MainWindow", "Node Id to Label"))
        self.actionNode_Complexity_to_Label.setText(_translate("MainWindow", "Node Complexity to Label"))
        self.actionEdge_Id_to_Label.setText(_translate("MainWindow", "Edge Id to Label"))
        self.actionEdge_Distance_to_Label.setText(_translate("MainWindow", "Edge distance to Label"))
        self.actionEdge_Description_to_Label.setText(_translate("MainWindow", "Edge Description to Label"))
        self.actionNode_Description_to_Label.setText(_translate("MainWindow", "Node Description to Label"))
        self.actionNode_Tooltips.setText(_translate("MainWindow", "Node Tooltips"))
        self.actionEdge_Tooltips.setText(_translate("MainWindow", "Edge Tooltips"))
        self.actionLayout_Manager.setText(_translate("MainWindow", "Layout Manager"))
        self.actionConsole.setText(_translate("MainWindow", "Console"))
        self.actionScript_Editor.setText(_translate("MainWindow", "Script Editor"))
        self.actionNew.setText(_translate("MainWindow", "New"))
        self.actionStart_Solver.setText(_translate("MainWindow", "Solver Contorller"))
        self.actionCut.setText(_translate("MainWindow", "Cut"))
        self.actionCopy.setText(_translate("MainWindow", "Copy"))
        self.actionPaste.setText(_translate("MainWindow", "Paste"))
        self.actionVisualizer.setText(_translate("MainWindow", "Visualizer"))
from gui.geomserializable import GeometrySerializableFrame
