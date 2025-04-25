import sqlite3
import io
from PIL import Image
import numpy as np
from dearpygui.core import *
from dearpygui.simple import *

conn = sqlite3.connect("word_data.db")
image_registry = {}

# 暫存新增圖片的 binary
new_image_bytes = b''

def load_image_from_blob(blob):
    image = Image.open(io.BytesIO(blob)).convert("RGBA")
    image = image.resize((64, 64))
    width, height = image.size
    data = np.array(image).flatten() / 255.0
    return width, height, data.tolist()

def refresh_table():
    delete_item("table_area", children_only=True)

    cursor = conn.cursor()
    cursor.execute("SELECT ID, sWord, sType, isIgnore, imgData FROM Word")
    rows = cursor.fetchall()

    for row in rows:
        id_, sWord, sType, isIgnore, imgData = row
        texture_id = f"img_{id_}"

        if texture_id not in image_registry:
            w, h, img_data = load_image_from_blob(imgData)
            add_static_texture(w, h, img_data, tag=texture_id)
            image_registry[texture_id] = True

        with group(horizontal=True, parent="table_area"):
            add_image(texture_id, width=64, height=64)
            add_input_text(f"word_{id_}", default_value=sWord, width=150)
            add_combo(f"type_{id_}", items=["noun", "verb", "adj"], default_value=sType, width=100)
            add_checkbox(f"ignore_{id_}", default_value=bool(isIgnore))
            add_button(f"儲存##{id_}", callback=lambda s, d, row_id=id_: update_row(row_id))
            add_button(f"刪除##{id_}", callback=lambda s, d, row_id=id_: delete_row(row_id))

def update_row(row_id):
    word = get_value(f"word_{row_id}")
    s_type = get_value(f"type_{row_id}")
    is_ignore = get_value(f"ignore_{row_id}")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Word SET sWord=?, sType=?, isIgnore=? WHERE ID=?",
        (word, s_type, int(is_ignore), row_id)
    )
    conn.commit()
    log_info(f"更新成功 ID: {row_id}")

def delete_row(row_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Word WHERE ID = ?", (row_id,))
    conn.commit()
    refresh_table()

def add_new_row_callback():
    global new_image_bytes

    word = get_value("new_word")
    s_type = get_value("new_type")
    is_ignore = get_value("new_ignore")

    if not word or not new_image_bytes:
        log_error("請輸入單字並選擇圖片")
        return

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Word (sWord, sType, isIgnore, imgData) VALUES (?, ?, ?, ?)",
        (word, s_type, int(is_ignore), new_image_bytes)
    )
    conn.commit()
    new_image_bytes = b''
    clear_entry("new_word")
    set_value("new_ignore", False)
    refresh_table()
    log_info("新增成功！")

def handle_file_picker(sender, data):
    global new_image_bytes
    path = data
    with open(path, "rb") as f:
        new_image_bytes = f.read()
    set_value("new_image_path", path)

with window("Word Table"):
    add_button("刷新資料", callback=lambda: refresh_table())
    add_spacing(count=1)

    with collapsing_header("新增資料", default_open=False):
        add_input_text("new_word", label="單字")
        add_combo("new_type", label="類型", items=["noun", "verb", "adj"], default_value="noun")
        add_checkbox("new_ignore", label="忽略")
        add_input_text("new_image_path", label="圖片路徑", readonly=True)
        add_button("選擇圖片", callback=lambda: open_file_dialog(callback=handle_file_picker))
        add_button("新增", callback=add_new_row_callback)

    add_separator()
    add_child("table_area", width=800, height=500)

refresh_table()
start_dearpygui()
