import os
import sys

# 常量
WORKING = 1
RELAXING = 0

# 数据库状态常量
# IS_INTERRUPTED, IS_UNFINISHED
UNKNOWN = 'UNKNOWN'
YES = 'YES'
NO = 'NO'

DRIVER_DATA_PATH = os.environ['DriverData']
HOSTS_PATH = os.path.abspath(os.path.join(DRIVER_DATA_PATH, '..')) + '\\etc/hosts'

SOFTWARE_PATH = os.environ['AppData'] + '\\TimeArranger'
DB_NAME = 'time_arranger.sqlite'



