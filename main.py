"""
Monkey Pose Mimic - Ana uygulama
PyQt5 arayüz + MediaPipe pose detection
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

import cv2
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont

from pose_detector import PoseDetector


class MonkeyPoseApp(QMainWindow):
    """Ana uygulama penceresi"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Monkey Pose Mimic (MediaPipe)")
        self.setGeometry(100, 100, 1200, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLabel {
                border: 2px solid #444;
                border-radius: 10px;
                background-color: #1e1e1e;
            }
        """)
        
        # Kamera başlat (CAP_DSHOW sadece Windows'ta daha kararlı, diğer platformlarda varsayılan)
        _backend = cv2.CAP_DSHOW if platform.system() == "Windows" else cv2.CAP_ANY
        self.camera = cv2.VideoCapture(0, _backend)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not self.camera.isOpened():
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Kamera Bulunamadı")
            msg.setText("Kamera açılamadı!")
            msg.setInformativeText(
                "Lütfen şunları kontrol edin:\n"
                "• Bilgisayarınızda kamera var mı?\n"
                "• Kamera başka bir uygulama tarafından kullanılıyor mu?\n"
                "• Kamera sürücüleri kurulu mu?"
            )
            msg.exec_()
            sys.exit(1)
        
        # Pose detector
        self.pose_detector = PoseDetector()
        
        # Maymun resimleri
        self.monkey_images = self._load_monkey_images()
        self.current_pose = "default"
        
        # UI oluştur
        self._setup_ui()
        
        # Timer (40 FPS - daha akıcı)
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)
        self.timer.start(25)
    
    def _setup_ui(self):
        """Arayüz oluştur"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Sol - Kamera
        left_layout = QVBoxLayout()
        
        camera_title = QLabel("📷 Canlı Kamera")
        camera_title.setFont(QFont("Arial", 14, QFont.Bold))
        camera_title.setAlignment(Qt.AlignCenter)
        camera_title.setStyleSheet("QLabel { color: #fff; border: none; background: transparent; padding: 5px; }")
        camera_title.setMaximumHeight(40)
        
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setScaledContents(True)
        
        left_layout.addWidget(camera_title, 0)
        left_layout.addWidget(self.camera_label, 1)
        left_layout.setSpacing(5)
        
        # Sağ - Maymun
        right_layout = QVBoxLayout()
        
        monkey_title = QLabel("🐵 Maymun Pozu")
        monkey_title.setFont(QFont("Arial", 14, QFont.Bold))
        monkey_title.setAlignment(Qt.AlignCenter)
        monkey_title.setStyleSheet("QLabel { color: #fff; border: none; background: transparent; padding: 5px; }")
        monkey_title.setMaximumHeight(40)
        
        self.monkey_label = QLabel()
        self.monkey_label.setMinimumSize(480, 480)
        self.monkey_label.setAlignment(Qt.AlignCenter)
        self.monkey_label.setScaledContents(True)
        
        self.pose_name_label = QLabel("Normal Duruş")
        self.pose_name_label.setFont(QFont("Arial", 12))
        self.pose_name_label.setAlignment(Qt.AlignCenter)
        self.pose_name_label.setStyleSheet("QLabel { color: #4CAF50; border: none; background: transparent; padding: 5px; }")
        self.pose_name_label.setMaximumHeight(35)
        
        right_layout.addWidget(monkey_title, 0)
        right_layout.addWidget(self.monkey_label, 1)
        right_layout.addWidget(self.pose_name_label, 0)
        right_layout.setSpacing(5)
        
        main_layout.addLayout(left_layout, 60)
        main_layout.addLayout(right_layout, 40)
        
        self._update_monkey_image("default")
    
    def _load_monkey_images(self):
        """Maymun resimlerini yükle"""
        assets_dir = Path(__file__).parent / "assets"
        images = {}
        pose_files = {
            "raising_hand": "raising_hand_pose.jpg",
            "shocking": "shocking_pose.jpg",
            "thinking": "thinking_pose.jpg",
            "default": "default_pose.jpg"
        }
        
        for pose, filename in pose_files.items():
            image_path = assets_dir / filename
            if image_path.exists():
                images[pose] = str(image_path)
            else:
                print(f"Uyarı: {image_path} bulunamadı!")
                images[pose] = None
        
        return images
    
    def _update_frame(self):
        """Kamera frame güncelle"""
        ret, frame = self.camera.read()
        if not ret:
            return
        
        # Ayna efekti kaldır
        frame = cv2.flip(frame, 1)
        
        # Pose detection
        processed_frame, pose_name = self.pose_detector.detect_pose(frame)
        
        # Kamera göster - direkt pixmap, Qt otomatik ölçeklendirir
        rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        qt_image = QImage(rgb_frame.data, w, h, ch * w, QImage.Format_RGB888)
        
        pixmap = QPixmap.fromImage(qt_image)
        self.camera_label.setPixmap(pixmap)
        
        # Poz değişti mi
        if pose_name != self.current_pose:
            self.current_pose = pose_name
            self._update_monkey_image(pose_name)
    
    def _update_monkey_image(self, pose_name):
        """Maymun resmini güncelle"""
        image_path = self.monkey_images.get(pose_name)
        
        if image_path:
            pixmap = QPixmap(image_path)
            self.monkey_label.setPixmap(pixmap)  # Qt otomatik ölçeklendirir
        else:
            self.monkey_label.setText(f"{pose_name}\n\n(Resim bulunamadı)")
            self.monkey_label.setStyleSheet("QLabel { color: #ff9800; font-size: 16px; border: 2px dashed #444; }")
        
        pose_names = {
            "raising_hand": "☝️ İşaret Parmağı Yukarıda",
            "shocking": "😲 Ağız Açık (Şaşkınlık)",
            "thinking": "🤔 El Yüzde (Düşünme)",
            "default": "😊 Normal Duruş"
        }
        self.pose_name_label.setText(pose_names.get(pose_name, pose_name))
    
    def closeEvent(self, event):
        """Kaynakları temizle"""
        self.timer.stop()
        self.camera.release()
        self.pose_detector.release()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MonkeyPoseApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
