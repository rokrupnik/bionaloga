@echo off
if not exist .venv\Scripts\activate (
    echo NAPAKA: Virtualno okolje ne obstaja.
    echo Najprej zazenite namesti.bat
    pause
    exit /b 1
)

call .venv\Scripts\activate
python -m bionaloga
