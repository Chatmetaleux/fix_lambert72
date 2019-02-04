# -*- coding: utf-8 -*-
"""
/***************************************************************************
 fix_lambert72
                                 A QGIS plugin
 Correction (x,y) en L72 et correction altimetrique (ellipsoisale->orthometrique)
                             -------------------
        begin                : 2019-01-31
        copyright            : (C) 2018 by GxABT ULiege
        email                : samuel.quevauvillers@uliege.be
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 Main class to manage the qgis plugin and ui;
"""

from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QRect
from PyQt5.QtWidgets import QAction, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon, QTextCursor
from qgis.core import *
import os.path
import traceback
import sys
# local imports
from .fl72_rc import *
from .fl72_dialog import Ui_Dialog
from .core import *


class fix_lambert72:
	"""QGIS Plugin Implementation."""

	def __init__(self, iface):
		"""Constructor.

		:param iface: An interface instance that will be passed to this class
			which provides the hook by which you can manipulate the QGIS
			application at run time.
		:type iface: QgsInterface
		"""
		# Save reference to the QGIS interface
		self.iface = iface
		
		
		# initialize plugin directory
		self.plugin_dir = os.path.dirname(__file__)
		# initialize locale
		locale = QSettings().value('locale/userLocale')[0:2]
		locale_path = os.path.join(
			self.plugin_dir,
			'i18n',
			'fix_lambert72_{}.qm'.format(locale))

		if os.path.exists(locale_path):
			self.translator = QTranslator()
			self.translator.load(locale_path)
		else:
			self.translator = QTranslator()
			self.translator.load(os.path.join(self.plugin_dir,'i18n','fix_lambert72_en.qm'))
		if qVersion() > '4.3.3':
			QCoreApplication.installTranslator(self.translator)
				
		# Declare instance attributes
		self.actions = []
		self.menu = u'Fix &Lambert 72'
		# TODO: We are going to let the user set this up in a future iteration
		self.toolbar = self.iface.addToolBar(u'Fix Lambert 72')
		self.toolbar.setObjectName(u'Fix Lambert 72')

	def tr(self, message):
		"""Get the translation for a string using Qt translation API.

		We implement this ourselves since we do not inherit QObject.

		:param message: String for translation.
		:type message: str, QString

		:returns: Translated version of message.
		:rtype: QString
		"""
		# noinspection PyTypeChecker,PyArgumentList,PyCallByClass
		return QCoreApplication.translate('fix_lambert72', message)

	def add_action(
		self,
		icon_path,
		text,
		callback,
		enabled_flag=True,
		add_to_menu=True,
		add_to_toolbar=True,
		status_tip=None,
		whats_this=None,
		parent=None):

		# Create the dialog (after translation) and keep reference
		self.dlg = Ui_Dialog()
		self.dlg.bL72.clicked.connect(self.run_algo_L72)
		self.dlg.bWGSL72.clicked.connect(self.run_algo_WGS84L72)
		self.dlg.bZ.clicked.connect(self.run_algo_Z)
		
		# icon
		icon = QIcon(icon_path)
		action = QAction(icon, text, parent)
		action.triggered.connect(callback)
		action.setEnabled(enabled_flag)

		if status_tip is not None:
			action.setStatusTip(status_tip)

		if whats_this is not None:
			action.setWhatsThis(whats_this)

		if add_to_toolbar:
			self.iface.addToolBarIcon(action)

		if add_to_menu:
			self.iface.addPluginToVectorMenu(
				self.menu,
				action)

		self.actions.append(action)

		return action

	def initGui(self):
		"""Create the menu entries and toolbar icons inside the QGIS GUI."""

		icon_path = ':/plugins/fix_lambert72/icon22.png'
		self.add_action(
			icon_path,
			text=self.tr(u'Fix &Lambert 72'),
			callback=self.run,
			parent=self.iface.mainWindow())

	def unload(self):
		"""Removes the plugin menu item and icon from QGIS GUI."""
		for action in self.actions:
			self.iface.removePluginVectorMenu(
				self.tr(u'Fix &Lambert 72'),
				action)
			self.iface.removeToolBarIcon(action)
		# remove the toolbar
		del self.toolbar

	def run(self):
		"""Run method that performs all the real work"""
		
		# init GUI
		self.dlg.cobL72.clear()
		self.dlg.cobZ.clear()
		self.dlg.cobWGSL72.clear()
		layers = [layer for layer in QgsProject.instance().mapLayers().values()]
		ll_point = []
		ll_pointWGS84 = []
		ll_pointL72 = []
		ll_line = []
		ll_polygone = []
		for layer in layers:
			#print layer.crs().authid()
			if layer.wkbType()==QgsWkbTypes.Point:
				if layer.crs().authid()=="EPSG:4326":
					ll_pointWGS84.append(layer.name())
					ll_point.append(layer.name())
				elif layer.crs().authid()=="EPSG:31370":
					ll_pointL72.append(layer.name())
					ll_point.append(layer.name())
				else:
					ll_point.append(layer.name())
			elif layer.wkbType()==QgsWkbTypes.LineString:
				ll_line.append(layer.name())
			elif layer.wkbType()==QgsWkbTypes.Polygon:
				ll_polygone.append(layer.name())
		
		self.dlg.cobL72.addItems(ll_pointL72)
		self.dlg.cobWGSL72.addItems(ll_pointWGS84)
		self.dlg.cobZ.addItems(ll_pointWGS84)
		
		# show the dialog
		self.dlg.show()
		
		# Run the dialog event loop
		result = self.dlg.exec_()
		# See if OK was pressed
		if result:
			# Do something useful here - delete the line containing pass and
			# substitute with your code.
			pass
	
	
	
	#def select_output_file(self):
	#	filename = QFileDialog.getExistingDirectory(self.dlg, "Selectionnez le dossier de sortie ","",  QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
	#	self.dlg.tbPath.setText(filename)
	
	def run_algo_L72(self):
		try:
			#check layers and params
			err=""
			if self.dlg.cobL72.currentIndex()==-1:
				err=self.tr("No selected layer")
						
			if err=="":
				c=fix_lambert72_core();
				c.fix_L72(self.iface,str(self.dlg.cobL72.currentText()),self.dlg.cbL72.isChecked())
				printinfo(self,self.tr("Job done. Layer added"))
			else:
				print(self.tr("Error : "))
				printinfo(self,err)
		except:
			trace = traceback.format_exc()
			printerror(self,self.tr("\n%s\nAbnormal termination") % trace)

	def run_algo_WGS84L72(self):
		try:
			#check layers and params
			err=""
			if self.dlg.cobWGSL72.currentIndex()==-1:
				err=self.tr("No selected layer")
						
			if err=="":
				c=fix_lambert72_core();
				c.fixNconvertWGS84toL72(self.iface,str(self.dlg.cobWGSL72.currentText()),self.dlg.tbColWGSL72.text(),self.dlg.cbWGSL72.isChecked())
				printinfo(self,self.tr("Job done. Layer added"))
			else:
				print("Error : ")
				printinfo(self,err)
		except:
			trace = traceback.format_exc()
			printerror(self,self.tr("\n%s\nAbnormal termination") % trace)

	def run_algo_Z(self):
		try:
		
			#check layers and params
			err=""
			if self.dlg.cobZ.currentIndex()==-1:
				err=self.tr("No selected layer")
						
			if err=="":
				c=fix_lambert72_core();
				c.fix_Z(self.iface,str(self.dlg.cobZ.currentText()),self.dlg.tbColZ.text())
				printinfo(self,self.tr("Job done. Layer modified"))
			else:
				print(self.tr("Error : "))
				printinfo(self,err)
		except:
			trace = traceback.format_exc()
			printerror(self,self.tr("\n%s\nAbnormal termination") % trace)

def printinfo(self,msg):
	QMessageBox.information(self.dlg,"Fix Lambert 72",msg)
def printerror(self,msg):
	QMessageBox.warning(self.dlg,"Fix Lambert 72",msg)
			