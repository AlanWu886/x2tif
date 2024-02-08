from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QWidget,
    QPushButton,

)
from ..widget import ch_group


class SetupTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # self.tab_setting_ui(parent_layout)
        self.ch_list = list()
        self.tab_setting = QVBoxLayout()

        self.tab_header_layout = QHBoxLayout()
        self.tab_header_layout.addWidget(QLabel('Index'), 2, Qt.AlignCenter)
        self.tab_header_layout.addWidget(QLabel('Name'), 3, Qt.AlignLeft)
        self.tab_header_layout.addWidget(QLabel('Color'), 3, Qt.AlignLeft)
        self.tab_setting.addLayout(self.tab_header_layout)

        self.parameter_form = QFormLayout()
        self.tab_setting.addLayout(self.parameter_form, 3)

        self.setLayout(self.tab_setting)


