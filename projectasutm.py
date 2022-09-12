#-----------------------------------------------------------
# Copyright (C) 2022 Florian Neukirchen
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------

from qgis.core import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.utils import iface
from pyproj import CRS
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info

class ProjectUTM:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.action = QAction('UTM', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        layer = iface.activeLayer()
        ext = layer.extent()
        utm_crs_list = query_utm_crs_info(
            datum_name="WGS 84",
            area_of_interest=AreaOfInterest(
            west_lon_degree=ext.center().x(),
            south_lat_degree=ext.center().y(),
            east_lon_degree=ext.center().x(),
            north_lat_degree=ext.center().y(),
            ),
        )
        
        if len(utm_crs_list) == 0:
            iface.messageBar().pushInfo('UTM', 'Please try with another layer, pyproj did not return a matching CRS.')
            utm_crs = None
        else:
            utm_crs = QgsCoordinateReferenceSystem("EPSG:" + utm_crs_list[0].code)

            if utm_crs.isValid() and utm_crs != QgsProject.instance().crs():
                QgsProject.instance().setCrs(utm_crs)
                iface.messageBar().pushInfo('UTM', 'Changed Project CRS to ' +
                    utm_crs.description())
       



