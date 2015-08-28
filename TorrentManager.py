# -*- coding: utf-8 -*-

import errno
import sys
import os
import types
import MyLib
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import QListWidget, QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QColor


if not "win32" in sys.platform:
	print u"Неизвестная ОС. sys.platrform = \"{0}\""
	sys.exit()

# определяем местоположение приложения
if __name__ == "__main__":
	APP_DIR = os.path.dirname(os.path.abspath(__file__))
else:
	APP_DIR = os.path.dirname(__file__)

# полное имя файла конфигурации по умолчанию
CFG_FILE_NAME = u"\\".join([APP_DIR, u"download_dirs.cfg"])


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
		uic.loadUi(os.path.abspath(u"MainWindow.ui"), self)
		self.setWindowIcon()
		self.readConfigFile()
		self.manageWorkingDirs()


	BORDER_STR = "<>"
	WKDIR_LINE = "->"
	ENTRY_STR = ">"

	# читаем файл конфигурации
	def readConfigFile(self):
		workingDirs = {}
		try:
			f = open(CFG_FILE_NAME)
		except IOError as e:
			if e.errno != errno.ENOENT:
				print u"{0}. Код ошибки: {1}".format(e.strerror, e.errno)
				print u"Программа завершается."
				sys.exit()
		except:
			print u"Неизвестная ошибка."
			sys.exit()
		else:
			borderCnt = 0
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


	# переходим к управлению списком рабочих каталогов
	def manageWorkingDirs(self):
		self.leMain.setText(u"Управление списком рабочих каталогов")
		self.lwMain.clear()

		self.lwMain.currentRowChanged.connect(self.showDirContent)
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
		for entry in self.workingDirs[wkDirName]["new"]:
			item = QtGui.QListWidgetItem(entry)
			item.setTextColor(QColor(0, 150, 0))
			self.lwAux.addItem(item)
		for entry in self.workingDirs[wkDirName]["entries"]:
			item = QtGui.QListWidgetItem(entry)
			if not self.workingDirs[wkDirName]["entries"][entry]["exists"]:
				item.setTextColor(QColor(255, 0, 0))
			self.lwAux.addItem(item)
		self.lwAux.setCurrentRow(0)

	def keyPressedOnManageWorkingDirsList(self, keyEvent):
		if keyEvent.key() == QtCore.Qt.Key_Escape:
			#self.lwMain = QListWidget()
			#self.lwMain.currentRowChanged.disconnect(self.showDirContent)
			#self.lwMain.currentRowChanged.disconnect()
			pass
		elif keyEvent.key() == QtCore.Qt.Key_Return:
			self.lwAux.addItem(u"Поздравляю. Вы нажали клавишу Enter.")
		else:
			pass
		QListWidget.keyPressEvent(self.lwMain, keyEvent)

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


