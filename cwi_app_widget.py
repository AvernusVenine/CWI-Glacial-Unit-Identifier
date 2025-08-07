import pandas as pd
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QComboBox, QFormLayout, \
    QLineEdit, QPushButton, QLabel, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal, QObject, pyqtSlot
import strat_unit_identifier as StratIdentifier

WINDOW_TITLE = "CWI Stratigraphy Unit Identifier"
COUNTY_DICT = {
    "Aitkin": 1,
    "Anoka": 2,
    "Becker": 3,
    "Beltrami": 4,
    "Benton": 5,
    "Big Stone": 6,
    "Blue Earth": 7,
    "Brown": 8,
    "Carlton": 9,
    "Carver": 10,
    "Cass": 11,
    "Chippewa": 12,
    "Chisago": 13,
    "Clay": 14,
    "Clearwater": 15,
    "Cook": 16,
    "Cottonwood": 17,
    "Crow Wing": 18,
    "Dakota": 19,
    "Dodge": 20,
    "Douglas": 21,
    "Faribault": 22,
    "Fillmore": 23,
    "Freeborn": 24,
    "Goodhue": 25,
    "Grant": 26,
    "Hennepin": 27,
    "Houston": 28,
    "Hubbard": 29,
    "Isanti": 30,
    "Itasca": 31,
    "Jackson": 32,
    "Kanabec": 33,
    "Kandiyohi": 34,
    "Kittson": 35,
    "Koochichng": 36,
    "Lac Qui Parle": 37,
    "Lake": 38,
    "Lake of The Woods": 39,
    "Le Sueur": 40,
    "Lincoln": 41,
    "Lyon": 42,
    "McLeod": 43,
    "Mahnomen": 44,
    "Marshall": 45,
    "Martin": 46,
    "Meeker": 47,
    "Mille Lacs": 48,
    "Morrison": 49,
    "Mower": 50,
    "Murray": 51,
    "Nicollet": 52,
    "Nobles": 53,
    "Norman": 54,
    "Olmsted": 55,
    "Otter Tail": 56,
    "Pennington": 57,
    "Pine": 58,
    "Pipestone": 59,
    "Polk": 60,
    "Pope": 61,
    "Ramsey": 62,
    "Red Lake": 63,
    "Redwood": 64,
    "Renville": 65,
    "Rice": 66,
    "Rock": 67,
    "Roseau": 68,
    "St. Louis": 69,
    "Scott": 70,
    "Sherburne": 71,
    "Sibley": 72,
    "Stearns": 73,
    "Steele": 74,
    "Stevens": 75,
    "Swift": 76,
    "Todd": 77,
    "Traverse": 78,
    "Wabasha": 79,
    "Wadena": 80,
    "Waseca": 81,
    "Washington": 82,
    "Watonwan": 83,
    "Wilkin": 84,
    "Winona": 85,
    "Wright": 86,
    "Yellow Medicine": 87,
    "Iowa": 88,
    "Wisconsin": 89,
    "North Dakota": 90,
    "South Dakota": 91,
    "Canada": 92,
    "Unknown": 99
}
SAVE_MODE_DICT = {'Append Existing File' : 'a', 'New File' : 'w'}
SAVE_TYPE_DICT = {'Majority Unit' : True, 'Every Unit' : False}
#TODO: Possible expand this to allow for 'units with percentage larger than X' modes as well

# CWI Worker class use to run on the thread found in the CWIWidget class
class CWIWorker(QObject):
    progress = pyqtSignal(str)
    completion = pyqtSignal()

    @pyqtSlot(str, str, str, str, str, bool, int)
    def run(self, gdb_path : str, cwi_path : str, st_path : str, save_path : str, save_mode : str, save_type : bool, county : int):
        self.progress.emit('Loading Rasters...')

        try:
            raster_list = StratIdentifier.get_raster_list(gdb_path)
        except Exception as e:
            self.progress.emit(f'Error Loading Rasters! {e}')
            self.completion.emit()
            return

        self.progress.emit('Loading CWI Data...')

        try:
            wells_df, layers_df = StratIdentifier.load_cwi_data(
                cwi_path,
                st_path,
                county
            )
        except Exception as e:
            self.progress.emit(f'Error Loading CWI Data! {e}')
            self.completion.emit()
            return

        unit_df = pd.DataFrame()

        for raster in raster_list:
            self.progress.emit(f'{raster_list.index(raster) + 1} OF {len(raster_list)} : UNIT {raster}')

            try:
                raster_df = StratIdentifier.parse_raster(gdb_path, raster, wells_df, layers_df)
                unit_df = pd.concat([unit_df, raster_df], ignore_index=True)
            except Exception as e:
                self.progress.emit(f'Error Parsing Raster! {e}')
                self.completion.emit()
                return

        self.progress.emit('Saving Data...')

        if save_type:
            try:
                unit_df = StratIdentifier.find_majority_unit(unit_df)
            except Exception as e:
                self.progress.emit(f'Error Finding Majority Unit! {e}')
                self.completion.emit()
                return

        try:
            if save_mode == 'a':
                unit_df.to_csv(save_path,
                             mode=save_mode,
                             index=False,
                             header=None)
            else:
                unit_df.to_csv(save_path,
                             mode=save_mode,
                             index=False)
        except Exception as e:
            self.progress.emit(f'Error Saving Data! {e}')
            self.completion.emit()
            return

        self.progress.emit('Complete!')
        self.completion.emit()

