import sqlite3
import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap, QFont
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, 
                               QCheckBox, QLineEdit, QPushButton, QHBoxLayout, QDialog, QFormLayout, QDialogButtonBox, 
                               QLabel, QVBoxLayout)
import base64
import binascii
from PySide6.QtGui import QClipboard

# Connect to SQLite DB
db_path = 'word_data.db'  # Replace with the path to your SQLite database

def fetch_data(search_term=""):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    query = "SELECT ID, sWord, sType, isIgnore, imgData FROM Word WHERE sWord LIKE ?"
    cursor.execute(query, ('%' + search_term + '%',))
    data = cursor.fetchall()
    connection.close()
    return data

def fetch_sType():
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT sType FROM Word")
    sTypes = [row[0] for row in cursor.fetchall()]
    connection.close()
    return sTypes

def handle_img_data(img_data):
    try:
        # If the data is base64, decode it
        decoded_data = base64.b64decode(img_data)
        img = QImage.fromData(decoded_data)
        if img.isNull():
            raise ValueError("Decoded image is null or invalid")
        return img
    except (binascii.Error, ValueError):
        img = QImage()
        img.loadFromData(img_data)
        if img.isNull():
            raise ValueError("Invalid image data")
        return img

def add_data(sWord, sType, isIgnore, imgData=None):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Word (sWord, sType, isIgnore, imgData) VALUES (?, ?, ?, ?)",
                   (sWord, sType, isIgnore, imgData))
    connection.commit()
    connection.close()

def update_data(ID, sWord, sType, isIgnore, imgData=None):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("UPDATE Word SET sWord=?, sType=?, isIgnore=?, imgData=? WHERE ID=?",
                   (sWord, sType, isIgnore, imgData, ID))
    connection.commit()
    connection.close()

def delete_data(ID):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Word WHERE ID=?", (ID,))
    connection.commit()
    connection.close()

class AddRecordDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add New Record")
        self.setFixedSize(400, 300)

        layout = QFormLayout()

        self.sWord_input = QLineEdit(self)
        layout.addRow("sWord:", self.sWord_input)

        self.sType_combo = QComboBox(self)
        self.sType_combo.addItems(fetch_sType())
        layout.addRow("sType:", self.sType_combo)

        self.isIgnore_checkbox = QCheckBox("Ignore", self)
        layout.addRow(self.isIgnore_checkbox)

        self.img_preview = QLabel(self)
        self.img_preview.setText("Paste an image (from clipboard) if needed")
        layout.addRow("Image Preview:", self.img_preview)

        # Clipboard handling
        clipboard = QApplication.clipboard()
        if clipboard.mimeData().hasImage():
            img = clipboard.image()
            self.img_preview.setPixmap(QPixmap(img).scaled(128, 128, Qt.KeepAspectRatio))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        return {
            "sWord": self.sWord_input.text(),
            "sType": self.sType_combo.currentText(),
            "isIgnore": 1 if self.isIgnore_checkbox.isChecked() else 0,
            "imgData": None  # You can implement clipboard image data handling if needed
        }

class WordTableApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Word Table")
        self.setFixedSize(800, 800)

        # Layout
        layout = QVBoxLayout()

        # Search Box
        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("Search by sWord...")
        self.search_box.textChanged.connect(self.update_table)
        layout.addWidget(self.search_box)

        # Table
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "sWord", "sType", "isIgnore", "imgData"])
        layout.addWidget(self.table)

        # Set row height and style
        font = QFont()
        font.setPointSize(24)
        self.table.setFont(font)

        header = self.table.horizontalHeader()
        header.setFont(QFont("Arial", 12, QFont.Bold))

        # Add, Update, and Delete Buttons
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add", self)
        self.add_button.clicked.connect(self.show_add_dialog)
        button_layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Delete", self)
        self.delete_button.clicked.connect(self.delete_row)
        button_layout.addWidget(self.delete_button)

        self.update_button = QPushButton("Update", self)
        self.update_button.clicked.connect(self.update_row)
        button_layout.addWidget(self.update_button)

        layout.addLayout(button_layout)

        # Initial Table Population
        self.update_table()

        self.setLayout(layout)

    def update_table(self):
        search_term = self.search_box.text()
        data = fetch_data(search_term)

        self.table.setRowCount(len(data))

        # Fetch sTypes for ComboBox
        sTypes = fetch_sType()

        for row_idx, row_data in enumerate(data):
            # ID Column
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_data[0])))

            # sWord Column (center-aligned)
            item = QTableWidgetItem(row_data[1])
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 1, item)

            # sType Column (ComboBox)
            combo_box = QComboBox()
            combo_box.addItems(sTypes)  # Populate with sType values from database
            combo_box.setCurrentText(row_data[2])
            self.table.setCellWidget(row_idx, 2, combo_box)

            # isIgnore Column (Checkbox, center-aligned)
            checkbox = QCheckBox()
            checkbox.setChecked(bool(row_data[3]))

            # Create a QWidget to hold the checkbox and align it properly
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setAlignment(Qt.AlignCenter)  # Center-align the checkbox
            layout.addWidget(checkbox)
            widget.setLayout(layout)

            self.table.setCellWidget(row_idx, 3, widget)

            # imgData Column (Image)
            img_data = row_data[4]
            if img_data:
                img = handle_img_data(img_data)
                img_pixmap = QPixmap(img)
                img_label = QTableWidgetItem()
                self.table.setItem(row_idx, 4, img_label)
                img_label.setData(Qt.DecorationRole, img_pixmap)

            # Set row height to 128 for each row
            self.table.setRowHeight(row_idx, 128)

    def show_add_dialog(self):
        dialog = AddRecordDialog()
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            add_data(data["sWord"], data["sType"], data["isIgnore"], data["imgData"])
            self.update_table()

    def delete_row(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            ID = self.table.item(selected_row, 0).text()
            delete_data(ID)
            self.update_table()

    def update_row(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            ID = self.table.item(selected_row, 0).text()
            sWord = self.table.item(selected_row, 1).text()
            sType = self.table.cellWidget(selected_row, 2).currentText()
            isIgnore = self.table.cellWidget(selected_row, 3).isChecked()
            # Here, you can also get imgData if needed
            imgData = None  # Replace with actual imgData if available
            update_data(ID, sWord, sType, isIgnore, imgData)
            self.update_table()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WordTableApp()
    window.show()
    sys.exit(app.exec())
