"""
Monkey Pose Mimic - Ana uygulama
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

        print("Kamera aciliyor (timeout=10s)...")
        self.camera = open_camera_safe(index=0, timeout=10)
        if self.camera is not None:
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        else:
            print("Kamera baglanamiyor - sadece resimler gosterilecek.")

        self.pose_detector = PoseDetector()
        self.monkey_images = self._load_monkey_images()
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

        left_layout = QVBoxLayout()
        camera_title = QLabel("Canli Kamera")
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

        right_layout = QVBoxLayout()
        monkey_title = QLabel("Maymun Pozu")
        monkey_title.setFont(QFont("Arial", 14, QFont.Bold))
        monkey_title.setAlignment(Qt.AlignCenter)
        monkey_title.setStyleSheet("QLabel { color: #fff; border: none; background: transparent; padding: 5px; }")
        monkey_title.setMaximumHeight(40)

        self.monkey_label = QLabel()
        self.monkey_label.setMinimumSize(480, 480)
        self.monkey_label.setAlignment(Qt.AlignCenter)
        self.monkey_label.setScaledContents(True)

        self.pose_name_label = QLabel("Normal Durus")
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
        """Maymun resimlerini yukle (mutlak yol)"""
        assets_dir = Path(ASSETS_DIR)
        images = {}
        pose_files = {
            "raising_hand": "raising_hand_pose.jpg",
            "shocking": "shocking_pose.jpg",
            "thinking": "thinking_pose.jpg",
            "default": "default_pose.jpg",
            "ironman": "ironman.jpg",
        }
        for pose, filename in pose_files.items():
            image_path = assets_dir / filename
            if image_path.exists():
                images[pose] = str(image_path)
            else:
                print(f"Uyari: {image_path} bulunamadi!")
                images[pose] = None
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
            self._update_monkey_image(pose_name)

    def _update_monkey_image(self, pose_name):
        """Maymun resmini guncelle"""
        image_path = self.monkey_images.get(pose_name)

        if image_path:
            pixmap = QPixmap(image_path)
            self.monkey_label.setPixmap(pixmap)
        else:
            self.monkey_label.setText(f"{pose_name}\n\n(Resim bulunamadi)")
            self.monkey_label.setStyleSheet(
                "QLabel { color: #ff9800; font-size: 16px; border: 2px dashed #444; }")

        pose_names = {
            "raising_hand": "Isaret Parmagi Yukarida",
            "shocking": "Agiz Acik (Saskinlik)",
            "thinking": "El Yuzde (Dusunme)",
            "default": "Normal Durus",
            "ironman": "Avuc Ileri (Stop Pozu)",
        }
        self.pose_name_label.setText(pose_names.get(pose_name, pose_name))

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

    window = MonkeyPoseApp()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()