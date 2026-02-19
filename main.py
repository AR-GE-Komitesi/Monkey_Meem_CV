"""
Hero Pose Mimic - Ana uygulama
Kamera ile poz algilayip super kahraman eslestirir
PyQt5 arayuz + MediaPipe pose detection
"""

# ─── Bootstrap ───────────────────────────────────────────────────────────────
# main.py doğrudan çalıştırılsa bile:
#   1. Python sürümü yanlışsa uyumlu olanı bulur, yoksa otomatik indirir/kurar
#   2. .venv yoksa oluşturur
#   3. Paketler yoksa requirements.lock'tan kurar
#   4. Her şey hazır olunca bu scripti .venv Python'u ile yeniden başlatır
# ─────────────────────────────────────────────────────────────────────────────

import sys
import subprocess
import platform
from pathlib import Path


def _find_compatible_python():
    """Python 3.12 → 3.11 → 3.10 sırasıyla arar, bulunanın tam yolunu döner."""
    for version in ["3.12", "3.11", "3.10"]:
        if platform.system() == "Windows":
            cmd = ["py", f"-{version}", "-c", "import sys; print(sys.executable)"]
        else:
            cmd = [f"python{version}", "-c", "import sys; print(sys.executable)"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if r.returncode == 0:
                path = r.stdout.strip()
                if path and Path(path).exists():
                    print(f"[OK] Python {version} bulundu: {path}")
                    return path
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return None


def _install_python_311():
    """Windows'ta Python 3.11'i winget ile, yoksa sessiz installer ile kurar."""
    if platform.system() != "Windows":
        return None

    print("[KURULUM] winget ile Python 3.11 kuruluyor...")
    r = subprocess.run([
        "winget", "install", "Python.Python.3.11",
        "--silent", "--accept-package-agreements", "--accept-source-agreements",
    ])
    if r.returncode == 0:
        found = _find_compatible_python()
        if found:
            return found

    print("[KURULUM] winget başarısız, installer indiriliyor (~27 MB)...")
    return _download_python_311()


def _download_python_311():
    """python.org'dan Python 3.11 installer indir ve sessizce kur."""
    import urllib.request
    import tempfile
    import urllib.error

    url       = "https://www.python.org/ftp/python/3.11.11/python-3.11.11-amd64.exe"
    installer = Path(tempfile.gettempdir()) / "python-3.11.11-amd64.exe"

    try:
        def _progress(count, block, total):
            if total > 0:
                pct = min(count * block * 100 // total, 100)
                print(f"\r  %{pct:3d} indiriliyor...", end="", flush=True)
        urllib.request.urlretrieve(url, str(installer), _progress)
        print()
    except urllib.error.URLError as e:
        print(f"\n[HATA] İndirme başarısız: {e}")
        return None

    print("[KURULUYOR] Python 3.11 kuruluyor (birkaç dakika sürebilir)...")
    r = subprocess.run([
        str(installer), "/quiet",
        "InstallAllUsers=0", "PrependPath=1",
        "Include_test=0", "Include_doc=0",
    ])
    try:
        installer.unlink()
    except OSError:
        pass

    if r.returncode == 0:
        print("[OK] Python 3.11 kuruldu")
        return _find_compatible_python()

    print(f"[HATA] Kurulum başarısız (kod: {r.returncode})")
    return None


def _fatal(msg):
    print("\n" + "=" * 60)
    print("HATA:", msg)
    print("=" * 60)
    input("\nÇıkmak için Enter'a basın...")
    sys.exit(1)


def _bootstrap():
    SCRIPT_DIR  = Path(__file__).parent.resolve()
    VENV_DIR    = SCRIPT_DIR / ".venv"
    IS_WIN      = platform.system() == "Windows"
    VENV_PYTHON = str(VENV_DIR / ("Scripts/python.exe" if IS_WIN else "bin/python"))
    REQ_FILE    = SCRIPT_DIR / "requirements.lock"
    if not REQ_FILE.exists():
        REQ_FILE = SCRIPT_DIR / "requirements.txt"

    # ── Zaten bu projenin .venv'i içinde mi? → Doğrudan devam et ────────────
    if Path(sys.executable).resolve() == Path(VENV_PYTHON).resolve():
        return

    # ── Mevcut Python uyumlu mu? ─────────────────────────────────────────────
    ver = sys.version_info
    if (3, 10) <= (ver.major, ver.minor) <= (3, 12):
        target_python = sys.executable
    else:
        print(f"[UYARI] Python {ver.major}.{ver.minor} desteklenmiyor (gerekli: 3.10–3.12)")
        target_python = _find_compatible_python()
        if not target_python:
            print("[KURULUM] Uyumlu Python bulunamadı, Python 3.11 kuruluyor...")
            target_python = _install_python_311()
        if not target_python:
            _fatal(
                "Python 3.11 kurulamadı!\n"
                "Lütfen https://www.python.org/ftp/python/3.11.11/python-3.11.11-amd64.exe\n"
                "adresinden indirip kurun, ardından bu scripti tekrar çalıştırın."
            )

    # ── .venv oluştur (yoksa) ────────────────────────────────────────────────
    if not Path(VENV_PYTHON).exists():
        print("[KURULUM] Sanal ortam oluşturuluyor...")
        r = subprocess.run([target_python, "-m", "venv", str(VENV_DIR)])
        if r.returncode != 0:
            _fatal("Sanal ortam oluşturulamadı!")
        print("[OK] Sanal ortam hazır")

    # ── Paketleri kur (yoksa) ────────────────────────────────────────────────
    check = subprocess.run(
        [VENV_PYTHON, "-c", "import mediapipe, cv2, PyQt5, numpy"],
        capture_output=True,
    )
    if check.returncode != 0:
        print("[KURULUM] Paketler yükleniyor (ilk kurulumda ~2-3 dk sürebilir)...")
        r = subprocess.run([VENV_PYTHON, "-m", "pip", "install", "--upgrade", "pip", "-q"])
        if r.returncode != 0:
            _fatal("pip güncellenemedi!")
        r = subprocess.run([VENV_PYTHON, "-m", "pip", "install", "-r", str(REQ_FILE)])
        if r.returncode != 0:
            _fatal("Paketler yüklenemedi! İnternet bağlantısını kontrol edin.")
        print("[OK] Paketler hazır\n")

    # ── Bu scripti .venv Python'u ile yeniden başlat ─────────────────────────
    print("[BAŞLATILIYOR] Uygulama başlatılıyor...\n")
    result = subprocess.run([VENV_PYTHON, str(Path(__file__).resolve())] + sys.argv[1:])
    sys.exit(result.returncode)


_bootstrap()
# ─── Bootstrap sonu ──────────────────────────────────────────────────────────

import os
import cv2
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont
from pose_detector import PoseDetector

# Mutlak yol - hangi dizinden calistirilirsa calistirilsin dogru bulur
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')


class HeroPoseApp(QMainWindow):
    """Ana uygulama penceresi - Super Kahraman Pose Mimic"""

    # Kahraman renkleri (UI tema)
    HERO_COLORS = {
        "ironman_snap": "#FF8F00",  # Altin (Infinity Gauntlet)
        "ironman":      "#EF5350",  # Kirmizi (Repulsor)
        "blackpanther": "#AB47BC",  # Mor (vibranium)
        "spiderman":    "#E53935",  # Kirmizi-mavi
        "default":      "#4CAF50",  # Yesil
    }

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hero Pose Mimic - Super Kahraman Poz Taklidi")
        self.setGeometry(100, 100, 1280, 650)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
            QLabel {
                border: 2px solid #333;
                border-radius: 10px;
                background-color: #16213e;
            }
        """)

        print("Kamera aciliyor (timeout=10s)...")
        self.camera = open_camera_safe(index=0, timeout=10)
        if self.camera is not None:
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        else:
            print("Kamera baglanamiyor - sadece resimler gosterilecek.")

        self.pose_detector = PoseDetector()
        self.hero_images = self._load_hero_images()
        self.current_pose = "default"

        self._setup_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)
        self.timer.start(25)

    def _setup_ui(self):
        """Arayuz olustur"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Sol: Kamera
        left_layout = QVBoxLayout()
        camera_title = QLabel("Canli Kamera")
        camera_title.setFont(QFont("Arial", 14, QFont.Bold))
        camera_title.setAlignment(Qt.AlignCenter)
        camera_title.setStyleSheet("QLabel { color: #e0e0e0; border: none; background: transparent; padding: 5px; }")
        camera_title.setMaximumHeight(40)

        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setScaledContents(True)

        left_layout.addWidget(camera_title, 0)
        left_layout.addWidget(self.camera_label, 1)
        left_layout.setSpacing(5)

        # Sag: Super Kahraman
        right_layout = QVBoxLayout()
        self.hero_title = QLabel("Super Kahraman")
        self.hero_title.setFont(QFont("Arial", 14, QFont.Bold))
        self.hero_title.setAlignment(Qt.AlignCenter)
        self.hero_title.setStyleSheet("QLabel { color: #e0e0e0; border: none; background: transparent; padding: 5px; }")
        self.hero_title.setMaximumHeight(40)

        self.hero_label = QLabel()
        self.hero_label.setMinimumSize(480, 480)
        self.hero_label.setAlignment(Qt.AlignCenter)
        self.hero_label.setScaledContents(True)

        self.pose_name_label = QLabel("Bir Super Kahraman Pozu Yap!")
        self.pose_name_label.setFont(QFont("Arial", 13, QFont.Bold))
        self.pose_name_label.setAlignment(Qt.AlignCenter)
        self.pose_name_label.setStyleSheet("QLabel { color: #4CAF50; border: none; background: transparent; padding: 5px; }")
        self.pose_name_label.setMaximumHeight(40)

        right_layout.addWidget(self.hero_title, 0)
        right_layout.addWidget(self.hero_label, 1)
        right_layout.addWidget(self.pose_name_label, 0)
        right_layout.setSpacing(5)

        main_layout.addLayout(left_layout, 55)
        main_layout.addLayout(right_layout, 45)

        self._update_hero_image("default")

    def _load_hero_images(self):
        """Super kahraman resimlerini yukle"""
        assets_dir = Path(ASSETS_DIR)
        images = {}
        pose_files = {
            "ironman_snap": "c.jpg",
            "ironman":      "ironman.jpg",
            "blackpanther": "black-panther-a4ad45f2c272490cbf8d569e0bd0bf85.jpg",
            "spiderman":    "b.jpg",
        }
        for hero, filename in pose_files.items():
            image_path = assets_dir / filename
            if image_path.exists():
                images[hero] = str(image_path)
                print(f"[Gorsel] {hero.upper()} yuklendi: {filename}")
            else:
                print(f"Uyari: {image_path} bulunamadi!")
                images[hero] = None
        return images

    def _update_frame(self):
        """Kamera frame guncelle"""
        if self.camera is None or not self.camera.isOpened():
            return

        ret, frame = self.camera.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)
        processed_frame, pose_name = self.pose_detector.detect_pose(frame)

        rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        qt_image = QImage(rgb_frame.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.camera_label.setPixmap(pixmap)

        if pose_name != self.current_pose:
            self.current_pose = pose_name
            self._update_hero_image(pose_name)

    def _update_hero_image(self, pose_name):
        """Super kahraman resmini guncelle"""
        image_path = self.hero_images.get(pose_name)
        color = self.HERO_COLORS.get(pose_name, "#4CAF50")

        if image_path:
            pixmap = QPixmap(image_path)
            self.hero_label.setPixmap(pixmap)
            self.hero_label.setStyleSheet(
                f"QLabel {{ border: 3px solid {color}; border-radius: 10px; background-color: #16213e; }}")
        else:
            # Default: bekleme ekrani
            self.hero_label.clear()
            self.hero_label.setText(
                "Bir poz yap!\n\n"
                "Parmak Siklat  =  Iron Man (Snap)\n"
                "Avuc Acik Kaldir  =  Iron Man (Repulsor)\n"
                "Kollar Capraz  =  Black Panther\n"
                "Ag Atma Isareti  =  Spider-Man"
            )
            self.hero_label.setStyleSheet(
                "QLabel { color: #aaa; font-size: 18px; border: 2px dashed #444; "
                "border-radius: 10px; background-color: #16213e; }")

        # Kahraman adi ve poz aciklamasi
        hero_info = {
            "ironman_snap": ("IRON MAN", "I Am Iron Man! (Parmak Siklama)"),
            "ironman":      ("IRON MAN", "Repulsor Blast (Avuc Acik Kaldir)"),
            "blackpanther": ("BLACK PANTHER", "Wakanda Forever (Kollar Capraz)"),
            "spiderman":    ("SPIDER-MAN", "Web Shooter (Ag Atma Isareti)"),
            "default":      ("", "Bir Super Kahraman Pozu Yap!"),
        }
        hero_name, pose_desc = hero_info.get(pose_name, ("", pose_name))

        if hero_name:
            self.hero_title.setText(hero_name)
            self.hero_title.setStyleSheet(
                f"QLabel {{ color: {color}; border: none; background: transparent; padding: 5px; }}")
        else:
            self.hero_title.setText("Super Kahraman")
            self.hero_title.setStyleSheet(
                "QLabel { color: #e0e0e0; border: none; background: transparent; padding: 5px; }")

        self.pose_name_label.setText(pose_desc)
        self.pose_name_label.setStyleSheet(
            f"QLabel {{ color: {color}; border: none; background: transparent; padding: 5px; }}")

    def closeEvent(self, event):
        """Kaynaklari temizle"""
        self.timer.stop()
        if self.camera is not None:
            self.camera.release()
        self.pose_detector.release()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = HeroPoseApp()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()