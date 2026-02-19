# 🐵 Monkey Pose Mimic

Real-time pose detection ile etkileşimli maymun taklit uygulaması.

---

## 🎯 Nedir?

Kamera önünde verdiğiniz pozları algılayan ve ekrandaki maymun karakteriyle taklit eden masaüstü uygulaması.

**Desteklenen Pozlar:**
- ☝️ El kaldırma
- 😲 Şaşırma (ağız açık)
- 🤔 Düşünme (el yüzde)
- 😊 Varsayılan duruş

---

## 🚀 Kurulum ve Çalıştırma

### Tek adım (önerilen)

`calistir.bat` dosyasına **çift tıklayın** — gerisini otomatik yapar:
- Uyumlu Python sürümünü tespit eder
- Sanal ortam (`.venv`) oluşturur
- Gereken kütüphaneleri yükler
- Uygulamayı başlatır

### Gereksinimler

⚠️ **Python 3.10, 3.11 veya 3.12** kurulu olmalı — Python 3.13+ desteklenmez.

Eğer uyumlu Python yoksa:

| Sürüm | İndirme |
|-------|---------|
| Python 3.12 (önerilen) | [python-3.12.9-amd64.exe](https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe) |
| Python 3.11 | [python-3.11.11-amd64.exe](https://www.python.org/ftp/python/3.11.11/python-3.11.11-amd64.exe) |

> Kurulumda **"Add Python to PATH"** seçeneğini işaretleyin!

### Manuel çalıştırma (isteğe bağlı)

```bash
# Sanal ortam oluştur
py -3.12 -m venv .venv

# Kütüphaneleri yükle
.venv\Scripts\pip install -r requirements.txt

# Çalıştır
.venv\Scripts\python main.py
```

---

## � Docker ile Çalıştırma

Python kurmadan, tek komutla çalıştır. Kütüphane sürümleri her ortamda birebir aynı.

### Gereksinimler
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) kurulu ve çalışıyor olmalı
- **Windows** için ek olarak [VcXsrv](https://sourceforge.net/projects/vcxsrv/) (GUI ekranı için)
- **Mac** için [XQuartz](https://www.xquartz.org/)

### Çalıştırma

| Platform | Komut |
|----------|-------|
| **Windows** | `docker_calistir.bat` dosyasına çift tıkla |
| **Linux** | `bash docker_calistir.sh` |
| **Mac** | `bash docker_calistir.sh` |

### Kamera desteği

| Platform | Durum |
|----------|-------|
| Linux (native) | ✅ Otomatik |
| WSL2 + usbipd-win | ✅ [Kurulum rehberi](https://learn.microsoft.com/en-us/windows/wsl/connect-usb) |
| Windows Docker Desktop | ⚠️ Kamera çalışmaz, GUI açılır ve hata diyaloğu gösterir |
| Mac | ⚠️ Kamera erişimi yok |

> **Not:** Kamera olmadan uygulama açılır; sadece kamera bulunamadı diyaloğu gösterir.

---

## �🛠️ Teknolojiler

- **Python 3.12** - Ana dil
- **MediaPipe** - Pose detection
- **OpenCV** - Görüntü işleme
- **PyQt5** - GUI
- **NumPy** - Hesaplamalar

---

## 📁 Proje Yapısı

```
monkey-pose-mimic/
├── main.py              # Ana uygulama
├── pose_detector.py     # Pose algılama
├── requirements.txt     # Bağımlılıklar
├── calistir.bat        # Başlatma scripti
└── assets/             # Maymun görselleri
```

## 👨‍💻 Geliştiriciler

**[Beyza Tanrıverdi]**
**[Kadir Talha Uncu]**

📧 tnrvrd.beyza@gmail.com
📧 talhauncu.dev@gmail.com

🔗 [GitHub](https://github.com/beyzatanriverdi) • [LinkedIn](https://www.linkedin.com/in/beyza-tanrıverdi-8a46b0364)

🔗 [GitHub](https://github.com/talhauncu) • [LinkedIn](https://www.linkedin.com/in/kadir-talha-uncu-622186339)

---


---

<div align="center">

</div>
