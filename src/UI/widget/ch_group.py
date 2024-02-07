from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QWidget,
    QPushButton,
    QFileDialog,
)

class ChannelGroup(QWidget):
    def __init__(self, ch_info: dict, parent=None, callback=None):
        super().__init__(parent)
        self._callback = callback
        self.index = None
        self.color = None
        self.name = None
        self.ch_info = ch_info

        self.ch_group_layout = QHBoxLayout()
        self.ch_group_layout.setContentsMargins(0,0,0,0)
        self.ch_group_layout.addWidget(QLabel(str(self.ch_info['index'])), 2, Qt.AlignRight)
        self.color_input = QLineEdit(self.ch_info['color'], )
        self.name_input = QLineEdit(self.ch_info['name'])
        self.ch_group_layout.addWidget(self.name_input, 3, Qt.AlignCenter)
        self.ch_group_layout.addWidget(self.color_input, 3, Qt.AlignCenter)

        # self.ch_group_layout.addWidget(self.name_input)
        # self.ch_group_layout.addWidget(self.color_input)

        self.setLayout(self.ch_group_layout)

