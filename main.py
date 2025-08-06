import sys
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QWidget, QListWidget, QListWidgetItem, QComboBox, QFormLayout, \
    QLineEdit, QPushButton, QLabel, QFileDialog

import glacial_unit_finder
from cwi_glacial_units import CWIGlacialUnits


app = QApplication([])

window = CWIGlacialUnits()
window.show()

sys.exit(app.exec())