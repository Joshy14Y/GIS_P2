from qgis.PyQt.QtWidgets import QAction, QMainWindow,QMessageBox
from qgis.gui import QgsMapCanvas, QgsMapToolZoom, QgsMapToolIdentify
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsVectorLayer, QgsProject ,QgsField, QgsFeature, QgsGeometry, QgsPalLayerSettings, QgsTextFormat, QgsTextBufferSettings, QgsVectorLayerSimpleLabeling, QgsSymbol, QgsSingleSymbolRenderer
from PyQt5.QtSql import *
from PyQt5.QtSql import QSqlQuery, QSqlDatabase
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QMessageBox, QPushButton
import sys
from PyQt5.QtWidgets import QApplication, QComboBox, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QFormLayout, QMessageBox, QDateTimeEdit, QDateEdit, QTableView
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel
from PyQt5.QtCore import QDate, QTime

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
                field_names = [field.name() for field in layer.fields()]
                print("Nombres de los atributos de la capa 'building':", field_names)
                buildings_clicked.extend([result.mFeature for result in results])

        if buildings_clicked:
            for building in buildings_clicked:
                building_id = int(building.attribute('building_id'))  # Assuming 'building_id' is the attribute name
                print("building: ", building_id)
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
        layer_settings.placement = QgsPalLayerSettings.Line
        

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
        msgBox.setText("¿Qué tipo de reserva desea hacer?")
        msgBox.setWindowTitle("Tipo de reserva")

        # Agregar botones personalizados
        buttonSemanal = QPushButton("Semanal")
        msgBox.addButton(buttonSemanal, QMessageBox.YesRole)
        buttonDiario = QPushButton("Diario")
        msgBox.addButton(buttonDiario, QMessageBox.NoRole)
        buttonCancelar = QPushButton("Cancelar")
        msgBox.addButton(buttonCancelar, QMessageBox.RejectRole)

        msgBox.exec()

        # Verificar qué botón se presionó
        clickedButton = msgBox.clickedButton()
        if clickedButton == buttonSemanal:
            return True
        elif clickedButton == buttonDiario:
            return False
        else:
            return None  # En este caso, cuando se presiona Cancelar, se devuelve None
    def canvasReleaseEvent(self, event):
        classroom_clicked = []

        # Identify all features clicked on the buildings layer
        for layer in self.canvas.layers():
            results = self.identify(event.x(), event.y(), [layer], QgsMapToolIdentify.TopDownStopAtFirst)
            if results and layer.name() == 'classrooms':
                field_names = [field.name() for field in layer.fields()]
                print("Nombres de los atributos de la capa 'classrooms':", field_names)
                classroom_clicked.extend([result.mFeature for result in results])

        if classroom_clicked:
            for classroom in classroom_clicked:
                classroom_id = int(classroom.attribute('classroom_id'))  # Assuming 'building_id' is the attribute name
                print(classroom_id)  
                self.response = self.showDialog()
                if self.response:
                    print("Reserva semestral")
                    self.window = WeeklyReservationWindow(classroom_id)
                    self.window.show()
                    
                elif self.response == False:
                    print("Reserva diaria")
                    self.window = SingleReservationWindow(classroom_id)
                    self.window.show()
                else:
                    print("Cancelado")
                    return

                    

    # FUNCION DE LUZ PARA ABRIR FORM CON ID  




db = db_conn()
#mi_mapa = BuildingMap()
#formularios

def validate_dates(start_date, end_date):
    # Convert start and end dates to QDate objects for comparison
    start_date_obj = QDate.fromString(start_date, "yyyy-MM-dd")
    end_date_obj = QDate.fromString(end_date, "yyyy-MM-dd")
    
    # Validate that start date is before end date
    if start_date_obj > end_date_obj:
        QMessageBox.critical(None, "Error", "Start date must be before end date")
        return False

    return True

def validate_times(start_time, end_time):
    # Convert start and end times to QTime objects for comparison
    start_time_obj = QTime.fromString(start_time, "HH:mm")
    end_time_obj = QTime.fromString(end_time, "HH:mm")
    
    # Validate that start time is before end time
    if start_time_obj >= end_time_obj:
        QMessageBox.critical(None, "Error", "Start time must be before end time")
        return False

    return True

