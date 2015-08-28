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
	CFG_FILE_NAME = u"download_dirs.cfg"

	def __init__(self, qApp):
		self.qApp = qApp
		QtGui.QMainWindow.__init__(self)
		uic.loadUi(os.path.abspath(u"MainWindow.ui"), self)
		self.setWindowIcon()
		self.readConfigFile()
		self.manageWorkingDirsList()


	# читаем файл конфигурации
	def readConfigFile(self):
		workingDirsList = []
		cfgFileName = u"\\".join([APP_DIR, self.CFG_FILE_NAME])
		try:
			f = open(cfgFileName)
		except IOError as e:
			if e.errno != errno.ENOENT:
				print u"{0}. Код ошибки: {1}".format(e.strerror, e.errno)
				print u"Программа завершается."
				sys.exit()
		except:
			print u"Неизвестная ошибка."
			sys.exit()
		else:
			for pathStr in f:
				pathStr = pathStr.replace("\n", "")
				if pathStr:
					workingDirsList.append(pathStr)
			f.close()
		self.workingDirsList = workingDirsList


	# переходим к управлению списком рабочих каталогов
	def manageWorkingDirsList(self):
		self.leMain.setText(u"Управление списком рабочих каталогов")
		self.lwMain.clear()

		self.lwMain.currentRowChanged.connect(self.showDirContent)
		self.lwMain.keyPressEvent = self.keyPressedOnManageWorkingDirsList		

		self.lwMain.setFocus()

		if self.workingDirsList:
			self.lwMain.addItems(self.workingDirsList)
			self.showDirContent(0)

		self.lwMain.setCurrentRow(0)

	def showDirContent(self, rowNum):
		dirPath = unicode(self.lwMain.item(rowNum).text())
		self.leAux.setText(dirPath)
		self.lwAux.clear()
		self.lwAux.addItems(MyLib.getEntries(dirPath))
		self.lwAux.setCurrentRow(0)

	def keyPressedOnManageWorkingDirsList(self, keyEvent):
		if keyEvent.key() == QtCore.Qt.Key_Escape:
			#self.lwAux.clear()
			#self.lwAux.addItem(u"Очищено...")
			pass
		elif keyEvent.key() == QtCore.Qt.Key_Return:
			self.lwAux.addItem(u"Поздравляю. Вы нажали клавишу Enter.")
		else:
			#self.lwAux.addItem(u"Нажали кнопочку?")
			pass
		QListWidget.keyPressEvent(self.lwMain, keyEvent)




	def initialize(self):
		self.leMain.setText(u"C:\\Work")
		self.lwMain.addItems(MyLib.getEntries(u"C:\\Work"))
		#self.lwMain.setCurrentRow(0)
		self.lwMain.setFocus()

		palette = self.lwMain.palette()
		palette.setColor(QtGui.QPalette.Text, QColor(255,0,0))
		self.lwMain.setPalette(palette)

		self.leAux.setText(u"C:\\Work\\Python")
		self.lwAux.addItems(MyLib.getEntries(unicode(self.leAux.text())))
		#self.lwAux.setCurrentRow(0)


		palette = self.lwAux.palette()
		palette.setColor(QtGui.QPalette.Text, QColor(0,255,0))
		self.lwAux.setPalette(palette)

#		self.lwAux.setTextColor(QColor(255,0,0))
#		self.lwAux.item(0).setTextColor(QColor(255,0,0))
#		self.lwAux.item(1).setTextColor(QColor(0,255,0))
#		self.lwAux.item(2).setTextColor(QColor(0,0,255))

		self.lwMain.currentRowChanged.connect(self.onRowChanged)
		self.lwMain.keyPressEvent = self.keyPressedInMainListWidget

	def setWindowIcon(self):
		myIcon = QtGui.QIcon(os.path.abspath(u"qt-logo.png"))
		QtGui.QMainWindow.setWindowIcon(self, myIcon)		


	def onRowChanged(self, rowNum):
		self.lwAux.addItem(u"Активирована новая строка, ее номер = {0}".format(rowNum))

	def keyPressedInMainListWidget(self, keyEvent):
		if keyEvent.key() == QtCore.Qt.Key_Escape:
			#self.lwAux.clear()
			#self.lwAux.addItem(u"Очищено...")
			pass
		elif keyEvent.key() == QtCore.Qt.Key_Return:
			self.lwAux.addItem(u"Поздравляю. Вы нажали клавишу Enter.")
		else:
			#self.lwAux.addItem(u"Нажали кнопочку?")
			pass
		QListWidget.keyPressEvent(self.lwMain, keyEvent)

		
def main():
	app = QtGui.QApplication(sys.argv)
	mainWindow = MainWindow(app)
	mainWindow.show()
	sys.exit(app.exec_())


if __name__ == "__main__":
	main()

