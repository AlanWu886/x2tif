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
    def __init__(self, run_command, parent=None):
        super().__init__(parent=parent)
        # self.tab_setting_ui(parent_layout)
        self.run_command = run_command
        self.ch_list = list()
        self.tab_setting = QVBoxLayout()

        self.tab_header_layout = QHBoxLayout()
        self.tab_header_layout.addWidget(QLabel('Index'), 2, Qt.AlignCenter)
        self.tab_header_layout.addWidget(QLabel('Name'), 3, Qt.AlignLeft)
        self.tab_header_layout.addWidget(QLabel('Color'), 3, Qt.AlignLeft)
        self.tab_setting.addLayout(self.tab_header_layout)

        self.parameter_form = QFormLayout()
        self.tab_setting.addLayout(self.parameter_form, 3)

        self.test_btn = QPushButton("Test")
        self.test_btn.clicked.connect(lambda: self.run_command(True))
        self.tab_setting.addWidget(self.test_btn)
        self.setLayout(self.tab_setting)


