import sys
from PyQt5.QtWidgets import QApplication
from cwi_app_widget import CWIWidget

app = QApplication([])

window = CWIWidget()
window.show()

sys.exit(app.exec())