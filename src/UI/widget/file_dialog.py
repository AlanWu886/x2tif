from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QLineEdit,
    QWidget,
    QPushButton,
    QFileDialog,
    QStyle
)


class FileDialog(QWidget):
    def __init__(self, title: str, parent=None, callback=None):
        super().__init__(parent)
        self._path = str()
        self._callback = callback
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(QLabel(title),1, Qt.AlignLeft)

        self.path_display = QLineEdit(self._path)
        self.path_display.setReadOnly(True)
        self.layout.addWidget(self.path_display, 3)

        self.dialog = QFileDialog()
        self.dialog.setFileMode(QFileDialog.DirectoryOnly)
        self.dialog.setViewMode(QFileDialog.Detail)
        self.browse_btn = QPushButton()
        self.browse_btn.setFixedWidth(30)
        self.icon = self.style().standardIcon(QStyle.SP_DirIcon)
        self.browse_btn.setIcon(self.icon)
        self.browse_btn.clicked.connect(self.open_file_dialog)
        self.layout.addWidget(self.browse_btn, 1, Qt.AlignRight)
        # self.layout.addWidget(self.browse_btn)
        self.setLayout(self.layout)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, new_path):
        self._path = new_path
        if self._callback:
            self._callback(new_path)

    def open_file_dialog(self):
        if self.dialog.exec():
            self.path = self.dialog.selectedFiles()[0]
            self.path_display.setText(self.path)
            print(self.path)