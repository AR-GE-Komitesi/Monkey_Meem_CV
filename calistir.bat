@echo off
chcp 65001 >nul

REM --- Her zaman kendi klasorunden calistir ---
cd /d "%~dp0"

echo.
echo =======================================
echo   Hero Pose Mimic - Super Kahraman
echo =======================================
echo.

REM --- Uyumlu Python bul: 3.12 > 3.11 > 3.10 ---
set PYTHON_EXE=

py -3.12 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_EXE=py -3.12
    goto :python_found
)

py -3.11 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_EXE=py -3.11
    goto :python_found
)

py -3.10 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_EXE=py -3.10
    goto :python_found
)

echo [HATA] Uyumlu Python bulunamadi!
echo.
echo MediaPipe icin Python 3.10, 3.11 veya 3.12 gereklidir.
echo Python 3.13 ve uzeri DESTEKLENMEZ.
echo.
echo Birini indirin ve kurun (kurulumda "Add to PATH" secin):
echo   Python 3.12 ^(onerilen^): https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe
echo   Python 3.11            : https://www.python.org/ftp/python/3.11.11/python-3.11.11-amd64.exe
echo.
pause
exit /b 1

:python_found
echo [OK] Python bulundu:
%PYTHON_EXE% --version
echo.

REM --- Sanal ortam olustur (ilk calistirmada bir kez) ---
if not exist ".venv\Scripts\activate.bat" (
    echo [KURULUYOR] Sanal ortam olusturuluyor...
    %PYTHON_EXE% -m venv .venv
    if errorlevel 1 (
        echo [HATA] Sanal ortam olusturulamadi!
        pause
        exit /b 1
    )
    echo [OK] Sanal ortam olusturuldu
    echo.
)

REM --- Kütüphaneleri kontrol et, yoksa lock dosyasından yükle ---
.venv\Scripts\python.exe -c "import mediapipe, cv2, PyQt5, numpy" >nul 2>&1
if errorlevel 1 (
    echo [KURULUYOR] Kutuphaneler yukleniyor, lutfen bekleyin...
    echo.
    .venv\Scripts\python.exe -m pip install --upgrade pip --quiet
    .venv\Scripts\python.exe -m pip install -r requirements.lock
    if errorlevel 1 (
        echo.
        echo [HATA] Kutuphaneler yuklenemedi!
        pause
        exit /b 1
    )
    echo.
    echo [OK] Kutuphaneler basariyla yuklendi
    echo.
) else (
    echo [OK] Kutuphaneler hazir
    echo.
)

REM --- Uygulamayi baslat ---
echo [BASLATILIYOR] Uygulama aciliyor...
echo.
.venv\Scripts\python.exe main.py

if errorlevel 1 (
    echo.
    echo [HATA] Uygulama hatayla kapandi!
    echo Yukaridaki hata mesajini okuyun.
    pause
)

