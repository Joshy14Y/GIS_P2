import sys
from PyQt5.QtWidgets import QApplication, QComboBox, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QFormLayout, QMessageBox, QDateTimeEdit, QDateEdit, QTableView
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel
from PyQt5.QtCore import QDate, QTime

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
        self.classroom = classroom_id
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
        submit_button.clicked.connect(self.submit_form)

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
        
        self.classroom = classroom_id
        
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
        submit_button.clicked.connect(self.submit_form)

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
        query.prepare("SELECT * FROM get_events_and_availability(:date, :classroom_id)")
        query.bindValue(":date", date)
        query.bindValue(":classroom_id", self.classroom_id)
        if not query.exec_():
            print("Error:", query.lastError().text())
        else:
            self.model.setQuery(query)
    
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


