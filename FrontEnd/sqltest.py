# import random
# import sys
#
# from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel
# from PyQt5.QtWidgets import QInputDialog, QWidget
# from PyQt5.Qt import QApplication
# from global_var import *
#
# # class Window(QWidget):
# #     def __init__(self):
# #         super().__init__()
# #         self.show()
# #         self.show_dialog()
# #
# #     def show_dialog(self):
# #         text, ok = QInputDialog.getText(self, 'hello', 'hello')
# #         print(text)
# #         print(ok)
# #
# #
# # app = QApplication(sys.argv)
# # widget = Window()
# # sys.exit(app.exec())
#
# conn = QSqlDatabase.addDatabase('QSQLITE')
# db_path = os.environ['AppData'] + '\\TimeArranger//time_arranger.sqlite'
# # db_path = '..\\TimeArranger//time_arranger.sqlite'
# print(db_path)
# conn.setDatabaseName(db_path)
# if not conn.open():
#     print('ERROR')
#
# query = QSqlQuery(conn)
#
# # query.prepare('DROP TABLE BasicUserData')
# # query.exec()
#
# # query.prepare("SELECT * FROM sqlite_schema WHERE type='table' ORDER BY name;")
# # if not query.exec():
# #     print('EXEC_ERROR2')
# # while(query.next()):
# #     print(query.value(4))
#
# # query.prepare("INSERT INTO Todolist VALUES (:text);")
# # query.bindValue(":text", "ues")
# # if not query.exec():
# #     print("1")
#
# # text = 'hhhh'
# # query.prepare('SELECT * FROM Todolist WHERE NAME = (:text);')
# # query.bindValue(":text", text)
# # if not query.exec():
# #     print("2")
# # while(query.next()):
# #     print(query.value('NAME'))
#
# # query.prepare("DELETE FROM BasicUserData WHERE IS_INTERRUPTED = (:is_interrupted)")
# # # query.bindValue(':is_interrupted', UNKNOWN)
# # # if not query.exec():
# # #     print('no')
# # #
# # # query.prepare('DELETE FROM BasicUserData WHERE DATE(START_TIME_STAMP, "localtime") = :begin')
# # # query.bindValue(':begin', '2023-04-13')
# # # if not query.exec():
# # #     sys.exit(1)
#
# # query.prepare('''
# #                 SELECT * FROM WebBlockList WHERE RELAXING_OR_WORKING = {r_or_w};
# #                 '''.format(r_or_w='\'RELAXING\''))
# # print('''
# #                 SELECT * FROM WebBlockList WHERE RELAXING_OR_WORKING = {r_or_w};
# #                 '''.format(r_or_w='\'RELAXING\''))
#
# from PyQt5.QtCore import (QTimer, QSettings, QPoint, QVariant, pyqtSignal, Qt, QSize)
# from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QMessageBox, QSystemTrayIcon, QMenu, QAction, QInputDialog, \
#     QWidget, QListWidgetItem
#
# import sys, os, re
#
# DRIVER_DATA_PATH = os.environ['DriverData']
# NEW_PATH = '/etc/hosts_new'
#
#
# # def run():
# #     try:
# #         if sys.argv[1] == 'add':
# #             with open(PATH, 'a+', encoding='utf-8') as f:
# #                 new_IP = sys.argv[2] + ' ' + sys.argv[3]
# #                 f.write('\n')
# #                 f.write(new_IP)
# #                 sys.exit('添加成功，请查看源文件')
# #         elif sys.argv[1] == 'del':
# #             with open(PATH, 'r+', encoding='utf-8') as f, open(NEW_PATH, 'a+', encoding='utf-8') as f2:
# #                 data = f.readlines()
# #                 for line in data:
# #                     if sys.argv[2] in line:
# #                         continue
# #                     f2.write(line)
# #             os.remove(PATH)
# #             os.rename(NEW_PATH, PATH)
# #             sys.exit('删除成功，请查看源文件')
# #         elif sys.argv[1] == 'change':
# #             open(NEW_PATH, 'a+').write(re.sub(r'%s' % sys.argv[2], '%s' % sys.argv[3], open(PATH).read()))
# #             os.remove(PATH)
# #             os.rename(NEW_PATH, PATH)
# #             sys.exit('修改成功，请查看源文件')
# #     except Exception as e:
# #         print(e)
#
#
# import ctypes
#
#
# def run():
#     with open(HOSTS_PATH, 'r', encoding='utf-8') as f_r:
#         data = f_r.readlines()
#         start_pattern = '# TimeArranger dev via Python 3.8.3\n'
#         end_pattern = '# end of TimeArranger dev via Python 3.8.3\n'
#         start_index = -1
#         end_index = -1
#         for i, line in enumerate(data):
#             print(data[i])
#             if data[i] == start_pattern:
#                 start_index = i
#
#             if data[i] == end_pattern:
#                 end_index = i
#                 break
#
#         query = QSqlQuery(conn)
#         query.prepare('''SELECT * FROM WebBlockList WHERE RELAXING_OR_WORKING = :r_or_w''')
#         query.bindValue(':r_or_w', 'WORKING')
#         with open(HOSTS_PATH, 'w', encoding='utf-8') as f_w:
#             redirect_ip = '0.0.0.0'
#             if start_index < 0:
#                 start_index = len(data)
#                 if not query.exec():
#                     sys.exit(1)
#
#                 data.insert(start_index, start_pattern)
#                 while query.next():
#                     start_index += 1
#                     item = redirect_ip + ' ' + query.value('WEB_DOMAIN') + '\n'
#                     data.insert(start_index, item)
#                     print(item)
#                 data.insert(start_index+1, end_pattern)
#             else:
#                 del data[start_index + 1:end_index]
#                 if not query.exec():
#                     sys.exit(1)
#                 while query.next():
#                     start_index += 1
#                     item = redirect_ip + ' ' + query.value('WEB_DOMAIN') + '\n'
#                     data.insert(start_index, item)
#                     print(item)
#
#             f_w.writelines(data)
#
#
# if __name__ == '__main__':
#     print(run())
#
#
# # if not query.exec():
# #     print(query.lastError().text())
# #     sys.exit(1)
# #
# # while(query.next()):
# #     string = ''
# #     for i in range(3):
# #         string += str(query.value(i)) + ' ||| '
# #     print(string)
#
#
# # WORK_LIST = ['jwifjef', 'dsfjdf', 'sfdfs', 'NONE']
# # YEAR = [2023, 2022]
# # query.prepare('''INSERT INTO BasicUserData
# #                 (TASK, START_TIME_STAMP, DURATION, IS_INTERRUPTED, IS_UNFINISHED)
# #                 VALUES (:task, :start_time, :duration, :is_interrupted, :is_unfinished);
# #                 ''')
# #
# # for i in range(1000):
# #     date_str = '%04d-%02d-%02d %02d:%02d:%02d' % (
# #         YEAR[random.randint(0, 1)], random.randint(1, 12), random.randint(1, 28),
# #         random.randint(0, 23), random.randint(0, 59), random.randint(0, 59)
# #                                                )
# #     task = WORK_LIST[random.randint(0, 3)]
# #     duration = random.randint(600, 3000)
# #     is_interrupted = NO
# #     is_unfinished = NO
# #     query.bindValue(':task', task)
# #     query.bindValue(':start_time', date_str)
# #     query.bindValue(':duration', duration)
# #     query.bindValue(':is_interrupted', is_interrupted)
# #     query.bindValue(':is_unfinished', is_unfinished)
# #
# #     if not query.exec():
# #         sys.exit(1)
# #
# #     print(date_str)
#
# # query.prepare('DELETE FROM BasicUserData WHERE START_TIME_STAMP > :hello')
# # query.bindValue(':hello', '2023-04-17 00:00:00')
# # if not query.exec():
# #     print('hello')
# #     sys.exit(1)
#
#
# conn.close()
import sys

