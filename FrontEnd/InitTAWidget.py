import os
import sys
import resources
from functools import partial

from PyQt5 import QtCore
from PyQt5.QtGui import QIcon

from UI.UI_InitTAWidget import Ui_InitTAWidget
from UI.UI_LogWidget import Ui_LogWidget
from FrontEnd.ClockWidget import ClockWidget
from FrontEnd.CountSetDialog import CountSetDialog
from FrontEnd.CopyRight import CopyRight
from FrontEnd.StatisticsWidget import StatisticsWidget
from Log.my_logger import LoggerHandler
from PyQt5.QtCore import (QTimer, QSettings, QPoint, QVariant, pyqtSignal, Qt, QSize)
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QMessageBox, QSystemTrayIcon, QMenu, QAction, QInputDialog, \
    QWidget, QListWidgetItem
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel
from FrontEnd.global_var import *


#  系统托盘类
class TrayIcon(QSystemTrayIcon):
    quit_signal = pyqtSignal(int)
    hide_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(TrayIcon, self).__init__(parent)
        self._logger_init()
        self._show_menu()
        self._other()

    def _logger_init(self):
        # 初始化日志器参数
        self.logger = LoggerHandler(
            name=__name__
        )
        self.logger.debug('Logger初始化')

    def _show_menu(self):
        # 设计托盘的菜单，这里我实现了一个二级菜单
        self.menu = QMenu()
        self.quitAction = QAction("退出", self, triggered=self.quit)
        self.menu.addAction(self.quitAction)
        self.setContextMenu(self.menu)

    def _other(self):
        # 添加信号与槽函数的绑定
        self.activated.connect(self.icon_clicked)

    def icon_clicked(self, reason):
        # 鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击
        if reason == 2 or reason == 3:
            self.hide_signal.emit()

    def quit(self):
        self.quit_signal.emit(0)


class LogWidget(QWidget, Ui_LogWidget):
    def __init__(self, log_time, log_msg, log_level, parent=None):
        super(LogWidget, self).__init__(parent)
        self.setupUi(self)
        self.log_msg.setText(log_msg)
        self.log_level.setText(log_level)
        self.log_time.setText(log_time)


