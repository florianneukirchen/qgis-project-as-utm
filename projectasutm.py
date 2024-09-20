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

        if not layer:
            iface.messageBar().pushWarning('UTM', "No active Layer")
            return


        center = layer.extent().center()

        # Make shure the coordinate of the query is in WGS84        
        wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")
        if layer.crs() != wgs84:
            geom = QgsGeometry.fromPointXY(center)
            tr = QgsCoordinateTransform(layer.crs(), wgs84, QgsProject.instance())
            geom.transform(tr)
            center = geom.asPoint() 

        # Look up in the database
        utm_crs_list = query_utm_crs_info(
            datum_name="WGS 84",
            area_of_interest=AreaOfInterest(
            west_lon_degree=center.x(),
            south_lat_degree=center.y(),
            east_lon_degree=center.x(),
            north_lat_degree=center.y(),
            ),
        )

        # Check if the extend is fully within UTM Zone
        ext = layer.extent()
        utm_crs_list2 = query_utm_crs_info(
            datum_name="WGS 84",
            area_of_interest=AreaOfInterest(
            west_lon_degree=ext.xMinimum(),
            south_lat_degree=ext.yMinimum(),
            east_lon_degree=ext.xMaximum(),
            north_lat_degree=ext.yMaximum(),
            ),
            contains=True
        )
        within = len(utm_crs_list2)
        # (is 1 if within, 0 if not within)

        # Do not crash if no CRS was returned        
        if len(utm_crs_list) == 0:
            iface.messageBar().pushWarning('UTM', 'Pyproj did not return a valid CRS.')
            utm_crs = None
        else:
            utm_crs = QgsCoordinateReferenceSystem("EPSG:" + utm_crs_list[0].code)

            if utm_crs.isValid() and utm_crs != QgsProject.instance().crs():
                QgsProject.instance().setCrs(utm_crs)
                if within > 0:
                    iface.messageBar().pushInfo('UTM', 'Changed Project CRS to ' +
                        utm_crs.description())
                else:
                    iface.messageBar().pushWarning('UTM', 'Changed Project CRS to ' +
                        utm_crs.description() + ', but the layer extend is not fully within this UTM zone.')
       



