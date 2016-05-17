import sys

from PyQt5.QtWidgets import QApplication, QStyleFactory

from ui import Posdit

if __name__ == "__main__":
    application = QApplication(sys.argv)
    application.setStyle(QStyleFactory.create("Fusion"))
    window = Posdit()
    window.show()
    window.raise_()
    application.exec_()



