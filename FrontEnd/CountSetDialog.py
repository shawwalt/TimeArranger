import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel

from UI.UI_CountSetDialog import Ui_CountSetDialog
from Log.my_logger import LoggerHandler
from PyQt5.QtWidgets import QDialog, QDesktopWidget, QMessageBox
from PyQt5.QtCore import QSettings, QPoint, pyqtSignal, Qt
from FrontEnd.global_var import *
from resources import *


class CountSetDialog(Ui_CountSetDialog, QDialog):
    # 自定义信号
    count_down_set_signal = pyqtSignal()
    task_to_be_complete_selected_signal = pyqtSignal(str)

    # 成员变量
    conn = None  # 数据库连接的引用
    mode = WORKING  # 工作模式

    def __init__(self, mode):
        super().__init__()
        self.mode = mode

        self.setupUi(self)
        self._logger_init()
        self._init_ui()
        self._init_DB()
        self._init_settings()

    def _init_ui(self):
        # 设定窗口位置到屏幕正中
        self.move(
            self._get_central_pos()
        )
        self.setWindowIcon(QIcon(':/icon/icon.png'))

        self.btn_ok.clicked.connect(self.btn_ok_clicked)
        self.btn_cancel.clicked.connect(self.btn_cancel_clicked)
        self.spinBox_h.setRange(0, 59)
        self.spinBox_m.setRange(0, 59)
        self.spinBox_s.setRange(0, 59)
        self.logger.info('TimeArranger启动')

    def _init_DB(self):
        global SOFTWARE_PATH, DB_NAME
        conn_name = SOFTWARE_PATH + '//' + DB_NAME
        self.conn = QSqlDatabase.database(conn_name)
        self.model_listView_task = QSqlQueryModel()
        self.model_listView_task.setQuery('SELECT * FROM Todolist', self.conn)
        self.listView_task.setModel(self.model_listView_task)

    def _init_settings(self):
        self.setting_manager = QSettings('ShawWalt', 'TimeArranger')
        b = self.setting_manager.value('MainWindow/WorkingPeriod', 900)
        self._set_spin_boxs(int(b))
        self.logger.debug('设置初始化')

    def _save_settings(self):
        count_time = self._get_time_from_spinbox()
        self.setting_manager.setValue('MainWindow/WorkingPeriod', str(count_time))
        self.logger.debug('保存新设置')

    def _logger_init(self):
        # 初始化日志器参数
        self.logger = LoggerHandler(
            name=__name__
        )
        self.logger.debug('Logger初始化')

    def _get_time_from_spinbox(self):
        h = self.spinBox_h.value()
        m = self.spinBox_m.value()
        s = self.spinBox_s.value()
        return h * 3600 + m * 60 + s

    def _set_spin_boxs(self, time):
        h = time / 60 / 60
        m = time % 3600 / 60
        s = time % 60
        self.spinBox_s.setValue(s)
        self.spinBox_m.setValue(m)
        self.spinBox_h.setValue(h)

    def btn_ok_clicked(self):
        # 检查数据库连接状态
        if self.conn is None:
            self.logger.error('数据库未连接')
            sys.exit(1)

        text = self.listView_task.currentIndex().data()
        if self.mode == WORKING:
            if text is None:
                QMessageBox.warning(self, '未选择该段时间内要完成的工作', '请选择将要完成的工作')
                return
            self._save_settings()
            #  将操作信息录入数据库
            query = QSqlQuery()
            query.prepare('''
            INSERT INTO BasicUserData 
            (TASK, DURATION)
            VALUES (:TASK, :DURATION);
            ''')
            # 此时只插入了要完成的任务和指定的完成时间，其他都为默认值
            query.bindValue(':TASK', text)
            query.bindValue(':DURATION', self._get_time_from_spinbox())
            if not query.exec():
                self.logger.error('用户数据初始化插入失败')
                sys.exit(1)

            #  触发软件计时
            self.task_to_be_complete_selected_signal.emit(text)
            self.count_down_set_signal.emit()
            self.logger.debug('保存按钮按下')
        else:
            #  将操作信息录入数据库
            query = QSqlQuery()
            query.prepare('''
                        INSERT INTO BasicUserData 
                        (DURATION)
                        VALUES (:DURATION);
                        ''')
            # 休息模式只插入休息时间，其他都为默认值
            query.bindValue(':DURATION', self._get_time_from_spinbox())
            if not query.exec():
                self.logger.error('用户数据初始化插入失败')
                sys.exit(1)
            self._save_settings()
            self.count_down_set_signal.emit()

        self.close()

    def btn_cancel_clicked(self):
        self.logger.debug('取消按钮按下')
        self.close()

    def _get_central_pos(self) -> QPoint:
        # 获取屏幕中心坐标
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        return QPoint(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))