from PyQt5.QtCore import QSharedMemory, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow


class MyApp(QMainWindow):
    # 定义自定义信号
    showMainWindowSignal = pyqtSignal()

    def __init__(self):
        super().__init__()

        # 连接自定义信号和槽函数
        self.showMainWindowSignal.connect(self.showMainWindow)

        # 创建共享内存区域
        self.sharedMemory = QSharedMemory("MyApp")

        # 将一个整数值写入共享内存区域
        self.sharedMemory.lock()
        if not self.sharedMemory.isAttached():
            self.sharedMemory.create(1)
            self.sharedMemory.data()[0] = 1
        else:
            self.sharedMemory.data()[0] = 2
        self.sharedMemory.unlock()

    def showMainWindow(self):
        # 在这里编写弹出主窗口的代码
        self.showNormal()


if __name__ == "__main__":
    # 尝试将共享内存区域锁定
    sharedMemory = QSharedMemory("MyApp")
    if not sharedMemory.lock():
        # 如果共享内存区域已经被锁定，则说明程序已经在运行
        # 触发自定义信号并退出程序
        sharedMemory.unlock()
        app = QApplication([])
        window = MyApp()
        window.showMainWindowSignal.emit()
        sys.exit(app.exec_())
    else:
        # 如果共享内存区域没有被锁定，则说明程序没有运行
        # 将共享内存区域中的整数值设为1，并启动程序
        sharedMemory.create(1)
        sharedMemory.lock()
        sharedMemory.data()[0] = 1
        sharedMemory.unlock()
        app = QApplication([])
        window = MyApp()
        window.show()
        sys.exit(app.exec_())

    # 释放共享内存区域
    sharedMemory.detach()
