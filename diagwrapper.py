from PyQt5 import QtWidgets

import aboutdiag


class Wrapper(QtWidgets.QDialog, aboutdiag.Ui_Dialog):
    def __init__(self, parent=None):
        super(QtWidgets.QDialog, self).__init__(parent)
        self.setupUi(self)
