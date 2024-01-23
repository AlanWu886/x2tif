from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QFormLayout,
    QWidget,
    QPushButton
)


class SetupTab(QWidget):
    def __init__(self, run_command, parent=None):
        super().__init__(parent=parent)
        # self.tab_setting_ui(parent_layout)
        self.run_command = run_command
        self.test = None
        self.configuration = dict()

        self.tab_setting = QVBoxLayout()
        self.tab_title = QLabel("Conversion parameters setup")
        self.tab_title.setStyleSheet(
            "font: italic 14px;"
        )
        self.tab_setting.addWidget(self.tab_title, 0, Qt.AlignLeft)

        self.parameter_form = QFormLayout()
        self.tab_setting.addLayout(self.parameter_form, 3)
        self.parameter_form.addRow(QLabel("Please set the paramenter for whole batch"))

        self.test_btn = QPushButton("Test")
        self.test_btn.clicked.connect(lambda: self.run_command(self.configuration))
        self.tab_setting.addWidget(self.test_btn)
        self.setLayout(self.tab_setting)

    # def render_setup_tab(self, parent):
    #     self.tab_setting = QVBoxLayout(parent)
    #     self.tab_title = QLabel("Conversion parameters setup")
    #     self.tab_title.setStyleSheet(
    #         "font: italic 14px;"
    #     )
    #     self.tab_setting.addWidget(self.tab_title, 0, Qt.AlignLeft)
    #
    #     self.parameter_form = QFormLayout()
    #     self.tab_setting.addLayout(self.parameter_form, 3)
    #     self.parameter_form.addRow(QLabel("Please set the paramenter for whole batch"))
    #
    #     self.test_btn = QPushButton("Test")
    #     self.test_btn.clicked.connect(lambda: self.run_command(self.configuration))
    #     self.tab_setting.addWidget(self.test_btn)

        # self.ch_parameter_form = QFormLayout()
        # self.tab_setting.addLayout(self.ch_parameter_form, 3)
        # self.ch_parameter_form.addRow(QLabel("Please set the crown thickness for each channel"))
        #
        # self.test_btn = QPushButton("Test")
        # self.test_btn.clicked.connect(lambda clicked: self.run_command(True))
        # self.tab_setting.addWidget(self.test_btn)
        #
        # self.run_btn = QPushButton("Run")
        # self.run_btn.clicked.connect(lambda clicked: self.run_command(False))
        # self.tab_setting.addWidget(self.run_btn)


