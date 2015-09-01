# -*- coding: utf-8 -*-

import os
import sys
import errno
import MyLib
from . import APP_DIR, CFG_FILE_NAME, CFG_FILE_BASE_NAME


BORDER_STR = "<>"
WKDIR_LINE = "->"
ENTRY_STR = ">"

class ConfigFile(object):

	# читаем файл конфигурации
	def read(self, fileName = CFG_FILE_NAME):
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
				if line.startswith(BORDER_STR):
					if borderCnt > 0:
						break
					borderCnt += 1
				elif line.startswith(WKDIR_LINE):
					wkDirName = line[2:-1].decode("utf-8")
					workingDirs[wkDirName] = {"entries": {}, "new": [], "exists": os.path.exists(wkDirName)}
					wkDir = workingDirs[wkDirName]
				elif line.startswith(ENTRY_STR):
					entryName = line[1:-1].decode("utf-8")
					wkDir["entries"][entryName] = {"links": [], "exists": os.path.exists(u"/".join([wkDirName, entryName]))}
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
		return workingDirs

	# сохранение файла конфигурации с заданным именем
	def save(self, workingDirs = None, fileName = CFG_FILE_NAME):
		if workingDirs is None:
			workingDirs = self.workingDirs
		f = open(fileName, "w")
		f.write(BORDER_STR + "\n")
		for wkDirName in workingDirs:
			wkDir = workingDirs[wkDirName]
			f.write("{0}{1}\n".format(WKDIR_LINE, wkDirName.encode("utf-8")))
			for entryName in wkDir["entries"]:
				entry = wkDir["entries"][entryName]
				f.write("{0}{1}\n".format(ENTRY_STR, entryName.encode("utf-8")))
				for link in entry["links"]:
					f.write("{0}\n".format(link.encode("utf-8")))
		f.write(BORDER_STR + "\n")
		f.close()
		print u"Файл конфигурации сохранен: {0}".format(fileName)

	def saveDefault(self):
		self.save()

	def backup(self):
		existsBackups = [int(fileName.replace(CFG_FILE_BASE_NAME, "").replace(u".bak", "")) for fileName in MyLib.getFiles(APP_DIR) if fileName.endswith(u".bak")]
		if existsBackups:
			maxNum = max(existsBackups) + 1
		else:
			maxNum = 0
		self.save(fileName = os.path.join(APP_DIR, u"{0}{1}.bak".format(CFG_FILE_BASE_NAME, maxNum)))




