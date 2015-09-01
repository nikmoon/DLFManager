# -*- coding: utf-8 -*-

import errno
import sys
import os
import types
import MyLib
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import QListWidget, QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QColor

from TorrentManager import APP_DIR, CFG_FILE_BASE_NAME, CFG_FILE_NAME

'''
# определяем местоположение приложения
if __name__ == "__main__":
	APP_DIR = os.path.dirname(os.path.abspath(__file__))
else:
	APP_DIR = os.path.dirname(__file__)

# полное имя файла конфигурации по умолчанию
CFG_FILE_BASE_NAME = u"download_dirs.cfg"
CFG_FILE_NAME = os.path.join(APP_DIR, CFG_FILE_BASE_NAME)
'''


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
		self.readConfigFile()

		self.action.triggered.connect(self.backupConfigFile)
		self.action_2.triggered.connect(self.saveConfigFileOnMenuAction)

		self.startManageWorkingDirs()

	BORDER_STR = "<>"
	WKDIR_LINE = "->"
	ENTRY_STR = ">"

	# читаем файл конфигурации
	def readConfigFile(self, fileName = CFG_FILE_NAME):
		workingDirs = {}
		try:
			f = open(fileName)
		except IOError as e:
			if e.errno != errno.ENOENT:
				print u"{0}. Код ошибки: {1}".format(e.strerror, e.errno)
				print u"Программа завершается."
				sys.exit()
		except:
			print u"Неизвестная ошибка."
			sys.exit()
		else:
			borderCnt = 0		# число прочитанных строк, содержащих BORDER_STR в начале
			for line in f:
				if line.startswith(self.BORDER_STR):
					if borderCnt > 0:
						break
					borderCnt += 1
				elif line.startswith(self.WKDIR_LINE):
					wkDirName = line[2:-1].decode("utf-8")
					workingDirs[wkDirName] = {"entries": {}, "new": [], "exists": os.path.exists(wkDirName)}
					wkDir = workingDirs[wkDirName]
				elif line.startswith(self.ENTRY_STR):
					entryName = line[1:-1].decode("utf-8")
					wkDir["entries"][entryName] = {"links": [], "exists": os.path.exists(u"\\".join([wkDirName, entryName]))}
					entryLinks = wkDir["entries"][entryName]["links"]
				else:
					linkName = line[:-1].decode("utf-8")
					entryLinks.append(linkName)

			# ищем неучтенные элементы в рабочих каталогах
			for wkDirName in workingDirs:
				wkDir = workingDirs[wkDirName]
				if wkDir["exists"]:
					entries = MyLib.getEntries(wkDirName)
					for entry in entries:
						if not entry in wkDir["entries"]:
							wkDir["new"].append(entry)

			f.close()

		self.workingDirs = workingDirs

	# сохранение файла конфигурации при выборе пункта в меню
	def saveConfigFileOnMenuAction(self):
		self.saveConfigFile()

	# сохранение файла конфигурации с заданным именем
	def saveConfigFile(self, fileName = CFG_FILE_NAME):
		print u"Типа сохранили файл конфигурации. Имя: {0}".format(fileName)
		f = open(fileName, "w")
		f.write(self.BORDER_STR + "\n")
		for wkDirName in self.workingDirs:
			wkDir = self.workingDirs[wkDirName]
			f.write("{0}{1}\n".format(self.WKDIR_LINE, wkDirName.encode("utf-8")))
			for entryName in wkDir["entries"]:
				entry = wkDir["entries"][entryName]
				f.write("{0}{1}\n".format(self.ENTRY_STR, entryName.encode("utf-8")))
				for link in entry["links"]:
					f.write("{0}\n".format(link.encode("utf-8")))
		f.write(self.BORDER_STR + "\n")
		f.close()


	def backupConfigFile(self):
		filesList = [int(fileName.replace(CFG_FILE_BASE_NAME, "").replace(u".bak", "")) for fileName in MyLib.getFiles(APP_DIR) if fileName.endswith(u".bak")]
		if filesList:
			maxNum = max(filesList) + 1
		else:
			maxNum = 0
		self.saveConfigFile(os.path.join(APP_DIR, u"{0}{1}.bak".format(CFG_FILE_BASE_NAME, maxNum)))


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
		else:
			pass
		QListWidget.keyPressEvent(self.lwMain, keyEvent)


	def startManageSelectedWkDir(self):
		self.leMain.setText(self.currentWkDir)
		self.lwMain.clear()

		self.lwMain.currentRowChanged.connect(self.showLinksForEntry)
		self.lwMain.keyPressEvent = self.keyPressedOnManageSelectedWkDir

		self.fillListWidgetWithDirContent(self.currentWkDir, self.lwMain)
		self.lwMain.setCurrentRow(0)

	
	def keyPressedOnManageSelectedWkDir(self, keyEvent):
		if keyEvent.key() == QtCore.Qt.Key_Backspace:		# возвращаемся к управлению рабочими каталогами
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
		myIcon = QtGui.QIcon(os.path.abspath(u"qt-logo.png"))
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


