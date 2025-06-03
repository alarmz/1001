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

POLYPHONE_DICT = {
    '行': ['xíng', 'háng'], '長': ['cháng', 'zhǎng'], '重': ['zhòng', 'chóng'],
    '數': ['shù', 'shǔ'], '分': ['fēn', 'fèn'], '中': ['zhōng', 'zhòng'],
    '為': ['wéi', 'wèi'], '間': ['jiān', 'jiàn'], '乾': ['gān', 'qián'],
    '血': ['xuè', 'xiě'], '角': ['jiǎo', 'jué'], '便': ['biàn', 'pián'],
    '調': ['tiáo', 'diào'], '量': ['liáng', 'liàng'], '教': ['jiāo', 'jiào'],
    '背': ['bèi', 'bēi'], '種': ['zhǒng', 'zhòng'], '少': ['shǎo', 'shào'],
    '還': ['hái', 'huán'], '了': ['le', 'liǎo']
}

VARIANT_DICT = {
    '台': '臺', '裏': '裡', '么': '麼', '着': '著', '説': '說', '綫': '線',
    '衆': '眾', '糰': '團', '麵': '面', '鞦韆': '秋千', '脩': '修', '衹': '只',
    '巖': '岩', '峯': '峰', '島': '島', '麽': '麼', '綵': '彩', '劃': '畫',
    '製': '制', '適': '適'
}

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
    def find_polyphones(text: str) -> List[Dict]:
        polyphones = []
        for char, pronunciations in POLYPHONE_DICT.items():
            positions = []
            for i, c in enumerate(text):
                if c == char:
                    start = max(0, i-5)
                    end = min(len(text), i+6)
                    context = text[start:end]
                    positions.append({
                        'position': i,
                        'context': context,
                        'char_index': i - start
                    })
            if positions:
                polyphones.append({
                    'char': char,
                    'pronunciations': pronunciations,
                    'positions': positions
                })
        return polyphones

    @staticmethod
    def find_variants(text: str) -> List[Dict]:
        variants = []
        for variant, standard in VARIANT_DICT.items():
            positions = []
            for pos in re.finditer(re.escape(variant), text):
                start_pos = pos.start()
                start = max(0, start_pos-5)
                end = min(len(text), start_pos+len(variant)+5)
                context = text[start:end]
                positions.append({
                    'position': start_pos,
                    'context': context,
                    'char_index': start_pos - start
                })
            if positions:
                variants.append({
                    'variant': variant,
                    'standard': standard,
                    'positions': positions
                })
        return variants

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
