@ECHO OFF
START cmd /k "cd /d catalogue_server\.venv\Scripts & activate & cd .. & cd .. & python app.py"
START cmd /k "cd /d data_base\.venv\Scripts & activate & cd .. & cd .. & python app.py"
START cmd /k "cd /d telegram_bot\.venv\Scripts & activate & cd .. & cd .. & python main.py"