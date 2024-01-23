import os
from qtpy.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QFormLayout,
    QWidget,
    QPushButton,
    QFileDialog,
)

class FileDialogGroup(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.path = str()
        self.dialog = QFileDialog()
        self.dialog.setFileMode(QFileDialog.DirectoryOnly)
        self.dialog.setViewMode(QFileDialog.Detail)

        self.layout = QVBoxLayout()
        self.path_form = QFormLayout()
        self.browse_btn = QPushButton('Browse')

        self.browse_btn.clicked.connect(self.open_file_dialog)
        self.path_form.addRow(QLabel(title), self.browse_btn)
        self.layout.addLayout(self.path_form)
        self.setLayout(self.layout)

    def open_file_dialog(self):
        if self.dialog.exec():
            filenames = self.dialog.selectedFiles()
            if filenames:
                self.path = filenames[0]
                print(self.path)

