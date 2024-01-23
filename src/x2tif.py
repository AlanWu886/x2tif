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


class MyWidget(QWidget):
    """Any QtWidgets.QWidget or magicgui.widgets.Widget subclass can be used."""
    def __init__(self, napari_viewer, parent=None):
        super().__init__(parent)
        self.viewer = napari_viewer
        self.parameters = dict()

        self.setLayout(QVBoxLayout())
        self.reader_title = "lif"
        self.plugin_title = QLabel(self.reader_title + ' convertor')
        self.plugin_title.setStyleSheet("font: bold 18px;")
        self.layout().addWidget(self.plugin_title)

        self.input_group = file_dialog.FileDialogGroup("Input Folder", parent=self)
        self.parameters['input_path'] = self.input_group.path
        self.layout().addWidget(self.input_group)
        self.output_group = file_dialog.FileDialogGroup("Output Folder", parent=self)
        self.parameters['output_path'] = self.output_group.path
        self.layout().addWidget(self.output_group)

        self.homogeneous_format = QRadioButton("Homogeneous format")
        self.homogeneous_format.setChecked(False)
        self.homogeneous_format.toggled.connect(self.toggle_homogeneous)
        self.layout().addWidget(self.homogeneous_format)

        self.tabs = QTabWidget(parent)
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(False)

        self.setup_tab = setup_tab.SetupTab(self.convert, parent=self.tabs)
        self.tabs.addTab(self.setup_tab, "Setup")
        # self.setup_tab.render_setup_tab(self.setup_tab)
        self.layout().addWidget(self.tabs)
        self.tabs.setTabVisible(0, self.homogeneous_format.isChecked())

        self.convert_btn = QPushButton("Run")
        self.convert_btn.clicked.connect(lambda: self.convert(self.setup_tab.configuration))

        self.layout().addWidget(self.convert_btn)
        # self.tabs.setVisible(False)

    def get_path(self):
        if self.input_group.path:
            self.parameters['input_path'] = self.input_group.path
            print(self.parameters['input_path'])

    def toggle_homogeneous(self):
        self.get_path()
        self.tabs.setTabVisible(0, self.homogeneous_format.isChecked())

    def convert(self, configuration=None):
        print('converting...')
        if configuration:
            print('limiting whole batch to follow configuration')
        else:
            pass


def lif_to_tif_by_ch(input_list, output_folder, img_format, channel_pattern, channel_color_list, channel_num_list=None,
                     img_dims="xy"):
    if "c" in img_dims:
        print("WARNING!!!! channel dimension should not be included in the image dimension!!!")

    # channel_channel_color_list = "{'EITC': 'Red', 'TRITC':'Green'}"
    ch_name_lookup = {}
    validate = ""
    for img_file in input_list:
        # keys = list(channel_list.keys())
        # values = list(channel_list.values())
        fname = os.path.splitext(img_file)[0]
        # print(fname)

        lif = AICSImage(os.path.realpath(img_file))
        for scene_index in range(len(lif.scenes)):
            print(scene_index)
            lif.set_scene(scene_index)
            print(lif.current_scene_index, lif.current_scene)
            print("metadata: ", lif.reader.metadata)
            print(lif.channel_names, lif.dims)
        return 0

def check_conversion_mode():
    homo = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    homo.add_argument("batch", help="0 for as is mode, 1 for batch mode", type=bool)
    args = homo.parse_args()
    return args.batch

def manage_user_input() -> argparse.Namespace:
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("img_format", help="desired image format. eg: np.int16", type=str)
    parser.add_argument("ch_pattern", help="the keyword indicates pattern", type=str)
    parser.add_argument("ch_color",
                        help='list of color for each channel. eg: "{\'FITC\': \'green\', \'TRITC\': \'red\', \'Cy5\': \'purple\', \'DAPI\': \'blue\'}"',
                        type=str)
    parser.add_argument("-ch_num",
                        help='list of index for channels. eg: "{\'FITC\': 1, \'TRITC\': 2, \'Cy5\': 3, \'DAPI\': 4}"',
                        default='None', type=str)
    parser.add_argument("-dims_out",
                        help="dimensions of your data. please do NOT include 'c' this parameter and 'yx should always be placed in the end'",
                        default='yx', type=str)
    args = parser.parse_args()
    print(args, type(args))
    for arg in vars(args):
        print(arg, getattr(args, arg))
    return args


def load_file_list(input_path=None, ext=".lif") -> list:
    if input_path is None:
        input_path = os.path.realpath("./input")
    else:
        input_path = os.path.realpath(input_path)

    path_with_ext = os.path.realpath(input_path + r'/*' + ext)
    files = glob.glob(path_with_ext)
    print(path_with_ext, files)
    return files


def setup_output_folder() -> str:
    # output_path = os.path.realpath("./output")
    ct = datetime.datetime.now()
    timestamp = ct.strftime("D%Y_%m_%dT%H_%M_%S")
    output_path_tstamp = os.path.realpath("./output/output_" + timestamp)
    os.mkdir(output_path_tstamp)
    return output_path_tstamp

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
