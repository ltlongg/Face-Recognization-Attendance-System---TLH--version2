"""
MODULE QUẢN LÝ CAMERA
======================
Module này chứa các lớp và hàm xử lý camera:
- CameraManager: Quản lý camera
- Các hàm vẽ UI lên frame
"""

import cv2
import threading
import time

import config


class CameraManager:
    """Quản lý camera với Threading để giảm độ trễ (đặc biệt cho RTSP)."""
    
    def __init__(self, camera_index=None):
        """Khởi tạo camera manager."""
        self.camera_index = camera_index or config.CAMERA_INDEX
        self.cap = None
        self.is_opened = False
        
        # Threading
        self.frame = None
        self.ret = False
        self.stopped = False
        self.thread = None
    
    def open(self):
        """Mở camera và bắt đầu thread đọc frame."""
        if self.is_opened:
            return True
        
        # Tối ưu cho RTSP để giảm độ trễ
        if isinstance(self.camera_index, str) and (self.camera_index.startswith('rtsp') or self.camera_index.startswith('http')):
            import os
            # Sử dụng UDP (nhanh hơn TCP cho video realtime)
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_FFMPEG)
            # Giảm buffer size xuống 1 để luôn lấy frame mới nhất
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        else:
            self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            print(f"[ERROR] {config.MESSAGES['camera_error']}")
            return False
        
        self.is_opened = True
        self.stopped = False
        
        # Khởi chạy thread đọc frame
        self.thread = threading.Thread(target=self._update, args=())
        self.thread.daemon = True
        self.thread.start()
        
        while self.frame is None:
            time.sleep(0.1)
            
        return True
    
    def _update(self):
        """Luôn đọc frame mới nhất từ camera (chạy trong thread riêng)."""
        while not self.stopped:
            if not self.is_opened:
                break
            self.ret, self.frame = self.cap.read()
            if not self.ret:
                self.stopped = True
    
    def read_frame(self):
        """Trả về frame mới nhất."""
        return self.ret, self.frame
    
    def close(self):
        """Đóng camera và dừng thread."""
        self.stopped = True
        if self.thread:
            self.thread.join(timeout=1.0)
            
        if self.cap:
            self.cap.release()
        self.is_opened = False
        cv2.destroyAllWindows()
    
    def __enter__(self):
        """Context manager - mở camera."""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager - đóng camera."""
        self.close()


class FrameRenderer:
    """Vẽ UI lên frame camera."""
    
    @staticmethod
    def _xywh_to_xyxy(bbox):
        """Chuyển bbox từ (x, y, w, h) sang (x1, y1, x2, y2)."""
        x, y, w, h = bbox
        return (x, y, x + w, y + h)
    
    @staticmethod
    def draw_recognized_face(frame, bbox, name, landmarks=None):
        """Vẽ bbox và tên cho khuôn mặt đã nhận dạng."""
        x1, y1, x2, y2 = FrameRenderer._xywh_to_xyxy(bbox)
        color = config.COLOR_SUCCESS
        
        # Vẽ bbox
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Hiển thị tên
        cv2.putText(frame, name, (x1, y1-8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    @staticmethod
    def draw_already_attended(frame, bbox, name):
        """Vẽ bbox và tên cho khuôn mặt đã điểm danh (cooldown)."""
        x1, y1, x2, y2 = FrameRenderer._xywh_to_xyxy(bbox)
        color = config.COLOR_WARNING
        
        # Vẽ bbox
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Hiển thị tên + thông báo
        cv2.putText(frame, f"{name} (Da ghi)", (x1, y1-8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    @staticmethod
    def draw_unknown_face(frame, bbox, landmarks=None):
        """Vẽ bbox cho khuôn mặt không nhận dạng được."""
        x1, y1, x2, y2 = FrameRenderer._xywh_to_xyxy(bbox)
        color = config.COLOR_ERROR
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, "Không nhan dang", (x1, y1-8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
    @staticmethod
    def draw_spoof_warning(frame, bbox, landmarks=None):
        """Vẽ bbox đỏ cho khuôn mặt giả mạo."""
        x1, y1, x2, y2 = FrameRenderer._xywh_to_xyxy(bbox)
        color = (0, 0, 255)
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
        cv2.putText(frame, "Khuon mat gia", (x1, y1-8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    
