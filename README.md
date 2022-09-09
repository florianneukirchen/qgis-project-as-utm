# qgis-project-as-utm
QGIS Plugin to set CRS of the Project to the UTM Zone of the area. It takes the central point of the extent of the active layer to look up the corresponding UTM Zone in the pyproj database. Finally the CRS of the project is set.

Usage: Select a layer that only contains features within the area of interest, e.g. an opened GPX track. Press the UTM Button in the Plugins Toolbar.



