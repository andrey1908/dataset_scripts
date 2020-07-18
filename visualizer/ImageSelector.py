from PyQt5.QtWidgets import QLineEdit, QLabel, QGroupBox, QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import pyqtSignal
from dataset_scripts.utils.coco_tools import get_category_name_to_id, get_image_id_to_annotations
from time import time


class ImageSelector(QGroupBox):
    imageChanged = pyqtSignal(int)

    def __init__(self, json_dict, images_folder, threshold, show_delay=False):
        super(ImageSelector, self).__init__('Image selector')
        self.json_dict = json_dict
        self.images_folder = images_folder
        self.threshold = threshold
        self.show_delay = show_delay
        self.images_number = len(json_dict['images'])
        self.current_image_idx = 0 if self.images_number > 0 else None
        self.category_name_to_id = get_category_name_to_id(json_dict)
        self.image_id_to_annotations = get_image_id_to_annotations(json_dict)
        self.only_with_these_categories = list()
        self.init_UI()
        self.prev_button.clicked.connect(self.go_to_prev_image)
        self.next_button.clicked.connect(self.go_to_next_image)
        self.apply_image_idx_button.clicked.connect(self.go_to_selected_image)
        self.apply_categories_filters_button.clicked.connect(self.refresh_categories_filters)

    def get_current_image_idx(self):
        return self.current_image_idx

    def init_UI(self):
        self.images_number_label = QLabel()
        self.images_number_label.setText('{} images'.format(self.images_number))
        self.prev_button = QPushButton('Prev')
        self.next_button = QPushButton('Next')
        self.current_image_idx_line_edit = QLineEdit()
        self.current_image_idx_line_edit.setValidator(QIntValidator())
        self.apply_image_idx_button = QPushButton('Apply')
        if self.show_delay:
            self.delay_label = QLabel()
            self.delay_label.setText('- ms')
        self.only_with_boxes_check_box = QCheckBox()
        self.only_with_boxes_check_box.setText('Only with boxes')
        self.only_with_these_categories_label = QLabel()
        self.only_with_these_categories_label.setText('Only with these categories:')
        self.only_with_these_categories_line_edit = QLineEdit()
        self.apply_categories_filters_button = QPushButton('Apply')

        vbox = QVBoxLayout()
        vbox.addWidget(self.images_number_label)

        hbox = QHBoxLayout()
        hbox.addWidget(self.prev_button)
        hbox.addWidget(self.next_button)
        hbox.addWidget(self.current_image_idx_line_edit)
        hbox.addWidget(self.apply_image_idx_button)
        if self.show_delay:
            hbox.addWidget(self.delay_label)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.only_with_boxes_check_box)
        hbox.addWidget(self.only_with_these_categories_label)
        hbox.addWidget(self.only_with_these_categories_line_edit)
        hbox.addWidget(self.apply_categories_filters_button)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        self.refresh_UI()

    def refresh_UI(self):
        self.current_image_idx_line_edit.setText(str(self.current_image_idx))

    def new_threshold(self, threshold):
        self.threshold = threshold

    def current_image_is_OK(self):
        if self.only_with_boxes_check_box.isChecked():
            annotations = self.image_id_to_annotations[self.json_dict['images'][self.current_image_idx]['id']]
            for annotation in annotations:
                if len(self.only_with_these_categories) > 0:
                    if annotation['category_id'] not in self.only_with_these_categories:
                        continue
                score = annotation.get('score')
                if score is not None:
                    if score >= self.threshold:
                        return True
                else:
                    return True
            return False
        return True

    def go_to_prev_image(self):
        if self.show_delay:
            start_time = time()
        old_current_image_idx = self.current_image_idx
        if self.current_image_idx > 0:
            self.current_image_idx -= 1
        else:
            self.current_image_idx = self.images_number - 1
        while not self.current_image_is_OK():
            assert self.current_image_idx != old_current_image_idx
            if self.current_image_idx > 0:
                self.current_image_idx -= 1
            else:
                self.current_image_idx = self.images_number - 1
        self.refresh_UI()
        self.imageChanged.emit(self.current_image_idx)
        if self.show_delay:
            time_passed = (time() - start_time) * 1000
            self.delay_label.setText('{:.1f} ms'.format(time_passed))

    def go_to_next_image(self):
        if self.show_delay:
            start_time = time()
        old_current_image_idx = self.current_image_idx
        if self.current_image_idx + 1 < self.images_number:
            self.current_image_idx += 1
        else:
            self.current_image_idx = 0
        while not self.current_image_is_OK():
            assert self.current_image_idx != old_current_image_idx
            if self.current_image_idx + 1 < self.images_number:
                self.current_image_idx += 1
            else:
                self.current_image_idx = 0
        self.refresh_UI()
        self.imageChanged.emit(self.current_image_idx)
        if self.show_delay:
            time_passed = (time() - start_time) * 1000
            self.delay_label.setText('{:.1f} ms'.format(time_passed))

    def go_to_selected_image(self):
        if self.show_delay:
            start_time = time()
        self.current_image_idx = int(self.current_image_idx_line_edit.text())
        if self.current_image_idx < 0:
            self.current_image_idx = 0
        if self.current_image_idx >= self.images_number:
            self.current_image_idx = self.images_number - 1
        self.refresh_UI()
        self.imageChanged.emit(self.current_image_idx)
        if self.show_delay:
            time_passed = (time() - start_time) * 1000
            self.delay_label.setText('{:.1f} ms'.format(time_passed))

    def refresh_categories_filters(self):
        only_with_these_categories = list()
        only_with_these_categories_line = self.only_with_these_categories_line_edit.text()
        only_with_these_categories_names = only_with_these_categories_line.split()
        for category_name in only_with_these_categories_names:
            category_id = self.category_name_to_id.get(category_name)
            assert category_id is not None
            only_with_these_categories.append(category_id)
        self.only_with_these_categories = only_with_these_categories
