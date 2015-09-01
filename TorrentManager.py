# -*- coding: utf-8 -*-

import errno
import sys
import os
import types
from DLFManager import MyLib
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import QListWidget, QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QColor

from DLFManager.ConfigFile import ConfigFile
from DLFManager import APP_DIR, CFG_FILE_BASE_NAME, CFG_FILE_NAME


"""
-----------------------------------------------------
Алгоритм работы программы
-----------------------------------------------------
	1.	Инициализация.
	2.	Чтение конфигурационного файла.
	3.	Управление списком рабочих каталогов:
		а. добавление нового каталога в список рабочих
		б. удаление существующего каталога из списка рабочих
		в. выбор каталога для работы
	4.	Управление рабочим каталогом.
	5.	Сохранение несохраненных изменений.
	6.	Выход.
"""



class MainWindow(QtGui.QMainWindow):

	def __init__(self, qApp):
		self.qApp = qApp
		QtGui.QMainWindow.__init__(self)
		uic.loadUi(os.path.join(APP_DIR, u"MainWindow.ui"), self)
		self.setWindowIcon()
		self.configFile = ConfigFile()
		self.workingDirs = self.configFile.read()

		self.action.triggered.connect(self.configFile.backup)
		self.action_2.triggered.connect(self.configFile.saveDefault)

		self.walkDir = APP_DIR

		self.startManageWorkingDirs()

	# переходим к управлению списком рабочих каталогов
	def startManageWorkingDirs(self):
		self.leMain.setText(u"Управление списком рабочих каталогов")
		self.lwMain.clear()

		self.lwMain.currentRowChanged.connect(self.showDirContent)
		self.lwMain.defKeyPressEvent = self.lwMain.keyPressEvent
		self.lwMain.keyPressEvent = self.keyPressedOnManageWorkingDirsList

		self.lwMain.setFocus()

		for wkDirName in self.workingDirs:
			item = QtGui.QListWidgetItem(wkDirName)
			if not self.workingDirs[wkDirName]["exists"]:
				item.setTextColor(QColor(255, 0, 0))
			self.lwMain.addItem(item)
		self.lwMain.setCurrentRow(0)


	def showDirContent(self, rowNum):
		wkDirName = unicode(self.lwMain.item(rowNum).text())
		self.leAux.setText(wkDirName)
		self.lwAux.clear()
		self.fillListWidgetWithDirContent(wkDirName, self.lwAux)


	def fillListWidgetWithDirContent(self, dirName, lWidget):
		for entry in self.workingDirs[dirName]["new"]:	# неучтенные элементы в рабочем каталоге
			item = QtGui.QListWidgetItem(entry)
			item.setTextColor(QColor(0, 150, 0))
			lWidget.addItem(item)
		for entry in self.workingDirs[dirName]["entries"]:	# учтенные элементы
			item = QtGui.QListWidgetItem(entry)
			if not self.workingDirs[dirName]["entries"][entry]["exists"]:		# учтенный элемент уже не существует
				item.setTextColor(QColor(255, 0, 0))
			lWidget.addItem(item)
		

	# Обработка нажатий клавиш в главном QListWidget в режиме управления рабочими каталогами
	def keyPressedOnManageWorkingDirsList(self, keyEvent):
		if keyEvent.key() == QtCore.Qt.Key_Escape:
			pass
		elif keyEvent.key() == QtCore.Qt.Key_Return:	# переходим к управлению текущим рабочим каталогом
			self.currentWkDir = unicode(self.lwMain.currentItem().text())
			if self.workingDirs[self.currentWkDir]["exists"]:
				QListWidget.keyPressEvent(self.lwMain, keyEvent)
				self.lwMain.currentRowChanged.disconnect(self.showDirContent)
				self.lwMain.keyPressEvent = self.lwMain.defKeyPressEvent
				self.startManageSelectedWkDir()
				return
		elif keyEvent.key() == QtCore.Qt.Key_Insert:	# переходим к добавлению нового рабочего каталога
			self.lwMain.keyPressEvent = self.lwMain.defKeyPressEvent
			self.startAddingNewWorkingDir()
		else:
			pass
		QListWidget.keyPressEvent(self.lwMain, keyEvent)


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

	
	def keyPressedOnManageSelectedWkDir(self, keyEvent):
		if keyEvent.key() == QtCore.Qt.Key_Escape:		# возвращаемся к управлению рабочими каталогами
			QListWidget.keyPressEvent(self.lwMain, keyEvent)
			self.lwMain.currentRowChanged.disconnect(self.showLinksForEntry)
			self.lwMain.keyPressEvent = self.lwMain.defKeyPressEvent
			self.startManageWorkingDirs()
			return
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

	def setWindowIcon(self):
		myIcon = QtGui.QIcon(os.path.join(APP_DIR, u"qt-logo.png"))
		QtGui.QMainWindow.setWindowIcon(self, myIcon)		

	"""
	пример использования палитры
	def initialize(self):
		palette = self.lwAux.palette()
		palette.setColor(QtGui.QPalette.Text, QColor(0,255,0))
		self.lwAux.setPalette(palette)
	"""

		
def main():
	app = QtGui.QApplication(sys.argv)
	mainWindow = MainWindow(app)
	mainWindow.show()
	sys.exit(app.exec_())


if __name__ == "__main__":
	main()
	pass


