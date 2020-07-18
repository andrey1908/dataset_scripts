from PyQt5.QtWidgets import QApplication, QWidget, QToolButton, QLineEdit, QVBoxLayout, QHBoxLayout, QGraphicsView,\
                            QGraphicsScene, QGraphicsPixmapItem, QFrame, QGraphicsItem, QGroupBox
from PyQt5.QtGui import QPixmap, QBrush, QColor
from PyQt5.QtCore import Qt, QPoint, QRectF, pyqtSignal


class Viewer(QGroupBox):
    def __init__(self, width, height):
        super(Viewer, self).__init__('Viewer')
        self.width = width
        self.height = height
        self.zoom = 0
        self.init_UI()

    def init_UI(self):
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene = QGraphicsScene()
        self.scene.addItem(self.pixmap_item)
        self.view = QGraphicsView()
        self.view.setScene(self.scene)
        self.view.wheelEvent = self.wheelEvent
        self.view.setFixedSize(self.width, self.height)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        # self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setBackgroundBrush(QBrush(QColor(0, 0, 0)))
        self.view.setFrameShape(QFrame.NoFrame)
        vbox = QVBoxLayout()
        vbox.addWidget(self.view)
        self.setLayout(vbox)

    def set_pixmap(self, pixmap=None):
        if pixmap is not None:
            self.pixmap_item.setPixmap(pixmap)
        if self.pixmap_item.pixmap().isNull():
            return
        rect = QRectF(self.pixmap_item.pixmap().rect())
        self.view.setSceneRect(rect)
        unity = self.view.transform().mapRect(QRectF(0, 0, 1, 1))
        self.view.scale(1 / unity.width(), 1 / unity.height())
        scenerect = self.view.transform().mapRect(rect)
        factor = min(self.width / scenerect.width(),
                     self.height / scenerect.height())
        self.view.scale(factor, factor)
        self.zoom = 0

    def wheelEvent(self, event):
        if self.pixmap_item.pixmap().isNull():
            return
        if event.angleDelta().y() > 0:
            factor = 1.25
            self.zoom += 1
        else:
            factor = 0.8
            self.zoom -= 1
        if self.zoom > 0:
            self.view.scale(factor, factor)
        elif self.zoom == 0:
            self.set_pixmap()
        else:
            self.zoom = 0
