# ── Aşama 1: Bağımlılıkları kur ──────────────────────────────────────────────
FROM python:3.11-slim AS deps

WORKDIR /app

# pip önce güncelle, sonra lock dosyasından kur
# (requirements.lock değişmediği sürece bu layer cache'den gelir)
COPY requirements.lock .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.lock


# ── Aşama 2: Çalışma ortamı ──────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL description="Monkey Pose Mimic — MediaPipe tabanlı gerçek zamanlı poz tespit uygulaması"

# Sistem kütüphaneleri: OpenCV + Qt5 XCB + MediaPipe
RUN apt-get update && apt-get install -y --no-install-recommends \
    # OpenCV
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    # Qt5 / PyQt5 — XCB eklentileri (pencere sistemi)
    libx11-6 \
    libxcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxcb-cursor0 \
    libxkbcommon-x11-0 \
    libxcb-util1 \
    # Sistem destekleri
    libdbus-1-3 \
    libfontconfig1 \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Önceki aşamadan kurulu paketleri kopyala
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Uygulama dosyaları
COPY . .

# Qt: pencereli mod (XCB), paylaşımlı bellek sorunu kapatılıyor
ENV QT_QPA_PLATFORM=xcb
ENV QT_X11_NO_MITSHM=1
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
