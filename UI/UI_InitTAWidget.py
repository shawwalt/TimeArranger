# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'InitTAWidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_InitTAWidget(object):
    def setupUi(self, InitTAWidget):
        InitTAWidget.setObjectName("InitTAWidget")
        InitTAWidget.resize(1122, 641)
        self.centralwidget = QtWidgets.QWidget(InitTAWidget)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lcdNumber = QtWidgets.QLCDNumber(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lcdNumber.sizePolicy().hasHeightForWidth())
        self.lcdNumber.setSizePolicy(sizePolicy)
        self.lcdNumber.setMaximumSize(QtCore.QSize(16777215, 1000))
        self.lcdNumber.setObjectName("lcdNumber")
        self.verticalLayout.addWidget(self.lcdNumber)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.btn_start_timing = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_start_timing.sizePolicy().hasHeightForWidth())
        self.btn_start_timing.setSizePolicy(sizePolicy)
        self.btn_start_timing.setObjectName("btn_start_timing")
        self.verticalLayout.addWidget(self.btn_start_timing)
        self.btn_stop_timing = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_stop_timing.sizePolicy().hasHeightForWidth())
        self.btn_stop_timing.setSizePolicy(sizePolicy)
        self.btn_stop_timing.setObjectName("btn_stop_timing")
        self.verticalLayout.addWidget(self.btn_stop_timing)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.listView = QtWidgets.QListView(self.tab)
        self.listView.setObjectName("listView")
        self.verticalLayout_2.addWidget(self.listView)
        self.btn_new_task = QtWidgets.QPushButton(self.tab)
        self.btn_new_task.setObjectName("btn_new_task")
        self.verticalLayout_2.addWidget(self.btn_new_task)
        self.btn_rm_task = QtWidgets.QPushButton(self.tab)
        self.btn_rm_task.setObjectName("btn_rm_task")
        self.verticalLayout_2.addWidget(self.btn_rm_task)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.listWidget_log = QtWidgets.QListWidget(self.tab_2)
        self.listWidget_log.setObjectName("listWidget_log")
        self.verticalLayout_3.addWidget(self.listWidget_log)
        self.tabWidget.addTab(self.tab_2, "")
        self.horizontalLayout.addWidget(self.tabWidget)
        InitTAWidget.setCentralWidget(self.centralwidget)
        self.toolBar = QtWidgets.QToolBar(InitTAWidget)
        self.toolBar.setMovable(False)
        self.toolBar.setObjectName("toolBar")
        InitTAWidget.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.action_config = QtWidgets.QAction(InitTAWidget)
        self.action_config.setObjectName("action_config")
        self.action_statistics = QtWidgets.QAction(InitTAWidget)
        self.action_statistics.setObjectName("action_statistics")
        self.toolBar.addSeparator()

        self.retranslateUi(InitTAWidget)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(InitTAWidget)

    def retranslateUi(self, InitTAWidget):
        _translate = QtCore.QCoreApplication.translate
        InitTAWidget.setWindowTitle(_translate("InitTAWidget", "TimeArranger"))
        self.btn_start_timing.setText(_translate("InitTAWidget", "开始计时"))
        self.btn_stop_timing.setText(_translate("InitTAWidget", "停止计时"))
        self.btn_new_task.setText(_translate("InitTAWidget", "添加新的待办"))
        self.btn_rm_task.setText(_translate("InitTAWidget", "删除待办"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("InitTAWidget", "任务列表"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("InitTAWidget", "运行日志"))
        self.toolBar.setWindowTitle(_translate("InitTAWidget", "toolBar"))
        self.action_config.setText(_translate("InitTAWidget", "配置"))
        self.action_config.setToolTip(_translate("InitTAWidget", "软件常规设置"))
        self.action_statistics.setText(_translate("InitTAWidget", "统计数据"))
        self.action_statistics.setToolTip(_translate("InitTAWidget", "可视化电脑使用时长统计"))
