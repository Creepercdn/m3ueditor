import io
import logging
import os
import re
import subprocess
import urllib
import urllib.request
import urllib.error

import chardet
import qdarkstyle
from PySide2 import QtCore, QtGui, QtUiTools, QtWidgets
from PySide2.QtUiTools import loadUiType

import m3u8wrapper
import res

res.qInitResources()

encoding_list = ['utf-8', 'cp1252', 'latin_1',
                 'ascii', 'gb2312', 'gbk', 'gb18030']


def abs2rel(root: os.PathLike, path: os.PathLike) -> os.PathLike:
    return path.replace(root, '.', 1)


def rel2abs(root: os.PathLike, path: os.PathLike):
    return path.replace('\\', '/')+('' if (str(path).endswith('\\') or str(path).endswith('/')) else '/.').replace('./', root, 1)


def iterlwidget(widget: QtWidgets.QListWidget):
    for i in range(widget.count()):
        yield widget.item(i), i

class playThread(QtCore.QThread):
    update = QtCore.Signal(int)

    def __init__(self, parent=None, playlist: list = None):
        super().__init__()
        self.playlist = playlist
        self.stopflag = False
        self.parent = parent
        self.process: subprocess.Popen = None

    def stop(self):
        self.parent.logger.info('Stoping Player Thread (Force Quit)')
        self.stopflag = True
        self.process.terminate()
        self.terminate()

    def run(self):
        index = 0
        for i in self.playlist:
            if self.stopflag:
                break
            self.update.emit(index+1)
            self.process = subprocess.Popen(
                [os.path.abspath("./ffplay/ffplay.exe"), "-showmode", "0", "-autoexit", i])
            self.process.wait()
            index += 1
        self.update.emit(0)
        # self.sleep(1)
        self.parent.logger.info('Exiting Player Thread (Done play)')


# wmainfileobj = QtCore.QFile(':/ui/m3ueditor.ui')
# wmainfileobj.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)
uimain, mainbaseclass = loadUiType('m3ueditor.ui')
# wmainfileobj.close()


