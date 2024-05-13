from qgis.PyQt.QtWidgets import QAction, QMainWindow,QMessageBox
from qgis.gui import QgsMapCanvas, QgsMapToolZoom, QgsMapToolIdentifyFeature
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsVectorLayer, QgsProject
from PyQt5.QtSql import *
from test import SingleReservationWindow
from test import WeeklyReservationWindow
class db_conn():
    def __init__(self):
        self.con = QSqlDatabase.addDatabase("QPSQL")
        self.con.setHostName("leoviquez.com")
        self.con.setPort(15432)
        self.con.setDatabaseName("cursoGIS")
        self.con.setUserName("usr_GIS")
        self.con.setPassword("usr_GIS")
   
def getUri(esquema, capa):
    return (f"""dbname='cursoGIS' 
                host='leoviquez.com' 
                port='15432' 
                user='usr_GIS'
                password='usr_GIS'
                key='id' 
                srid='5367' 
                type='MultiPolygon' 
                checkPrimaryKeyUnicity='1' 
                table=\"{esquema}\".\"{capa}\" 
                (geom)""")

def getLayer(esquema, capa):
    uri = getUri(esquema, capa)
    return QgsVectorLayer(uri, capa, "postgres")

class BuildingMap(QMainWindow):
    def __init__(self):
        # Configuracion de ventana
        super().__init__()
        self.setWindowTitle('Selector de aulas TEC')
        # Configuracion del canvas para mostrar el mapa con las capas
        self.layer = getLayer("p2jjl", "buildings")
        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(Qt.white)
        self.canvas.setExtent(self.layer.extent())
        self.canvas.setLayers([self.layer])
        self.setCentralWidget(self.canvas)

        self.map_tool = BuildingSelectTool(self.canvas)
        self.canvas.setMapTool(self.map_tool)
        self.show()

class BuildingSelectTool(QgsMapToolIdentify):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.canvas = canvas
        self.classroom_windows = {}


    def canvasReleaseEvent(self, event):
        buildings_clicked = []

        # Identify all features clicked on the buildings layer
        for layer in self.canvas.layers():
            results = self.identify(event.x(), event.y(), [layer], QgsMapToolIdentify.TopDownStopAtFirst)
            if results and layer.name() == 'buildings':
                buildings_clicked.extend([result.mFeature for result in results])

        if buildings_clicked:
            for building in buildings_clicked:
                building_id = building.attribute('building_id')  # Assuming 'building_id' is the attribute name
                self.showClassroomsInBuilding(building_id)      
    
    def showClassroomsInBuilding(self, building_id):
        if building_id in self.classroom_windows:
            # If window for building_id already exists, destroy it
            self.classroom_windows[building_id].destroy()
            
        # Create a new instance of classroom_map
        classroom_window = ClassroomMap(building_id)
        
        # Show the new window
        classroom_window.show()
        
        # Store the new window in the dictionary
        self.classroom_windows[building_id] = classroom_window

