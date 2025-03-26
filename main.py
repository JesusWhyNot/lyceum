import sqlite3
import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox


class AddEditCoffeeForm(QtWidgets.QDialog):
    def __init__(self, parent=None, coffee_id=None):
        super().__init__(parent)
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.coffee_id = coffee_id
        self.setup_ui()
        self.load_data() if coffee_id else None

    def setup_ui(self):
        self.combo_roast.addItems(['Светлая', 'Средняя', 'Темная'])
        self.combo_type.addItems(['Молотый', 'В зернах'])
        self.btn_save.clicked.connect(self.save_data)
        self.btn_cancel.clicked.connect(self.reject)

    def load_data(self):
        conn = sqlite3.connect('coffee.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM coffee WHERE id=?", (self.coffee_id,))
        coffee = cursor.fetchone()
        conn.close()

        if coffee:
            self.edit_name.setText(coffee[1])
            self.combo_roast.setCurrentText(coffee[2])
            self.combo_type.setCurrentText(coffee[3])
            self.text_description.setPlainText(coffee[4])
            self.spin_price.setValue(coffee[5])
            self.edit_volume.setText(coffee[6])

    def save_data(self):
        data = (
            self.edit_name.text(),
            self.combo_roast.currentText(),
            self.combo_type.currentText(),
            self.text_description.toPlainText(),
            self.spin_price.value(),
            self.edit_volume.text()
        )

        if not all(data):
            QMessageBox.warning(
                self, 'Ошибка', 'Все поля должны быть заполнены!')
            return

        conn = sqlite3.connect('coffee.sqlite')
        cursor = conn.cursor()

        if self.coffee_id:
            cursor.execute("""UPDATE coffee SET 
                            name=?, roast_level=?, ground_or_beans=?,
                            taste_description=?, price=?, package_volume=?
                            WHERE id=?""", (*data, self.coffee_id))
        else:
            cursor.execute("""INSERT INTO coffee 
                            (name, roast_level, ground_or_beans, 
                            taste_description, price, package_volume)
                            VALUES (?, ?, ?, ?, ?, ?)""", data)

        conn.commit()
        conn.close()
        self.accept()


class CoffeeApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.setup_ui()
        self.load_coffee_data()

    def setup_ui(self):
        self.btn_add.clicked.connect(self.add_coffee)
        self.btn_edit.clicked.connect(self.edit_coffee)
        self.tableWidget.doubleClicked.connect(self.edit_coffee)

    def load_coffee_data(self):
        conn = sqlite3.connect('coffee.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM coffee")
        rows = cursor.fetchall()
        conn.close()

        self.tableWidget.setRowCount(len(rows))
        self.tableWidget.setColumnCount(7)

        for row_idx, row in enumerate(rows):
            for col_idx, col in enumerate(row):
                self.tableWidget.setItem(row_idx, col_idx,
                                         QtWidgets.QTableWidgetItem(str(col)))

    def add_coffee(self):
        dialog = AddEditCoffeeForm(self)
        if dialog.exec():
            self.load_coffee_data()

    def edit_coffee(self):
        selected = self.tableWidget.currentRow()
        if selected == -1:
            QMessageBox.warning(
                self, 'Ошибка', 'Выберите запись для редактирования!')
            return

        coffee_id = int(self.tableWidget.item(selected, 0).text())
        dialog = AddEditCoffeeForm(self, coffee_id)
        if dialog.exec():
            self.load_coffee_data()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CoffeeApp()
    window.show()
    sys.exit(app.exec())
