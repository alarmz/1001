import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QFileDialog, QMessageBox
)

from PreProcess import docx1001
from Create_Docx import  CreateDocx

class SubDialogA(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("功能A - 建立或更新資料庫")
        self.setFixedSize(400, 200)

        self.file_path_input = QLineEdit()
        btn_select_file = QPushButton("選擇檔案")
        btn_select_file.clicked.connect(self.select_file)

        btn_execute = QPushButton("確定執行")
        btn_execute.clicked.connect(self.execute_action)

        layout = QFormLayout()
        layout.addRow("檔案路徑：", self.file_path_input)
        layout.addRow(btn_select_file, btn_execute)

        self.setLayout(layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "選擇 Word 文件",
            "",
            "Word 文件 (*.docx)"
        )
        if file_path:
            self.file_path_input.setText(file_path)

    def execute_action(self):
        file_path = self.file_path_input.text()
        if not file_path:
            QMessageBox.warning(self, "錯誤", "請先選擇一個 .docx 檔案")
            return
        doc101 =  docx1001()
        doc101.docx_files.append(file_path)
        doc101.OpenAll_PreProcess_Files()
        QMessageBox.information(self, "執行", f"已選擇檔案：\n{file_path}")
        self.accept()


class SubDialogB(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("功能B - 從 txt 建立 Docx 文件")
        self.setFixedSize(400, 200)

        self.file_path_input = QLineEdit()
        btn_select_file = QPushButton("選擇檔案")
        btn_select_file.clicked.connect(self.select_file)

        btn_execute = QPushButton("確定執行")
        btn_execute.clicked.connect(self.execute_action)

        layout = QFormLayout()
        layout.addRow("檔案路徑：", self.file_path_input)
        layout.addRow(btn_select_file, btn_execute)

        self.setLayout(layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "選擇文字檔案",
            "",
            "文字檔案 (*.txt)"
        )
        if file_path:
            self.file_path_input.setText(file_path)

    def execute_action(self):
        file_path = self.file_path_input.text()
        if not file_path:
            QMessageBox.warning(self, "錯誤", "請先選擇一個 .txt 檔案")
            return
        docx =  CreateDocx()
        docx.text_files.append(file_path)
        Loop_Text_Files_Create_Docx = docx.Loop_Text_Files_Create_Docx()
        print(f"Export File: {Loop_Text_Files_Create_Docx}")
        note = f" 匯出檔案到: {Loop_Text_Files_Create_Docx}"
        QMessageBox.information(self, "執行", f"已選擇檔案：\n{file_path}\n\n{note}")
        self.accept()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("師兄功能選單")
        self.setFixedSize(400, 250)

        layout = QVBoxLayout()
        label = QLabel("****師兄您想要做什麼?****")
        layout.addWidget(label)

        btn_a = QPushButton("A. 建立或是更新資料庫 / 字庫A 或是字庫B")
        btn_a.clicked.connect(self.open_a)
        layout.addWidget(btn_a)

        btn_b = QPushButton("B. 從 txt 文字檔建立 Docx 文件")
        btn_b.clicked.connect(self.open_b)
        layout.addWidget(btn_b)

        btn_c = QPushButton("C. 掃描既有的Docx 比對字庫B移除")
        btn_c.clicked.connect(lambda: self.open_sub_dialog("功能C", "這裡是比對字庫B 移除 Docx 字"))
        layout.addWidget(btn_c)

        self.setLayout(layout)

    def open_a(self):
        dialog = SubDialogA()
        dialog.exec()

    def open_b(self):
        dialog = SubDialogB()
        dialog.exec()

    def open_sub_dialog(self, title, content):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(content))
        dialog.setLayout(layout)
        dialog.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
