#!/bin/bash
# Linux ve macOS için Docker başlatıcı
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================="
echo "  Monkey Pose Mimic - Docker Başlatıcı"
echo "======================================="
echo

# ── 1. Docker çalışıyor mu? ────────────────────────────────────────────────
if ! docker info > /dev/null 2>&1; then
    echo "[HATA] Docker çalışmıyor!"
    echo "  Linux: sudo systemctl start docker"
    echo "  Mac:   Docker Desktop uygulamasını açın"
    exit 1
fi
echo "[OK] Docker hazır"

# ── 2. Image build ─────────────────────────────────────────────────────────
echo "[BUILD] Image oluşturuluyor... (ilk seferinde 3-5 dakika sürebilir)"
echo
docker compose build
echo
echo "[OK] Image hazır"
echo

# ── 3. Platform tespiti ve run args ────────────────────────────────────────
OS="$(uname)"
DISPLAY_ARGS=()
CAMERA_ARGS=()

if [ "$OS" = "Linux" ]; then
    # X11 soketine erişim izni ver
    xhost +local:docker > /dev/null 2>&1 || \
        echo "[UYARI] xhost komutu bulunamadı — erişim sorunu yaşanabilir"
    DISPLAY_ARGS=(-e DISPLAY="$DISPLAY" -v /tmp/.X11-unix:/tmp/.X11-unix:rw)

    # Kamera var mı?
    if [ -e /dev/video0 ]; then
        CAMERA_ARGS=(--device /dev/video0:/dev/video0 --group-add video)
        echo "[OK] Kamera tespit edildi: /dev/video0"
    else
        echo "[UYARI] /dev/video0 bulunamadı — kamera devredışı"
        echo "  WSL2 kullanıyorsanız: https://learn.microsoft.com/en-us/windows/wsl/connect-usb"
    fi

elif [ "$OS" = "Darwin" ]; then
    # Mac: XQuartz gerekli
    if ! pgrep -x "Xquartz" > /dev/null 2>&1; then
        echo "[HATA] XQuartz çalışmıyor!"
        echo "  Kurulum: brew install --cask xquartz"
        echo "  Ardından: XQuartz > Settings > Security > Allow connections from network clients"
        exit 1
    fi
    xhost + 127.0.0.1 > /dev/null 2>&1 || true
    DISPLAY_ARGS=(-e DISPLAY=host.docker.internal:0)
    echo "[OK] XQuartz tespit edildi"
    echo "[UYARI] Mac'te kamera erişimi desteklenmiyor"
fi

echo

# ── 4. Çalıştır ────────────────────────────────────────────────────────────
echo "[BAŞLATILIYOR] Uygulama açılıyor..."
echo "  Kapatmak için: pencereyi kapatın veya Ctrl+C"
echo

docker run --rm \
    "${DISPLAY_ARGS[@]}" \
    "${CAMERA_ARGS[@]}" \
    --network host \
    monkey-pose-mimic:latest

# ── Temizlik ───────────────────────────────────────────────────────────────
if [ "$OS" = "Linux" ]; then
    xhost -local:docker > /dev/null 2>&1 || true
fi
