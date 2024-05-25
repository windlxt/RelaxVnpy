"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年05月21日
"""
from time import sleep
from threading import Thread
from multiprocessing import Process
from PySide6.QtWidgets import QWidget, QApplication, QCheckBox, QVBoxLayout, QSpacerItem, QSizePolicy, QPushButton, QHBoxLayout, QLabel
from PySide6.QtCore import QSize, QRect
from vnpy.trader.ui.database_widget import download_data_scheduler


class DatabaseWindow(QWidget):
    def __init__(self, main_engine=None, event_engine=None):
        super().__init__()
        self.main_engine = main_engine
        self.event_engine = event_engine

        self.init_ui()
        self.init_data_management()

    def init_ui(self):
        self.cbox_download_date_schuduler = QCheckBox('按计划更新数据')
        self.cbox_download_date_schuduler.setGeometry(0, 0, 100, 50)
        self.cbox_download_date_schuduler.stateChanged.connect(self.init_data_management)

        self.pbtn_update_data = QPushButton('立即更新数据')
        self.pbtn_update_data.setGeometry(0, 0, 100, 50)

        self.hlayout = QHBoxLayout()
        self.hlayout.addWidget(self.cbox_download_date_schuduler)
        self.hlayout.addWidget(self.pbtn_update_data)



        self.vlayout_left = QVBoxLayout()
        self.vlayout_left.addLayout(self.hlayout)
        self.vlayout_left.addStretch()

        self.vlayout_right = QVBoxLayout()
        self.label_right = QLabel('占位')
        self.vlayout_right.addWidget(self.label_right)

        self.hlayout_all = QHBoxLayout(self)
        self.hlayout_all.addLayout(self.vlayout_left)
        self.hlayout_all.addLayout(self.vlayout_right)

    def init_data_management(self):
        if self.cbox_download_date_schuduler.isChecked():
            # 启动新的进程，进行数据下载
            p = Process(target=download_data_scheduler)
            p.start()
            self.cbox_download_date_schuduler.setEnabled(False)

            def func():
                while p.is_alive():
                    sleep(0.2)
                self.cbox_download_date_schuduler.setEnabled(True)
            t = Thread(target=func)
            t.start()




if __name__ == '__main__':
    app = QApplication()
    win = DatabaseWindow()
    win.resize(500, 500)
    win.show()
    # win.show()
    app.exec()
