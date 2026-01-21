"""
MODULE DỊCH VỤ ĐIỂM DANH
=========================
Module này chứa logic nghiệp vụ chính:
- AttendanceService: Xử lý điểm danh
- RegistrationService: Xử lý đăng ký nhân viên
"""

import cv2
import time
from datetime import datetime

import config
from camera import CameraManager, FrameRenderer


class AttendanceService:
    """
    Dịch vụ xử lý điểm danh.
    
    Cung cấp các chức năng:
    - Nhận dạng khuôn mặt
    - Kiểm tra giả mạo (anti-spoofing)
    - Ghi nhận điểm danh
    - Chạy điểm danh realtime
    
    Attributes:
        detector: Mô hình phát hiện khuôn mặt
        recognizer: Mô hình nhận dạng khuôn mặt
        anti_spoof: Mô hình chống giả mạo (optional)
        employee_db: Database nhân viên
        attendance_db: Database điểm danh
    """
    
    def __init__(self, detector, recognizer, employee_db, attendance_db, anti_spoof=None):
        """
        Khởi tạo dịch vụ điểm danh.
        
        Args:
            detector: FaceDetector instance
            recognizer: FaceRecognizer instance
            employee_db: EmployeeDatabase instance
            attendance_db: AttendanceDatabase instance
            anti_spoof: FaceAntiSpoof instance (optional)
        """
        self.detector = detector
        self.recognizer = recognizer
        self.anti_spoof = anti_spoof
        self.employee_db = employee_db
        self.attendance_db = attendance_db
        self.renderer = FrameRenderer()
    
    def recognize_face(self, image):
        """
        Nhận dạng khuôn mặt lớn nhất trong ảnh.
        
        Returns:
            dict: Kết quả nhận dạng hoặc None
        """
        face = self.detector.detect(image)  # Mặc định lấy 1 khuôn mặt lớn nhất
        
        if face is None:
            return None
        
        # Lấy embedding matrix
        embedding_matrix, embedding_map = self.employee_db.get_embedding_matrix()
        
        if embedding_matrix is None:
            return {"recognized": False, "bbox": face.bbox, "landmarks": face.landmarks}
        
        # Kiểm tra anti-spoofing
        if self.anti_spoof is not None:
            is_real, spoof_conf = self.anti_spoof.check(image, face.bbox)
            if not is_real:
                return {"recognized": False, "is_spoof": True, "bbox": face.bbox, "landmarks": face.landmarks}
        
        # Trích xuất embedding và tìm người giống nhất
        embedding = self.recognizer.get_embedding(image, face)
        best_id, similarity = self.recognizer.find_best_match(embedding, embedding_matrix, embedding_map)
        
        if similarity >= self.recognizer.similarity_threshold:
            emp = self.employee_db.get_employee(best_id)
            return {
                "recognized": True,
                "emp_id": best_id,
                "name": emp["name"],
                "department": emp["department"],
                "similarity": similarity,
                "bbox": face.bbox,
                "landmarks": face.landmarks
            }
        
        return {"recognized": False, "bbox": face.bbox, "landmarks": face.landmarks, "similarity": similarity}
    

    def run_recognition_camera(self):
        """Chạy nhận diện khuôn mặt realtime qua camera (Đã tối ưu Production)."""
        recognition_counter = {}
        last_attendance_time = {}
        frame_count = 0
        
        # Biến đếm lỗi để log
        error_count = 0
        
        print(f"[INFO] Bắt đầu luồng Camera AI...")

        while True: # Vòng lặp vĩnh cửu bên ngoài để tái khởi động camera manager
            try:
                with CameraManager() as camera:
                    if not camera.is_opened:
                        print("[ERROR] Không thể mở camera. Thử lại sau 5s...")
                        time.sleep(5)
                        continue
                    
                    print("[INFO] Đã kết nối Camera thành công.")
                    error_count = 0 # Reset lỗi khi kết nối lại được

                    while True:
                        ret, frame = camera.read_frame()
                        
                        # 1. XỬ LÝ MẤT KẾT NỐI (Resilient)
                        if not ret or frame is None:
                            error_count += 1
                            print(f"[WARN] Mất tín hiệu Camera ({error_count})...")
                            if error_count > 10: # Nếu mất liên tục 10 lần
                                print("[WARN] Camera có vẻ bị treo. Đang khởi động lại kết nối...")
                                break # Thoát vòng lặp trong để ra ngoài init lại CameraManager
                            time.sleep(0.5)
                            continue
                        
                        error_count = 0 # Reset lỗi nếu đọc được frame

                        # 2. FRAME SKIPPING
                        frame_count += 1
                        if frame_count % config.FRAME_SKIP != 0:
                            continue # Bỏ qua ngay lập tức, không resize, không tính toán
                        
                        # 3. CHỈ RESIZE KHI CẦN (Lazy Resize)
                        if config.PROCESS_WIDTH and frame.shape[1] > config.PROCESS_WIDTH:
                            scale = config.PROCESS_WIDTH / frame.shape[1]
                            frame = cv2.resize(frame, (config.PROCESS_WIDTH, int(frame.shape[0] * scale)))

                        # 4. NHẬN DIỆN
                        result = self.recognize_face(frame)
                        
                        # --- XỬ LÝ LOGIC CHẤM CÔNG ---
                        if result is None:
                            # Không thấy ai -> Reset counter
                            recognition_counter.clear()
                            # Để tránh việc người đi qua nhanh rồi 10s sau quay lại vẫn bị tính tiếp
                            continue

                        # Kiểm tra Spoofing
                        if result.get("is_spoof", False):
                            print(f"[ALERT] FACE SPOOF DETECTED at {datetime.now()}")
                            continue

                        # Nếu không nhận diện được ai (Unknown)
                        if not result.get("recognized"):
                            # Reset counter tất cả
                            for eid in recognition_counter: recognition_counter[eid] = 0
                            continue

                        # Nhận diện thành công
                        emp_id = result["emp_id"]
                        name = result["name"]
                        dept = result["department"]

                        # Logic độc quyền: Chỉ reset người khác, giữ người này
                        for eid in list(recognition_counter.keys()):
                            if eid != emp_id: recognition_counter[eid] = 0

                        # Kiểm tra Cooldown
                        now = time.time()
                        last_time = last_attendance_time.get(emp_id, 0)

                        if now - last_time >= config.ATTENDANCE_COOLDOWN:
                            # Tăng bộ đếm
                            recognition_counter[emp_id] = recognition_counter.get(emp_id, 0) + 1

                            if recognition_counter[emp_id] >= config.CONFIRM_FRAMES:
                                # --- CHỐT ĐƠN ---
                                self.attendance_db.record(emp_id, name, dept)
                                last_attendance_time[emp_id] = now
                                recognition_counter[emp_id] = 0 # Reset sau khi điểm danh xong
                                
                                # Log đẹp
                                print(f"\n>>> [SUCCESS] ĐIỂM DANH: {name} ({dept}) - {datetime.now().strftime('%H:%M:%S')}")

                        # Nghỉ cực ngắn để CPU thở
                        time.sleep(0.01)

            except Exception as e:
                print(f"[CRITICAL ERROR] Lỗi không xác định trong luồng Camera: {e}")
                print("Hệ thống sẽ tự khởi động lại sau 5s...")
                time.sleep(5)


