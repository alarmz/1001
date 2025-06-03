from nicegui import ui, app
from pathlib import Path
import uuid
import os
import traceback

from core import get_user_session, DocumentProcessor, TEMP_DIR

@ui.page('/')
def main():
    session = get_user_session()
    render_header()

    with ui.tabs().classes('w-full') as tabs:
        tab1 = ui.tab('文字轉 docx', icon='text_fields')
        tab2 = ui.tab('docx 分析', icon='analytics')

    with ui.tab_panels(tabs, value=tab1).classes('w-full'):
        with ui.tab_panel(tab1):
            render_text_to_docx_tab(session)
        with ui.tab_panel(tab2):
            render_docx_analysis_tab(session)

    render_footer()

def render_header():
    ui.html('<h1 style="text-align: center; color: #2563eb;">📄 文檔處理系統</h1>')
    ui.html('<p style="text-align: center; color: #64748b;">支持文字轉 docx 和文檔內容分析</p>')

def render_footer():
    ui.separator().classes('mt-8')
    ui.html("""
        <div style="text-align: center; padding: 20px; color: #64748b;">
            <p>🔧 多用戶文檔處理系統 | 支持並發使用</p>
            <p><small>支持的格式: .txt, .md, .docx | 文件大小限制: 10MB</small></p>
        </div>
    """)

def render_text_to_docx_tab(session):
    ui.html('<h2>📝 文字轉 docx</h2>')
    ui.html('<p>上傳文字檔案或直接輸入文字，系統將生成 docx 文檔供您下載。</p>')

    with ui.card().classes('w-full max-w-4xl mx-auto'):
        text_input = ui.textarea(
            label='輸入文字內容',
            placeholder='請輸入要轉換的文字內容...'
        ).classes('w-full').style('min-height: 200px;')

        ui.separator()
        ui.label('或上傳文字檔案 (.txt, .md):')

        def handle_text_upload(e):
            try:
                if not e.name.lower().endswith(('.txt', '.md')):
                    ui.notify('請上傳 .txt 或 .md 文件！', type='warning')
                    return
                content = e.content.read().decode('utf-8')
                text_input.value = content
                ui.notify(f'文件 "{e.name}" 上傳成功！', type='positive')
            except Exception as ex:
                ui.notify(f'文件上傳失敗: {str(ex)}', type='negative')

        ui.upload(on_upload=handle_text_upload, auto_upload=True).classes('w-full')
        ui.separator()

        def convert_to_docx():
            if not text_input.value.strip():
                ui.notify('請輸入文字內容或上傳文件！', type='warning')
                return
            #try:
            filename = f"converted_{uuid.uuid4().hex[:8]}.docx"
            filepath = DocumentProcessor.text_to_docx(text_input, filename)
            #session.generated_files.append(filepath)
            ui.download(filepath, filename)
            ui.notify('文檔生成成功！', type='positive')
            #except Exception as ex:
            #    ui.notify(f'轉換失敗: {str(ex)}', type='negative')

        ui.button('🔄 轉換為 docx', on_click=convert_to_docx).classes('w-full')

def render_docx_analysis_tab(session):
    ui.html('<h2>🔍 docx 文檔分析</h2>')
    ui.html('<p>上傳 docx 文檔，系統將分析其中的破音字和異體字，並生成詳細報告。</p>')

    with ui.card().classes('w-full max-w-4xl mx-auto'):
        upload_result = ui.label('').classes('mt-4')
        download_area = ui.column().classes('w-full mt-4')

        def handle_docx_upload(e):
            try:
                if not e.name.lower().endswith('.docx'):
                    ui.notify('請上傳 .docx 文件！', type='warning')
                    return

                temp_path = TEMP_DIR / f"upload_{uuid.uuid4().hex[:8]}_{e.name}"
                with open(temp_path, 'wb') as f:
                    f.write(e.content.read())

                upload_result.text = f'正在分析文件: {e.name}...'
                upload_result.classes('text-blue-600')

                polyphone_path, variant_path = DocumentProcessor.process_docx_file(str(temp_path))

                download_area.clear()
                with download_area:
                    render_download_buttons(polyphone_path, variant_path)

                upload_result.text = f'✅ 文件 "{e.name}" 分析完成！請下載報告查看結果。'
                upload_result.classes('text-green-600')
                os.unlink(temp_path)
            except Exception as ex:
                upload_result.text = f'❌ 處理失敗: {str(ex)}'
                upload_result.classes('text-red-600')
                traceback.print_exc()    

        ui.label('選擇 docx 文件上傳:')
        ui.upload(
            on_upload=handle_docx_upload,
            auto_upload=True,
            max_file_size=10_000_000
        ).classes('w-full')

def render_download_buttons(polyphone_path, variant_path):
    ui.html('<h3>📥 分析結果下載</h3>')
    with ui.row().classes('w-full gap-4'):
        with ui.card().classes('flex-1'):
            ui.html('<h4>🔤 破音字報告</h4>')
            ui.html('<p>檢查文檔中可能存在讀音歧義的字詞</p>')
            ui.button('下載破音字報告',
                      on_click=lambda: ui.download(polyphone_path, Path(polyphone_path).name),
                      icon='download').classes('w-full')

        with ui.card().classes('flex-1'):
            ui.html('<h4>📝 異體字報告</h4>')
            ui.html('<p>檢查文檔中的異體字使用情況</p>')
            ui.button('下載異體字報告',
                      on_click=lambda: ui.download(variant_path, Path(variant_path).name),
                      icon='download').classes('w-full')
