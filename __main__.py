"""
This is an entrance
"""

from PyQt5 import QtWidgets, QtCore
import sys
import mainwindow
import res
import logging

class CallHandler(logging.Handler): # A handler to call a function to send log
    def emit(self, record):
        try:
            msg = self.format(record)
            w.log(msg)
            w.statusBar.showMessage(msg, -1)
        except Exception:
            self.handleError(record)

if __name__=="__main__":
    print('Starting...')
    app = QtWidgets.QApplication(sys.argv)
    w = mainwindow.Wrapper()

    w.logger = logging.getLogger(__name__)
    w.logger.setLevel(logging.DEBUG) # You can change it

    chandler = CallHandler()
    shandler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter('[%(asctime)s] [%(name)s/%(levelname)s]: %(message)s')
    chandler.setFormatter(formatter)
    shandler.setFormatter(formatter)

    w.logger.addHandler(chandler)
    w.logger.addHandler(shandler)

    w.logger.info('Log start')


    translator = QtCore.QTranslator()
    translator.load(QtCore.QLocale(), "untitled", ".", ":/lang", ".qt.qm") # Auto load translate file
    app.installTranslator(translator)
    w.retranslateUi(w)
    w.logger.info('Start UI')
    w.new()
    w.syncall()
    w.show()
    sys.exit(app.exec_())

