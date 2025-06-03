import os
import uuid
import tempfile
import secrets
from pathlib import Path
from typing import Dict, List
import re
from docx import Document

from Create_Docx import  CreateDocx
from Scan_Exists_Docx import Scan_Exists_Docx

TEMP_DIR = Path(tempfile.gettempdir()) / "nicegui_docs"
TEMP_DIR.mkdir(exist_ok=True)

class DocumentProcessor:
    @staticmethod
    def text_to_docx(text_content: str, filename: str) -> str:
        #doc = Document()
        docx = CreateDocx()
        
        filepath = TEMP_DIR / filename
        docx.text_files.append(filepath)
        sDocxTextPath = docx.Save_Text_to_Docx_web(text_content, TEMP_DIR, filename)
        docx.Process_Docx_Word_by_word(sDocxTextPath)
        return str(sDocxTextPath)




    @staticmethod
    def process_docx_file(filepath: str) -> tuple:
        docx = Scan_Exists_Docx()
        #docx.docx_files.append(filepath)
        docx.OpenDocx_ReadWords_by_Words_web(filepath)
        
        polyphone_path = TEMP_DIR / f"todo_破音字_{uuid.uuid4().hex[:8]}.docx"
        variant_path = TEMP_DIR / f"todo_異體字_{uuid.uuid4().hex[:8]}.docx"
        docx.A_Dual_sound_todo = Document()
        docx.A_Font_todo = Document()        
        docx.A_Font_todo.save(variant_path)
        docx.A_Dual_sound_todo.save(polyphone_path)
        
        return str(polyphone_path), str(variant_path)

class UserSession:
    def __init__(self):
        self.user_id = str(uuid.uuid4())
        self.uploaded_files = []
        self.generated_files = []

user_sessions: Dict[str, UserSession] = {}

def get_user_session():
    from nicegui import app
    if not hasattr(app.storage.user, 'session_id'):
        app.storage.user.session_id = str(uuid.uuid4())
        user_sessions[app.storage.user.session_id] = UserSession()
    return user_sessions[app.storage.user.session_id]

def cleanup_old_files():
    import time
    try:
        for file_path in TEMP_DIR.glob("*"):
            if file_path.is_file() and file_path.stat().st_mtime < (time.time() - 3600):
                file_path.unlink()
    except Exception as e:
        print(f"清理文件時出錯: {e}")
