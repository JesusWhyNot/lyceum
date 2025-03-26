import sqlite3
import sys
from PyQt6 import QtWidgets, uic

class CoffeeApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.load_coffee_data()
        
    def load_coffee_data(self):
        conn = sqlite3.connect('coffee.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM coffee")
        rows = cursor.fetchall()
        
        self.tableWidget.setRowCount(len(rows))
        self.tableWidget.setColumnCount(7)
        
        for row_idx, row in enumerate(rows):
            for col_idx, col in enumerate(row):
                self.tableWidget.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(col)))
        
        conn.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CoffeeApp()
    window.show()
    app.exec()