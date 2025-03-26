import sys
import os
import sqlite3
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QTableWidgetItem,
    QDialog
)
from ui.main_window import Ui_MainWindow
from ui.add_edit_form import Ui_Dialog as Ui_AddEditForm


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class AddEditCoffeeForm(QDialog):
    def __init__(self, parent=None, coffee_id=None):
        super().__init__(parent)
        self.ui = Ui_AddEditForm()
        self.ui.setupUi(self)
        self.coffee_id = coffee_id
        self.setup_ui()
        if coffee_id:
            self.load_data()

    def setup_ui(self):
        self.ui.combo_roast.addItems(['Светлая', 'Средняя', 'Темная'])
        self.ui.combo_type.addItems(['Молотый', 'В зернах'])
        self.ui.btn_save.clicked.connect(self.save_data)
        self.ui.btn_cancel.clicked.connect(self.reject)

    def load_data(self):
        try:
            conn = sqlite3.connect(resource_path('data/coffee.sqlite'))
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM coffee WHERE id=?",
                           (self.coffee_id,))
            coffee = cursor.fetchone()
            conn.close()

            if coffee:
                self.ui.edit_name.setText(coffee[1])
                self.ui.combo_roast.setCurrentText(coffee[2])
                self.ui.combo_type.setCurrentText(coffee[3])
                self.ui.text_description.setPlainText(coffee[4])
                self.ui.spin_price.setValue(coffee[5])
                self.ui.edit_volume.setText(coffee[6])
        except Exception as e:
            QMessageBox.critical(
                self, 'Ошибка', f'Не удалось загрузить данные: {str(e)}')

    def save_data(self):
        try:
            data = (
                self.ui.edit_name.text(),
                self.ui.combo_roast.currentText(),
                self.ui.combo_type.currentText(),
                self.ui.text_description.toPlainText(),
                self.ui.spin_price.value(),
                self.ui.edit_volume.text()
            )

            if not all(data):
                QMessageBox.warning(
                    self, 'Ошибка', 'Все поля должны быть заполнены!')
                return

            conn = sqlite3.connect(resource_path('data/coffee.sqlite'))
            cursor = conn.cursor()

            if self.coffee_id:
                cursor.execute(
                    """
                    UPDATE coffee SET 
                    name=?, roast_level=?, ground_or_beans=?,
                    taste_description=?, price=?, package_volume=?
                    WHERE id=?
                    """,
                    (*data, self.coffee_id)
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO coffee 
                    (name, roast_level, ground_or_beans, 
                    taste_description, price, package_volume)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    data
                )

            conn.commit()
            conn.close()
            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self, 'Ошибка', f'Не удалось сохранить данные: {str(e)}')


class CoffeeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_ui()
        self.load_coffee_data()

    def setup_ui(self):
        self.ui.btn_add.clicked.connect(self.add_coffee)
        self.ui.btn_edit.clicked.connect(self.edit_coffee)

    def load_coffee_data(self):
        try:
            conn = sqlite3.connect(resource_path('data/coffee.sqlite'))
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM coffee")
            rows = cursor.fetchall()
            conn.close()

            self.ui.tableWidget.setRowCount(len(rows))
            self.ui.tableWidget.setColumnCount(7)

            for row_idx, row in enumerate(rows):
                for col_idx, col in enumerate(row):
                    self.ui.tableWidget.setItem(
                        row_idx, col_idx, QTableWidgetItem(str(col)))
        except Exception as e:
            QMessageBox.critical(
                self, 'Ошибка', f'Не удалось загрузить данные: {str(e)}')

    def add_coffee(self):
        dialog = AddEditCoffeeForm(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_coffee_data()

    def edit_coffee(self):
        selected = self.ui.tableWidget.currentRow()
        if selected == -1:
            QMessageBox.warning(
                self, 'Ошибка', 'Выберите запись для редактирования!')
            return

        coffee_id = int(self.ui.tableWidget.item(selected, 0).text())
        dialog = AddEditCoffeeForm(self, coffee_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_coffee_data()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    if not os.path.exists(resource_path('data')):
        os.makedirs(resource_path('data'))

    window = CoffeeApp()
    window.show()
    sys.exit(app.exec())
