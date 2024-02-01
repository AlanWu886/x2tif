import tifffile
import os
import glob
import datetime
import sys
import argparse
import numpy as np
from aicsimageio import AICSImage
import napari
from qtpy.QtCore import Qt, QRegExp
from qtpy.QtWidgets import (
    QComboBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
    QFormLayout,
    QTabWidget,
    QFileDialog,
    QMessageBox,
    QCheckBox
)
from qtpy.QtGui import QRegExpValidator
from UI import setup_tab
from UI.widget import file_dialog
from napari_plugin_engine import napari_hook_implementation

import lif2tif


class MyWidget(QWidget):
    """Any QtWidgets.QWidget or magicgui.widgets.Widget subclass can be used."""
    def __init__(self, napari_viewer, parent=None):
        super().__init__(parent)
        self.viewer = napari_viewer
        self.parameters = dict()
        self.parameters['image_stacks'] = ''
        self.default_stacks = ''
        self.stack_pattern_regex = None

        self.main_layout = QVBoxLayout()
        # self.setLayout(QVBoxLayout())
        self.reader_title = "lif"
        self.plugin_title = QLabel(self.reader_title + ' convertor')
        self.plugin_title.setStyleSheet("font: bold 18px;")
        self.main_layout.addWidget(self.plugin_title)

        self.input_group = file_dialog.FileDialogGroup("Input Folder", parent=self, callback=self.get_path)
        self.parameters['input_path'] = self.input_group.path
        self.main_layout.addWidget(self.input_group)
        self.output_group = file_dialog.FileDialogGroup("Output Folder", parent=self)
        self.parameters['output_path'] = self.output_group.path
        self.main_layout.addWidget(self.output_group)

        self.form_layout = QFormLayout()
        self.image_stack_input = QLineEdit(self.parameters['image_stacks'])
        self.form_layout.addRow(QLabel("Image Stack(s)"), self.image_stack_input)
        self.homogeneous_format = QRadioButton("Homogeneous Batch Conversion")
        self.homogeneous_format.setChecked(False)
        self.form_layout.addRow(self.homogeneous_format)
        self.main_layout.addLayout(self.form_layout)
        # self.layout().addWidget(self.homogeneous_format)

        self.tabs = QTabWidget(parent)
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(False)

        self.setup_tab = setup_tab.SetupTab(self.convert, parent=self.tabs)
        self.tabs.addTab(self.setup_tab, "Setup")
        # self.setup_tab.render_setup_tab(self.setup_tab)
        self.main_layout.addWidget(self.tabs)
        self.tabs.setTabVisible(0, self.homogeneous_format.isChecked())

        self.convert_btn = QPushButton("Run")
        self.convert_btn.clicked.connect(lambda: self.convert(self.setup_tab.configuration))

        self.main_layout.addWidget(self.convert_btn)
        self.setLayout(self.main_layout)
        # self.tabs.setVisible(False)

    def get_path(self, path=None):
        print("pick path: ", path)
        if path:
            self.parameters['input_path'] = path
            print(self.parameters['input_path'])
            lif_dims = lif2tif.preview_image_dimensions(lif2tif.load_file_list(self.parameters['input_path']))

            self.default_stacks = lif_dims.order.replace('YX', '')
            self.parameters['image_stacks'] = lif_dims.order.replace('YX', '')
            self.image_stack_input.setText(self.parameters['image_stacks'])
            # regex_str = r"^(?:([TCZ])(?!.*\1)){0,}$"
            regex_str = r'^(?!.*(.).*\1)[' + str(self.default_stacks) + r']{0,3}$'
            stack_pattern_regex = QRegExp(regex_str)
            stack_pattern_validator = QRegExpValidator(stack_pattern_regex, self.image_stack_input)
            self.image_stack_input.setValidator(stack_pattern_validator)
            # self.image_stack_input.editingFinished.connect(self.ch_pattern_out_focus)
        # if self.input_group.path:
        #     self.parameters['input_path'] = self.input_group.path
        #     print(self.parameters['input_path'])

    def convert(self, configuration=None):
        print('converting...')
        if configuration:
            print('limiting whole batch to follow configuration')
        else:
            pass


def main():
    viewer = napari.Viewer()
    toTif = MyWidget(viewer)
    # sg_gui.setFixedWidth(550)
    viewer.window.add_dock_widget(toTif, name='toTif')
    napari.run()

# def show_dock_widget(viewer):
#     toTif = MyWidget(viewer)
#     viewer.window.add_dock_widget(toTif)
#
# def napari_experimental_provide_dock_widget(viewer):
#     return {'name': 'toTif', 'dock_widget': show_dock_widget()}

if __name__ == '__main__':
    main()
    # user_input = manage_user_input()
    # file_list = load_file_list()
    # output_path = setup_output_folder()
    # lif_to_tif_by_ch(file_list, output_path, eval(user_input.img_format), user_input.ch_pattern, eval(user_input.ch_color), eval(user_input.ch_num), user_input.dims_out)

    print("conversion finished")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
