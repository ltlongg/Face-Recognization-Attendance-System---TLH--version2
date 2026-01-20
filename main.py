"""
HỆ THỐNG ĐIỂM DANH NHÂN VIÊN BẰNG KHUÔN MẶT - DeepFace
======================================================

File chính để chạy hệ thống.
Sử dụng: python main.py

Cấu trúc module:
- config.py: Cấu hình hệ thống
- models.py: Mô hình AI (FaceDetector, FaceRecognizer, FaceAntiSpoof)
- database.py: Quản lý database (Employee, Attendance)
- camera.py: Quản lý camera và vẽ UI
- attendance_service.py: Logic nghiệp vụ
- web_dashboard.py: Quản lý nhân viên qua web
- main.py: File chính (entry point)

Models sử dụng (tối ưu cho CPU):
- YuNet: Face detection (OpenCV)
- SFace: Face recognition 128 dims (OpenCV ONNX) 
- FasNet: Anti-spoofing (PyTorch)
"""

import config
from models import FaceDetector, FaceRecognizer, FaceAntiSpoof
from database import EmployeeDatabase, AttendanceDatabase
from attendance_service import AttendanceService


class AttendanceSystem:
    """Lớp chính quản lý toàn bộ hệ thống điểm danh."""
    
    def __init__(self):
        """Khởi tạo hệ thống."""
        # Khởi tạo các thành phần
        self.detector = FaceDetector()
        self.recognizer = FaceRecognizer()
        self.anti_spoof = FaceAntiSpoof() if config.ANTISPOOF_ENABLED else None
        self.employee_db = EmployeeDatabase()
        self.attendance_db = AttendanceDatabase()
        
        # Khởi tạo service
        self.attendance_service = AttendanceService(
            self.detector,
            self.recognizer,
            self.employee_db,
            self.attendance_db,
            self.anti_spoof
        )
        

    def run(self):
        """Chạy nhận diện khuôn mặt realtime."""
        self.attendance_service.run_recognition_camera()


def main():
    """Entry point của chương trình."""
    print("======================================================")
    print("   HỆ THỐNG ĐIỂM DANH KHUÔN MẶT ĐANG KHỞI ĐỘNG...   ")
    print("======================================================")
    
    system = AttendanceSystem()
    
    print("\n[HỆ THỐNG] Đã sẵn sàng!")
    print(f"[CHẾ ĐỘ] Headless (Không cửa sổ) - Theo dõi qua Terminal")
    print("[THÔNG TIN] Đang sử dụng mô hình YuNet + SFace")
    print("-" * 54)
    
    system.run()


# Entry point
if __name__ == "__main__":
    main()
