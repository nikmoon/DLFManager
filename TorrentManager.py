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
		#self.walkDir = APP_DIR
		self.walkDir = u"C:\\"

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


	def onChangeCurrentWorkingDir(self, rowNum):
		workingDirName = unicode(self.lwMain.item(rowNum).text())
		self.showWorkingDirContent(workingDirName, self.lwAux)


	def onKeyPress_lwMain_manageWorkingDirs(self, keyEvent):
		self.lwMain.defKeyPressEvent(keyEvent)

		if keyEvent.key() == QtCore.Qt.Key_Return:		# переход в режим управления выбранным рабочим каталогом
			if self.lwMain.currentRow() >= 0:
				self.selectedWorkingDir = unicode(self.lwMain.currentItem().text())
				if self.workingDirs[self.selectedWorkingDir]["exists"]:
					print u"Переходим в режим управления выбранным рабочим каталогом"
					print self.selectedWorkingDir
					self.startManageSelectedWorkingDir()
			
		elif keyEvent.key() == QtCore.Qt.Key_Insert:	# переходим в режим добавления нового рабочего каталога
			print u"Переходим в режим добавления нового рабочего каталога"
			self.startAddingNewWorkingDir()
		elif keyEvent.key() == QtCore.Qt.Key_Delete:	# удаление каталога из списка рабочих
			print u"Удаление каталога из списка рабочих"


	# Режим добавления нового рабочего каталога
	def startAddingNewWorkingDir(self):
		self.lwAux.setFocusPolicy(Qt.NoFocus)
		self.lwMain.currentRowChanged.disconnect(self.onChangeCurrentWorkingDir)
		self.lwMain.keyPressEvent = self.onKeyPress_lwMain_addingNewWorkingDir
		self.showDirContent(self.walkDir, self.lwMain)


	def onKeyPress_lwMain_addingNewWorkingDir(self, keyEvent):
		self.lwMain.defKeyPressEvent(keyEvent)

		if keyEvent.key() == QtCore.Qt.Key_Escape:		# возвращаемся в режим управления списком рабочих каталогов
			print u"Возвращаемся в режим управления списком рабочих каталогов"
			self.lwAux.setFocusPolicy(Qt.StrongFocus)
			self.startManageWorkingDirs()

		elif keyEvent.key() == QtCore.Qt.Key_Return:	# переход во вложенный каталог
			if self.lwMain.currentRow() >= 0:
				entryPath = os.path.join(self.walkDir, unicode(self.lwMain.currentItem().text()))
				if os.path.isdir(entryPath):
					self.walkDir = entryPath
					self.showDirContent(entryPath, self.lwMain)

		elif keyEvent.key() == QtCore.Qt.Key_Backspace:	# переход в каталог уровнем выше
			self.walkDir = os.path.dirname(self.walkDir)
			self.showDirContent(self.walkDir, self.lwMain)

		elif keyEvent.key() == QtCore.Qt.Key_Insert:	# текущий каталог выбран в качестве нового рабочего
			if self.walkDir in self.workingDirs:
				QMessageBox(text = u"Каталог {0} уже есть в списке рабочих".format(self.walkDir), parent = self).exec_()
			else:
				self.workingDirs[self.walkDir] = {"entries": {}, "new": MyLib.getEntries(self.walkDir), "exists": True}
				print u"Возвращаемся в режим управления списком рабочих каталогов"
				self.lwAux.setFocusPolicy(Qt.StrongFocus)
				self.startManageWorkingDirs()


	def startManageSelectedWorkingDir(self):
		pass

	'''
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
	'''


	# Вывод содержимого заданного каталога в заданном виджете QListWidget
	def showDirContent(self, dirPath, lw):
		lw.bindedLineEdit.setText(dirPath)
		lw.clear()
		entryList = sorted(MyLib.getEntries(dirPath))
		for entry in entryList:
			item = MyListWidgetItem(entry)
			lw.addItem(item)


	# Вывод данных рабочего каталога wkDirName в виджете lw (QListWidget)
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


	# Достаем пользователя при закрытии приложения
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