class WeeklyReservationWindow(QMainWindow):
    def __init__(self, classroom_id):
        self.classroom = int(classroom_id)
        super().__init__()

        self.setWindowTitle("Insert Weekly Reservation")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())

        self.start_time_edit = QComboBox()
        self.end_time_edit = QComboBox()

        for hour in range(24):
            self.start_time_edit.addItem(f"{hour:02}:00")
            self.end_time_edit.addItem(f"{hour:02}:00")

        self.day_of_week_edit = QComboBox()
        self.day_of_week_edit.addItems(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])

        self.name_edit = QLineEdit()
        self.user_id_edit = QLineEdit()
        
        form_layout.addRow(QLabel("Event Name:"), self.name_edit)
        form_layout.addRow(QLabel("Start Date:"), self.start_date_edit)
        form_layout.addRow(QLabel("End Date:"), self.end_date_edit)
        form_layout.addRow(QLabel("Start Time:"), self.start_time_edit)
        form_layout.addRow(QLabel("End Time:"), self.end_time_edit)
        form_layout.addRow(QLabel("Day of the Week:"), self.day_of_week_edit)
        form_layout.addRow(QLabel("User ID:"), self.user_id_edit)

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submit_and_close)

        layout.addLayout(form_layout)
        layout.addWidget(submit_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Connect to the database
        self.db = QSqlDatabase.addDatabase("QPSQL")
        self.db.setHostName("leoviquez.com")
        self.db.setDatabaseName("cursoGIS")
        self.db.setUserName("usr_GIS")
        self.db.setPassword("usr_GIS")
        self.db.setPort(15432)  # Set the port here
        if not self.db.open():
            QMessageBox.critical(self, "Error", f"Failed to connect to database: {self.db.lastError().text()}")
            sys.exit(1)
    def submit_and_close(self):
    # Lógica para enviar el formulario
        self.submit_form()
        self.close()
    def submit_form(self):
        name = self.name_edit.text()
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        start_time = self.start_time_edit.currentText()
        end_time = self.end_time_edit.currentText()
        day_of_week_index = self.day_of_week_edit.currentIndex()  # Index of selected day of the week
        user_id = self.user_id_edit.text()

        # Map day of the week index to 1-based indexing as required by SQL
        day_of_week = (day_of_week_index + 1) % 7

        if not validate_dates(start_date, end_date) or not validate_times(start_time, end_time):
            return
        
        query = QSqlQuery()
        query.prepare("SELECT * FROM p2jjl.insert_weekly_reservation(:name, :tec_id, :classroom_id, :start_date, :end_date, :start_time, :end_time, :day_of_week)")
        query.bindValue(":name", name)
        query.bindValue(":tec_id", user_id)
        query.bindValue(":classroom_id", self.classroom)  # Assuming classroom_id is 1
        query.bindValue(":start_date", start_date)
        query.bindValue(":end_date", end_date)
        query.bindValue(":start_time", start_time)
        query.bindValue(":end_time", end_time)
        query.bindValue(":day_of_week", day_of_week)
        
        if not query.exec_():
            error_msg = query.lastError().text()
            QMessageBox.critical(self, "Error", f"Failed to insert weekly events: {error_msg}")
            print(error_msg)
        else:
            # Retrieve the results
            results = []
            while query.next():
                results.append((query.value(0),
                                query.value(1).toString("yyyy-MM-dd"),
                                query.value(2).toString("hh:mm:ss"),
                                query.value(3).toString("hh:mm:ss"),
                                query.value(4)))
                print(results)
            # Check for events that were not added
            not_added_events = [result for result in results if not result[4]]  # Check the 'added' flag

            if not_added_events:
                # Construct a message with the details of events that were not added
                message = "The following events were not added:\n"
                for event in not_added_events:
                    name, date, start_time, end_time, added = event  # Unpack the tuple
                    message += f"Name: {name}, Date: {date}, Start Time: {start_time}, End Time: {end_time}\n"
                QMessageBox.information(self, "Warning", message)
            else:
                QMessageBox.information(self, "Success", "Weekly events inserted successfully")

class SingleReservationWindow(QMainWindow):
    def __init__(self, classroom_id):
        super().__init__()
        
        self.classroom = int(classroom_id)
        
        self.setWindowTitle("Insert Single Reservation")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.dateChanged.connect(self.update_model)  # Connect the signal to update the model

        self.start_time_edit = QComboBox()
        self.end_time_edit = QComboBox()

        for hour in range(24):
            self.start_time_edit.addItem(f"{hour:02}:00")
            self.end_time_edit.addItem(f"{hour:02}:00")

        self.name_edit = QLineEdit()
        self.user_id_edit = QLineEdit()
        
        form_layout.addRow(QLabel("Event Name:"), self.name_edit)
        form_layout.addRow(QLabel("Date:"), self.date_edit)
        form_layout.addRow(QLabel("Start Time:"), self.start_time_edit)
        form_layout.addRow(QLabel("End Time:"), self.end_time_edit)
        form_layout.addRow(QLabel("User ID:"), self.user_id_edit)

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submit_and_close)

        layout.addLayout(form_layout)
        layout.addWidget(submit_button)


        self.table_view = QTableView()  # Create a table view to display the data
        layout.addWidget(self.table_view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        # Connect to the database
        self.db = QSqlDatabase.addDatabase("QPSQL")
        self.db.setHostName("leoviquez.com")
        self.db.setDatabaseName("cursoGIS")
        self.db.setUserName("usr_GIS")
        self.db.setPassword("usr_GIS")
        self.db.setPort(15432)  # Set the port here
        if not self.db.open():
            QMessageBox.critical(self, "Error", f"Failed to connect to database: {self.db.lastError().text()}")
            sys.exit(1)

        # Create a QSqlQueryModel to fetch data from the database
        self.model = QSqlQueryModel()
        self.table_view.setModel(self.model)
        self.update_model()
        
    
    def update_model(self):
        # Execute the SQL query to fetch data
        query = QSqlQuery()
        date = self.date_edit.date().toString("yyyy-MM-dd")
        query.prepare("SELECT * FROM p2jjl.get_events_and_availability(:date, :classroom_id)")
        query.bindValue(":date", date)
        query.bindValue(":classroom_id", self.classroom)
        if not query.exec_():
            print("Error:", query.lastError().text())
        else:
            self.model.setQuery(query)
    def submit_and_close(self):
    # Lógica para enviar el formulario
        self.submit_form()
        self.close()
    def submit_form(self):
        name = self.name_edit.text()
        date = self.date_edit.date().toString("yyyy-MM-dd")
        start_time = self.start_time_edit.currentText()
        end_time = self.end_time_edit.currentText()
        user_id = self.user_id_edit.text()

        # Validate that start time is before end time
        if not validate_times(start_time, end_time): 
            return

        query = QSqlQuery()
        query.prepare("SELECT * FROM p2jjl.insert_single_reservation(:name, :tec_id, :classroom_id, :date, :start_time, :end_time)")
        query.bindValue(":name", name)
        query.bindValue(":tec_id", user_id)
        query.bindValue(":classroom_id", self.classroom )  # Assuming classroom_id is 1
        query.bindValue(":date", date)
        query.bindValue(":start_time", start_time)
        query.bindValue(":end_time", end_time)
        
        if not query.exec_():
            error_msg = query.lastError().text()
            QMessageBox.critical(self, "Error", f"Failed to insert single reservation: {error_msg}")
            print(error_msg)
        else:
            # Retrieve the results
            results = []
            while query.next():
                results.append((query.value(0),
                                query.value(1).toString("yyyy-MM-dd"),
                                query.value(2).toString("hh:mm:ss"),
                                query.value(3).toString("hh:mm:ss"),
                                query.value(4)))
                print(results)
            # Check for events that were not added
            not_added_events = [result for result in results if not result[4]]  # Check the 'added' flag

            if not_added_events:
                # Construct a message with the details of events that were not added
                message = "The following events were not added:\n"
                for event in not_added_events:
                    name, date, start_time, end_time, added = event  # Unpack the tuple
                    message += f"Name: {name}, Date: {date}, Start Time: {start_time}, End Time: {end_time}\n"
                QMessageBox.information(self, "Warning", message)
            else:
                QMessageBox.information(self, "Success", "Single reservation inserted successfully")
        self.update_model()
        
        
 



