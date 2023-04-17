import sys

from PyQt5.QtCore import QSize, QDate, Qt
from PyQt5.QtGui import QPainter, QIcon

from UI.UI_StatisticsWidget import Ui_StatisticsWidget
from PyQt5.QtWidgets import QWidget, QSizePolicy, QMessageBox
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtChart import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis
from FrontEnd.global_var import *
from Log.my_logger import LoggerHandler
from resources import *

class StatisticsWidget(Ui_StatisticsWidget, QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._init_ui()
        self._init_DB()
        self._data_plot()

    date_begin = None
    date_end = None

    def _init_ui(self):
        self.setWindowIcon(QIcon(':/icon/icon.png'))
        self.dateEdit_begin.setDisplayFormat('yyyy-MM-dd')
        self.dateEdit_end.setDisplayFormat('yyyy-MM-dd')

        self.dateEdit_end.setDate(QDate.currentDate())
        self.dateEdit_end.setMaximumDate(QDate.currentDate())
        date_week_ago = QDate.currentDate().addDays(-6)
        self.dateEdit_begin.setDate(date_week_ago)
        self.dateEdit_end.setCalendarPopup(True)
        self.dateEdit_begin.setCalendarPopup(True)
        self.date_begin = self.dateEdit_begin.date()
        self.date_end = self.dateEdit_end.date()

        self.chart_view = QChartView()
        self.chart_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.GraphicLayout.addWidget(self.chart_view)

        self.comboBox_view_mode.currentIndexChanged.connect(self._data_plot)
        self.dateEdit_begin.dateChanged.connect(self.date_changed)
        self.dateEdit_end.dateChanged.connect(self.date_changed)

    def date_changed(self):
        # 为了防止程序出发信号，打开两次弹窗
        self.dateEdit_begin.dateChanged.disconnect(self.date_changed)

        date_format = self.dateEdit_begin.displayFormat()
        compare_result = self.dateEdit_begin.date().toString(date_format) > self.dateEdit_end.date().toString(date_format)

        if compare_result:
            QMessageBox.warning(self, '统计的开始时间必须大于或等于结束时间', '请重新设置时间值')
            self.dateEdit_begin.setDate(self.date_begin)
            self.dateEdit_end.setDate(self.date_end)
            self.dateEdit_begin.dateChanged.connect(self.date_changed)
            return

        self.date_begin = self.dateEdit_begin.date()
        self.date_end = self.dateEdit_end.date()
        self.dateEdit_begin.dateChanged.connect(self.date_changed)

        self._data_plot()

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

    def _init_DB(self):
        db_path = SOFTWARE_PATH + '//' + DB_NAME
        self.conn = QSqlDatabase.database(db_path)
        if self.conn is None:
            self.logger.error('数据库连接丢失')
            sys.exit(1)

    def _data_plot(self):
        # todo 数据展示功能实现

        if self.conn is None:
            self.logger.error('数据库连接丢失')
            sys.exit(1)

        query = QSqlQuery()

        date_format = self.dateEdit_begin.displayFormat()
        date_begin = self.dateEdit_begin.date().toString(date_format)
        date_end = self.dateEdit_end.date().toString(date_format)

        if self.comboBox_view_mode.currentText() == '日视图':
            # 获取时间段内的数据
            query.prepare('''
            SELECT 
            CASE TASK WHEN 'NONE' THEN 'RELAXING' ELSE 'WORKING' END AS IS_RELAXING,
            DATE(START_TIME_STAMP, 'localtime') AS START_DATE,
            SUM(DURATION) AS TOTAL_DURATION
            FROM BasicUserData
            WHERE START_DATE BETWEEN :begin AND :end 
            GROUP BY START_DATE, IS_RELAXING;
            ''')

            query.bindValue(':begin', date_begin)
            query.bindValue(':end', date_end)
            if not query.exec():
                self.logger.error('抓取数据出错')
                sys.exit(1)

            # 创建图表对象，绘制使用情况柱状图
            bar_set_relaxing = QBarSet('RELAXING')
            bar_set_working = QBarSet('WORKING')

            while query.next():
                state = query.value('IS_RELAXING')
                if state == 'RELAXING':
                    value = query.value('TOTAL_DURATION')/3600
                    bar_set_relaxing.append(value)
                else:
                    value = query.value('TOTAL_DURATION')/3600
                    bar_set_working.append(value)


            series = QBarSeries()
            series.append(bar_set_working)
            series.append(bar_set_relaxing)

            chart = QChart()
            chart.addSeries(series)
            chart.setTitle('使用情况总览')
            chart.setAnimationOptions(QChart.SeriesAnimations)

            axisX = QBarCategoryAxis()
            catogories = []
            query.first()
            while query.next():
                start_date = query.value('START_DATE')
                if start_date not in catogories:
                    catogories.append(start_date)
            axisX.append(catogories)
            axisX.setTitleText('Date')
            chart.addAxis(axisX, Qt.AlignBottom)
            series.attachAxis(axisX)

            axisY = QValueAxis()
            axisY.setTitleText('TimeCost(hour)')
            chart.addAxis(axisY, Qt.AlignLeft)
            series.attachAxis(axisY)
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignBottom)

            self.chart_view.setChart(chart)
            self.chart_view.setRenderHint(QPainter.Antialiasing)

        if self.comboBox_view_mode.currentText() == '周视图':
            # 获取时间段内的数据
            query.prepare('''
                        SELECT 
                        CASE TASK WHEN 'NONE' THEN 'RELAXING' ELSE 'WORKING' END AS IS_RELAXING,
                        DATE(START_TIME_STAMP, 'localtime') AS START_DATE,
                        SUM(DURATION) AS TOTAL_DURATION
                        FROM BasicUserData
                        WHERE START_DATE BETWEEN :begin AND :end 
                        GROUP BY START_DATE, IS_RELAXING;
                        ''')

            # 创建图表对象，绘制使用情况柱状图
            bar_set_relaxing = QBarSet('RELAXING')
            bar_set_working = QBarSet('WORKING')

            value_week_relaxing = 0
            value_week_working = 0

            week_start_date = QDate.fromString(date_begin, 'yyyy-MM-dd')
            week_end_date = week_start_date.addDays(7)  # 临时记录7天的结束
            date_format = self.dateEdit_begin.displayFormat()

            while week_start_date.toString(date_format) <= date_end:
                query.bindValue(':begin', week_start_date.toString(date_format))
                query.bindValue(':end', week_end_date.toString(date_format))
                if not query.exec():
                    self.logger.error('抓取数据失败')
                    sys.exit(1)

                while query.next():
                    if query.value('IS_RELAXING') == 'RELAXING':
                        value_week_relaxing += query.value('TOTAL_DURATION')/3600
                    else:
                        value_week_working += query.value('TOTAL_DURATION')/3600

                bar_set_working.append(value_week_working)
                bar_set_relaxing.append(value_week_relaxing)
                value_week_working = 0
                value_week_relaxing = 0
                week_start_date = week_start_date.addDays(7)
                week_end_date = week_end_date.addDays(7)

            series = QBarSeries()
            series.append(bar_set_working)
            series.append(bar_set_relaxing)

            chart = QChart()
            chart.addSeries(series)
            chart.setTitle('使用情况总览')
            chart.setAnimationOptions(QChart.SeriesAnimations)
            axisX = QBarCategoryAxis()
            catogories = []
            query.first()

            week_start_date = QDate.fromString(date_begin, 'yyyy-MM-dd')
            week_end_date = week_start_date.addDays(7)  # 临时记录7天的结束
            while week_start_date.toString(date_format) <= date_end:
                week_str = week_start_date.toString(date_format) + '--->' + week_end_date.toString(date_format)
                if week_start_date.toString(date_format) == week_end_date.toString(date_format):
                    week_str = week_start_date.toString()
                catogories.append(week_str)
                week_start_date = week_start_date.addDays(7)
                week_end_date = week_end_date.addDays(7)


            axisX.append(catogories)
            axisX.setTitleText('Period by Seven Days')
            chart.addAxis(axisX, Qt.AlignBottom)
            series.attachAxis(axisX)

            axisY = QValueAxis()
            chart.addAxis(axisY, Qt.AlignLeft)
            axisY.setTitleText('TimeCost(hour)')
            series.attachAxis(axisY)
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignBottom)

            self.chart_view.setChart(chart)
            self.chart_view.setRenderHint(QPainter.Antialiasing)

        if self.comboBox_view_mode.currentText() == '月视图':
            # 获取时间段内的数据
            query.prepare('''
                            SELECT 
                            CASE TASK WHEN 'NONE' THEN 'RELAXING' ELSE 'WORKING' END AS IS_RELAXING,
                            strftime('%Y', START_TIME_STAMP) AS START_YEAR,
                            strftime('%m', START_TIME_STAMP) AS START_MONTH,
                            SUM(DURATION) AS TOTAL_DURATION
                            FROM BasicUserData 
                            WHERE START_YEAR = :YEAR
                            GROUP BY START_MONTH, IS_RELAXING
                            ''')

            # 创建图表对象，绘制使用情况柱状图
            bar_set_relaxing = QBarSet('RELAXING')
            bar_set_working = QBarSet('WORKING')

            query.bindValue(':YEAR', str(self.dateEdit_begin.date().year()))
            if not query.exec():
                self.logger.error('数据抓取失败')
                sys.exit(1)

            while query.next():
                if query.value('IS_RELAXING') == 'RELAXING':
                    bar_set_relaxing.append(query.value('TOTAL_DURATION')/3600)
                else:
                    bar_set_working.append(query.value('TOTAL_DURATION')/3600)

            series = QBarSeries()
            series.append(bar_set_working)
            series.append(bar_set_relaxing)

            chart = QChart()
            chart.addSeries(series)
            chart.setTitle('使用情况总览')
            chart.setAnimationOptions(QChart.SeriesAnimations)
            axisX = QBarCategoryAxis()
            catogories = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

            axisX.append(catogories)
            axisX.setTitleText('Month')
            chart.addAxis(axisX, Qt.AlignBottom)
            series.attachAxis(axisX)

            axisY = QValueAxis()
            axisY.setTitleText('TimeCost(hour)')
            chart.addAxis(axisY, Qt.AlignLeft)
            series.attachAxis(axisY)
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignBottom)

            self.chart_view.setChart(chart)
            self.chart_view.setRenderHint(QPainter.Antialiasing)


