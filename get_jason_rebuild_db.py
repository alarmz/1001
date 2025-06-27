import requests
import sqlite3
import os

class WordDatabase:
    def __init__(self, db_name="word_data2.db"):
        self.db_name = db_name
        self._recreate_database()

    def _recreate_database(self):
        # 如果資料庫已存在，先刪除
        if os.path.exists(self.db_name):
            os.remove(self.db_name)
        self.conn = sqlite3.connect(self.db_name)
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE [Word] (
            [ID] integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
            [sWord] text, 
            [sType] text, 
            [isIgnore] integer, 
            [imgData] blob
        )
        ''')
        self.conn.commit()

    def insert_record(self, record):
        # 判斷 isIgnore 條件
        ignore_map = {
            "a1": 0, "a2": 0, "a3": 0, "a4": 0, "a5": 0,
            "b": 1
        }
        is_ignore = ignore_map.get(record.type.lower(), None)
        if is_ignore is None:
            return  # 忽略未知類型

        img_data = None
        if record.url:
            try:
                response = requests.get(record.url, timeout=10)
                response.raise_for_status()
                img_data = response.content
            except Exception as e:
                print(f"無法下載圖片: {record.url}，錯誤: {e}")

        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO Word (sWord, sType, isIgnore, imgData)
            VALUES (?, ?, ?, ?)
        ''', (record.sword, record.type, is_ignore, img_data))
        self.conn.commit()

    def close(self):
        self.conn.close()

class Record:
    def __init__(self, id: str, data: dict):
        self.id = id
        self.type = data.get("type")
        self.sword = data.get("sword")
        self.url = data.get("url")
        self.date = data.get("date")

    def __str__(self):
        return f"ID: {self.id}\nType: {self.type}\nSword: {self.sword}\nURL: {self.url}\nDate: {self.date}\n"

class RecordFetcher():
    
    def __init__(self, url: str):
        self.url = url
        self.records = []

    def fetch(self):
        try:
            response = requests.get(self.url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            json_data = response.json()
            self.records = [Record(id_, data) for id_, data in json_data.items()]
        except Exception as e:
            print(f"Error fetching data: {e}")

    def print_records(self):
        for record in self.records:
            print(record)


if __name__ == "__main__":
    url = "https://tw-brand.net/%E9%96%B1%E8%97%8F%E7%B6%B2/file_fonts/B.json"
    #url = "https://tw-brand.net/%E9%96%B1%E8%97%8F%E7%B6%B2/file_fonts/A.json"
    fetcher = RecordFetcher(url)
    fetcher.fetch()
    fetcher.print_records()
    
    db = WordDatabase()

    for rec in fetcher.records:
        print(rec.id)
        db.insert_record(rec)

    db.close()    
