import random
import sys

from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel
from PyQt5.QtWidgets import QInputDialog, QWidget
from PyQt5.Qt import QApplication
from global_var import *

# class Window(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.show()
#         self.show_dialog()
#
#     def show_dialog(self):
#         text, ok = QInputDialog.getText(self, 'hello', 'hello')
#         print(text)
#         print(ok)
#
#
# app = QApplication(sys.argv)
# widget = Window()
# sys.exit(app.exec())

conn = QSqlDatabase.addDatabase('QSQLITE')
db_path = '..\\TimeArranger//time_arranger.sqlite'
print(db_path)
conn.setDatabaseName(db_path)
if not conn.open():
    print('ERROR')

query = QSqlQuery(conn)

# query.prepare('DROP TABLE BasicUserData')
# query.exec()

# query.prepare("SELECT * FROM sqlite_schema WHERE type='table' ORDER BY name;")
# if not query.exec():
#     print('EXEC_ERROR2')
# while(query.next()):
#     print(query.value(4))

# query.prepare("INSERT INTO Todolist VALUES (:text);")
# query.bindValue(":text", "ues")
# if not query.exec():
#     print("1")

# text = 'hhhh'
# query.prepare('SELECT * FROM Todolist WHERE NAME = (:text);')
# query.bindValue(":text", text)
# if not query.exec():
#     print("2")
# while(query.next()):
#     print(query.value('NAME'))

# query.prepare("DELETE FROM BasicUserData WHERE IS_INTERRUPTED = (:is_interrupted)")
# # query.bindValue(':is_interrupted', UNKNOWN)
# # if not query.exec():
# #     print('no')
# #
# # query.prepare('DELETE FROM BasicUserData WHERE DATE(START_TIME_STAMP, "localtime") = :begin')
# # query.bindValue(':begin', '2023-04-13')
# # if not query.exec():
# #     sys.exit(1)

query.prepare('''
                SELECT 
                CASE TASK WHEN 'NONE' THEN 'RELAXING' ELSE 'WORKING' END AS IS_RELAXING,
                strftime('%Y', START_TIME_STAMP) AS START_YEAR,
                strftime('%m', START_TIME_STAMP) AS START_MONTH,
                SUM(DURATION) AS TOTAL_DURATION
                FROM BasicUserData 
                GROUP BY START_MONTH, IS_RELAXING
                ''')

query.bindValue(':YEAR', '2022')
if not query.exec():
    sys.exit(1)

while(query.next()):
    string = ''
    for i in range(3):
        string += str(query.value(i)) + ' ||| '
    print(string)


# WORK_LIST = ['jwifjef', 'dsfjdf', 'sfdfs', 'NONE']
# YEAR = [2023, 2022]
# query.prepare('''INSERT INTO BasicUserData
#                 (TASK, START_TIME_STAMP, DURATION, IS_INTERRUPTED, IS_UNFINISHED)
#                 VALUES (:task, :start_time, :duration, :is_interrupted, :is_unfinished);
#                 ''')
#
# for i in range(1000):
#     date_str = '%04d-%02d-%02d %02d:%02d:%02d' % (
#         YEAR[random.randint(0, 1)], random.randint(1, 12), random.randint(1, 28),
#         random.randint(0, 23), random.randint(0, 59), random.randint(0, 59)
#                                                )
#     task = WORK_LIST[random.randint(0, 3)]
#     duration = random.randint(600, 3000)
#     is_interrupted = NO
#     is_unfinished = NO
#     query.bindValue(':task', task)
#     query.bindValue(':start_time', date_str)
#     query.bindValue(':duration', duration)
#     query.bindValue(':is_interrupted', is_interrupted)
#     query.bindValue(':is_unfinished', is_unfinished)
#
#     if not query.exec():
#         sys.exit(1)
#
#     print(date_str)

# query.prepare('DELETE FROM BasicUserData WHERE START_TIME_STAMP > :hello')
# query.bindValue(':hello', '2023-04-17 00:00:00')
# if not query.exec():
#     print('hello')
#     sys.exit(1)


conn.close()
