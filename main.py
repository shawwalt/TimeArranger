import ctypes
from PyQt5.QtWidgets import QApplication, QMessageBox
from FrontEnd.InitTAWidget import InitTAWidget
from FrontEnd.global_var import *

if __name__ == '__main__':
    # 系统初始化代码
    # 获取管理员权限便于修改Hosts文件
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit(0)

    if not os.path.exists(SOFTWARE_PATH):
        try:
            os.makedirs(SOFTWARE_PATH)
        except Exception:
            sys.exit(1)

    app = QApplication(sys.argv)
    win = InitTAWidget()
    sys.exit(app.exec())