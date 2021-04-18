"""
This is an entrance
"""
import logging
import sys

from PySide2 import QtCore, QtWidgets

import mainwindow
import res

"""
Logging Notice:
Task you want to perform                            |The best tool for the task
                                                    |
Display console output for ordinary usage of a      | print()
command line script or program                      |
                                                    |
                                                    |
Report events that occur during normal operation of | logging.info() (or logging.debug() for very detailed
a program (e.g. for status monitoring or fault      | output for diagnostic purposes)
investigation)                                      |
                                                    |
                                                    |
Issue a warning regarding a particular runtime event| warnings.warn() in library code if the issue is
                                                    | avoidable and the client application should be
                                                    | modified to eliminate the warning

                                                    | logging.warning() if there is nothing the client
                                                    | application can do about the situation, but the event
                                                    | should still be noted
                                                    |
                                                    |
Report an error regarding a particular runtime event| Raise an exception
                                                    |
                                                    |
Report suppression of an error without raising an   | logging.error(), logging.exception() or
exception (e.g. error handler in a long-running     | logging.critical() as appropriate for the specific
server process)                                     | error and application domain




DEBUG

Detailed information, typically of interest only when diagnosing problems.

INFO

Confirmation that things are working as expected.

WARNING

An indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk space low’). The software is still working as expected.

ERROR

Due to a more serious problem, the software has not been able to perform some function.

CRITICAL

A serious error, indicating that the program itself may be unable to continue running.

"""


res.qInitResources()


class CallHandler(logging.Handler):
    """
    A handler to call a function to send log
    """

    def emit(self, record):
        try:
            msg = self.format(record)
            w.log(msg)
            w.statusBar.showMessage(msg, 0)
        except Exception:
            self.handleError(record)


if __name__ == "__main__":
    print('Starting...')
    app = QtWidgets.QApplication(sys.argv)
    w = mainwindow.Wrapper()

    w.qapp = app

    w.logger = logging.getLogger(__name__)
    w.logger.setLevel(logging.DEBUG)  # You can change it

    # if you do not want to logging
    # Please uncomment the next line and comment addHandler
    # w.logger.addHandler(logging.NullHandler())

    chandler = CallHandler()
    shandler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        '[%(asctime)s] [%(name)s/%(levelname)s]: %(message)s')
    chandler.setFormatter(formatter)
    shandler.setFormatter(formatter)

    w.logger.addHandler(chandler)
    w.logger.addHandler(shandler)

    w.logger.info('Log start')
    translator = QtCore.QTranslator()
    translator.load(QtCore.QLocale(), "m3ueditor", ".", ":/lang",
                    ".qt.qm")  # Auto load translate file
    app.installTranslator(translator)
    w.retranslateUi(w)
    w.logger.info('Start UI')
    w.new()
    w.syncall()
    w.show()
    sys.exit(app.exec_())
