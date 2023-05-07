import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel

from Log.my_logger import LoggerHandler
from UI.UI_WebBlockDialog import Ui_WebBlockDialog
from PyQt5.QtWidgets import QDialog, QInputDialog, QMenu, QAction, QMessageBox, QDialogButtonBox
from FrontEnd.global_var import *


class WebBlockDialog(Ui_WebBlockDialog, QDialog):
    is_timing = False

    def __init__(self, is_timing):
        super().__init__()
        self.is_timing = is_timing
        self.setupUi(self)
        self._logger_init()
        self._init_DB()
        self._init_ui()

    def _logger_init(self):
        # 初始化日志器参数
        self.logger = LoggerHandler(
            name=__name__
        )
        self.logger.debug('Logger初始化')

    def _init_ui(self):
        self.setWindowTitle('网络屏蔽')
        self.setWindowIcon(QIcon(':/icon/icon.png'))
        if self.is_timing:
            self.listView.setDisabled(True)
        else:
            self.listView.setEnabled(True)
        self.listView.setContextMenuPolicy(Qt.CustomContextMenu)  # 要先设置为自定义弹出菜单，否则无响应
        self.listView.customContextMenuRequested.connect(self._customize_context_menu)
        self.model = QSqlQueryModel()
        self.model.setQuery('SELECT WEB_DOMAIN FROM WebBlockList', self.conn)
        self.listView.setModel(self.model)

        self.pop_menu = QMenu()
        self.action_add_domain = QAction('添加域名', self)
        self.action_del_domain = QAction('删除域名', self)
        self.action_working_only = QAction('只显示工作时域名', self.pop_menu, checkable=True)
        self.action_relaxing_only = QAction('只显示休息时域名', self.pop_menu, checkable=True)
        self.action_add_domain.triggered.connect(self.action_add_domain_triggered)
        self.action_del_domain.triggered.connect(self.action_del_domain_triggered)
        self.action_working_only.triggered.connect(self.action_working_only_triggered)
        self.action_relaxing_only.triggered.connect(self.action_relaxing_only_triggered)
        self.pop_menu.addAction(self.action_add_domain)
        self.pop_menu.addAction(self.action_del_domain)
        self.pop_menu.addSeparator()
        self.pop_menu.addAction(self.action_working_only)
        self.pop_menu.addAction(self.action_relaxing_only)

    def _init_DB(self):
        db_path = SOFTWARE_PATH + '//' + DB_NAME
        self.conn = QSqlDatabase.database(db_path)
        if self.conn is None:
            self.logger.error('数据库连接丢失')
            sys.exit(1)

    def _customize_context_menu(self, position):
        self.pop_menu.exec(self.listView.mapToGlobal(position))

    def action_working_only_triggered(self):
        if not self.action_relaxing_only.isChecked() and not self.action_working_only.isChecked():
            self.model.setQuery('SELECT WEB_DOMAIN FROM WebBlockList', self.conn)
            return

        if self.action_relaxing_only.isChecked():
            self.action_relaxing_only.setChecked(False)
            self.action_working_only.setChecked(True)

        if self.conn is None:
            self.logger.error('数据库连接丢失')
            sys.exit(1)

        query = "SELECT WEB_DOMAIN FROM WebBlockList WHERE RELAXING_OR_WORKING == {r_or_w}".format(r_or_w='\'WORKING\'')

        self.model.setQuery(query, self.conn)

    def action_relaxing_only_triggered(self):
        if not self.action_relaxing_only.isChecked() and not self.action_working_only.isChecked():
            self.model.setQuery('SELECT WEB_DOMAIN FROM WebBlockList', self.conn)
            return

        if self.action_working_only.isChecked():
            self.action_working_only.setChecked(False)
            self.action_relaxing_only.setChecked(True)

        if self.conn is None:
            self.logger.error('数据库连接丢失')
            sys.exit(1)

        query = "SELECT WEB_DOMAIN FROM WebBlockList WHERE RELAXING_OR_WORKING == {r_or_w}".format(r_or_w='\'RELAXING\'')

        self.model.setQuery(query, self.conn)

    def action_add_domain_triggered(self):
        text, ok = QInputDialog.getText(self, '添加域名', '请输入要屏蔽的域名:')

        if text == '':
            QMessageBox.warning(self, '空输入', '域名不能为空')
            return

        if ok:
            if self.conn == None:
                self.logger.error('数据库连接丢失')
                sys.exit(1)

            # 检查输入内容
            query = QSqlQuery(self.conn)
            query.prepare('SELECT WEB_DOMAIN FROM WebBlockList WHERE WEB_DOMAIN = (:text);')
            query.bindValue(':text', text)
            if not query.exec():
                self.logger.error('SELECT执行失败')
                sys.exit(1)

            flag = query.next()
            tmp = query.value('WEB_DOMAIN')
            if flag and tmp == text:
                QMessageBox.warning(self, '警告', '域名已存在')
                return

            is_working = QMessageBox.question(self, '询问', '域名是要在工作时段屏蔽吗')

            query = QSqlQuery(self.conn)
            query.prepare('''
                INSERT INTO WebBlockList (WEB_DOMAIN, RELAXING_OR_WORKING) VALUES (:web_domain, :relaxing_or_working);
            ''')
            query.bindValue(':web_domain', text)
            if is_working == QDialogButtonBox.Yes:
                query.bindValue(':relaxing_or_working', 'WORKING')
            else:
                query.bindValue(':relaxing_or_working', 'RELAXING')

            if not query.exec():
                self.logger.error('WebBlockList未插入')
                sys.exit(1)

            last_query = self.model.query().executedQuery()
            self.model.setQuery('')
            self.model.setQuery(last_query)

            self.list_view_refresh()

    def action_del_domain_triggered(self):
        if self.conn is None:
            self.logger.error('数据库连接丢失')
            sys.exit(1)

        query = QSqlQuery(self.conn)
        query.prepare('''
        DELETE FROM WebBlockList WHERE WEB_DOMAIN = :web_domain;
        ''')
        query.bindValue(':web_domain', self.listView.currentIndex().data())
        if not query.exec():
            self.logger.error('删除未执行')
            sys.exit(1)

        self.list_view_refresh()

    def list_view_refresh(self):
        if self.action_working_only.isChecked():
            query = "SELECT WEB_DOMAIN FROM WebBlockList WHERE RELAXING_OR_WORKING == {r_or_w}".format(
                r_or_w='\'WORKING\'')
            self.model.setQuery(query, self.conn)
        elif self.action_relaxing_only.isChecked():
            query = "SELECT WEB_DOMAIN FROM WebBlockList WHERE RELAXING_OR_WORKING == {r_or_w}".format(
                r_or_w='\'RELAXING\'')
            self.model.setQuery(query, self.conn)
        else:
            self.model.setQuery('SELECT WEB_DOMAIN FROM WebBlockList;', self.conn)

