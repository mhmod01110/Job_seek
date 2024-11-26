@echo off
start cmd /k "python -m uvicorn server:app --reload"
start cmd /k "python client.py"

