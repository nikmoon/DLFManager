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
		self.lwMain.currentRowChanged.connect(self.onChangeCurrentWorkingDir)
		self.lwMain.keyPressEvent = self.onKeyPress_lwMain_manageWorkingDirs
		self.showWorkingDirs(self.lwMain)
		self.lwMain.setFocus()


	def onChangeCurrentWorkingDir(self, rowNum):
		if rowNum >= 0:
			print "onChangeCurrentWorkingDir called, rowNum = {0}".format(rowNum)
			workingDirName = unicode(self.lwMain.item(rowNum).text())
			self.showWorkingDirContent(workingDirName, self.lwAux)


	def onKeyPress_lwMain_manageWorkingDirs(self, keyEvent):
		self.lwMain.defKeyPressEvent(keyEvent)
		key = keyEvent.key()

		if key == Qt.Key_Return:				# переход в режим управления выбранным рабочим каталогом
			if self.lwMain.currentRow() >= 0:
				self.selectedWorkingDir = unicode(self.lwMain.currentItem().text())
				if self.workingDirs[self.selectedWorkingDir]["exists"]:
					print u"Переходим в режим управления выбранным рабочим каталогом"
					print self.selectedWorkingDir
					self.lwMain.currentRowChanged.disconnect(self.onChangeCurrentWorkingDir)
					self.lwMain.keyPressEvent = self.lwMain.defKeyPressEvent
					self.startManageSelectedWorkingDir()
			
		elif key == Qt.Key_Insert:				# переходим в режим добавления нового рабочего каталога
			print u"Переходим в режим добавления нового рабочего каталога"
			self.lwMain.currentRowChanged.disconnect(self.onChangeCurrentWorkingDir)
			self.lwMain.keyPressEvent = self.lwMain.defKeyPressEvent
			self.startAddingNewWorkingDir()

		elif key == Qt.Key_Delete:				# удаление каталога из списка рабочих
			if self.lwMain.count():
				self.selectedWorkingDir = unicode(self.lwMain.currentItem().text())
				print u"Удаление каталога из списка рабочих: {0}".format(self.selectedWorkingDir)
				del self.workingDirs[self.selectedWorkingDir]
				self.configFile.needToSave = True
				self.showWorkingDirs(self.lwMain)


	# Режим добавления нового рабочего каталога
	def startAddingNewWorkingDir(self):
		self.lwAux.setDisabled(True)
		self.lwMain.keyPressEvent = self.onKeyPress_lwMain_addingNewWorkingDir
		self.showDirContent(self.walkDir, self.lwMain)
		self.lwMain.setCurrentRow(0)


	def onKeyPress_lwMain_addingNewWorkingDir(self, keyEvent):
		self.lwMain.defKeyPressEvent(keyEvent)

		if keyEvent.key() == QtCore.Qt.Key_Escape:		# возвращаемся в режим управления списком рабочих каталогов
			print u"Возвращаемся в режим управления списком рабочих каталогов"
			self.lwAux.setEnabled(True)
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
				self.configFile.needToSave = True
				print u"Возвращаемся в режим управления списком рабочих каталогов"
				self.lwAux.setEnabled(True)
				self.startManageWorkingDirs()


	def startManageSelectedWorkingDir(self, setRow = None):
		self.lwAux.clear()
		self.showWorkingDirContent(self.selectedWorkingDir, self.lwMain)
		self.lwMain.currentRowChanged.connect(self.onCurrentEntryChanged)
		self.lwAux.currentRowChanged.connect(self.onCurrentLinkChanged)
		self.lwMain.keyPressEvent = self.onKeyPress_lwMain_manageSelectedWorkingDir
		self.lwAux.keyPressEvent = self.onKeyPress_lwAux_manageSelectedWorkingDir
		if not setRow is None:
			self.lwMain.setCurrentRow(setRow)


	def onCurrentEntryChanged(self, rowNum):
		if rowNum >= 0:
			entryName = unicode(self.lwMain.currentItem().text())
			self.showLinks(entryName, self.lwAux)


	def onCurrentLinkChanged(self, rowNum):
		print rowNum


	def onKeyPress_lwMain_manageSelectedWorkingDir(self, keyEvent):
		self.lwMain.defKeyPressEvent(keyEvent)
		key = keyEvent.key()

		if key == Qt.Key_Escape:			# возвращаемся к управлению списком рабочих каталогов
			self.lwMain.currentRowChanged.disconnect(self.onCurrentEntryChanged)
			self.lwAux.currentRowChanged.disconnect(self.onCurrentLinkChanged)
			self.lwMain.keyPressEvent = self.lwMain.defKeyPressEvent
			self.lwAux.keyPressEvent = self.lwAux.defKeyPressEvent
			self.startManageWorkingDirs()

		elif key == Qt.Key_Return:
			self.lwAux.setFocus()


	def onKeyPress_lwAux_manageSelectedWorkingDir(self, keyEvent):
		self.lwAux.defKeyPressEvent(keyEvent)
	
		key = keyEvent.key()

		if key == Qt.Key_Escape:			# возвращаем фокус главному виджету
			self.lwMain.setEnabled(True)
			self.lwMain.setFocus()

		elif key == Qt.Key_Insert:			# добавляем новую ссылку для выбранного элемента 
			if self.lwMain.currentRow() >= 0:
				self.selectedEntryName = unicode(self.lwMain.currentItem().text())
				self.selectedEntryRow = self.lwMain.currentRow()
				self.lwMain.setDisabled(True)
				self.lwMain.currentRowChanged.disconnect(self.onCurrentEntryChanged)
				self.lwAux.currentRowChanged.disconnect(self.onCurrentLinkChanged)
				self.lwAux.keyPressEvent = self.lwAux.defKeyPressEvent
				self.startNewLinkMaking()


	def startNewLinkMaking(self):
		self.lwAux.keyPressEvent = self.onKeyPress_lwAux_NewLinkMaking
		self.showDirContent(self.walkDir, self.lwAux)

	def onKeyPress_lwAux_NewLinkMaking(self, keyEvent):
		self.lwAux.defKeyPressEvent(keyEvent)
		key = keyEvent.key()

		if key == Qt.Key_Escape:				# возвращаемся к управлению выбранным рабочим каталогом
			self.lwAux.keyPressEvent = self.lwAux.defKeyPressEvent
			self.lwMain.setEnabled(True)
			self.lwMain.setFocus()
			self.startManageSelectedWorkingDir(self.selectedEntryRow)

		elif key == Qt.Key_Return:				# переход во вложенный каталог
			print self.lwAux.currentRow()
			if self.lwAux.currentRow() >= 0:
				entryPath = os.path.join(self.walkDir, unicode(self.lwAux.currentItem().text()))
				if os.path.isdir(entryPath):
					self.walkDir = entryPath
					self.showDirContent(entryPath, self.lwAux)

		elif key == Qt.Key_Backspace:			# переход в каталог уровнем выше
			self.walkDir = os.path.dirname(self.walkDir)
			self.showDirContent(self.walkDir, self.lwAux)

		
		elif key == Qt.Key_Insert:				# выбран каталог, в котором будет создана ссылкa
			linkDest = os.path.join(self.walkDir, self.selectedEntryName)
			if not os.path.exists(linkDest):
				linkSrc = os.path.join(self.selectedWorkingDir, self.selectedEntryName)
				if os.path.isfile(linkSrc):
					os.link(linkSrc, linkDest)
				elif os.path.isdir(linkSrc):
					os.symlink(linkSrc, linkDest)
				else:
					print u"Неизвестный тип элемента каталога с именем {0}".format(linkSrc)
					return

				wkDir = self.workingDirs[self.selectedWorkingDir]
				self.configFile.needToSave = True
				if self.selectedEntryName in wkDir["new"]:
					wkDir["new"].remove(self.selectedEntryName)
					wkDir["entries"][self.selectedEntryName] = {"links": [], "exists": True}
				wkDir["entries"][self.selectedEntryName]["links"].append(linkDest)
				self.showDirContent(self.walkDir, self.lwAux)


	def showLinks(self, entryName, lw):
		lw.bindedLineEdit.setText(u"Ссылки на \"{0}\":".format(entryName))
		lw.clear()
		if entryName in self.workingDirs[self.selectedWorkingDir]["entries"]:
			entry = self.workingDirs[self.selectedWorkingDir]["entries"][entryName]
			for link in entry["links"]:
				item = MyListWidgetItem(link)
				lw.addItem(item)
	

	def showWorkingDirs(self, lw):
		lw.clear()
		for wkDirName in sorted(self.workingDirs):
			item = MyListWidgetItem(wkDirName)
			if not self.workingDirs[wkDirName]["exists"]:
				item.setTextColor(QColor(255, 0, 0))
			lw.addItem(item)
		lw.setCurrentRow(0)



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


	# "Достаем" пользователя вопросами при закрытии приложения
	def closeEvent(self, event):
		msgBox = QMessageBox(text = u"Действительно закрыть приложение?", parent = self)
		msgBox.setWindowTitle(u"Подтверждение")
		msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
		msgBox.setDefaultButton(QMessageBox.Yes)
		if msgBox.exec_() == QMessageBox.No:
			event.ignore()
		else:
			if self.configFile.needToSave:
				msgBox.setText(u"Сохранить файл конфигурации?")
				msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
				msgBox.setDefaultButton(QMessageBox.Yes)
				userChoice = msgBox.exec_()
				if userChoice == QMessageBox.Cancel:
					event.ignore()
				else:
					if userChoice == QMessageBox.Yes:
						self.configFile.save()
					self.lwMain.keyPressEvent = self.lwMain.defKeyPressEvent
					self.lwAux.keyPressEvent = self.lwAux.defKeyPressEvent
					event.accept()



		
def main():
	mainWindow = MainWindow()
	mainWindow.show()
	sys.exit(app.exec_())


if __name__ == "__main__":
	main()
	pass


