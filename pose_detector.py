"""
Pose Detection Module - Super Kahraman Edition
MediaPipe ile pose, hand ve face detection
4 kahraman: Iron Man (Snap), Iron Man (Repulsor), Black Panther, Spider-Man
"""

import cv2
import mediapipe as mp
import numpy as np


class PoseDetector:
    """MediaPipe ile pose algilama - 4 super kahraman pozu"""
    
    def __init__(self):
        # MediaPipe modullerini baslat
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        self.mp_face_mesh = mp.solutions.face_mesh
        
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Debug bilgileri
        self.debug_info = {
            'hands_detected': 0,
            'face_detected': False,
            'arms_crossed': False,
            'web_shoot': False,
            'finger_snap': False,
            'open_palm': False,
        }
        
    def _is_finger_extended(self, hand_landmarks, finger_tip_id, finger_pip_id):
        """Parmak acik (uzamis) mi kontrol et - tip, pip'den yukarda ise acik"""
        tip = hand_landmarks.landmark[finger_tip_id]
        pip = hand_landmarks.landmark[finger_pip_id]
        return tip.y < pip.y
    
    def _is_finger_curled(self, hand_landmarks, finger_tip_id, finger_pip_id):
        """Parmak kapali (bukulmus) mu kontrol et"""
        tip = hand_landmarks.landmark[finger_tip_id]
        pip = hand_landmarks.landmark[finger_pip_id]
        return tip.y > pip.y

    def detect_pose(self, frame):
        """Frame uzerinde pose detection yapar"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detection'lar
        pose_results = self.pose.process(rgb_frame)
        hand_results = self.hands.process(rgb_frame)
        face_results = self.face_mesh.process(rgb_frame)
        
        # Debug sifirla
        self.debug_info['hands_detected'] = 0
        self.debug_info['face_detected'] = False
        self.debug_info['arms_crossed'] = False
        self.debug_info['web_shoot'] = False
        self.debug_info['finger_snap'] = False
        self.debug_info['open_palm'] = False
        
        # Yuz ciz (dudak konturu)
        if face_results.multi_face_landmarks:
            self.debug_info['face_detected'] = True
            for face_landmarks in face_results.multi_face_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    face_landmarks,
                    self.mp_face_mesh.FACEMESH_LIPS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=1)
                )
        
        # Eller ciz
        if hand_results.multi_hand_landmarks:
            self.debug_info['hands_detected'] = len(hand_results.multi_hand_landmarks)
            for hand_landmarks in hand_results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
        
        # Pozu / kahramani belirle
        pose_name = self._determine_pose(pose_results, hand_results, face_results)
        
        # Debug bilgileri goster
        y_pos = 30
        debug_items = [
            f"Eller: {self.debug_info['hands_detected']}",
            f"Capraz: {'EVET' if self.debug_info['arms_crossed'] else '-'}",
            f"Ag Atma: {'EVET' if self.debug_info['web_shoot'] else '-'}",
            f"Siklama: {'EVET' if self.debug_info['finger_snap'] else '-'}",
            f"Avuc Acik: {'EVET' if self.debug_info['open_palm'] else '-'}",
        ]
        for text in debug_items:
            cv2.putText(frame, text, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2)
            y_pos += 25
        
        # Kahraman goster
        hero_labels = {
            "ironman_snap": "IRON MAN (SNAP)",
            "ironman":      "IRON MAN (REPULSOR)",
            "blackpanther": "BLACK PANTHER",
            "spiderman":    "SPIDER-MAN",
            "default":      "Bekleniyor..."
        }
        label = hero_labels.get(pose_name, pose_name)
        cv2.putText(frame, f"Hero: {label}", (10, frame.shape[0] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return frame, pose_name
    
    def _determine_pose(self, pose_results, hand_results, face_results):
        """
        Pozu belirler - oncelik sirasi:
        1. Black Panther  -> Kollar goguste capraz (Wakanda Forever)
        2. Spider-Man     -> Ag atma hareketi (isaret+serce acik, orta+yuzuk kapali)
        3. Iron Man Snap  -> Parmak siklama (basparmak + orta parmak birlesik)
        4. Iron Man       -> Avuc acik el yukari kaldirma (repulsor)
        5. default        -> Hicbiri
        """
        if self._is_wakanda_pose(pose_results):
            return "blackpanther"
        if self._is_web_shooting(hand_results):
            return "spiderman"
        if self._is_finger_snap(hand_results):
            return "ironman_snap"
        if self._is_open_palm_raised(pose_results, hand_results):
            return "ironman"
        return "default"

    def _is_wakanda_pose(self, pose_results):
        """
        Kollar gogus onunde capraz - Black Panther Wakanda Forever pozu.
        """
        if not pose_results.pose_landmarks:
            return False
        
        landmarks = pose_results.pose_landmarks.landmark
        
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST]
        
        chest_x = (left_shoulder.x + right_shoulder.x) / 2
        chest_y = (left_shoulder.y + right_shoulder.y) / 2
        
        shoulder_width = abs(left_shoulder.x - right_shoulder.x)
        if shoulder_width < 0.01:
            return False
        
        left_near = (abs(left_wrist.x - chest_x) < shoulder_width * 0.9 and 
                     abs(left_wrist.y - chest_y) < shoulder_width * 1.2)
        right_near = (abs(right_wrist.x - chest_x) < shoulder_width * 0.9 and 
                      abs(right_wrist.y - chest_y) < shoulder_width * 1.2)
        
        wrists_crossed = left_wrist.x > right_wrist.x
        
        is_wakanda = left_near and right_near and wrists_crossed
        self.debug_info['arms_crossed'] = is_wakanda
        
        return is_wakanda
    
    def _is_web_shooting(self, hand_results):
        """
        Spider-Man ag atma hareketi:
        - Isaret parmagi ACIK (uzamis)
        - Serce parmagi ACIK (uzamis)
        - Orta parmak KAPALI (bukulmus)
        - Yuzuk parmagi KAPALI (bukulmus)
        Tek el yeterli.
        """
        if not hand_results.multi_hand_landmarks:
            return False
        
        H = self.mp_hands.HandLandmark
        
        for hand_landmarks in hand_results.multi_hand_landmarks:
            index_extended = self._is_finger_extended(hand_landmarks, H.INDEX_FINGER_TIP, H.INDEX_FINGER_PIP)
            pinky_extended = self._is_finger_extended(hand_landmarks, H.PINKY_TIP, H.PINKY_PIP)
            middle_curled = self._is_finger_curled(hand_landmarks, H.MIDDLE_FINGER_TIP, H.MIDDLE_FINGER_PIP)
            ring_curled = self._is_finger_curled(hand_landmarks, H.RING_FINGER_TIP, H.RING_FINGER_PIP)
            
            if index_extended and pinky_extended and middle_curled and ring_curled:
                self.debug_info['web_shoot'] = True
                return True
        
        return False

    def _is_finger_snap(self, hand_results):
        """
        Parmak siklama hareketi (Iron Man Endgame snap):
        - Basparmak ucu ve orta parmak ucu birbirine cok yakin (siklatma pozisyonu)
        - Isaret parmagi acik
        - Yuzuk ve serce serbest
        Tek el yeterli.
        """
        if not hand_results.multi_hand_landmarks:
            return False
        
        H = self.mp_hands.HandLandmark
        
        for hand_landmarks in hand_results.multi_hand_landmarks:
            thumb_tip = hand_landmarks.landmark[H.THUMB_TIP]
            middle_tip = hand_landmarks.landmark[H.MIDDLE_FINGER_TIP]
            
            # Basparmak ile orta parmak arasi mesafe
            snap_dist = np.sqrt((thumb_tip.x - middle_tip.x)**2 + (thumb_tip.y - middle_tip.y)**2)
            
            # Isaret parmagi acik olmali (siklama sirasinda isaret parmak yukari kalkar)
            index_extended = self._is_finger_extended(hand_landmarks, H.INDEX_FINGER_TIP, H.INDEX_FINGER_PIP)
            
            # Basparmak ve orta parmak birlesik + isaret parmak acik
            if snap_dist < 0.06 and index_extended:
                self.debug_info['finger_snap'] = True
                return True
        
        return False

    def _is_open_palm_raised(self, pose_results, hand_results):
        """
        Avucu acik sekilde tek el kaldirma - Iron Man repulsor pozu:
        - El omuz hizasinda veya yukarida
        - Tum parmaklar acik (avuc acik)
        """
        if not pose_results.pose_landmarks or not hand_results.multi_hand_landmarks:
            return False
        
        # Sadece tek el olmali (iki el ise baska pozlari karistirabilir)
        if len(hand_results.multi_hand_landmarks) != 1:
            return False
        
        H = self.mp_hands.HandLandmark
        pose_landmarks = pose_results.pose_landmarks.landmark
        
        # Omuz yuksekligi referans
        left_shoulder_y = pose_landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].y
        right_shoulder_y = pose_landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].y
        shoulder_y = (left_shoulder_y + right_shoulder_y) / 2
        
        hand_landmarks = hand_results.multi_hand_landmarks[0]
        wrist = hand_landmarks.landmark[H.WRIST]
        
        # El omuz hizasinda veya yukarida mi?
        hand_raised = wrist.y < shoulder_y + 0.05
        
        if not hand_raised:
            return False
        
        # Tum 4 parmak acik mi? (basparmak haric, o farkli eksen)
        index_ext = self._is_finger_extended(hand_landmarks, H.INDEX_FINGER_TIP, H.INDEX_FINGER_PIP)
        middle_ext = self._is_finger_extended(hand_landmarks, H.MIDDLE_FINGER_TIP, H.MIDDLE_FINGER_PIP)
        ring_ext = self._is_finger_extended(hand_landmarks, H.RING_FINGER_TIP, H.RING_FINGER_PIP)
        pinky_ext = self._is_finger_extended(hand_landmarks, H.PINKY_TIP, H.PINKY_PIP)
        
        all_open = index_ext and middle_ext and ring_ext and pinky_ext
        
        if all_open:
            self.debug_info['open_palm'] = True
            return True
        
        return False
    
    def release(self):
        """Kaynaklari serbest birak"""
        self.pose.close()
        self.hands.close()
        self.face_mesh.close()