class ClassroomMap(QMainWindow):
    def __init__(self, building_id):
        super().__init__()
        # Configuracion de ventana
        self.setWindowTitle('Selector de aulas TEC')
        self.building_id = building_id
        self.layer = QgsVectorLayer("MultiPolygon?crs=EPSG:5367", "classrooms", "memory")
        self.provider = self.layer.dataProvider()
        self.provider.addAttributes([QgsField("classroom_id", QVariant.Int), QgsField("classroom_name", QVariant.String)])

        # Initializing the canvas
        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(Qt.white)
        self.setCentralWidget(self.canvas)

        # Adding layers to canvas
        self.createClassroomLayer()
        self.canvas.setExtent(self.layer.extent())
        self.canvas.setLayers([self.layer])
        self.setCentralWidget(self.canvas)

        # Add labeling and styling
        self.setLabeling()
        self.setStyle()

        self.map_tool = ClassroomSelectTool(self.canvas)
        self.canvas.setMapTool(self.map_tool)

        # Set the extent of the canvas after layers are added
        self.canvas.setExtent(self.layer.extent())

    def setLabeling(self):
        layer_settings = QgsPalLayerSettings()
        text_format = QgsTextFormat()

        text_format.setFont(QFont("Open Sans", 12))
        text_format.setSize(12)

        buffer_settings = QgsTextBufferSettings()
        buffer_settings.setEnabled(True)
        buffer_settings.setSize(1)
        buffer_settings.setColor(QColor("white"))

        text_format.setBuffer(buffer_settings)
        layer_settings.setFormat(text_format)

        layer_settings.fieldName = "classroom_name"

        # Set placement mode to Free (Angled)
        layer_settings.placement = Qgis.LabelPlacement.Free

        layer_settings.enabled = True

        layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
        self.layer.setLabelsEnabled(True)
        self.layer.setLabeling(layer_settings)
        self.layer.triggerRepaint()

    def setStyle(self):
        # Define style options
        symbol = QgsSymbol.defaultSymbol(self.layer.geometryType())
        symbol.setColor(QColor("#0f86a7"))  # Example color

        renderer = QgsSingleSymbolRenderer(symbol)

        # Apply style to the layer
        self.layer.setRenderer(renderer)

        # Refresh the canvas to apply changes
        self.canvas.refresh()

    def createClassroomLayer(self):

        global db

        db.con.open()

        # Execute SQL query
        query = QSqlQuery(db.con)
        query.exec_(f"SELECT * FROM p2jjl.get_classrooms_in_building({self.building_id})")

        # Prepare an empty list to store features
        lf = []

         # Iterate over query results and create features
        while query.next():
            feature = QgsFeature()
            # Assuming column 1 contains geometry in WKT format and column 0 contains classroom_id
            geometry = QgsGeometry.fromWkt(query.value(1))
            if geometry.isGeosValid():
                feature.setGeometry(geometry)
                feature.setAttributes([query.value(0), query.value(2)])
                lf.append(feature)
            else:
                print("Invalid geometry found:", query.value(1))
        
        print("Features retrieved from the database:", len(lf))

        # Start editing the layer
        self.layer.startEditing()

        # Add features to the layer
        self.provider.addFeatures(lf)

        # Commit changes
        self.layer.commitChanges()

        # Update layer extents
        self.layer.updateExtents()

        db.con.close()

class ClassroomSelectTool(QgsMapToolIdentify):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.canvas = canvas
        self.classroom_windows = {}
    def showDialog(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Desea reservar de manera semestral?")
        msgBox.setWindowTitle("Tipo de reserva")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            return True
        else:
            return False
    def canvasReleaseEvent(self, event):
        classroom_clicked = []

        # Identify all features clicked on the buildings layer
        for layer in self.canvas.layers():
            results = self.identify(event.x(), event.y(), [layer], QgsMapToolIdentify.TopDownStopAtFirst)
            if results and layer.name() == 'classrooms':
                classroom_clicked.extend([result.mFeature for result in results])

        if classroom_clicked:
            for classroom in classroom_clicked:
                classroom_id = classroom.attribute('classroom_id')  # Assuming 'building_id' is the attribute name
                print(classroom_id)  
                self.response = self.showDialog()
                if self.response:
                    print("Reserva semestral")
                    self.window = WeeklyReservationWindow(classroom_id)
                    self.window.show()
                else:
                    print("Reserva diaria")
                    self.window = SingleReservationWindow(classroom_id)
                    self.window.show()

                    

    # FUNCION DE LUZ PARA ABRIR FORM CON ID  




db = db_conn()
                
mi_mapa = BuildingMap()

# class MapActionsToolbar(QToolBar):
#     def __init__(self, canvas):
#         super().__init__("Acciones del mapa")
#         self.canvas = canvas
#         self.setup_actions()
#         self.setup_toolbar()

#     def setup_actions(self):
#         self.actionZoomIn = QAction("Acercamiento", self.canvas)
#         self.actionZoomIn.setCheckable(True)
#         self.actionZoomIn.triggered.connect(self.zoomIn)

#         self.actionZoomOut = QAction("Alejamiento", self.canvas)
#         self.actionZoomOut.setCheckable(True)
#         self.actionZoomOut.triggered.connect(self.zoomOut)

#     def setup_toolbar(self):
#         self.addAction(self.actionZoomIn)
#         self.addAction(self.actionZoomOut)

#     def zoomIn(self):
#         self.canvas.setMapTool(QgsMapToolZoom(self.canvas, True))

#     def zoomOut(self):
#         self.canvas.setMapTool(QgsMapToolZoom(self.canvas, False))

