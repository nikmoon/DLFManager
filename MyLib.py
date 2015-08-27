# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        MyLib.py
# Purpose:
#
# Author:      karpachevnk
#
# Created:     13.05.2015
# Copyright:   (c) karpachevnk 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from __future__ import print_function

import datetime as dt
from datetime import date, datetime, timedelta
import os
from cx_Oracle import connect as ora_connect

#
# Кириллические названия месяцев в Unicode
#
MONTH_NAMES	=	(
	u"Январь", u"Февраль", u"Март",
	u"Апрель", u"Май", u"Июнь",
	u"Июль", u"Август", u"Сентябрь",
	u"Октябрь", u"Ноябрь", u"Декабрь"
)

#
# Допустимые строковые представления дат
#		key		-> длина строкового представления даты
#		value	-> шаблон для datetime.strptime
#
DATE_STR_FORMATS = {
	7: "%m.%Y",
	10: "%d.%m.%Y",
	16: "%d.%m.%Y %H:%M"
}

#
#	Преобразование строкового представления даты в datetime
#		dateStr	-> строковое представление даты
#
#		Если dateStr не соответствует ин одному из форматов DATE_STR_FORMATS
#	возвращается None.
#
def strToDatetime(dateStr):
	try:
		dateTime = datetime.strptime(dateStr, DATE_STR_FORMATS[len(dateStr)])
	except Exception:
		dateTime = None
	return dateTime

#
# String => Date (Datetime)
#
def strToDate(s, fmt = None):
	fmt = DATE_STR_FORMATS[ len(s) ] if fmt is None else fmt
	try:
		d = datetime.strptime(s, fmt)
	except Exception:
		d = None
	return d

#
# Date (Datetime) => String
#
def dateToStr(d, fmt = DATE_STR_FORMATS[16]):
	try:
		s = d.strftime(fmt)
	except Exception:
		s = None
	return s



# строка для соединения с базой данных Oracle
CONNECT_STRING = '{0}/{1}@10.28.140.40/asqb'


# число дней в указанном году
def daysInYear(year):
	return (dt.date(year + 1, 1, 1) - dt.date(year, 1, 1)).days


# число дней в указанном месяце года
def daysInMonth(year, month):
	if month == 12:
		delta = dt.date(year + 1, 1, 1) - dt.date(year, 12, 1)
	else:
		delta = dt.date(year, month + 1, 1) - dt.date(year, month, 1)
	return delta.days

def is_weekend(date):
	return bool(date.weekday() > 4)




# ------- УСТАРЕЛО --------------
# Преобразование строковой даты в datetime
def make_dt_val(dt_val_str):
	try:
		dtVal = dt.datetime.strptime(dt_val_str, DATE_STR_FORMATS[len(dt_val_str)])
	except KeyError:
		dtVal = None
	return dtVal

def lastDayInMonthDate(d):
	return dt.date(d.year, d.month, daysInMonth(d.year, d.month))


# полный список полных имен файлов в заданном каталоге и всех вложенных каталогах
def get_files(dirPath):
	dirList = [dirPath]
	fileList = []
	while dirList:
		curDir = dirList.pop()
		for dirEntry in os.listdir(curDir):
			fullEntryPath = curDir + "/" + dirEntry
			if os.path.isdir(fullEntryPath):
				dirList.append(fullEntryPath)
			else:
				fileList.append(fullEntryPath)
	return fileList


#	Получение списка имен всех файлов и каталогов в указанном каталоге
getEntries = os.listdir

#	Получение списка полных имен всех файлов и каталогов в указанном каталоге
def getEntriesPaths(dirPath):
	return [dirPath + "\\" + entry for entry in os.listdir(dirPath)]

#	Получение списка имен всех каталогов в указанном каталоге
def getDirectories(dirPath):
	return [entry for entry in os.listdir(dirPath) if os.path.isdir(dirPath + "\\" + entry)]

#	Получение списка имен всех файлов в указанном каталоге
def getFiles(dirPath):
	return [entry for entry in os.listdir(dirPath) if not os.path.isdir(dirPath + "\\" + entry)]

#	Получение списка полных имен каталогов в указанном каталоге
def getDirectoriesPaths(dirPath):
	return [dirPath + "\\" + entry for entry in os.listdir(dirPath) if os.path.isdir(dirPath + "\\" + entry)]

#	Получение списка полных имен всех файлов в указанном каталоге
def getFilesPaths(dirPath):
	return [dirPath + "\\" + entry for entry in os.listdir(dirPath) if not os.path.isdir(dirPath + "\\" + entry)]




