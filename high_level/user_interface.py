from PyQt4 import QtCore, QtGui
from demo import Ui_MainWindow

from image_processing import ImageProcessing
from factory import filter_factory

import cv2
import time
import threading
import ConfigParser

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class mainWin(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self,MainWindow, file_cfg):
        super(mainWin, self).__init__(parent = None)
        self.setupUi(MainWindow)
        self.get_config(file_cfg)
        self.setup_filter()
        self.set_menu_bar()
        self.__start_flag = threading.Event()
        self.__start_flag.clear()
        self.__ImageProcessing_thread = None
        self.__filter_manager_factory = None
        self.__tween_factory = None

    def get_config(self, file_cfg):
        self.__config = ConfigParser.ConfigParser()
        self.__config.read(file_cfg)

    def setup_filter(self):
        num_sec = 1
        y = 50
        while 1==1:
            if self.__config.has_section(str(num_sec)):
                name = self.__config.get(str(num_sec), 'filter_name')
                setattr(self, "is_"+name, QtGui.QCheckBox(self.tab1_scroll))
                getattr(self, "is_"+name).setObjectName(_fromUtf8("is_"+name))
                getattr(self, "is_"+name).setGeometry(QtCore.QRect(10, y, 150, 20))
                getattr(self, "is_"+name).setText(_translate("MainWindow", name, None))

                num_param = 1
                x = 200
                while self.__config.has_option(str(num_sec), "parameter"+str(num_param)+"_name"):
                    dial_name = name + "_" + self.__config.get(str(num_sec), "parameter" + str(num_param) + "_name")
                    setattr(self, dial_name, QtGui.QDial(self.tab1_scroll))
                    getattr(self, dial_name).setGeometry(QtCore.QRect(x, y-30, 50, 60))
                    getattr(self, dial_name).setObjectName(_fromUtf8(dial_name))
                    getattr(self, dial_name).setMaximum( self.__config.getint(str(num_sec), "parameter" + str(num_param) + "_max") )
                    getattr(self, dial_name).setMinimum( self.__config.getint(str(num_sec), "parameter" + str(num_param) + "_min") )

                    spin_name = dial_name + "_spin"
                    setattr(self, spin_name, QtGui.QSpinBox(self.tab1_scroll))
                    getattr(self, spin_name).setGeometry(QtCore.QRect(x+50, y-10, 50, 20))
                    getattr(self, spin_name).setObjectName(_fromUtf8(spin_name))
                    getattr(self, spin_name).setMaximum( self.__config.getint(str(num_sec), "parameter" + str(num_param) + "_max") )
                    getattr(self, spin_name).setMinimum( self.__config.getint(str(num_sec), "parameter" + str(num_param) + "_min") )

                    label_name = dial_name + "_label"
                    setattr(self, label_name, QtGui.QLabel(self.tab1_scroll))
                    getattr(self, label_name).setGeometry(QtCore.QRect(x, y+20, 46, 13))
                    getattr(self, label_name).setObjectName(_fromUtf8(label_name))
                    getattr(self, label_name).setText(_translate("MainWindow",  self.__config.get(str(num_sec), "parameter" + str(num_param) + "_name"), None))

                    QtCore.QObject.connect(getattr(self, spin_name), QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), getattr(self, dial_name).setValue)
                    QtCore.QObject.connect(getattr(self, dial_name), QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), getattr(self, spin_name).setValue)

                    x += 200
                    num_param += 1
            else:
                break
            num_sec += 1
            y += 75

    def set_menu_bar(self):
        self.actionUse_local_file.triggered.connect(self.create_project_from_local_file)

    def get_filter_manager_factory(self, filter_manager_factory):
        self.__filter_manager_factory = filter_manager_factory

    def get_tween_factory(self, tween_factory):
        self.__tween_factory = tween_factory

    def create_project_from_local_file(self):
        file_name = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
        self.__create_ImageProcessing_thread( str(file_name) ) 

    def __create_ImageProcessing_thread(self, file_name):
        self.__start_flag.clear()
        if self.__ImageProcessing_thread is not None:
            self.__ImageProcessing_thread.join()
        self.__ImageProcessing_thread = ImageProcessing(start_flag = self.__start_flag)
        self.__ImageProcessing_thread.recieve_image_from_filename(file_name)
        self.__ImageProcessing_thread.attach_filter( self.__filter_manager_factory(self) )
        self.__ImageProcessing_thread.attach_tween( self.__tween_factory(self) )
        
        self.__start_flag.set()
        self.__ImageProcessing_thread.start()

    def closeEvent(self, event):
        print "closing"
        self.__start_flag.clear()
        if self.__ImageProcessing_thread is not None:
            self.__ImageProcessing_thread.join()

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = mainWin(MainWindow, "development.cfg")
    ui.get_filter_manager_factory(filter_factory)
    ui.get_tween_factory(lambda x:x)
    MainWindow.show()
    sys.exit(app.exec_())