pyinstaller --onefile --icon=icon.icns DB_mgr_GUI.py
pyinstaller --onefile --windowed main.py

# 打包 ARM：
pyinstaller --onefile --name DB_mgr_GUI_arm --icon=icon.icns --distpath build_universal DB_mgr_GUI.py

# 打包 Intel（記得進入 venv_x86）：
source venv_x86/bin/activate
pyinstaller --onefile --windowed --name DB_mgr_GUI_intel --icon=icon.icns --distpath build_universal 
DB_mgr_GUI.py

