import sys
import os

from PyQt5.QtWidgets import QApplication
from FrontEnd.InitTAWidget import InitTAWidget
from FrontEnd.global_var import *


if __name__ == '__main__':
    # 系统初始化代码
    if not os.path.exists(SOFTWARE_PATH):
        try:
            os.makedirs(SOFTWARE_PATH)
        except Exception:
            # todo 写一个消息框提醒创建文件夹出错
            sys.exit(1)

    app = QApplication(sys.argv)
    win = InitTAWidget()
    sys.exit(app.exec())