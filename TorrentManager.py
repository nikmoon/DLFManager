#
# -*- coding: utf-8 -*-
#

import errno
import sys
import os

from DLFManager.ConfigFile import MyLib, ConfigFile, APP_DIR, CFG_FILE_BASE_NAME, CFG_FILE_NAME

from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import (
	QListWidget, QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QColor, QListWidgetItem,
	QMessageBox, QIcon, QMainWindow
)
from PyQt4.QtCore import Qt



app = QtGui.QApplication(sys.argv)
MAIN_WINDOW_UI_FILE = os.path.join(APP_DIR, u"MainWindow.ui")
MAIN_WINDOW_ICON = QIcon(os.path.join(APP_DIR, u"qt-logo.png"))

ASK_SAVE_CFG_ON_EXIT = False


class MyListWidgetItem(QListWidgetItem):
	def __init__(self, text):
		QListWidgetItem.__init__(self, text)
		self.setTextColor(QColor(0, 0, 255))


class MainWindow(QtGui.QMainWindow):

	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		uic.loadUi(MAIN_WINDOW_UI_FILE, self)
		self.setWindowIcon(MAIN_WINDOW_ICON)
		self.configFile = ConfigFile()
		self.workingDirs = self.configFile.read()
		self.walkDir = APP_DIR

		self.action.triggered.connect(self.configFile.backup)
		self.action_2.triggered.connect(self.configFile.saveDefault)
		self.action_3.triggered.connect(self.close)

		# сохраняем дефолные обработчики
		self.lwMain.defKeyPressEvent = self.lwMain.keyPressEvent
		self.lwAux.defKeyPressEvent = self.lwAux.keyPressEvent

		# связываем QLineEdit с соответствующими QListWidget
		self.lwMain.bindedLineEdit = self.leMain
		self.lwAux.bindedLineEdit = self.leAux

		self.startManageWorkingDirs()


	# режим управления списком рабочих каталогов
	def startManageWorkingDirs(self):
		self.leMain.setText(u"Список рабочих каталогов:")
		self.lwMain.clear()
		self.lwMain.currentRowChanged.connect(self.onChangeCurrentWorkingDir)
		self.lwMain.keyPressEvent = self.onKeyPress_lwMain_manageWorkingDirs
		self.lwMain.setFocus()
		for wkDirName in sorted(self.workingDirs):
			item = MyListWidgetItem(wkDirName)
			if not self.workingDirs[wkDirName]["exists"]:
				item.setTextColor(QColor(255, 0, 0))
			self.lwMain.addItem(item)
		self.lwMain.setCurrentRow(0)


	def onChangeCurrentWorkingDir(self, rowNum):
		self.showWorkingDirContent(unicode(self.lwMain.item(rowNum).text()), self.lwAux)


	def showWorkingDirContent(self, wkDirName, lw):
		lw.bindedLineEdit.setText(wkDirName)
		lw.clear()
		wkDir = self.workingDirs[wkDirName]
		entryList = sorted(wkDir["new"] + wkDir["entries"].keys())
		for entry in entryList:
			item = MyListWidgetItem(entry)
			if entry in wkDir["entries"]:
				if not wkDir["entries"][entry]["exists"]:
					item.setTextColor(QColor(255, 0, 0))
			else:
				item.setTextColor(QColor(0, 150, 0))
			lw.addItem(item)


	def onKeyPress_lwMain_manageWorkingDirs(self, keyEvent):
		if keyEvent.key() == QtCore.Qt.Key_Return:		# переход в режим управления выбранным рабочим каталогом
			print u"Переходим в режим управления выбранным рабочим каталогом"
		elif keyEvent.key() == QtCore.Qt.Key_Insert:	# переходим в режим добавления нового рабочего каталога
			print u"Переходим в режим добавления нового рабочего каталога"
		elif keyEvent.key() == QtCore.Qt.Key_Delete:	# удаление каталога из списка рабочих
			print u"Удаление каталога из списка рабочих"
		self.lwMain.defKeyPressEvent(keyEvent)


	'''
	# Обработка нажатий клавиш в главном QListWidget в режиме управления рабочими каталогами
	def keyPressedOnManageWorkingDirsList(self, keyEvent):
		if keyEvent.key() == QtCore.Qt.Key_Escape:
			pass
		elif keyEvent.key() == QtCore.Qt.Key_Return:	# переходим к управлению текущим рабочим каталогом
			self.currentWkDir = unicode(self.lwMain.currentItem().text())
			if self.workingDirs[self.currentWkDir]["exists"]:
				QListWidget.keyPressEvent(self.lwMain, keyEvent)
				#self.lwMain.currentRowChanged.disconnect(self.showDirContent)
				self.lwMain.keyPressEvent = self.lwMain.defKeyPressEvent
				self.startManageSelectedWkDir()
				return
		elif keyEvent.key() == QtCore.Qt.Key_Insert:	# переходим к добавлению нового рабочего каталога
			self.lwMain.keyPressEvent = self.lwMain.defKeyPressEvent
			self.startAddingNewWorkingDir()
		else:
			pass
		QListWidget.keyPressEvent(self.lwMain, keyEvent)
	'''


	def startAddingNewWorkingDir(self):
		self.lwMain.currentRowChanged.disconnect(self.showDirContent)
		self.lwMain.keyPressEvent = self.keyPressedOnAddingNewWorkingDir
		self.lwMain.clear()
		self.showWalkDirEntries(self.lwMain)


	def keyPressedOnAddingNewWorkingDir(self, keyEvent):
		if keyEvent.key() == QtCore.Qt.Key_Return:		# переходим во вложенный каталог
			pathName = os.path.join(self.walkDir, unicode(self.lwMain.currentItem().text()))
			if os.path.isdir(pathName):
				self.walkDir = pathName
				self.showWalkDirEntries(self.lwMain)
		elif keyEvent.key() == QtCore.Qt.Key_Backspace:		# переходим в каталог выше
			self.walkDir = os.path.dirname(self.walkDir)
			self.showWalkDirEntries(self.lwMain)
		elif keyEvent.key() == QtCore.Qt.Key_Escape:		# отмена добавления нового рабочего каталога
			QListWidget.keyPressEvent(self.lwMain, keyEvent)
			self.lwMain.keyPressEvent = self.lwMain.defKeyPressEvent
			self.startManageWorkingDirs()
			return
		elif keyEvent.key() == QtCore.Qt.Key_Insert:	# переходим обратно к управлению списком рабочих каталогов
			wkDirName = os.path.join(self.walkDir, self.walkDir)
			if not wkDirName in self.workingDirs:
				QListWidget.keyPressEvent(self.lwMain, keyEvent)
				self.workingDirs[wkDirName] = {"entries": {}, "new": [], "exists": os.path.exists(wkDirName)}
				wkDir = self.workingDirs[wkDirName]
				wkDir["new"] = MyLib.getEntries(wkDirName)
				self.lwMain.keyPressEvent = self.lwMain.defKeyPressEvent
				self.startManageWorkingDirs()
				return
		QListWidget.keyPressEvent(self.lwMain, keyEvent)


	def showWalkDirEntries(self, lw):
		self.leMain.setText(self.walkDir)
		lw.clear()
		entryList = MyLib.getEntries(self.walkDir)
		for entry in entryList:
			item = QtGui.QListWidgetItem(entry)
			lw.addItem(item)



	def startManageSelectedWkDir(self):
		self.leMain.setText(self.currentWkDir)
		self.lwMain.clear()
		self.lwMain.currentRowChanged.connect(self.showLinksForEntry)
		self.lwMain.keyPressEvent = self.keyPressedOnManageSelectedWkDir
		self.fillListWidgetWithDirContent(self.currentWkDir, self.lwMain)
		self.lwMain.setCurrentRow(0)

	# обработка нажатия клавиш в режиме управления рабочим каталогом
	def keyPressedOnManageSelectedWkDir(self, keyEvent):
		if keyEvent.key() == QtCore.Qt.Key_Escape:		# возвращаемся к управлению рабочими каталогами
			self.lwMain.currentRowChanged.disconnect(self.showLinksForEntry)
			self.lwMain.keyPressEvent = self.lwMain.defKeyPressEvent
			self.startManageWorkingDirs()
		QListWidget.keyPressEvent(self.lwMain, keyEvent)


	def showLinksForEntry(self, rowNum):
		entryName = unicode(self.lwMain.item(rowNum).text())
		self.leAux.setText(u"Ссылки для {0}".format(entryName))
		self.lwAux.clear()
		if entryName in self.workingDirs[self.currentWkDir]["entries"]:
			for link in self.workingDirs[self.currentWkDir]["entries"][entryName]["links"]:
				item = QtGui.QListWidgetItem(link)
				self.lwAux.addItem(item)
			self.lwAux.addItem(QtGui.QListWidgetItem(u"Здесь должны быть ссылки"))


	def closeEvent(self, event):
		msgBox = QMessageBox(text = u"Действительно закрыть приложение?", parent = self)
		msgBox.setWindowTitle(u"Подтверждение")
		msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
		msgBox.setDefaultButton(QMessageBox.Yes)
		if msgBox.exec_() == QMessageBox.No:
			event.ignore()
		elif ASK_SAVE_CFG_ON_EXIT:
			msgBox.setText(u"Сохранить файл конфигурации?")
			msgBox.setDefaultButton(QMessageBox.Yes)
			if msgBox.exec_() == QMessageBox.Yes:
				self.configFile.save()
			event.accept()
		else:
			event.accept()


		
def main():
	mainWindow = MainWindow()
	mainWindow.show()
	sys.exit(app.exec_())


if __name__ == "__main__":
	main()
	pass


