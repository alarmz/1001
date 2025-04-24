import sqlite3
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import io

PAGE_SIZE = 100

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("SQLite GUI Grid with Pagination and Search")
        self.current_page = 0
        self.search_text = ""
        self.image_refs = {}

        # 搜尋欄
        search_frame = tk.Frame(root)
        search_frame.pack(pady=5)
        self.search_entry = tk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="搜尋", command=self.search).pack(side=tk.LEFT)

        # Treeview
        self.tree = ttk.Treeview(root, columns=("ID", "Text", "Checkbox", "Combobox", "Image"), show="headings", height=20)
        for col in ("ID", "Text", "Checkbox", "Combobox", "Image"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # 分頁按鈕
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        self.prev_btn = tk.Button(btn_frame, text="上一頁", command=self.prev_page)
        self.prev_btn.grid(row=0, column=0, padx=10)
        self.page_label = tk.Label(btn_frame, text="Page 1")
        self.page_label.grid(row=0, column=1, padx=10)
        self.next_btn = tk.Button(btn_frame, text="下一頁", command=self.next_page)
        self.next_btn.grid(row=0, column=2, padx=10)

        self.load_page()

    def search(self):
        self.search_text = self.search_entry.get()
        self.current_page = 0
        self.load_page()

    def load_page(self):
        self.tree.delete(*self.tree.get_children())
        self.image_refs.clear()

        conn = sqlite3.connect("word_data.db")
        cursor = conn.cursor()

        params = []
        query = "SELECT id, sWord, isIgnore, sType, imgData FROM Word"
        if self.search_text:
            query += " WHERE text LIKE ?"
            params.append(f"%{self.search_text}%")
        query += " LIMIT ? OFFSET ?"
        params.extend([PAGE_SIZE, self.current_page * PAGE_SIZE])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        for row in rows:
            id_val, text, checked, option, image_blob = row
            if image_blob:
                image = Image.open(io.BytesIO(image_blob))
                image.thumbnail((50, 50))
                photo = ImageTk.PhotoImage(image)
                self.image_refs[id_val] = photo
            else:
                photo = None
            self.tree.insert("", "end", values=(id_val, text, "✓" if checked else "", option), image=photo)

        self.page_label.config(text=f"Page {self.current_page + 1}")
        conn.close()

    def next_page(self):
        self.current_page += 1
        self.load_page()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_page()

# 建立測試資料（第一次用）
def create_sample_db():
    import random
    conn = sqlite3.connect("sample.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        checked INTEGER,
        option TEXT,
        image_blob BLOB
    )
    """)
    with open("sample_image.jpg", "rb") as f:
        img_data = f.read()
    cursor.execute("DELETE FROM records")
    for i in range(300):
        keyword = "範例" if i % 10 == 0 else "資料"
        cursor.execute("INSERT INTO records (text, checked, option, image_blob) VALUES (?, ?, ?, ?)",
                       (f"{keyword} {i+1}", random.randint(0, 1), f"選項{chr(65 + i % 3)}", img_data))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    #create_sample_db()  # 跑一次即可

    root = tk.Tk()
    app = App(root)
    root.mainloop()
