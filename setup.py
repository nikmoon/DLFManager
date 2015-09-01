# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
	name = "DLFManager",
	version = "0.1",
	scripts = ['TorrentManager.py'],
	packages = ['DLFManager'],
	package_data = {'DLFManager': ['qt-logo.png', 'MainWindow.ui', 'LICENSE', 'README.md']},
)
