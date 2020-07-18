from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGroupBox, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QPixmap, QPainter, QPen, QFont
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from numpy import clip
from dataset_scripts.utils.coco_tools import get_category_id_to_name, get_image_id_to_annotations
import os.path as osp


class Painter(QObject):
    boxesDrawn = pyqtSignal(QPixmap)

    def __init__(self, json_dict, images_folder, image_idx, threshold):
        super(Painter, self).__init__()
        self.json_dict = json_dict
        self.images_folder = images_folder
        self.category_id_to_name = get_category_id_to_name(json_dict)
        self.image_id_to_annotations = get_image_id_to_annotations(json_dict)
        self.pen = QPen(Qt.red)
        self.pen.setWidth(3)
        self.font = QFont('Decorative', 20)

        self.image_idx = image_idx
        self.image_file = osp.join(images_folder, json_dict['images'][image_idx]['file_name'])
        self.image_pixmap = QPixmap(self.image_file)
        self.annotations = self.image_id_to_annotations[json_dict['images'][image_idx]['id']]
        self.threshold = threshold

    def new_image(self, image_idx):
        self.image_idx = image_idx
        self.image_file = osp.join(self.images_folder, self.json_dict['images'][image_idx]['file_name'])
        self.image_pixmap = QPixmap(self.image_file)
        self.annotations = self.image_id_to_annotations[self.json_dict['images'][self.image_idx]['id']]
        self.draw()

    def new_threshold(self, threshold):
        self.threshold = threshold
        self.draw()

    def draw(self):
        image = self.image_pixmap.copy()
        image_draw = QPainter(image)
        image_draw.setPen(self.pen)
        image_draw.setFont(self.font)
        for annotation in self.annotations:
            score = annotation.get('score')
            if score is not None:
                if score < self.threshold:
                    continue
            bbox = annotation['bbox']
            self.preprocess_box(bbox, image.width(), image.height())
            text = self.category_id_to_name[annotation['category_id']]
            if score is not None:
                text = text + ' {:.2f}'.format(score)
            image_draw.drawRect(bbox[0], bbox[1], bbox[2], bbox[3])
            image_draw.drawText(bbox[0], bbox[1], text)
        image_draw.end()
        self.boxesDrawn.emit(image)

    def preprocess_box(self, bbox, im_w, im_h):
        bbox[2] += bbox[0]
        bbox[3] += bbox[1]
        bbox[0] = clip(bbox[0], 0, im_w-1)
        bbox[1] = clip(bbox[1], 0, im_h-1)
        bbox[2] = clip(bbox[2], 0, im_w-1)
        bbox[3] = clip(bbox[3], 0, im_h-1)
        bbox[:] = [round(b) for b in bbox]
        bbox[2] -= bbox[0]
        bbox[3] -= bbox[1]