#
#		Последовательных временных отметок
#
class TimestampSequence(object):

	DEF_STEP = timedelta(hours = 1)


	def __init__(self, begStamp, endStamp, step = DEF_STEP):
		if isinstance(begStamp, basestring):
			begStamp = strToDate(begStamp)
		if isinstance(endStamp, basestring):
			endStamp = strToDate(endStamp)

		self.stampList = []
		currStamp = begStamp
		while currStamp <= endStamp:
			self.stampList.append(currStamp)
			currStamp += step

		self.begStamp = begStamp
		self.endStamp = endStamp
		self.step = step


	def __str__(self):
		return "[beg={0}, end={1}, count={2}]".format(dateToStr(self.begStamp), dateToStr(self.endStamp), len(self.stampList))


	def __len__(self):
		return len(self.stampList)


	def __getitem__(self, key):
		if isinstance(key, slice):
			newStampList = self.stampList[key.start:key.stop]
			if not newStampList:
				raise TypeError
			return TimestampSequence(newStampList[0], newStampList[-1], self.step)
		else:
			return self.stampList[key]


	def index(self, stamp):
		return self.stampList.index(stamp)


#
#		Массив последовательных временных отметок
#
class DatetimeRange(object):

	DEF_DT_STEP = dt.timedelta(hours = 1)

	@classmethod
	def new(cls, dt_beg, dt_end, dt_step = DEF_DT_STEP):
		if isinstance(dt_beg, basestring):
			dt_beg = make_dt_val(dt_beg)
		if isinstance(dt_end,  basestring):
			dt_end = make_dt_val(dt_end)
		dt_range = []
		dt_cur = dt_beg
		while dt_cur <= dt_end:
			dt_range.append(dt_cur)
			dt_cur += dt_step
		return DatetimeRange(dt_range, dt_step)
	
	@classmethod
	def from_str(cls, range_str):
		dt_beg_str = range_str[1:17]
		dt_end_str = range_str[20:-6]
		return DatetimeRange.new(dt_beg_str, dt_end_str)

	def __init__(self, dt_range, dt_step):
		self.dt_range = dt_range
		self.dt_beg = dt_range[0]
		self.dt_end = dt_range[-1]
		self.dt_step = dt_step

	def __str__(self):
		return "({0} - {1}), {2}".format(self.dt_beg.strftime("%d.%m.%Y %H:%M"), self.dt_end.strftime("%d.%m.%Y %H:%M"), len(self.dt_range))
		#return str([self.dt_beg.strftime("%d.%m.%Y %H:%M"), self.dt_end.strftime("%d.%m.%Y %H:%M"), str(self.dt_step), len(self.dt_range)])
	
	def get_date_range_str(self):
		return "{0} - {1}".format(self.dt_beg.strftime("%d.%m.%Y"),  self.dt_end.strftime("%d.%m.%Y"))
	
	def __len__(self):
		return len(self.dt_range)

	def __getitem__(self, key):
		if isinstance(key, slice):
			dt_range = self.dt_range[key.start:key.stop]
			if not dt_range:
				raise TypeError
			return DatetimeRange(dt_range, self.dt_step)
		else:
			return self.dt_range[key]

	def index(self, dt_val):
		return self.dt_range.index(dt_val)


#   ------------------------------------
#   Соединение с базой данных Oracle
#	------------------------------------
class DB_Conn(object):

	def __init__(self, user = "stok", password = "tok"):
		self.conn = ora_connect(CONNECT_STRING.format(user, password))
		self.cur = self.conn.cursor()

	def close(self):
		self.cur.close()
		self.conn.close()

	def commit(self):
		self.conn.commit()



def testStrToDateTime():
	strTemplate = "{0:18}{1!s:21}{2}"
	testList = ["05.2015", "01.06.2015", "01.12.2015 23:15", "12.12.99"]
	resultList = [datetime(2015, 5, 1), datetime(2015, 6, 1), datetime(2015, 12, 1, 23, 15), None]
	passCount = 0

	print("\n{0:^50}\n".format("Test function strToDateTime:"))
	print(strTemplate.format("String date", "Datetime", "Type"))
	print(strTemplate.format("-------------", "----------", "---------" ))

	for i in range(len(testList)):
		myStrDate = testList[i]
		myDate = strToDatetime(myStrDate)
		if myDate == resultList[i]:
			passCount += 1
		print(strTemplate.format(myStrDate, myDate, type(myDate)))

	print("\nPassed: {0}".format(passCount))

def main():
#	myDateTime = datetime(2015, 6, 5, 6, 15)
#	print(dateToStr(myDateTime))
#	myTimeStampSeq = TimestampSequence("01.01.2015", "01.02.2015")
#	print(myTimeStampSeq)
	a = [1,2,3]
	print(a[-1])
	return

if __name__ == '__main__':
	main()
