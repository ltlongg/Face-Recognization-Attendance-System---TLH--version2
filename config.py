"""
CẤU HÌNH HỆ THỐNG ĐIỂM DANH
============================
File này chứa tất cả các cấu hình của hệ thống.
Khi cần thay đổi cấu hình, chỉ cần sửa file này.
"""

import os

# =============================================================================
# CẤU HÌNH THƯ MỤC
# =============================================================================

# Thư mục gốc lưu trữ dữ liệu
DATA_FOLDER = "employee_data"

# Các thư mục con
PHOTOS_FOLDER = os.path.join(DATA_FOLDER, "photos")          # Lưu ảnh nhân viên
ATTENDANCE_FOLDER = os.path.join(DATA_FOLDER, "attendance")  # Lưu file điểm danh CSV

# File database nhân viên
EMPLOYEES_DB_FILE = os.path.join(DATA_FOLDER, "employees.json")


# =============================================================================
# CẤU HÌNH NHẬN DẠNG KHUÔN MẶT
# =============================================================================

# Ngưỡng độ tương đồng để xác nhận nhân viên (0.0 - 1.0)
SIMILARITY_THRESHOLD = 0.5

# CẤU HÌNH CHỐNG GIẢ MẠO (ANTI-SPOOFING)
ANTISPOOF_ENABLED = False
ANTISPOOF_THRESHOLD = 0.7

# Số frame liên tiếp cần nhận dạng thành công để xác nhận điểm danh
CONFIRM_FRAMES = 10

# Tối ưu hóa hiệu năng
FRAME_SKIP = 5
PROCESS_WIDTH = 640

# Số ảnh tối đa lưu trữ cho mỗi nhân viên
NUM_REGISTRATION_PHOTOS = 20

# =============================================================================
# CẤU HÌNH CAMERA
# =============================================================================

# Index camera (0 = camera mặc định)
CAMERA_INDEX = 'rtsp://admin:Tlh@2026@187.26.222.251/ISAPI/Streaming/channels/102'
# CAMERA_INDEX = 0


# =============================================================================
# CẤU HÌNH HIỂN THỊ
# =============================================================================
# Màu sắc (BGR format)
COLOR_SUCCESS = (0, 255, 0)      # Màu xanh lá - nhận dạng thành công
COLOR_WARNING = (0, 165, 255)    # Màu cam - đã điểm danh
COLOR_ERROR = (0, 0, 255)        # Màu đỏ - không nhận dạng được




# =============================================================================
# CẤU HÌNH ĐIỂM DANH
# =============================================================================

# Loại điểm danh (hệ thống chỉ sử dụng DETECT)
ATTENDANCE_DETECT = "DETECT"

# Thời gian chờ giữa 2 lần điểm danh của cùng 1 người (giây)
ATTENDANCE_COOLDOWN = 60

# Format thời gian
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Cấu hình giờ làm việc
WORK_START_TIME = "08:00:00"  # Giờ bắt đầu làm việc
WORK_END_TIME = "17:30:00"    # Giờ kết thúc làm việc


# =============================================================================
# CẤU HÌNH WEB (WEB PORTAL SETTINGS)
# =============================================================================

# Quản trị viên (Full access)
USERNAME = 'admin'
PASSWORD = 'Tlh@1988'

# Nhân viên (View only)
USER_USERNAME = 'user'
USER_PASSWORD = '123'

# =============================================================================
# THÔNG BÁO HỆ THỐNG
# =============================================================================

MESSAGES = {
    "system_name": "HỆ THỐNG ĐIỂM DANH NHÂN VIÊN BẰNG KHUÔN MẶT",
    "loading_detector": "Đang tải mô hình phát hiện khuôn mặt (YuNet)...",
    "loading_recognizer": "Đang tải mô hình nhận dạng khuôn mặt (SFace)...",
    "loading_antispoof": "Đang tải mô hình chống giả mạo (FasNet)...",
    "system_ready": "Hệ thống đã sẵn sàng!",
    "no_face_detected": "Không phát hiện được khuôn mặt trong ảnh!",
    "multiple_faces": "Phát hiện nhiều khuôn mặt. Vui lòng chỉ có 1 người trong ảnh!",
    "employee_exists": "Mã nhân viên đã tồn tại trong hệ thống!",
    "employee_not_found": "Không tìm thấy nhân viên!",
    "register_success": "Đăng ký thành công!",
    "camera_error": "Không thể mở camera!",
    "no_employees": "Chưa có nhân viên nào trong hệ thống!",
    "spoof_detected": "CẢNH BÁO: Phát hiện khuôn mặt GIẢ!",
}

