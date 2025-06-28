import sqlite3
import os

def export_images_from_db(db_path="word_data.db", output_dir="exported_images"):
    # 建立資料夾
    os.makedirs(output_dir, exist_ok=True)

    # 連接資料庫
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 查詢所有有圖片的資料
    cursor.execute("SELECT ID, sWord, imgData FROM Word WHERE imgData IS NOT NULL")

    count = 0
    for row in cursor.fetchall():
        id_, sword, img_blob = row
        filename = f"{id_}_{sword}.png"
        filepath = os.path.join(output_dir, filename)

        try:
            with open(filepath, "wb") as f:
                f.write(img_blob)
            count += 1
        except Exception as e:
            print(f"❌ 存檔失敗: {filename}, 錯誤: {e}")

    conn.close()
    print(f"✅ 共匯出 {count} 張圖片至：{output_dir}")

# 呼叫範例
if __name__ == "__main__":
    export_images_from_db("word_data.db")  # 或是你的檔名 word_data2.db
