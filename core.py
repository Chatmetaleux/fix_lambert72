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
 Main functions are here;
"""

from PyQt5 import QtCore
from PyQt5.QtCore import QVariant, QTranslator, QCoreApplication, QSettings, qVersion
from PyQt5.QtWidgets import QMessageBox
from qgis.core import *
import os
from .vars import *


class fix_lambert72_core:
	def __init__(self):
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
		
	def tr(self, message):
		"""Get the translation for a string using Qt translation API.

		We implement this ourselves since we do not inherit QObject.

		:param message: String for translation.
		:type message: str, QString

		:returns: Translated version of message.
		:rtype: QString
		"""
		# noinspection PyTypeChecker,PyArgumentList,PyCallByClass
		return QCoreApplication.translate('fix_lambert72_core', message)


	def fixNconvertWGS84toL72(self,iface,layer,colonne,saveSHP):
		#iface=self.iface
		layerToConvert=0

		layers = [layer for layer in QgsProject.instance().mapLayers().values()]
		for l in layers:
			#print l.name()
			if l.name()==layer:
				layerToConvert=l
				break
		
		if layerToConvert==0:
			print("Error: no layer "+layer)
			return 0
			
		# some checks
		pf=layerToConvert.fields()
		_found=False
		for f in pf:
			# print f.name()
			if f.name()==colonne:
				_found=True
				break
		if not _found:
			raise Exception("Error",self.tr("No column %s flound in attributes table") % colonne)
			
		# create shp memory
		vl = QgsVectorLayer("Point?crs=epsg:31370", layer+"_fix", "memory")
		pr = vl.dataProvider()
		pr.addAttributes(pf)
		pr.addAttributes([QgsField("HDNG", QVariant.Double)])
		vl.updateFields()
		vl.startEditing()
		
		crsSrc = QgsCoordinateReferenceSystem(4326)
		crsDest = QgsCoordinateReferenceSystem(31370)
		xform = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
		
		for feat in layerToConvert.getFeatures():
			pt=feat.geometry().asPoint()
			
			ptL72 = xform.transform(pt)
			
			# get xy corrections
			x=ptL72.x()
			y=ptL72.y()
			
			if x<20000 or x>300000 :
				raise Exception('Error L72', self.tr('x out of bounds of Belgium'))
			if y<20000 or y>250000 :
				raise Exception('Error L72', self.tr('y out of bounds of Belgium'))
			
			rx = int((x - 20000)/2000 + 0.5)
			ry = int((y - 20000)/2000 + 0.5)
					
			corr=tabyx[ry][rx]
			
			cx = x + float(corr[0])
			cy = y + float(corr[1])
			
			#get z correction
			fs=feat.attributes()
			
			
				
			ss=feat[colonne].split(" ")
			z=0
			if len(ss)==1:
				z=float(ss[0])
			else:
				z=float(ss[2])
			# print "z=%s" % z
			x=pt.x()
			y=pt.y()
			
			rx = int((x - 1)/0.01666667 + 0.5)
			ry = int((y - 48.5)/0.01666667 + 0.5)
					
			corrZ=tabz[rx][ry]
			fs.append(z-corrZ)
			
			fet = QgsFeature()
			fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(cx,cy)))
			fet.setAttributes(fs)
			(r,nf) = vl.dataProvider().addFeatures([fet])
		
		vl.commitChanges()
		
		# write shp to disk or not ?
		if saveSHP:
			path=layerToConvert.dataProvider().dataSourceUri().split("|")[0]
			npath=path.replace(".shp","_fix.shp")
			
			self.delSHP(npath[0:-4])
			
			QgsVectorFileWriter.writeAsVectorFormat(vl, npath, "UTF-8", crsDest , "ESRI Shapefile")
			iface.addVectorLayer(npath,layer+"_fix","ogr")
		else:
			QgsProject.instance().addMapLayer(vl)
			
		
		
		

	def fix_L72(self,iface,layer,saveSHP):
		#iface=self.iface
		layerToConvert=0

		layers = [layer for layer in QgsProject.instance().mapLayers().values()]
		for l in layers:
			#print l.name()
			if l.name()==layer:
				layerToConvert=l
				break
		
		if layerToConvert==0:
			print("Error: no layer "+layer)
			return 0
			
		# create shp memory
		vl = QgsVectorLayer("Point?crs=epsg:31370", layer+"_fix", "memory")
		pr = vl.dataProvider()
		pr.addAttributes(layerToConvert.fields())
		vl.updateFields()
		vl.startEditing()
		
		for feat in layerToConvert.getFeatures():
			pt=feat.geometry().asPoint()
			x=pt.x()
			y=pt.y()
			
			if x<20000 or x>300000 :
				raise Exception('Error L72', self.tr('x out of bounds of Belgium'))
			if y<20000 or y>250000 :
				raise Exception('Error L72', self.tr('y out of bounds of Belgium'))
			
			rx = int((x - 20000)/2000 + 0.5)
			ry = int((y - 20000)/2000 + 0.5)
					
			corr=tabyx[ry][rx]
			
			cx = x + float(corr[0])
			cy = y + float(corr[1])
			
			fet = QgsFeature()
			fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(cx,cy)))
			fet.setAttributes(feat.attributes())
			(r,nf) = vl.dataProvider().addFeatures([fet])
		
		vl.commitChanges()
		
		# write shp to disk or not ?
		if saveSHP:
			path=layerToConvert.dataProvider().dataSourceUri().split("|")[0]
			npath=path.replace(".shp","_fix.shp")
			
			delSHP(npath[0:-4])
			
			QgsVectorFileWriter.writeAsVectorFormat(vl, npath, "UTF-8", layerToConvert.crs() , "ESRI Shapefile")
			iface.addVectorLayer(npath,layer+"_fix","ogr")
		else:
			QgsProject.instance().addMapLayer(vl)
			


	def fix_Z(self,iface,layer,colonne):
		#iface=self.iface
		layerToConvert=0

		layers = [layer for layer in QgsProject.instance().mapLayers().values()]
		for l in layers:
			#print l.name()
			if l.name()==layer:
				layerToConvert=l
				break
		
		if layerToConvert==0:
			print("Error no layer "+layer)
			return 0	
		
		# add field
		pf=layerToConvert.fields()
		indice=len(pf)
		_found=False
		for f in pf:
			if f.name()==colonne:
				_found=True
				break
		if not _found:
			raise Exception("Error",self.tr("No column %s flound in attributes table") % colonne)
		
		pr = layerToConvert.dataProvider()
		pr.addAttributes([QgsField("HDNG", QVariant.Double)])
		layerToConvert.updateFields()
		layerToConvert.startEditing()
		
		
		for feat in layerToConvert.getFeatures():
			pt=feat.geometry().asPoint()
			x=pt.x()
			y=pt.y()
			# print "x=%s  y=%s" % (x,y)
			
			if x<1 or x>7 :
				raise Exception('Error WGS84', self.tr('x out of bounds of Belgium'))
			if y<48.5 or y>52.5 :
				raise Exception('Error WGS84', self.tr('y out of bounds of Belgium'))
			
			#get z correction			
			ss=feat[colonne].split(" ")
			z=0
			if len(ss)==1:
				z=float(ss[0])
			else:
				z=float(ss[2])
			# print "z=%s" % z

			
			rx = int((x - 1)/0.01666667 + 0.5)
			ry = int((y - 48.5)/0.01666667 + 0.5)
			# print "ix=%s  iy=%s" % (rx,ry)
			
			corrZ=tabz[rx][ry]
			layerToConvert.dataProvider().changeAttributeValues({ feat.id() : {indice:z-corrZ} })	
			
		layerToConvert.commitChanges()
	
	
	def delSHP(self,path):
		exts = [".shp",".dbf",".prj",".qpj",".shx"]
		for ext in exts:
			if os.path.exists(path+ext):
				os.remove(path+ext)

