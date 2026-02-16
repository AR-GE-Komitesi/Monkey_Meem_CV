"""
Hero Pose Mimic - Ana uygulama
Kamera ile poz algilayip super kahraman eslestirir
PyQt5 arayuz + MediaPipe pose detection
"""

import sys
import os
import cv2
import threading
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont


def _open_camera_worker(result, index, backend):
    """Kamerayi ayri thread'de ac (hang onleme)"""
    try:
        cap = cv2.VideoCapture(index, backend)
        result.append(cap)
    except Exception:
        pass


def open_camera_safe(index=0, timeout=20):
    """Kamera acmayi timeout ile dene - hang ederse None dondur"""
    backends = [cv2.CAP_MSMF, cv2.CAP_DSHOW, cv2.CAP_ANY]
    print(f"[Kamera] Acilisi baslatiliyor (timeout={timeout}s)...")
    
    for backend in backends:
        backend_name = {cv2.CAP_MSMF: "MSMF", cv2.CAP_DSHOW: "DSHOW", cv2.CAP_ANY: "ANY"}.get(backend, str(backend))
        print(f"[Kamera] {backend_name} backend'i deneniyor...")
        
        result = []
        t = threading.Thread(target=_open_camera_worker, args=(result, index, backend), daemon=True)
        t.start()
        t.join(timeout)
        
        if t.is_alive():
            print(f"[Kamera] {backend_name} timeout oldu, sonraki deneniyor...")
            continue
        
        if result and result[0].isOpened():
            print(f"[Kamera] BASARILI: {backend_name} backend'i ile acildi!")
            return result[0]
        
        if result:
            try:
                result[0].release()
            except:
                pass
        
        print(f"[Kamera] {backend_name} acalamadi")
    
    print("[Kamera] HATA: Hicbir backend ile acalamadi!")
    return None

try:
    from pose_detector import PoseDetector
    print("MediaPipe ile pose detection aktif!")
except ImportError:
    print("=" * 60)
    print("HATA: MediaPipe bulunamadi!")
    print("=" * 60)
    print(f"Python versiyonu: {sys.version}")
    print()
    print("MediaPipe sadece Python 3.12 ve altinda calisir.")
    print("Python 3.13 kullaniyorsaniz:")
    print()
    print("1. Python 3.12 yukleyin:")
    print("   https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe")
    print()
    print("2. Su komutla calistirin:")
    print("   py -3.12 main.py")
    print()
    print("VEYA:")
    print("   calistir.bat dosyasina cift tiklayin")
    print()
    print("=" * 60)
    sys.exit(1)

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