import ui_pgdialog
from PyQt5 import QtCore, QtGui, QtWidgets


class pgdialog(QtWidgets.QDialog, ui_pgdialog.Ui_Dialog):
    def __init__(self, parent=None):
        super(QtWidgets.QDialog, self).__init__(parent)
        self.setupUi(self)

    def setmax(self, n: int = 0):
        self.progressBar.setMaximum(n)

    def setmin(self, n: int = 0):
        self.progressBar.setMinimum(n)

    def setvalue(self, n: int = 0):
        self.progressBar.setValue(n)

    def log(self, s: str = ''):
        self.plainTextEdit.setPlainText(
            self.plainTextEdit.toPlainText()+s+'\n')
