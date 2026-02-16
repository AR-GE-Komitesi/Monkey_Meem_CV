# 🦸 Hero Pose Mimic

Real-time pose detection ile etkileşimli süper kahraman taklit uygulaması.

---

## 🎯 Nedir?

Kamera önünde verdiğiniz pozları algılayan ve ekrandaki süper kahraman görseli ile eşleştiren masaüstü uygulaması.

**Desteklenen Süper Kahramanlar:**
- ⚡ **Thor** — El yukarı kaldırma (Mjolnir pozu)
- 🤖 **Iron Man** — Avuç ileri (Repulsor blast)
- 🐾 **Black Panther** — Kollar göğüste çapraz (Wakanda Forever)
- 🕷️ **Spider-Man** — Ağız açık / şaşırma (Spider-Sense)

---

## 🚀 Kurulum

### 1. Python 3.12 kurun
⚠️ **Önemli:** MediaPipe Python 3.13'te çalışmaz!

📥 [Python 3.12.8 İndir](https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe)

### 2. Projeyi indirin
```bash
git clone https://github.com/beyzatanriverdi/hero_pose_mimic
cd hero-pose-mimic
```

### 3. Kütüphaneleri yükleyin
```bash
py -3.12 -m pip install opencv-python mediapipe PyQt5 numpy
```

---

## 💻 Çalıştırma

**Kolay yol:**
```bash
calistir.bat
```

**Manuel:**
```bash
py -3.12 main.py
```

---

## 🛠️ Teknolojiler

- **Python 3.12** - Ana dil
- **MediaPipe** - Pose detection
- **OpenCV** - Görüntü işleme
- **PyQt5** - GUI
- **NumPy** - Hesaplamalar

---

## 📁 Proje Yapısı

```
hero-pose-mimic/
├── main.py              # Ana uygulama
├── pose_detector.py     # Pose algılama (4 kahraman)
├── requirements.txt     # Bağımlılıklar
├── calistir.bat        # Başlatma scripti
└── assets/             # Süper kahraman görselleri
    ├── b.jpg           # Thor
    ├── ironman.jpg     # Iron Man
    ├── black-panther-*.jpg  # Black Panther
    └── c.jpg           # Spider-Man
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
