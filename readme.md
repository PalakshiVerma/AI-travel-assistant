#Backend command
.\venv\Scripts\python.exe -m uvicorn src.main:app --reload

#Frontend command
.\venv\Scripts\python.exe -m streamlit run src/app.py

#activated  virtual environment  
.\venv\Scripts\Activate.ps1