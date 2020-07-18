from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGroupBox, QPushButton, QHBoxLayout, QVBoxLayout, QSlider
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from time import time


class ThresholdSelector(QGroupBox):
    thresholdChanged = pyqtSignal(float)

    def __init__(self, show_delay=False):
        super(ThresholdSelector, self).__init__('Threshold')
        self.show_delay = show_delay
        self.init_UI()
        self.slider.valueChanged.connect(self.threshold_changed)

    def init_UI(self):
        self.slider = QSlider(Qt.Vertical)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(40)
        self.label = QLabel()
        vbox = QVBoxLayout()
        vbox.addWidget(self.slider)
        vbox.addWidget(self.label)
        if self.show_delay:
            self.delay_label = QLabel()
            self.delay_label.setText('- ms')
            vbox.addWidget(self.delay_label)
        self.setLayout(vbox)

        self.refresh_UI()

    def refresh_UI(self):
        self.label.setNum(self.get_current_threshold())

    def get_current_threshold(self):
        return self.slider.value() / 100

    def threshold_changed(self, new_value):
        if self.show_delay:
            start_time = time()
        self.refresh_UI()
        self.thresholdChanged.emit(new_value / 100)
        if self.show_delay:
            time_passed = (time() - start_time) * 1000
            self.delay_label.setText('{:.1f} ms'.format(time_passed))