class VideoRegistrationService:
    """
    Dịch vụ đăng ký nhân viên từ các frame ảnh.
    Trích xuất embeddings từ các frame đã được lọc (có mặt người, không mờ).
    """
    
    def __init__(self, detector, recognizer, employee_db):
        self.detector = detector
        self.recognizer = recognizer
        self.employee_db = employee_db
    
    def extract_embeddings_from_frames(self, frames, sample_interval=5):
        """
        Trích xuất embeddings từ các frames.
        
        Args:
            frames: List các frame BGR
            sample_interval: Lấy mỗi N frame để tránh trùng lặp
        
        Returns:
            tuple: (embeddings_list, photos_list)
        """
        embeddings = []
        photos = []
        
        for i, frame in enumerate(frames):
            if i % sample_interval != 0:
                continue
            
            # Detect khuôn mặt lớn nhất
            face = self.detector.detect(frame)
            if face is None:
                continue
            
            # Trích xuất embedding
            embedding = self.recognizer.get_embedding(frame, face)
            embeddings.append(embedding)
            photos.append(frame)
        
        return embeddings, photos
    
    def register_from_video_frames(self, emp_id, name, department, frames):
        """
        Đăng ký nhân viên từ các frame video.
        
        Returns:
            tuple: (success, message)
        """
        # Trích xuất embeddings (dùng sample_interval=1 vì frames đã được lọc có mặt người từ web)
        embeddings, photos = self.extract_embeddings_from_frames(frames, sample_interval=1)
        
        if len(embeddings) < 3:
            return False, f"Không đủ khuôn mặt hợp lệ (chỉ có {len(embeddings)} ảnh)"
        
        # Giới hạn số embeddings để tránh quá nhiều theo cấu hình
        max_embeddings = config.NUM_REGISTRATION_PHOTOS
        if len(embeddings) > max_embeddings:
            # Rải đều việc chọn ảnh trên toàn bộ dữ liệu đã capture thay vì chỉ lấy phần đầu
            # Điều này giúp lấy được nhiều góc mặt hơn nếu người dùng quay mặt trong lúc quay
            indices = [int(i * (len(embeddings) - 1) / (max_embeddings - 1)) for i in range(max_embeddings)]
            embeddings = [embeddings[i] for i in indices]
            photos = [photos[i] for i in indices]
        
        # Đảm bảo mỗi người đều lấy đúng số lượng ảnh nếu có thể
        # Nếu dư thì đã cắt ở trên, nếu thiếu thì lấy hết
        
        # Lưu vào database
        return self.employee_db.add_employee(emp_id, name, department, embeddings, photos, overwrite=True)