# Main App and GUI class for CWI Strat Identifier
class CWIWidget(QWidget):

    run_signal = pyqtSignal(str, str, str, str, str, bool, int)

    run_button : QPushButton

    gdb_path : QLineEdit
    st_path : QLineEdit
    cwi_path : QLineEdit
    save_path : QLineEdit

    progress_label : QLabel

    county : QComboBox
    save_mode = QComboBox
    save_type = QComboBox

    thread : QThread
    worker : CWIWorker

    def __init__(self):
        super().__init__()
        self.create_ui()

    def create_ui(self):
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(100, 100, 600, 200)

        layout = QFormLayout()

        gdb_layout = QHBoxLayout()

        gdb_button = QPushButton('Browse')
        gdb_button.clicked.connect(self.open_gdb_file_dialog)
        self.gdb_path = QLineEdit()

        gdb_layout.addWidget(self.gdb_path)
        gdb_layout.addWidget(gdb_button)

        layout.addRow('GDB Path:', gdb_layout)

        cwi_layout = QHBoxLayout()

        cwi_button = QPushButton('Browse')
        cwi_button.clicked.connect(self.open_cwi_file_dialog)
        self.cwi_path = QLineEdit()

        cwi_layout.addWidget(self.cwi_path)
        cwi_layout.addWidget(cwi_button)

        layout.addRow('CWI5 Path:', cwi_layout)

        st_layout = QHBoxLayout()

        st_button = QPushButton('Browse')
        st_button.clicked.connect(self.open_st_file_dialog)
        self.st_path = QLineEdit()

        st_layout.addWidget(self.st_path)
        st_layout.addWidget(st_button)

        layout.addRow('C5ST Path:', st_layout)

        self.county = QComboBox()
        self.county.addItems([county for county in COUNTY_DICT.keys()])
        layout.addRow('County:', self.county)

        self.setLayout(layout)

        save_layout = QHBoxLayout()

        save_button = QPushButton('Browse')
        save_button.clicked.connect(self.open_save_file_dialog)
        self.save_path = QLineEdit()

        save_layout.addWidget(self.save_path)
        save_layout.addWidget(save_button)

        layout.addRow('Save Path:', save_layout)

        self.save_mode = QComboBox()
        self.save_mode.addItems([mode for mode in SAVE_MODE_DICT.keys()])
        layout.addRow('Save Mode:', self.save_mode)

        self.save_type = QComboBox()
        self.save_type.addItems([type for type in SAVE_TYPE_DICT.keys()])
        layout.addRow('Save Type:', self.save_type)

        self.run_button = QPushButton('Run')
        self.run_button.clicked.connect(self.run_app)
        layout.addRow(self.run_button)

        self.progress_label = QLabel('')
        layout.addRow('Progress:', self.progress_label)

        self.setLayout(layout)

        self.thread = QThread()
        self.worker = CWIWorker()

        self.worker.moveToThread(self.thread)

        self.worker.progress.connect(self.update_progress)
        self.worker.completion.connect(self.show_run_button)
        self.run_signal.connect(self.worker.run)

        self.thread.start()

    def run_app(self):
        self.run_button.hide()

        self.run_signal.emit(
            self.gdb_path.text(),
            self.cwi_path.text(),
            self.st_path.text(),
            self.save_path.text(),
            SAVE_MODE_DICT.get(self.save_mode.currentText()),
            SAVE_TYPE_DICT.get(self.save_type.currentText()),
            COUNTY_DICT.get(self.county.currentText())
        )

    def show_run_button(self):
        self.run_button.show()

    def update_progress(self, msg : str):
        self.progress_label.setText(msg)

    # Used to open a file dialogue option for ease of use
    def open_file_dialog(self, label : QLabel, name_filter : str = '',
                         mode : QFileDialog.FileMode = QFileDialog.FileMode.ExistingFile):
        dialog = QFileDialog()
        dialog.setFileMode(mode)
        dialog.setNameFilter(name_filter)

        if dialog.exec():
            filename = dialog.selectedFiles()

            if filename:
                label.setText(filename[0])

    def open_save_file_dialog(self):
        self.open_file_dialog(self.save_path, mode = QFileDialog.FileMode.AnyFile)

    def open_cwi_file_dialog(self):
        self.open_file_dialog(self.cwi_path, name_filter = 'CSV (*.csv)')

    def open_st_file_dialog(self):
        self.open_file_dialog(self.st_path, name_filter = 'CSV (*.csv)')

    def open_gdb_file_dialog(self):
        self.open_file_dialog(self.gdb_path, mode=QFileDialog.FileMode.Directory)