class InitTAWidget(Ui_InitTAWidget, QMainWindow):

    statistics_widget = None
    copy_right = None
    clock_widget = None
    count_set_dialog = None
    ti = None

    timer = None
    timer_copy_right = None
    setting_manager = None

    # 软件状态变量
    is_timing = False  # 计时状态变量
    duration = 0  # 计时持续时间
    mode = WORKING  # 计时模式变量
    conn = None  # 数据库连接的引用
    selected_task = ''  # 被选中的要完成的任务

    # 自定义信号
    count_down_terminate_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._logger_init()  # 初始化日志模块
        self._init_ui()  # 初始化信号与槽的绑定，界面大小等参数的设置，数据库的的加载等
        self._init_settings()
        self._init_DB()
        self._copy_right_init()
        self._tray_icon_init()
        self._clock_widget_init()
        self._init_listView_log()

    def _init_ui(self):
        # 初始化信号与槽的绑定，界面大小等参数的设置，数据库的的加载等
        self.setFixedSize(self.size())
        self.setWindowIcon(QIcon(':/icon/icon.png'))

        # 1.向工具栏添加按钮用于模式切换
        self.action_mode = QAction()
        if self.mode == WORKING:
            self.action_mode.setIcon(QIcon(':/icon/work.png'))
        else:
            self.action_data_analysis.setIcon(QIcon(':/icon/relaxing.png'))
        self.action_data_analysis = QAction()
        self.action_data_analysis.setIcon(QIcon(':/icon/statistics.png'))
        self.toolBar.addAction(self.action_mode)
        self.toolBar.addAction(self.action_data_analysis)
        self.toolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.btn_stop_timing.setDisabled(True)
        self.btn_start_timing.setDisabled(False)

        # 初始话定时器模块
        self._timer_init()
        self._lcd_init()
        self.action_statistics.triggered.connect(self.action_statistics_triggered)
        self.btn_start_timing.clicked.connect(self.btn_start_timing_clicked)
        self.btn_stop_timing.clicked.connect(self.btn_stop_timing_clicked)
        self.btn_new_task.clicked.connect(self.btn_new_task_clicked)
        self.btn_rm_task.clicked.connect(self.btn_rm_task_clicked)
        self.action_mode.triggered.connect(self.btn_mode_clicked)
        self.action_data_analysis.triggered.connect(self.btn_data_analysis_clicked)
        self.count_down_terminate_signal.connect(self.count_down_terminate_signal_triggered)

    def _init_settings(self):
        self.setting_manager = QSettings('ShawWalt', 'TimeArranger')
        self.move(
            self.setting_manager.value('MainWindow/win_pos', QVariant(self._get_central_pos()))
        )

        self.mode = self.setting_manager.value('MainWindow/mode', WORKING)
        self._switch_widget_with_mode()

    def _save_settings(self):
        self.setting_manager.setValue('MainWindow/mode', self.mode)
        self.setting_manager.setValue('MainWindow/win_pos', QVariant(QPoint(self.x(), self.y())))

    def _open_DB(self):
        # 初始化数据库，默认没有则新建，已有则沿用
        global SOFTWARE_PATH, DB_NAME
        self.conn = QSqlDatabase.addDatabase("QSQLITE")
        self.db_path = SOFTWARE_PATH + '//' + DB_NAME
        self.conn.setDatabaseName(self.db_path)
        if not self.conn.open():
            QMessageBox.critical(
                None,
                "TimeArranger - 错误!",
                "数据库连接错误: %s" % self.conn.lastError().databaseText(),
            )
            sys.exit(1)
        self.logger.debug('开启数据库访问')

    def _close_DB(self):
        self.conn.close()
        self.logger.debug('关闭数据库访问')

    def _init_DB(self):
        # todo 一系列的根据数据库初始话控件的操作
        # 开启数据库，确定连接已建立
        self._open_DB()
        if self.conn is None:
            self.logger.error('数据库建立失败')
            sys.exit(1)

        # 获取整个数据库的数据表清单
        query = QSqlQuery(self.conn)
        query.prepare('SELECT * FROM sqlite_schema WHERE type=\'table\' ORDER BY name;')
        if not query.exec():
            self.logger.error('获取tables错误')
        tables = []
        while(query.next()):
            tables.append(query.value('name'))

        # 初始话代办清单的控件相关的数据表
        if 'Todolist' not in tables:
            query.prepare('''
                CREATE TABLE Todolist(
                    NAME text PRIMARY KEY UNIQUE 
                );
            ''')
            if not query.exec():
                self.logger.error('Todolist建表错误')
                sys.exit(1)

        # 初始化ListView模型并绑定视图
        self.model_listView = QSqlQueryModel()
        self.model_listView.setQuery('SELECT * FROM Todolist')
        self.model_listView.setHeaderData(0, Qt.Horizontal, 'NAME')
        self.listView.setModel(self.model_listView)

        # 创建用户使用数据的数据表
        if 'BasicUserData' not in tables:
            # 切记获取时间时要转成本地时间(UTC -> LOCAL_TIME)
            query.prepare('''
                CREATE TABLE BasicUserData(
                    TASK TEXT DEFAULT 'NONE' NOT NULL ,
                    START_TIME_STAMP TEXT DEFAULT CURRENT_TIMESTAMP PRIMARY KEY,
                    END_TIME_STAMP TEXT DEFAULT CURRENT_TIMESTAMP ,
                    IS_INTERRUPTED TEXT DEFAULT 'UNKNOWN',
                    IS_UNFINISHED TEXT DEFAULT 'YES',
                    DURATION INTEGER NOT NULL DEFAULT -1
                );
            ''')
            if not query.exec():
                self.logger.error('用户数据库建立失败: %s' % query.lastError().text())
                sys.exit(1)

            # 删除异常退出留下的垃圾数据
            query.prepare("DELETE FROM BasicUserData WHERE IS_INTERRUPTED = (:is_interrupted)")
            query.bindValue(':is_interrupted', UNKNOWN)
            if not query.exec():
                self.logger.error('删除数据异常')
                sys.exit(1)

    def _switch_widget_with_mode(self):
        if self.mode == WORKING:
            self.lcdNumber.setStyleSheet('border: 1px solid green; color: green; background: silver;')
            self.action_mode.setIcon(QIcon(':/icon/work.png'))
            self.btn_new_task.setEnabled(True)
            self.btn_rm_task.setEnabled(True)
            self.listView.setEnabled(True)
        else:
            self.lcdNumber.setStyleSheet('border: 1px solid blue; color: blue; background: silver;')
            self.action_mode.setIcon(QIcon(':/icon/relaxing.png'))
            self.btn_new_task.setEnabled(False)
            self.btn_rm_task.setEnabled(False)
            self.listView.setEnabled(False)

    def btn_data_analysis_clicked(self):
        # todo 数据分析功能的具体实现
        self.statistics_widget = StatisticsWidget()
        self.statistics_widget.show()

    def _tray_icon_init(self):
        self.ti = TrayIcon(self)
        self.ti.setIcon(QIcon(':/icon/icon.png'))
        self.ti.quit_signal.connect(self.quit)
        self.ti.hide_signal.connect(self.switch_between_show_n_hide)
        self.ti.show()
        self.logger.debug('托盘图标初始化')

    def _count_set_widget_init(self):
        self.count_set_dialog = CountSetDialog(self.mode)
        self.count_set_dialog.count_down_set_signal.connect(self.count_down_set_signal_triggered)
        self.count_set_dialog.task_to_be_complete_selected_signal.connect(self.task_to_be_complete_selected_triggered)
        self.logger.debug('计时设置面板初始化')

    def _copy_right_init(self):
        if self.copy_right is None:
            self.copy_right = CopyRight()
        self.copy_right.show()
        self.timer_copy_right.start(3000)
        self.logger.debug('加载版权页')

    def _copy_right_close(self):
        self.copy_right.close()
        self.timer_copy_right.stop()
        self.activateWindow()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.showNormal()
        self.logger.debug('版权页关闭 ,显示主界面')

    def _clock_widget_init(self):
        self.clock_widget = ClockWidget()
        self.clock_widget.label.setText('工作时间剩余:00:00:00')
        self.logger.debug('计时小控件初始化')

    def _statistics_widget_init(self):
        # 数据分析界面初始化
        self.statistics_widget = StatisticsWidget()
        self.statistics_widget.show()
        self.logger.debug('数据分析界面初始化')

    def _logger_init(self):
        # 初始化日志器参数
        self.logger = LoggerHandler(
            name=__name__
        )
        self.logger.set_file_handler(
            file=SOFTWARE_PATH,
            logger_level='INFO',
            fmt='%(asctime)s %(levelname)s %(message)s'
        )
        self.logger.debug('Logger初始化')

    def _lcd_init(self):
        self.lcdNumber.setDigitCount(8)
        self.lcdNumber.display('00:00:00')
        self.logger.debug('LCD初始化')

    def _timer_init(self):
        self.timer = QTimer()
        self.timer_copy_right = QTimer()
        self.timer.timeout.connect(self.timer_count_down)
        self.timer_copy_right.timeout.connect(self._copy_right_close)
        self.logger.debug('QTimer初始化')

    def _get_central_pos(self) -> QPoint:
        # 获取屏幕中心坐标
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        return QPoint(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))

    def action_statistics_triggered(self):
        if self.statistics_widget is None:
            self.statistics_widget = StatisticsWidget()
        self.statistics_widget.show()
        self.logger.debug('打开数据分析面板')

    def btn_start_timing_clicked(self):
        # 绑定计时函数，一旦按下Ok，配置界面关闭
        self._count_set_widget_init()
        if self.mode == WORKING:
            self.count_set_dialog.show()
            self.logger.debug('打开计时设置面板,工作模式')
        else:
            self.count_set_dialog.show()
            self.count_set_dialog.listView_task.setDisabled(True)
            self.logger.debug('打开计时设置面板,休息模式')

    def btn_stop_timing_clicked(self):
        self.logger.debug('停止计时按钮按下')
        msg = QMessageBox()
        if self.mode == WORKING:
            msg.setText('还在计时中')
            msg.setInformativeText('规定的工作时长还未达到，确定放弃自律了吗？')
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        else:
            msg.setText('还在计时中')
            msg.setInformativeText('再休息一下吧，恢复精力也是工作的一部分')
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        ret = msg.exec()

        if ret == QMessageBox.Ok:
            self.timer.stop()

            self.is_timing = False
            self.btn_stop_timing.setDisabled(True)
            self.btn_start_timing.setDisabled(False)
            if self.mode == WORKING:
                self.listView.setDisabled(False)
                self.btn_new_task.setDisabled(False)
                self.btn_rm_task.setDisabled(False)
            self.lcdNumber.display('00:00:00')
            self.clock_widget.label.setText('工作时间剩余00:00:00')
            self.clock_widget.close()

        # 用户数据录入
        global YES, NO, UNKNOWN
        if self.conn is None:
            self.logger.error('数据库未连接')
            sys.exit(1)

        query = QSqlQuery()
        query.prepare('''
                UPDATE BasicUserData 
                SET END_TIME_STAMP = DATETIME('now'), IS_INTERRUPTED = :IS_INTERRUPTED,
                DURATION = DURATION - (:TIME_LEFT)
                WHERE START_TIME_STAMP = (SELECT MAX(START_TIME_STAMP) FROM BasicUserData);
        ''')
        query.bindValue(':IS_INTERRUPTED', YES)
        query.bindValue(':TIME_LEFT', self.duration)
        if not query.exec():
            self.logger.error('更新记录失败')
            sys.exit(1)


    def task_to_be_complete_selected_triggered(self, text):
        # 完成对任务的选择
        self.selected_task = text

    def count_down_set_signal_triggered(self):
        # 从注册表加载计时时间
        # 加载计时时间
        self.duration = self.setting_manager.value('MainWindow/WorkingPeriod', 300)
        self.duration = int(self.duration)  # 切记注册表存的是字符串，要转回原类型
        h, m, s = self._int2time(self.duration)
        time_fmt = "%02d:%02d:%02d" % (h, m, s)
        self.lcdNumber.display(
            time_fmt
        )
        # 设置对应的控件状态
        self.btn_start_timing.setDisabled(True)
        self.btn_stop_timing.setDisabled(False)
        self.btn_rm_task.setDisabled(True)
        self.btn_new_task.setDisabled(True)

        # 根据不同状态设置不同文本和日志
        if self.mode == WORKING:
            self.clock_widget.label.setText('工作时间剩余:' + time_fmt)
            self.logger.info('开始执行任务')
        else:
            self.clock_widget.label.setText('休息时间剩余:' + time_fmt)
            self.logger.info('开始休息')
            self.logger.debug('开始计时(休息时间)')

        self.is_timing = True
        self.timer.start(1000)

    def count_down_terminate_signal_triggered(self):
        # 录入用户数据到BasicUserData
        global UNKNOWN, YES, NO

        # 检查数据库连接状态
        if self.conn is None:
            self.logger.error('数据库连接丢失')
            sys.exit(1)

        # 首先关闭定时器
        self.timer.stop()

        self.logger.debug('计时结束')
        self.showNormal()
        # 提示框
        msg = QMessageBox(self)

        if self.mode == WORKING:
            self.listView.setDisabled(False)
            self.btn_rm_task.setDisabled(False)
            self.btn_new_task.setDisabled(False)
            msg.setText('计时结束, %s是否已完成' % self.selected_task)
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.buttonClicked.connect(self.msg_remove_task_ok)
            msg.show()
        else:
            self.listView.setDisabled(True)
            self.btn_rm_task.setDisabled(True)
            self.btn_new_task.setDisabled(True)
            msg.setWindowTitle('计时结束')
            msg.setInformativeText('休息结束了，恢复精力后继续认真完成工作吧')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.show()
            self.logger.info('休息结束')

            query = QSqlQuery()
            # 默认选择时间最近的一条记录，就是当前维护的任务数据
            query.prepare('''
                    UPDATE BasicUserData 
                    SET END_TIME_STAMP = DATETIME('now'), IS_INTERRUPTED = (:is_interrupted), IS_UNFINISHED = (:is_unfinished)
                    WHERE START_TIME_STAMP = (SELECT MAX(START_TIME_STAMP) FROM BasicUserData);
                    ''')
            query.bindValue(':is_interrupted', NO)
            query.bindValue(':is_unfinished', NO)
            if not query.exec():
                self.logger.error('更新记录失败 %s' % query.lastError().text())
                sys.exit(1)

        self.btn_start_timing.setDisabled(False)
        self.btn_stop_timing.setDisabled(True)
        self.clock_widget.close()

    def msg_remove_task_ok(self, i):
        # 更新数据库
        query = QSqlQuery()
        # 默认选择时间最近的一条记录，就是当前维护的任务数据
        query.prepare('''
                        UPDATE BasicUserData 
                        SET END_TIME_STAMP = DATETIME('now'), IS_INTERRUPTED = (:is_interrupted), IS_UNFINISHED = (:is_unfinished)
                        WHERE START_TIME_STAMP = (SELECT MAX(START_TIME_STAMP) FROM BasicUserData);
                        ''')
        if i.text() == '&No':
            query.bindValue(':is_unfinished', YES)
        else:
            query.bindValue(':is_unfinished', NO)
        query.bindValue(':is_interrupted', NO)
        if not query.exec():
            self.logger.error('更新记录失败 %s' % query.lastError().text())
            sys.exit(1)

        if i.text() == '&No':
            return
        if self.conn is None:
            self.logger.error('数据库未连接')
            sys.exit(1)

        query = QSqlQuery()
        query.prepare('DELETE FROM Todolist WHERE NAME = (:text);')
        query.bindValue(':text', self.selected_task)
        if not query.exec():
            self.logger.error('删除操作未执行')
            sys.exit(1)

        last_query = self.model_listView.query().executedQuery()
        self.model_listView.setQuery('')
        self.model_listView.setQuery(last_query)


    def _int2time(self, time):
        h = time / 60 / 60
        m = time % 3600 / 60
        s = time % 60
        return int(h), int(m), int(s)

    def timer_count_down(self):
        self.duration = self.duration - 1;
        h, m, s = self._int2time(self.duration)
        time_fmt = "%02d:%02d:%02d" % (h, m, s)
        self.lcdNumber.display(time_fmt)
        if self.mode == WORKING:
            self.clock_widget.label.setText('工作时间剩余:' + time_fmt)
        else:
            self.clock_widget.label.setText('休息时间剩余:' + time_fmt)
        if self.duration == 0:
            self.is_timing = False  # 更新标志，计时结束
            self.count_down_terminate_signal.emit()

    def btn_new_task_clicked(self):
        text, ok = QInputDialog.getText(self, '又有新工作了呢！！！', '请输入工作名称:')

        if not ok:
            return

        if text == '':
            QMessageBox.warning(self, '空输入', '工作内容不能为空')
            return

        if self.conn is None:
            self.logger.error('数据库未连接')
            sys.exit(1)

        # 检查输入内容
        query = QSqlQuery(self.conn)
        query.prepare('SELECT * FROM Todolist WHERE NAME = (:text);')
        query.bindValue(':text', text)
        if not query.exec():
            self.logger.error('SELECT执行失败')
            sys.exit(1)

        flag = query.next()
        tmp = query.value('NAME')
        if flag and tmp == text:
            QMessageBox.warning(self, '工作内容已存在', '工作内容已存在，请关闭该窗口后重新添加')
            return

        # 插入操作
        query.prepare("INSERT INTO Todolist (NAME) VALUES (:text);")
        query.bindValue(':text', text)
        if not query.exec():
            self.logger.error('INSERT执行失败')
            sys.exit(1)

        # 刷新视图
        last_query = self.model_listView.query().executedQuery()
        self.model_listView.setQuery("")
        self.model_listView.setQuery(last_query)

    def btn_rm_task_clicked(self):
        if self.conn is None:
            self.logger.error('数据库未连接')

        if self.listView.currentIndex().row() < 0:
            QMessageBox.warning(self, "未选择要删除项", "请选择要删除的工作")
            return
        else:
            index = self.listView.currentIndex()
            text = index.data()

            query = QSqlQuery(self.conn)
            query.prepare("DELETE FROM Todolist WHERE NAME = (:text);")
            query.bindValue(':text', text)
            if not query.exec():
                self.logger.error('Todolist删除失败')
                sys.exit(1)

        # 刷新视图
        last_query = self.model_listView.query().executedQuery()
        self.model_listView.setQuery('')
        self.model_listView.setQuery(last_query)


    def btn_mode_clicked(self):
        if self.mode == WORKING:
            self.mode = RELAXING
        else:
            self.mode = WORKING
        self._switch_widget_with_mode()

    def switch_between_show_n_hide(self):
        #  用于主界面和计时小窗口显示状态切换
        if self.isVisible() is True:
            self.hide()
            if self.is_timing is False:
                return
            self.clock_widget.show()
        else:
            self.activateWindow()
            # setWindowState()：根据Flags值设置窗口的状态,多个 WindowFlags之间用 | 连接
            # windowState()正常状态， WindowMinimized最小化， WindowActive活动状态
            # 窗口取消最小化并设置为活动状态
            self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.showNormal()
            if self.is_timing is False:
                return
            self.clock_widget.hide()

    def _init_listView_log(self):
        self._init_log_list()  # 初始化日志列表
        self._check_n_remove_log()  # 检查日志数量并且删除时间过早的日志
        self.listWidget_log.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget_log.customContextMenuRequested.connect(self._customize_context_menu) # 设置右键菜单栏，加载日志名称，绑定菜单栏触发事件
        self._load_log_widget()  # 加载日志控件
        self.tabWidget.setCurrentIndex(0)  # 依旧设置代办列表为默认

    def _init_log_list(self):
        global SOFTWARE_PATH
        list_directory = os.listdir(SOFTWARE_PATH)
        self.log_list = []
        for directory in list_directory:
            de_path = SOFTWARE_PATH + '//' + directory
            if os.path.isfile(de_path):
                if de_path.endswith('.log'):
                    self.log_list.append(de_path)
        self.log_list.sort(key=None, reverse=True)
        self.logger.debug('加载日志列表')

    def _check_n_remove_log(self):
        # 删除过早的日志文件
        if len(self.log_list) > 20:
            for i in self.log_list[20:len(self.log_list)]:
                self.log_list.remove(i)
                os.remove(i)

    def _customize_context_menu(self, position):
        # 设置右键菜单栏，加载日志名称，绑定菜单栏触发事件
        pop_menu = QMenu()
        for log_path in self.log_list:
            action = QAction(os.path.basename(log_path), self)
            action.triggered.connect(partial(self._refresh_list_view_log, log_path))
            pop_menu.addAction(action)
        pop_menu.exec(self.listWidget_log.mapToGlobal(position))

    def _refresh_list_view_log(self, log_path):
        self.listWidget_log.clear()
        path = log_path
        with open(path) as f:
            data_list = f.readlines()
            if data_list:
                for line in data_list:
                    str_list = line.split(' ')
                    w = LogWidget(str_list[0]+' '+str_list[1], str_list[3], str_list[2])
                    item = QListWidgetItem()
                    item.setSizeHint(QSize(200, 80))
                    self.listWidget_log.addItem(item)
                    self.listWidget_log.setItemWidget(item, w)

    def _load_log_widget(self):
        # 加载日志控件, 默认加载列表第一位日志
        with open(self.log_list[0]) as f:
            data_list = f.readlines()
            if data_list:
                for line in data_list:
                    str_list = line.split(' ')
                    w = LogWidget(str_list[0] +' '+ str_list[1], str_list[3], str_list[2])
                    item = QListWidgetItem()
                    item.setSizeHint(QSize(200, 80))
                    self.listWidget_log.addItem(item)
                    self.listWidget_log.setItemWidget(item, w)

    def quit(self):
        if self.is_timing:  # 检测到还在计时，弹窗确认退出
            msg = QMessageBox(self)
            msg.setWindowTitle('TimeArranger')
            if self.mode == WORKING:
                msg.setText('还在计时中')
                msg.setInformativeText('规定的工作时长还未达到，确定放弃自律了吗？')
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            else:
                msg.setText('还在计时中')
                msg.setInformativeText('再休息一下吧，恢复精力也是工作的一部分')
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            ret = msg.exec()
            if ret == QMessageBox.Ok:
                self.clock_widget.save_settings()
                self._save_settings()
                if self.mode == WORKING:
                    self.logger.info('在工作时中途放弃,要养成自律的好习惯!!!')
                else:
                    self.logger.info('工作很重要,但也要注意眼睛和身体!!!')

                # 录入数据库
                query = QSqlQuery()
                query.prepare('''
                            UPDATE BasicUserData 
                            SET END_TIME_STAMP = DATETIME('now'), IS_INTERRUPTED = :IS_INTERRUPTED,
                            DURATION = DURATION - (:TIME_LEFT)
                            WHERE START_TIME_STAMP = (SELECT MAX(START_TIME_STAMP) FROM BasicUserData);
                        ''')
                query.bindValue(':IS_INTERRUPTED', YES)
                query.bindValue(':TIME_LEFT', self.duration)
                if not query.exec():
                    self.logger.error('更新记录失败')
                    sys.exit(1)
                sys.exit(0)
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle('TimeArranger')
            msg.setText('离开TimeArranger')
            msg.setInformativeText('确认离开TimeArranger吗？')
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            ret = msg.exec()
            if ret == QMessageBox.Ok:
                self.clock_widget.save_settings()
                self._save_settings()
                self.logger.info('TimeArranger正常退出')
                sys.exit(0)

    def closeEvent(self, event):
        event.ignore()
        if self.is_timing is True:
            self.clock_widget.show()
        self.hide()
