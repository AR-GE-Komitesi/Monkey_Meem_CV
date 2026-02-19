@echo off
chcp 65001 >nul
echo.
echo =======================================
echo   Monkey Pose Mimic - Docker Başlatıcı
echo =======================================
echo.

REM ── 1. Docker Desktop çalışıyor mu? ──────────────────────────────────────
docker info >nul 2>&1
if errorlevel 1 (
    echo [HATA] Docker Desktop çalışmıyor!
    echo.
    echo Lütfen Docker Desktop'u başlatın ve tekrar deneyin.
    echo İndirme: https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)
echo [OK] Docker hazır
echo.

REM ── 2. VcXsrv (GUI penceresini göstermek için X11 sunucusu) ──────────────
tasklist /fi "imagename eq vcxsrv.exe" 2>nul | find /i "vcxsrv.exe" >nul
if errorlevel 1 (
    set "VCXSRV=C:\Program Files\VcXsrv\vcxsrv.exe"
    if exist "%VCXSRV%" (
        echo [BAŞLATILIYOR] VcXsrv başlatılıyor...
        start "" "%VCXSRV%" :0 -multiwindow -clipboard -noprimary -wgl -ac
        timeout /t 3 /nobreak >nul
        echo [OK] VcXsrv başlatıldı
    ) else (
        echo [HATA] VcXsrv bulunamadı!
        echo.
        echo Docker ile GUI gösterebilmek için VcXsrv kurulu olmalı.
        echo.
        echo  Kurulum adımları:
        echo   1. https://sourceforge.net/projects/vcxsrv/ adresinden indirin
        echo   2. Kurulumda "Full installation" seçin
        echo   3. İlk çalıştırmada "Disable access control" işaretleyin
        echo   4. Bu dosyayı tekrar çalıştırın
        echo.
        pause
        exit /b 1
    )
) else (
    echo [OK] VcXsrv zaten çalışıyor
)
echo.

REM ── 3. Kamera notu ───────────────────────────────────────────────────────
echo [BİLGİ] Kamera hakkında:
echo   Windows Docker'da kamera için WSL2 + usbipd-win gereklidir.
echo   Kamera olmadan uygulama açılır, kamera hatası diyalog olarak görünür.
echo   WSL2 kullanıyorsanız: docker_calistir.sh scriptini kullanın.
echo.

REM ── 4. Docker image build ─────────────────────────────────────────────────
echo [BUILD] Image oluşturuluyor... (ilk seferinde 3-5 dakika sürebilir)
echo.
docker compose build
if errorlevel 1 (
    echo.
    echo [HATA] Build başarısız!
    pause
    exit /b 1
)
echo.
echo [OK] Image hazır
echo.

REM ── 5. Çalıştır ───────────────────────────────────────────────────────────
echo [BAŞLATILIYOR] Uygulama açılıyor...
echo   Pencereyi kapatarak çıkabilirsiniz.
echo.
docker run --rm ^
    -e DISPLAY=host.docker.internal:0.0 ^
    -e QT_X11_NO_MITSHM=1 ^
    --network host ^
    monkey-pose-mimic:latest

if errorlevel 1 (
    echo.
    echo [HATA] Uygulama kapandı.
    echo.
    echo  Sorun giderme:
    echo   1. VcXsrv çalışırken "Disable access control" işaretli olmalı
    echo   2. Windows Güvenlik Duvarı VcXsrv'e izin vermeli
    echo      ^(İlk açılışta "Erişime izin ver" deyin^)
    echo.
    pause
)
