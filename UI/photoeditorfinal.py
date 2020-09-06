from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtGui import QIcon, QPixmap
import cv2
from logging.config import fileConfig
import logging
import numpy as np


# constants


class Ui_MainWindow2(object):
    def setup2(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(381, 305)
        MainWindow.setMinimumSize(QtCore.QSize(400, 330))
        MainWindow.setMaximumSize(QtCore.QSize(400, 330))
        MainWindow.setStyleSheet("background-color:rgb(255, 255, 255)")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 50, 181, 221))
        self.label.setStyleSheet("border:2px solid black")
        self.label.setObjectName("label")
        self.label.setScaledContents(True)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 10, 101, 16))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.buttonBox = QtWidgets.QDialogButtonBox(self.centralwidget)
        self.buttonBox.setGeometry(QtCore.QRect(220, 240, 141, 23))
        self.buttonBox.setStyleSheet("background-color:rgb(207, 235, 255);")
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        # self.buttonBox.clicked.connect(self.save_button)
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(220, 50, 141, 44))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_3 = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)

        # brightness slider
        self.horizontalSlider = QtWidgets.QSlider(self.widget)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.horizontalSlider.setMinimum(0)
        self.horizontalSlider.setMaximum(100)
        self.horizontalSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.horizontalSlider.setTickInterval(10)
        self.horizontalSlider.valueChanged[int].connect(self.brightness)

        self.verticalLayout.addWidget(self.horizontalSlider)
        self.widget1 = QtWidgets.QWidget(self.centralwidget)
        self.widget1.setGeometry(QtCore.QRect(220, 120, 141, 44))
        self.widget1.setObjectName("widget1")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget1)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_4 = QtWidgets.QLabel(self.widget1)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_2.addWidget(self.label_4)

        # contrast slider
        self.horizontalSlider_2 = QtWidgets.QSlider(self.widget1)
        self.horizontalSlider_2.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_2.setObjectName("horizontalSlider_2")
        self.horizontalSlider_2.setMinimum(0)
        self.horizontalSlider_2.setMaximum(100)
        self.horizontalSlider_2.setValue(10)
        self.horizontalSlider_2.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.horizontalSlider_2.setTickInterval(10)
        self.horizontalSlider_2.valueChanged[int].connect(self.Contrast)

        self.verticalLayout_2.addWidget(self.horizontalSlider_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def Contrast(self, value):
        photo_final = cv2.imread("photo_final.png")
        # read the image
        f = float(131 * (value + 127)) / (127 * (131 - value))
        alpha_c = f
        gamma_c = 127 * (1 - f)

        photo_final = cv2.addWeighted(photo_final, alpha_c, photo_final, 0, gamma_c)
        cv2.imwrite("contrast_image.png", photo_final)
        contrast_fctn = QPixmap("contrast_image.png")
        self.label.setPixmap(contrast_fctn)
        self.label.setScaledContents(True)

    def brightness(self, value):
        photo_final = cv2.imread("photo_final.png")
        image = cv2.cvtColor(photo_final, cv2.COLOR_BGR2HSV)

        increase = value
        print(value)
        v = image[:, :, 2]
        v = np.where(v <= 255 - increase, v + increase, 255)
        image[:, :, 2] = v

        image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
        cv2.imwrite("brightness_image.png", image)
        bright_fctn = QPixmap("brightness_image.png")
        self.label.setPixmap(bright_fctn)
        self.label.setScaledContents(True)

    def save_button(self):
        Bright_value = self.horizontalSlider.value()
        contrast_value = self.horizontalSlider_2.value()

        # Reading image
        image = cv2.imread("photo.png")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # brightness function
        v = image[:, :, 2]
        v = np.where(v <= 255 - Bright_value, v + Bright_value, 255)
        image[:, :, 2] = v

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", " "))
        self.label_2.setText(_translate("MainWindow", "Photo Editor"))
        self.label_3.setText(_translate("MainWindow", "Brightness:"))
        self.label_4.setText(_translate("MainWindow", "Contast:"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow2()
    ui.setup2(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
