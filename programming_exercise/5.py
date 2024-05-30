"""
作者：太乙真人
心境：行到水穷处 坐看云起时
日期：2024年05月25日
"""
import sys

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QStyleFactory, QLabel
from PySide6.QtCore import Slot, QSize

import qdarkstyle
from qt_material import apply_stylesheet
import qtawesome as qta


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        label = QLabel('标签')
        color1 = QColor(211, 66, 44)
        color2 = QColor(23, 156, 44)
        style_sheet = "color: {}; background: {};".format(color1.name(), color2.name())
        label.setStyleSheet(style_sheet)

        self.button = QPushButton("打印所有小部件")
        self.button.clicked.connect(self.printAllWidgets)

        spin_widget = qta.IconWidget()
        animation = qta.Spin(spin_widget, autostart=False)
        spin_icon = qta.icon('mdi.loading', color='red', animation=animation)
        spin_widget.setIcon(spin_icon)

        # Simple icon widget
        simple_widget = qta.IconWidget('mdi.web', color='blue',
                                       size=QSize(16, 16))
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(label)
        self.layout.addWidget(self.button)
        self.layout.addWidget(simple_widget)
        self.layout.addWidget(spin_widget)

        # Start and stop the animation when needed
        animation.start()
        # animation.stop()

    @Slot()
    def printAllWidgets(self):
        for widget in app.allWidgets():#遍历返回的小部件对象列表
            print(widget)

app = QApplication([])
# apply_stylesheet(app, theme='qdarkstyle.xml')
app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6'))

widget = MyWidget()
widget.resize(300, 200)
widget.show()

print(QStyleFactory.keys())
# app.setStyle(QStyleFactory.create("Windows"))
app.setStyle(QStyleFactory.create("Fusion"))

print(app.widgetAt(50, 50))  # 获取屏幕位置50，50处的Qt小部件

sys.exit(app.exec())
