@echo off
echo Namestitev BioNaloga...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo NAPAKA: Python ni najden.
    echo Namestite Python z https://www.python.org/downloads/
    echo Med namestitvijo obkljukajte "Add Python to PATH".
    pause
    exit /b 1
)

echo Ustvarjam virtualno okolje...
python -m venv .venv
if errorlevel 1 (
    echo NAPAKA: Ustvarjanje virtualnega okolja ni uspelo.
    pause
    exit /b 1
)

echo Nameščam odvisnosti...
.venv\Scripts\pip install -q -r requirements.txt
if errorlevel 1 (
    echo NAPAKA: Namestitev odvisnosti ni uspela.
    pause
    exit /b 1
)

echo.
echo Namestitev uspesna! Za zagon aplikacije uporabite start.bat
pause
