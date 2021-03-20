import io
import logging
import os

import chardet
from PyQt5 import QtCore, QtWidgets, QtGui

import diagwrapper
import m3u8wrapper
import m3ueditor
import pgdialog

encoding_list = ['utf-8', 'cp1252', 'latin_1',
                 'ascii', 'gb2312', 'gbk', 'gb18030']

def abs2rel(root: os.PathLike, path: os.PathLike) -> os.PathLike:
    return path.replace(root,'.',1)

def rel2abs(root: os.PathLike, path: os.PathLike):
    return path.replace('\\','/').replace('./',root,1)

def iterlwidget(widget: QtWidgets.QListWidget):
    for i in range(widget.count()):
        yield widget.item(i),i

class Wrapper(QtWidgets.QMainWindow, m3ueditor.Ui_MainWindow):
    def __init__(self, parent=None):
        super(QtWidgets.QMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.comboBox.addItems(encoding_list)
        self.lineEdit.setText(os.getcwd().replace('\\','/'))
        self.menuui_mbar_window.addActions([self.dockWidget_2.toggleViewAction(),self.dockWidget_3.toggleViewAction(),self.dockWidget_5.toggleViewAction(),self.dockWidget_6.toggleViewAction()])

    memoryio: io.StringIO = None
    fileio = ''
    logger: logging.Logger = None  # You must set this in main function

    def msyncg(self):  # memoryio -> gui
        self.plainTextEdit_source.setPlainText(self.memoryio.getvalue())
        self.setWindowTitle(
            self.tr('M3U Editor - {0}').format(self.fileio if self.fileio else 'Untitled'))

        m3u8 = m3u8wrapper.loads(self.memoryio.getvalue())
        self.listWidget.clear()
        self.listWidget.addItems(m3u8.filelist)
        self.checkBox.setChecked(m3u8.extm3u)

        self.plainTextEdit_source.setPlainText(self.memoryio.getvalue())

    def gsyncm(self):  # gui -> memory
        em3u = self.checkBox.isChecked()
        fl = []
        for i in range(self.listWidget.count()):
            fl.append(self.listWidget.item(i).text())
        self.setvalue(m3u8wrapper.M3U8(em3u, fl).dumps())

    def syncall(self):
        self.setnumber(self.listWidget.count())
        self.gsyncm()
        self.msyncg()
        # self.gsyncm()

    def browse_wdir(self):
        fdialog = QtWidgets.QFileDialog(self)
        fdialog.setFileMode(QtWidgets.QFileDialog.Directory)
        fileNames = []
        if fdialog.exec_():
            fileNames = fdialog.selectedFiles()
            self.lineEdit.setText(fileNames[0])
        del fdialog

    def addfiles(self):
        fdialog = QtWidgets.QFileDialog(self)
        fdialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        # fdialog.setNameFilter(self.tr("M3U (*.m3u *.m3u8)"))
        fileNames = []
        if fdialog.exec_():
            fileNames = fdialog.selectedFiles()
        if not self.checkBox_2.isChecked():
            fileNames = [abs2rel(self.lineEdit.text(),i) for i in fileNames]
        self.listWidget.addItems(fileNames)
        self.logger.info(f'Selected {len(fileNames)} file(s)')
        self.syncall()

    def addfolder(self):
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
                    flist += os.path.join(root, file)
                    self.logger.debug(file)
            if not self.checkBox_2.isChecked():
                fileNames = [abs2rel(self.lineEdit.text(),i) for i in fileNames]
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

    def change_extm3u(self, _pos: int=0):
        self.syncall()

    def setvalue(self, value=''):
        self.memoryio.seek(0)
        self.memoryio.truncate()
        self.memoryio.write(value)

    def loadfile(self, reload=False):
        fdialog = QtWidgets.QFileDialog(self)
        fdialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        fdialog.setNameFilter(
            self.tr("M3U (*.m3u *.m3u8);;All Files (*)"))
        fileNames = []
        if fdialog.exec_() and not reload:
            fileNames = fdialog.selectedFiles()
            if fileNames:
                self.logger.info('Loading file')
                self.fileio = fileNames[0]

        if fileNames or reload:
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
        dlg = diagwrapper.Wrapper(self)
        dlg.exec_()

    def log(self, text):
        self.plainTextEdit_log.setPlainText(
            self.plainTextEdit_log.toPlainText()+text+'\n')
    
    def customcontext_list(self, point: QtWidgets.QAction):
        curItem = self.listWidget.itemAt(point)
        if not curItem:
            return
        menu = QtWidgets.QMenu(self)
        open_action = QtWidgets.QAction(self.tr('Open'), self)
        del_action = QtWidgets.QAction(self.tr('Delete'),self)
        menu.addAction(open_action)
        menu.addAction(del_action)
        open_action.triggered.connect(self.open_slot)
        del_action.triggered.connect(self.rmedia)
        menu.exec(QtGui.QCursor.pos())
        del menu
        del open_action

    def open_slot(self):
        curItem = self.listWidget.currentItem()
        if not curItem:
            return
        filename = curItem.text()
        if not self.checkBox_2.isChecked():
            filename = filename.replace('.',self.lineEdit.text(),1)
        os.startfile(filename)

    def verify(self):
        if not self.listWidget.count():
            self.logger.warning("Playlist is empty. Add some things before check playlist.")
            return
        
        pgd = QtWidgets.QProgressDialog('Verifying playlist...', self.tr('Cancel'), 0, self.listWidget.count(),self)
        pgd.setAutoClose(False)
        pgd.setAutoReset(False)
        pgd.setMinimumDuration(2000)
        pgd.open(lambda : None)

        for i,index in iterlwidget(self.listWidget):
            pgd.setValue(index+1)
            path = i.text()
            if not self.checkBox_2.isChecked():
                path = rel2abs(self.lineEdit.text(), path)
            if not os.path.exists(i.text()):
                msgbox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, self.tr("Check Failed"), self.tr("Check Failed on file {0}: File not found").format(path), [QtWidgets.QMessageBox.Close],self)
                msgbox.exec()
                del msgbox
                break
        else:
            msgbox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, self.tr("Check Completed"), self.tr("Check Completed"), QtWidgets.QMessageBox.Close,self)
            msgbox.exec()
            del msgbox
        pgd.close()
        del pgd

    def play(self):
        if not self.listWidget.count():
            return

    def setnumber(self,n:int=0):
        n = int(n)
        digits = len(str(n))
        self.lcdNumber.setDigitCount(digits)
        self.lcdNumber.display(n)
