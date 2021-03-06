# Built-in module
from vision import camera1
from vision import camera2

# PyQt5 Module
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QImage

# Other Module
import sys
import os
import imutils
import redis as rd

path = os.path.dirname(os.path.abspath('robot-camera'))


class CalibrationGUI(QMainWindow):

    def __init__(self, database):
        super().__init__()
        self.path_ui = path + "/views/calibration-gui.ui"

        loadUi(self.path_ui, self)

        self.timer = QTimer(self)
        self.pixmap = None
        self.frame = []
        self.upper = []
        self.lower = []
        self.db = database
        self.objects = ['ball', 'field', 'line', 'obstacle']
        self.camera = camera1

        # Camera ComboBox
        self.cameraCBox.addItem(camera1.name)
        self.cameraCBox.addItem(camera2.name)
        self.cameraCBox.currentIndexChanged.connect(self.change_camera)

        # Objects ComboBox
        for i, obj in enumerate(self.objects):
            self.objectCBox.addItem(obj, i)

        # Horizontal Slider
        self.set_HSV()
        self.activate_YUV_signal()

        # get camm param from redis
        self.load_cameraParameter()

        # Saved Button
        self.saveButton.clicked.connect(self.saveButton_clicked)

        self.timer.start(1)

        self.play_button_clicked()

    def load_cameraParameter(self):
        upper_check_val = self.db.hget(
            self.camera.name,
            self.camera.name + '_upper'
        )
        lower_check_val = self.db.hget(
            self.camera.name,
            self.camera.name + '_lower'
        )

        print(self.camera.name)

        if upper_check_val is not None and lower_check_val is not None:
            upper = str(self.db.hget(self.camera.name, self.camera.name + '_upper')
                        ).strip("b'").split(',')

            upper = list(map(int, upper))

            lower = str(self.db.hget(self.camera.name, self.camera.name + '_lower')
                        ).strip("b'").split(',')

            lower = list(map(int, lower))

        else:
            upper = [0, 0, 0]
            lower = [0, 0, 0]

        print(f"Lower: {lower}")
        print(f"Upper: {upper}")

        self.upper = upper
        self.lower = lower

        # update slider value
        self.hSliderUH.setValue(upper[0])
        self.hSliderUS.setValue(upper[1])
        self.hSliderUV.setValue(upper[2])

        self.hSliderLH.setValue(lower[0])
        self.hSliderLS.setValue(lower[1])
        self.hSliderLV.setValue(lower[2])

        # update label value
        self.upperHue.setText(str(upper[0]))
        self.upperSat.setText(str(upper[1]))
        self.upperVal.setText(str(upper[2]))

        self.lowerHue.setText(str(lower[0]))
        self.lowerSat.setText(str(lower[1]))
        self.lowerVal.setText(str(lower[2]))

        self.camera.set_upperHSV(self.upper)
        self.camera.set_lowerHSV(self.lower)

    def update_colorValue():
        pass

    def saveButton_clicked(self):
        lower_color = str(self.lower).translate({ord(i): None for i in '[]'})
        upper_color = str(self.upper).translate({ord(i): None for i in '[]'})

        print(lower_color, upper_color)
        self.db.hset(self.camera.name, self.camera.name +
                     '_upper', upper_color)
        self.db.hset(self.camera.name, self.camera.name +
                     '_lower', lower_color)
        print('Save button clicked')

    def set_HSV(self):
        # Horizontal Slider

        self.MAXIMUM_HSV_HUE = 180
        self.MAXIMUM_HSV_OTHER = 255
        self.MINIMUM_HSV = 0

        # upper minimum
        self.hSliderUH.setMinimum(self.MINIMUM_HSV)
        self.hSliderUS.setMinimum(self.MINIMUM_HSV)
        self.hSliderUV.setMinimum(self.MINIMUM_HSV)

        # lower minimum
        self.hSliderLH.setMinimum(self.MINIMUM_HSV)
        self.hSliderLS.setMinimum(self.MINIMUM_HSV)
        self.hSliderLV.setMinimum(self.MINIMUM_HSV)

        # upper maximum
        self.hSliderUH.setMaximum(self.MAXIMUM_HSV_HUE)
        self.hSliderUS.setMaximum(self.MAXIMUM_HSV_OTHER)
        self.hSliderUV.setMaximum(self.MAXIMUM_HSV_OTHER)

        # lower maximum
        self.hSliderLH.setMaximum(self.MAXIMUM_HSV_HUE)
        self.hSliderLS.setMaximum(self.MAXIMUM_HSV_OTHER)
        self.hSliderLV.setMaximum(self.MAXIMUM_HSV_OTHER)

    def activate_YUV_signal(self):
        # upper minimum
        self.hSliderUH.valueChanged.connect(self.update_hue_upperSlider)
        self.hSliderUS.valueChanged.connect(self.update_sat_upperSlider)
        self.hSliderUV.valueChanged.connect(self.update_val_upperSlider)

        # lower minimum
        self.hSliderLH.valueChanged.connect(self.update_hue_lowerSlider)
        self.hSliderLS.valueChanged.connect(self.update_sat_lowerSlider)
        self.hSliderLV.valueChanged.connect(self.update_val_lowerSlider)

    def update_hue_upperSlider(self):
        if self.hSliderUH.isEnabled():
            self.hSliderUH.setValue(self.hSliderUH.value())
            self.upperHue.setText(str(self.hSliderUH.value()))
            self.upper[0] = self.hSliderUH.value()
            self.camera.set_upperHSV(self.upper)

    def update_sat_upperSlider(self):
        if self.hSliderUS.isEnabled():
            self.hSliderUS.setValue(self.hSliderUS.value())
            self.upperSat.setText(str(self.hSliderUS.value()))
            self.upper[1] = self.hSliderUS.value()
            self.camera.set_upperHSV(self.upper)

    def update_val_upperSlider(self):
        if self.hSliderUV.isEnabled():
            self.hSliderUV.setValue(self.hSliderUV.value())
            self.upperVal.setText(str(self.hSliderUV.value()))
            self.upper[2] = self.hSliderUV.value()
            self.camera.set_upperHSV(self.upper)

    def update_hue_lowerSlider(self):
        if self.hSliderLH.isEnabled():
            self.hSliderLH.setValue(self.hSliderLH.value())
            self.lowerHue.setText(str(self.hSliderLH.value()))
            self.lower[0] = self.hSliderLH.value()
            self.camera.set_lowerHSV(self.lower)

    def update_sat_lowerSlider(self):
        if self.hSliderLS.isEnabled():
            self.hSliderLS.setValue(self.hSliderLS.value())
            self.lowerSat.setText(str(self.hSliderLS.value()))
            self.lower[1] = self.hSliderLS.value()
            self.camera.set_lowerHSV(self.lower)

    def update_val_lowerSlider(self):
        if self.hSliderLV.isEnabled():
            self.hSliderLV.setValue(self.hSliderLV.value())
            self.lowerVal.setText(str(self.hSliderLV.value()))
            self.lower[2] = self.hSliderLV.value()
            self.camera.set_lowerHSV(self.lower)

    def display_frame(self, img, win):
        """ Method untuk menampilkan frame yang diambil melalui video

        Args:
            img ('nparray'): frame yang diambil melalui kamera yang terpilih
        """
        qformat = QImage.Format_Indexed8
        if len(img.shape) == 3:
            if img.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888

        out_image = QImage(img, img.shape[1],
                           img.shape[0], img.strides[0], qformat)
        # BGR >> RGB
        out_image = out_image.rgbSwapped()

        # original image frame
        if win == 1:
            self.pixmap = QPixmap.fromImage(out_image)
            self.videoFrameOri.setPixmap(self.pixmap)
            self.videoFrameOri.setScaledContents(True)

        # HSV calibrated image frame
        elif win == 2:
            self.videoFrameHSV.setPixmap(QPixmap(out_image))
            self.videoFrameHSV.setScaledContents(True)

    def play_button_clicked(self):
        text = self.playButton.text()
        if text == "Play":
            self.start_timer(self.update_frame)
            self.start_timer(self.update_threshold)
            self.playButton.setText('Stop')
        elif text == 'Stop':
            self.stop_timer(self.update_frame)
            self.stop_timer(self.update_threshold)
            self.playButton.setText('Play')

    def update_frame(self):
        if self.camera is not None:
            self.frame = self.camera.get_frame()
            self.frame = imutils.resize(self.frame, height=480)
            self.display_frame(self.frame, 1)

    def update_threshold(self):
        if self.camera is not None:
            self.frame = self.camera.get_frame()
            self.frame = imutils.resize(self.frame, height=480)
            self.frame = self.camera.HSV_calibration(self.frame)
            self.display_frame(self.frame, 2)

    def change_camera(self):
        cam = self.cameraCBox.currentIndex()
        if cam == 0:
            self.camera = camera1
        elif cam == 1:
            self.camera = camera2

    def start_timer(self, callback):
        try:
            self.timer.timeout.disconnect(callback)
        except:
            pass
        self.timer.timeout.connect(callback)

    def stop_time(self, callback=None):
        if callback is None:
            self.timer.stop(())
        else:
            try:
                self.timer.timeout.disconnect(callback)
            except:
                pass


if __name__ == "__main__":

    database = rd.Redis(
        host='localhost',
        port=6379
    )
    try:
        app = QApplication(sys.argv)
        main_window = CalibrationGUI(database)
        main_window.setWindowTitle('Color Calibration App')

        main_window.show()
        sys.exit(app.exec())

    except Exception as e:
        print('Exiting Application')
