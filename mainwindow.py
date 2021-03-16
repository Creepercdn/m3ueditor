import io
import logging
import os

import chardet
from PyQt5 import QtCore, QtWidgets

import diagwrapper
import m3u8wrapper
import m3ueditor

tr = QtCore.QCoreApplication.translate
encoding_list = ['utf-8', 'cp1252', 'latin_1',
                 'ascii', 'gb2312', 'gbk', 'gb18030']


class Wrapper(QtWidgets.QMainWindow, m3ueditor.Ui_MainWindow):
    def __init__(self, parent=None):
        super(QtWidgets.QMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.comboBox.addItems(encoding_list)

    memoryio: io.StringIO = None
    fileio = ''
    logger: logging.Logger = None  # You must set this in main function

    def msyncg(self):  # memoryio -> gui
        self.plainTextEdit_source.setPlainText(self.memoryio.getvalue())
        self.setWindowTitle(
            tr('MainWindow', 'M3U Editor - {0}').format(self.fileio if self.fileio else 'Untitled'))

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
        self.gsyncm()
        self.msyncg()
        # self.gsyncm()

    def addfiles(self):
        fdialog = QtWidgets.QFileDialog(self)
        fdialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        # fdialog.setNameFilter(self.tr("M3U (*.m3u *.m3u8)"))
        fileNames = []
        if fdialog.exec_():
            fileNames = fdialog.selectedFiles()
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
                for file in files:
                    flist += os.path.join(root, file)
                    self.logger.debug(file)
            self.listWidget.addItems(flist)
            self.logger.info(f'Added {len(flist)} file(s)')
        self.syncall()

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
            tr("MainWindow", "M3U (*.m3u *.m3u8);;All Files (*)"))
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
