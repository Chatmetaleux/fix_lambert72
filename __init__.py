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
 This script initializes the plugin, making it known to QGIS.
 
 
 
 pyuic4 fl72_dialog_base.ui -o fl72_dialog_base.py
 pyrcc4 -o fl72_rc.py resources.qrc
"""


def classFactory(iface): 
    """Load fix_lambert72 class from file main.py

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .main import fix_lambert72
    return fix_lambert72(iface)
