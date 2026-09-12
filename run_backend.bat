@echo off
chcp 65001 >nul
cd /d D:\CropMind-main\CropMind-main\backend
set PYTHONPATH=D:\CropMind-main\CropMind-main;D:\CropMind-main\CropMind-main\backend
set PYTHONIOENCODING=utf-8
call venv\Scripts\activate.bat
python -c "import sqlite3; c=sqlite3.connect(\"cropmind.db\"); r=c.execute(\"SELECT COUNT(*) FROM farms\").fetchone()[0]; c.close(); exit(0 if r==0 else 1)" && python seed_data.py
python -c "import sqlite3; c=sqlite3.connect(\"cropmind.db\"); r=c.execute(\"SELECT COUNT(*) FROM users\").fetchone()[0]; c.close(); exit(0 if r==0 else 1)" && python create_admin.py
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
