from io import BytesIO
import uuid

from fastapi.responses import StreamingResponse
from nicegui import ui, app  # 不要再 import open

# 用于暂存用户的下载内容
_pending_downloads: dict[str, tuple[bytes, str]] = {}

def create_docx(text: str) -> bytes:
    from docx import Document
    buf = BytesIO()
    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)
    doc.save(buf)
    return buf.getvalue()

@ui.page('/')
def index():
    ui.markdown('## 上傳 .txt → 下載 .docx 範例')
    ui.upload(on_upload=on_upload) \
      .props('accept=".txt"') \
      .classes('m-4')

def on_upload(event):
    # 1. 讀取並轉檔
    text = event.content.read().decode('utf-8')
    docx_bytes = create_docx(text)
    uid = uuid.uuid4().hex
    filename = event.name.rsplit('.', 1)[0] + '.docx'
    _pending_downloads[uid] = (docx_bytes, filename)

    # 2. 建立一個按鈕，點擊時使用 ui.navigate.to()
    ui.button(f'下載 {filename}').on(
        'click',
        lambda uid=uid: ui.navigate.to(f'/download/{uid}')
    ).classes('m-2')

@app.get('/download/{uid}')
def download(uid: str):
    data, filename = _pending_downloads.pop(uid)
    return StreamingResponse(
        BytesIO(data),
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )

if __name__ in {'__main__', '__mp_main__'}:
    ui.run(title='NiceGUI 上傳 .txt 轉 .docx', reload=True, port=8080)
