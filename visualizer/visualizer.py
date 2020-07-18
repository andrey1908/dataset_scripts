from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGroupBox, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from ImageSelector import ImageSelector
from ThresholdSelector import ThresholdSelector
from Viewer import Viewer
from Painter import Painter
import os
import json
import argparse


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', '--json-file', required=True, type=str)
    parser.add_argument('-img-fld', '--images-folder', required=True, type=str)
    parser.add_argument('-w', '--width', type=int, default=900)
    parser.add_argument('-ht', '--height', type=int, default=500)
    return parser


class Visualizer(QWidget):
    def __init__(self, json_dict, images_folder, window_width, window_height):
        super(Visualizer, self).__init__()
        self.image_selector = ImageSelector(json_dict, images_folder, show_delay=True)
        self.threshold_selector = ThresholdSelector(show_delay=True)
        self.viewer = Viewer(window_width, window_height)
        self.painter = Painter(json_dict, images_folder, self.image_selector.get_current_image_idx(),
                               self.threshold_selector.get_current_threshold())
        self.image_selector.imageChanged.connect(self.painter.new_image)
        self.threshold_selector.thresholdChanged.connect(self.painter.new_threshold)
        self.painter.boxesDrawn.connect(self.viewer.set_pixmap)
        self.init_UI()
        self.painter.draw()

    def init_UI(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.image_selector)
        vbox.addWidget(self.viewer)
        hbox = QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addWidget(self.threshold_selector)
        self.setLayout(hbox)


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    with open(args.json_file, 'r') as f:
        json_dict = json.load(f)
    app = QApplication([])
    vis = Visualizer(json_dict, args.images_folder, args.width, args.height)
    vis.show()
    app.exec_()
