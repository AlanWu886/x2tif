import os
import re
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
    QProgressBar,

)
from qtpy.QtGui import QRegExpValidator

from UI.widget import file_dialog, ch_group
from UI.tabs import setup_tab

import importlib


class MyWidget(QWidget):
    """Any QtWidgets.QWidget or magicgui.widgets.Widget subclass can be used."""

    def __init__(self, napari_viewer, parent=None):
        super().__init__(parent)
        self.viewer = napari_viewer
        self.parameters = \
            {
                'input_path': str | os.PathLike,
                'output_path': str | os.PathLike,
                'image_stacks': str,
                'channels': {}
                # 'channels:': list | dict,
            }

        self.default_stacks = ''
        self.stack_pattern_regex = None
        self.reader_options = {
            '': 'placeholder',
            '.lif': 'lif2tif',
            '.nd2': 'TBD',
            '.czi': 'TBD'
        }
        self.reader = None
        self.preview = None
        self.ch_group_list = list()

        self.main_layout = QVBoxLayout()
        # self.setLayout(QVBoxLayout())
        self.reader_title = "x2tif"
        self.plugin_title = QLabel(self.reader_title + ' convertor')
        self.plugin_title.setStyleSheet("font: bold 18px;")
        self.main_layout.addWidget(self.plugin_title)

        # self.input_group = file_dialog.FileDialogGroup(parent=self, callback=self.get_path)
        # # self.parameters['input_path'] = self.input_group.path
        # self.main_layout.addWidget(self.input_group)
        # self.output_group = file_dialog.FileDialogGroup("Output Folder", parent=self)
        # # self.parameters['output_path'] = self.output_group.path
        # self.main_layout.addWidget(self.output_group)

        self.form_layout = QFormLayout()
        self.ext_dropdown = QComboBox()
        # self.ext_dropdown.addItem('')
        self.ext_dropdown.addItems(self.reader_options.keys())
        self.ext_dropdown.currentTextChanged.connect(
            lambda: self._import_module(self.reader_options[self.ext_dropdown.currentText()]))
        self.form_layout.addRow('Extension', self.ext_dropdown)

        self.input_dialog = file_dialog.FileDialog('Input', callback=self._get_path)
        self.input_dialog.browse_btn.setEnabled(False)
        self.form_layout.addRow(self.input_dialog)

        self.output_dialog = file_dialog.FileDialog('Output', )
        self.form_layout.addRow(self.output_dialog)

        self.form_layout.addRow(QLabel('Preview Section'), None)
        self.file_list_dropdown = QComboBox()
        self.file_list_label = QLabel('Image')
        self.file_list_dropdown.setHidden(True)
        self.file_list_label.setHidden(True)
        self.file_list_dropdown.currentTextChanged.connect(self.preview_image)
        self.form_layout.addRow(self.file_list_label,self.file_list_dropdown)

        self.lif_series_dropdown = QComboBox()
        self.lif_series_label = QLabel('Series')
        self.lif_series_dropdown.setHidden(True)
        self.lif_series_label.setHidden(True)
        self.lif_series_dropdown.currentTextChanged.connect(self._preview_lif_series)
        self.form_layout.addRow(self.lif_series_label, self.lif_series_dropdown)

        self.image_stack_input = QLineEdit()
        self.image_stack_input.setEnabled(False)
        self.image_stack_input.textChanged.connect(self._update_suffix)
        self.form_layout.addRow(QLabel("Image Stack(s)"), self.image_stack_input)

        self.file_suffix = QLineEdit()
        self.file_suffix.setReadOnly(True)
        self.form_layout.addRow(QLabel("File Suffix"), self.file_suffix)

        self.training_data = QRadioButton("Training Data Batch Conversion")
        self.training_data.setChecked(False)
        self.training_data.toggled.connect(self.toggle_training_data)
        self.form_layout.addRow(self.training_data)

        self.main_layout.addLayout(self.form_layout)
        # self.layout().addWidget(self.homogeneous_format)

        self.tabs = QTabWidget(parent)
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(False)

        self.setup_tab = setup_tab.SetupTab(parent=self.tabs)
        self.tabs.addTab(self.setup_tab, "Channels")
        # self.setup_tab.render_setup_tab(self.setup_tab)
        self.main_layout.addWidget(self.tabs)
        self.tabs.setTabVisible(0, self.training_data.isChecked())

        self.test_btn = QPushButton("Test")
        self.test_btn.clicked.connect(lambda: self.convert(True))
        self.main_layout.addWidget(self.test_btn)
        self.convert_btn = QPushButton("Run")
        self.convert_btn.clicked.connect(self.convert)
        self.main_layout.addWidget(self.convert_btn)

        self.setLayout(self.main_layout)
        # self.tabs.setVisible(False)

    # def enable_widget(self, widget):
    #     if isinstance(widget, QLineEdit):
    #         widget.setEnabled(True)
    #     if isinstance(widget, QPushButton):
    #         widget.se
    def _reset_parameters(self):
        self.parameters = \
            {'input_path': '', 'output_path': str | os.PathLike, 'image_stacks': str, 'channels': {}}
        self.input_dialog.path_display.setText('')
        self.input_dialog.path = ''
        self.default_stacks = ''
        self.stack_pattern_regex = None
        self.input_dialog.browse_btn.setEnabled(False)
        self.image_stack_input.setText('')
        self.image_stack_input.setEnabled(False)
        self.reader = None
        self.preview = None

    def _import_module(self, module_name: str):
        self._reset_parameters()
        self._reset_image_preview()
        self._reset_channel_group()

        try:
            self.reader = importlib.import_module(module_name)
            print('select reader: ', self.reader.__name__)
            if self.reader:
                print('module imported, enable input dialog')
                self.input_dialog.browse_btn.setEnabled(True)

        except ModuleNotFoundError:
            print("Module not found")

    def _reset_image_preview(self):
        self.file_suffix.setText('')
        self.file_list_dropdown.clear()
        self.file_list_dropdown.setHidden(True)
        self.file_list_label.setHidden(True)
        if self.lif_series_dropdown.count() > 0:
            self.lif_series_dropdown.clear()
            self.lif_series_dropdown.setHidden(True)
            self.lif_series_label.setHidden(True)

    def _reset_channel_group(self):
        while len(self.ch_group_list) > 0:
            ch = self.ch_group_list.pop()
            self.setup_tab.parameter_form.removeRow(ch)
        self.setup_tab.ch_list.clear()

    def preview_image(self):
        if self.file_list_dropdown.currentText() != '':
            file = os.path.join(self.parameters['input_path'], self.file_list_dropdown.currentText())
            print('file: ', file)
            if self.reader.__name__ == 'lif2tif':
                self.lif_series_dropdown.clear()
                self.preview = self.reader.load_preview(file, reader=self.reader)
                series = self.preview.scenes
                print('series: ', series)
                self.lif_series_dropdown.setHidden(False)
                self.lif_series_label.setHidden(False)
                self.lif_series_dropdown.addItems(series)
            else:
                # wait for other reader to be implemented
                pass

    def _set_default_stacks(self):
        if isinstance(self.preview, AICSImage):
            self.image_stack_input.setEnabled(True)
            self.default_stacks = self.preview.dims.order.replace('YX', '')
        # self.parameters['image_stacks'] = lif.dims.order.replace('YX', '')
        if not self.training_data.isChecked():
            self.image_stack_input.setText(self.default_stacks)
        regex_str = r'^(?!.*(.).*\1)[' + str(self.default_stacks) + r']{0,3}$'
        stack_pattern_regex = QRegExp(regex_str)
        stack_pattern_validator = QRegExpValidator(stack_pattern_regex, self.image_stack_input)
        self.image_stack_input.setValidator(stack_pattern_validator)

    def _generate_channel_group(self):
        if self.preview.channel_names:
            for i, color in enumerate(self.preview.channel_names):
                print(i, color)
                self.setup_tab.ch_list.append({'index': i, 'name': color, 'color': color})
                ch = ch_group.ChannelGroup(self.setup_tab.ch_list[i], parent=self)
                self.ch_group_list.append(ch)
                self.setup_tab.parameter_form.addRow(ch)

    def _preview_lif_series(self):
        if self.lif_series_dropdown.currentText() != '':
            self._reset_channel_group()
            self.preview.set_scene(self.lif_series_dropdown.currentText())
            self._set_default_stacks()
            self._update_suffix()
            print('previewing lif series:', self.preview.current_scene)
            self._generate_channel_group()
            self.viewer.layers.clear()
            self.viewer.add_image(self.preview.data, name=self.preview.current_scene)

    def _get_path(self, path=None):
        self.parameters = \
            {
                'input_path': str | os.PathLike,
                'output_path': str | os.PathLike,
                'image_stacks': str,
                'channels': {}
            }
        # self.file_suffix.setText('')
        self._reset_channel_group()
        self._reset_image_preview()

        print('reader: ', self.reader_options[self.ext_dropdown.currentText()])
        print("pick path: ", path)
        if path and self.ext_dropdown.currentText() == '.lif':
            self.parameters['input_path'] = path
            lif_list = self.reader.load_file_list(self.parameters['input_path'])
            if len(lif_list) > 0:
                print('lif list: ', lif_list)
                lit_fname_list = map(lambda f: os.path.basename(f), lif_list)
                self.file_list_dropdown.setHidden(False)
                self.file_list_label.setHidden(False)
                self.file_list_dropdown.addItems(lit_fname_list)
            # self.parameters['input_path'] = path
            # print(self.parameters['input_path'])
            #
            # lif = self.reader.preview_image(self.reader.load_file_list(self.parameters['input_path']))
            # if isinstance(lif, AICSImage):
            #     self.image_stack_input.setEnabled(True)
            #     self.default_stacks = lif.dims.order.replace('YX', '')
            # # self.parameters['image_stacks'] = lif.dims.order.replace('YX', '')
            # if not self.training_data.isChecked():
            #     self.image_stack_input.setText(self.default_stacks)
            # # regex_str = r"^(?:([TCZ])(?!.*\1)){0,}$"
            # self.toggle_channel_setup()
            # regex_str = r'^(?!.*(.).*\1)[' + str(self.default_stacks) + r']{0,3}$'
            # stack_pattern_regex = QRegExp(regex_str)
            # stack_pattern_validator = QRegExpValidator(stack_pattern_regex, self.image_stack_input)
            # self.image_stack_input.setValidator(stack_pattern_validator)
            #
            # if lif.channel_names:
            #     for i, color in enumerate(lif.channel_names):
            #         print(i, color)
            #         self.setup_tab.ch_list.append({'index': i, 'name': color, 'color': color})
            #         ch = ch_group.ChannelGroup(self.setup_tab.ch_list[i], parent=self)
            #         self.ch_group_list.append(ch)
            #         self.setup_tab.parameter_form.addRow(ch)

    def _update_suffix(self):
        if 'C' not in self.image_stack_input.text():
            self.tabs.setTabVisible(0, True)
        else:
            self.tabs.setTabVisible(0, False)
        self.generate_suffix()

    def generate_suffix(self):
        suffix = ''
        split_dims = self.preview.dims.order.replace('YX', '')
        for dim in self.image_stack_input.text():
            split_dims = split_dims.replace(dim, '')
        print('split dims: ', split_dims)
        if split_dims != '':
            if 'C' in split_dims:
                split_dims = split_dims.replace('C', '') + 'C'

            for char in split_dims:
                suffix += ('_' + char + '=0')

            suffix = self.reader.append_ch_suffix(suffix, {'ch_names': ['NAME'], 'ch_colors': ['COLOR']})
            self.file_suffix.setText(suffix)
        else:
            self.file_suffix.setText('')

    def toggle_training_data(self):
        if self.training_data.isChecked():
            self.image_stack_input.setDisabled(True)
            if self.image_stack_input.text() != '':
                self.image_stack_input.setText('')
        else:
            self.image_stack_input.setDisabled(False)
            self.image_stack_input.setText(self.default_stacks)
        self._update_suffix()

    def fill_parameters(self):
        print('filling parameters...')
        self.parameters['output_path'] = self.output_dialog.path
        self.parameters['image_stacks'] = self.image_stack_input.text()
        self.parameters['channels']['ch_colors'] = list()
        self.parameters['channels']['ch_names'] = list()
        for ch in self.ch_group_list:
            self.parameters['channels']['ch_colors'].append(ch.color_input.text())
            self.parameters['channels']['ch_names'].append(ch.name_input.text())
            # print(ch.color_input.text(), ch.name_input.text(), ch.ch_info['index'])
        # self.parameters['channels'] = self.setup_tab.ch_list

    def convert(self, test_mode: bool = None):
        self.fill_parameters()
        self.viewer.layers.clear()
        if self.ext_dropdown.currentText() == '.lif':
            files = self.reader.load_file_list(self.parameters['input_path'])
            output_path = self.reader.setup_output_folder(self.parameters['output_path'])
            # file_list = list()
            print('converting...')
            print(self.parameters)
            print('test mode: ', test_mode)
            file_list = files if not test_mode else files[0]
            if not test_mode:
                self.reader.convert_lif2tif(file_list,
                                            output_path,
                                            desired_stacks=self.parameters['image_stacks'],
                                            image_output_details=self.parameters['channels']
                                            )

            if test_mode:
                new_img_details = {
                    'ch_colors': self.parameters['channels']['ch_colors'],
                    'ch_names': self.parameters['channels']['ch_names'],
                    'dims': ''
                }
                file_name = os.path.splitext(os.path.basename(file_list))[0]
                scene_name = self.preview.current_scene.replace('/', '_').replace('\\', '_').replace(' ', '_')
                # output_path = self.reader.setup_output_folder(self.parameters['output_path'])
                split_dims, new_img_details['dims'] = self.reader.reorder_hyperstack(self.preview.dims, self.parameters['image_stacks'])
                test_output_path = os.path.join(output_path, file_name + '_' + scene_name)
                self.reader.gen_stack_combo(
                    test_output_path,
                    self.preview,
                    vars(self.preview.dims),
                    split_dims,
                    new_img_details
                                            )
                tif_list = self.reader.load_file_list(output_path, 'tif')
                for tif in tif_list:
                    tif_name = os.path.basename(tif)   # get color without extension
                    ch_color = os.path.splitext(tif_name)[0].split('_')[-1].lower()
                    try:
                        self.viewer.open(os.path.join(output_path, tif_name), name=tif_name, colormap=ch_color)
                        # colormap list
                        # "GrBu", "GrBu_d", "PiYG", "PuGr", "RdBu", "RdYeBuCy", "autumn", "blues", "cool", "coolwarm",
                        # "cubehelix", "diverging", "fire", "gist_earth", "gray", "gray_r", "grays", "greens", "hot", "hsl",
                        # "hsv", "husl", "ice", "inferno", "light_blues", "magma", "orange", "plasma", "reds", "single_hue",
                        # "spring", "summer", "turbo", "twilight", "twilight_shifted", "viridis", "winter"
                    except KeyError:
                        print(f'colormap not found as {ch_color}, using default colormap of grayscale')
                        self.viewer.open(os.path.join(output_path, tif_name), name=tif_name)
        print('conversion finished')


def main():
    viewer = napari.Viewer()
    toTif = MyWidget(viewer)
    # sg_gui.setFixedWidth(550)
    viewer.window.add_dock_widget(toTif, name='toTif')
    napari.run()


if __name__ == '__main__':
    main()


