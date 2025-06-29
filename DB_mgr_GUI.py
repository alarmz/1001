import sys
from get_jason_rebuild_db import RecordFetcher, WordDatabase
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QDialog, QFormLayout, QLineEdit, QFileDialog, QMessageBox, QApplication
)
from PySide6.QtCore import QThread, Signal
from PreProcess import docx1001
from Create_Docx import  CreateDocx
from Scan_Exists_Docx import Scan_Exists_Docx
import os


class DBWorkerThread(QThread):
    status_update = Signal(str)
    finished = Signal()

    def run(self):
        dicURL = {
            "A": "https://tw-brand.net/%E9%96%B1%E8%97%8F%E7%B6%B2/file_fonts/A.json",
            "B": "https://tw-brand.net/%E9%96%B1%E8%97%8F%E7%B6%B2/file_fonts/B.json"
        }
        db = WordDatabase()

        for aURL_Key, url in dicURL.items():
            self.status_update.emit(f"🟡 處理 {aURL_Key} 中...")

            fetcher = RecordFetcher(url)
            fetcher.fetch()
            for rec in fetcher.records:
                db.insert_record(rec)
                self.status_update.emit(f"✅ {aURL_Key} ➜ ID: {rec.id}")

        db.close()
        self.status_update.emit("🎉 A/B 資料庫更新完成")
        self.finished.emit()

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


class SubDialogC(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("功能C - 比對字庫B移除 Docx 字")
        self.setFixedSize(500, 250)

        self.input1 = QLineEdit()
        self.input2 = QLineEdit()
        self.input3 = QLineEdit()

        btn_select_file = QPushButton("選擇檔案")
        btn_select_file.clicked.connect(self.select_file)

        btn_execute = QPushButton("執行")
        btn_execute.clicked.connect(self.execute_action)

        layout = QFormLayout()
        layout.addRow("要掃描的目標檔案：", self.input1)
        layout.addRow("等待審核的差異字：", self.input2)
        layout.addRow("等待審核的破音/難字：", self.input3)
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
            self.input1.setText(file_path)

    def execute_action(self):
        file1 = self.input1.text()
        if not file1:
            QMessageBox.warning(self, "錯誤", "請選擇檔案")
            return
        # 執行你的處理邏輯 (可替換以下內容)
        docx = Scan_Exists_Docx()
        docx.docx_files.append(file1)
        docx.OpenAll_PreProcess_Files()
        self.input2.setText(os.path.join(os.getcwd(), docx.A_Font_todo_File))
        self.input3.setText(os.path.join(os.getcwd(), docx.A_Dual_sound_todo_File))
        QMessageBox.information(self, "執行完成", f"要掃描的目標檔案: {self.input1.text()}\n等待審核的差異字: {self.input2.text()}\n等待審核的破音/難字: {self.input3.text()}")
        self.accept()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("師兄功能選單")
        self.setFixedSize(400, 250)

        layout = QVBoxLayout()
        self.label = QLabel("****師兄您想要做什麼?****")
        layout.addWidget(self.label)
        
        self.btn_a1 = QPushButton("A1. 線上是更新資料庫字庫A/B，注意!!舊的資料庫將會被清除")
        self.btn_a1.clicked.connect(self.online_upgrade_DB)
        layout.addWidget(self.btn_a1)        

        btn_a = QPushButton("A2. 自行下載docx 建立或是更新資料庫 / 字庫A 或是字庫B")
        btn_a.clicked.connect(self.open_a)
        layout.addWidget(btn_a)

        btn_b = QPushButton("B. 從 txt 文字檔建立 Docx 文件")
        btn_b.clicked.connect(self.open_b)
        layout.addWidget(btn_b)

        btn_c = QPushButton("C. 掃描既有的Docx 比對字庫B移除")
        btn_c.clicked.connect(lambda: self.open_sub_dialog("功能C", "這裡是比對字庫B 移除 Docx 字"))
        layout.addWidget(btn_c)

        self.setLayout(layout)
        
    def online_upgrade_DB(self):
        self.btn_a1.setEnabled(False)
        self.label.setText("🚀 開始更新資料庫...")
    
        self.worker = DBWorkerThread()
        self.worker.status_update.connect(self.label.setText)
        self.worker.finished.connect(lambda: self.btn_a1.setEnabled(True))
        self.worker.start()      
    
    def open_a(self):
        dialog = SubDialogA()
        dialog.exec()

    def open_b(self):
        dialog = SubDialogB()
        dialog.exec()

    def open_sub_dialog(self, title, content):
        dialog = SubDialogC()
        dialog.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
