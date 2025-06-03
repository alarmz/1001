
import time
import os
import secrets
from nicegui import ui

from core import cleanup_old_files
import ui_main  # 註冊頁面

if __name__ in {"__main__", "__mp_main__"}:
    ui.timer(3600, cleanup_old_files)

    storage_secret = os.getenv('NICEGUI_STORAGE_SECRET', secrets.token_urlsafe(32))

    ui.run(
        title='文檔處理系統',
        favicon='📄',
        port=8080,
        host='0.0.0.0',
        reload=True,
        show=True,
        storage_secret=storage_secret
    )