class Wrapper(mainbaseclass, uimain):
    def __init__(self, parent=None):
        super().__init__(parent)
        # a = uic.loadUi(fileobj, self)
        self.setupUi(self)

        self.comboBox.addItems(encoding_list)
        self.lineEdit.setText(os.getcwd().replace('\\', '/'))
        self.menuui_mbar_window.addActions([self.dockWidget_2.toggleViewAction(), self.dockWidget_3.toggleViewAction(
        ), self.dockWidget_5.toggleViewAction(), self.dockWidget_6.toggleViewAction()])
        self.bar = QtWidgets.QProgressBar()
        self.bar.setFormat("%v/%m (%p%)")
        self.bar.setValue(0)
        self.bar.setRange(0, 100)

    memoryio: io.StringIO = None
    fileio = ''
    logger: logging.Logger = None  # You must set this in main function
    qapp: QtWidgets.QApplication = None

    def msyncg(self):  # memoryio -> gui
        self.logger.debug('Syncing memoryio -> GUI')
        self.plainTextEdit_source.setPlainText(self.memoryio.getvalue())
        self.setWindowTitle(
            self.tr('M3U Editor - {0}').format(self.fileio if self.fileio else 'Untitled'))

        m3u8 = m3u8wrapper.loads(self.memoryio.getvalue())
        self.listWidget.clear()
        self.listWidget.addItems(m3u8.filelist)
        self.checkBox.setChecked(m3u8.extm3u)

        self.plainTextEdit_source.setPlainText(self.memoryio.getvalue())
        self.setnumber(self.listWidget.count())

    def gsyncm(self):  # gui -> memory
        self.logger.debug('Syncing GUI -> memoryio')
        em3u = self.checkBox.isChecked()
        fl = []
        for i in range(self.listWidget.count()):
            fl.append(self.listWidget.item(i).text())
        self.setvalue(m3u8wrapper.M3U8(em3u, fl).dumps())

    def syncall(self):
        self.logger.debug('Syncing all')
        self.gsyncm()
        self.msyncg()
        # self.gsyncm()

    def browse_wdir(self):
        self.logger.debug('Start working dir browser window')
        fdialog = QtWidgets.QFileDialog(self)
        fdialog.setFileMode(QtWidgets.QFileDialog.Directory)
        fileNames = []
        if fdialog.exec_():
            fileNames = fdialog.selectedFiles()
            self.lineEdit.setText(fileNames[0])
        del fdialog

    def addfiles(self):
        self.logger.debug('Start add files browser window')
        fdialog = QtWidgets.QFileDialog(self)
        fdialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        # fdialog.setNameFilter(self.tr("M3U (*.m3u *.m3u8)"))
        fileNames = []
        if fdialog.exec_():
            fileNames = fdialog.selectedFiles()
        if not self.checkBox_2.isChecked():
            fileNames = [abs2rel(self.lineEdit.text(), i) for i in fileNames]
        self.listWidget.addItems(fileNames)
        self.logger.info(f'Selected {len(fileNames)} file(s)')
        self.syncall()

    def addfolder(self):
        self.logger.debug('Start add folder browser window')
        flist = []
        fdialog = QtWidgets.QFileDialog(self)
        fdialog.setFileMode(QtWidgets.QFileDialog.Directory)
        fileNames = None
        if fdialog.exec_():
            fileNames = fdialog.selectedFiles()
        if fileNames:
            self.logger.info('Start os.walk()')
            for root, _, files in os.walk(fileNames[0]):
                flist = []
                for file in files:
                    flist.append(os.path.join(root, file))
                    self.logger.debug(file)
            if not self.checkBox_2.isChecked():
                fileNames = [abs2rel(self.lineEdit.text(), i)
                             for i in fileNames]
            self.listWidget.addItems(flist)
            self.logger.info(f'Added {len(flist)} file(s)')
        self.syncall()
        del fdialog

    def rmedia(self):
        self.logger.info(
            f'Delete Selected {len(self.listWidget.selectedItems())} file(s)')
        for i in self.listWidget.selectedItems():
            self.listWidget.takeItem(self.listWidget.row(i))
            self.listWidget.removeItemWidget(i)
        self.syncall()

    def change_extm3u(self, _pos: int = 0):
        self.syncall()

    def setvalue(self, value=''):
        self.logger.debug('Changing memoryio content')
        self.memoryio.seek(0)
        self.memoryio.truncate()
        self.memoryio.write(value)

    def loadfile(self, reload=False):
        self.logger.debug('Calling Loading file function')
        fdialog = QtWidgets.QFileDialog(self)
        fdialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        fdialog.setNameFilter(
            self.tr("M3U (*.m3u *.m3u8);;All Files (*)"))
        fileNames = []
        if not self.fileio:
            fdialog.exec_()
        fileNames = fdialog.selectedFiles()
        if fileNames:
            self.logger.info('Loading file')
            self.fileio = fileNames[0]

        if fileNames or reload:
            self.logger.debug('Loading file {0}'.format(self.fileio))
            try:
                f = open(self.fileio, 'rb')
                c = f.read()
                codec = chardet.detect(c)
                self.logger.info(f'Detect file coding: {repr(codec)}')
                self.setvalue(
                    c.decode("utf-8" if not codec['encoding'] else codec['encoding']))
                self.comboBox.setEditText(
                    "utf-8" if not codec['encoding'] else codec['encoding'])
            except Exception:
                self.logger.exception('Failed to open file: ')
            finally:
                f.close()
            self.msyncg()

    def reloadfile(self):
        self.logger.info('Reloading file')
        if self.fileio:
            self.loadfile(True)
        else:
            self.logger.warning('Not loaded a file.')
            self.logger.warning('Please load a file first.')

    def save(self):
        self.logger.info('Saving')
        if not self.fileio:
            self.logger.debug('save() -> saveto()')
            self.saveto()
        else:
            self.logger.info('StringIO in memory -> file')
            try:
                f = open(self.fileio, 'w', encoding=(
                    "utf-8" if not self.comboBox.currentText() else self.comboBox.currentText()))
                f.truncate()
                f.write(self.memoryio.getvalue())
            except Exception:
                self.logger.exception('Failed to save file: ')

    def saveto(self):
        fdialog = QtWidgets.QFileDialog(self)
        fdialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        fdialog.setNameFilter(self.tr("M3U (*.m3u *.m3u8);;All Files (*)"))
        fileNames = []
        if fdialog.exec_():
            fileNames = fdialog.selectedFiles()

        if fileNames:
            self.logger.info('Setted file name')
            self.fileio = fileNames[0]
            self.logger.debug('saveto() -> save()')
            self.save()
            self.msyncg()

    def new(self):
        if not self.memoryio:
            self.logger.info('Create StringIO in memory')
            self.memoryio = io.StringIO()
        else:
            self.logger.info('Empty StringIO in memory')
            self.setvalue()
        self.fileio = ''
        self.msyncg()

    def openabout(self):
        self.logger.info('Opening About window')
        fileobj = QtCore.QFile(':/ui/aboutdiag.ui')
        fileobj.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)
        loader = QtUiTools.QUiLoader()
        diag = loader.load(fileobj, self)
        diag.show()
        diag.exec()
        del diag

    def log(self, text):
        self.plainTextEdit_log.setPlainText(
            self.plainTextEdit_log.toPlainText()+text+'\n')

    def customcontext_list(self, point: QtWidgets.QAction):
        curItem = self.listWidget.itemAt(point)
        if not curItem:
            return
        menu = QtWidgets.QMenu(self)
        open_action = QtWidgets.QAction(self.tr('Open'), self)
        del_action = QtWidgets.QAction(self.tr('Delete'), self)
        menu.addAction(open_action)
        menu.addAction(del_action)
        open_action.triggered.connect(self.open_slot)
        del_action.triggered.connect(self.rmedia)
        menu.exec_(QtGui.QCursor.pos())
        del menu
        del open_action

    def open_slot(self):
        curItem = self.listWidget.currentItem()
        if not curItem:
            return
        filename = curItem.text()
        if not self.checkBox_2.isChecked():
            filename = filename.replace('.', self.lineEdit.text(), 1)
        os.startfile(filename)

    def verify(self):
        if not self.listWidget.count():
            self.logger.warning(
                "Playlist is empty. Add some things before check playlist.")
            return

        self.logger.info('Start checking...')

        pgd = QtWidgets.QProgressDialog(
            'Verifying playlist...', self.tr('Cancel'), 0, 0, self)
        pgd.setBar(self.bar)
        pgd.setRange(0, self.listWidget.count())
        pgd.setAutoClose(False)
        pgd.setAutoReset(False)
        pgd.setMinimumDuration(2000)
        pgd.open()

        for i, index in iterlwidget(self.listWidget):
            pgd.setValue(index+1)
            path = i.text()
            failed = False
            errormsg = ''
            if re.match(r'^https?:/{2}\w.+$', path):
                req = urllib.request.Request(path, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.57'})
                try:
                    rep = urllib.request.urlopen(req)
                except urllib.error.URLError as e:
                    self.logger.log(f'Failed on check URL {path}, because {str(e.reason)}')
                    errormsg = 'Failed on check URL {0}, because %s, error type: %s' % (str(e.reason), repr(e))

            else:
                if not self.checkBox_2.isChecked():
                    path = rel2abs(self.lineEdit.text(), path)
                failed = not os.path.exists(path)
                errormsg = 'Check failed! File not found at file {0}'
            

            if failed:
                self.logger.info(
                    errormsg.format(i.text()+f' ({path})'))
                msgbox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, self.tr("Check Failed"), errormsg.format(path), QtWidgets.QMessageBox.Close, self)
                msgbox.exec()
                del msgbox
                break
        else:
            msgbox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, self.tr(
                "Check Completed"), self.tr("Check Completed"), QtWidgets.QMessageBox.Close, self)
            msgbox.exec()
            del msgbox
        pgd.close()
        del pgd

    def play(self):
        if not self.listWidget.count():
            self.logger.warning(
                "Playlist is empty. Add some things before check playlist.")
            return

        try:
            if self.player.isRunning():
                msgbox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, self.tr("Warning"), self.tr(
                    "Warning: Multi player will raise fatal unrecover error."), QtWidgets.QMessageBox.Close, self)
                msgbox.exec()
                return
        except AttributeError:
            pass

        items = []
        for i, _ in iterlwidget(self.listWidget):
            path = i.text()
            if not self.checkBox_2.isChecked():
                path = rel2abs(self.lineEdit.text()+'/', path)
            items.append(path)

        def update(a: int = 0):
            pgd.setValue(a)

        pgd = QtWidgets.QProgressDialog(
            'Playing playlist...', self.tr('Stop'), 0, 0)
        pgd.setBar(self.bar)
        pgd.setRange(0, len(items))
        pgd.setAutoClose(False)
        pgd.setAutoReset(False)
        pgd.setMinimumDuration(2000)
        self.player = playThread(self, items)
        pgd.canceled.connect(self.player.stop)
        self.player.update.connect(update)
        pgd.open()

        self.logger.info('Start Player thread')
        self.player.start()

    def setnumber(self, n: int = 0):
        n = int(n)
        digits = len(str(n))
        self.lcdNumber.setDigitCount(digits)
        self.lcdNumber.display(n)

    def addurl(self):
        self.logger.debug('Start QInputDialog')
        dialog = QtWidgets.QInputDialog(self)
        content, d = dialog.getText(dialog, self.tr("Add URL"), "URL:")
        if d and content:
            self.listWidget.addItem(content.strip())
            self.logger.info(f'Add an URL')
            self.syncall()

    def startfile(self):
        if self.fileio:
            os.startfile(self.fileio)
        else:
            self.logger.warning('File IO not seted. Please load a file first.')

    def startdir(self):
        if self.fileio:
            os.startfile(os.path.dirname(self.fileio))
        else:
            self.logger.warning('File IO not seted. Please load a file first.')

    def setstyle(self, a: bool):
        if a:
            self.qapp.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
        else:
            self.qapp.setStyleSheet('')
