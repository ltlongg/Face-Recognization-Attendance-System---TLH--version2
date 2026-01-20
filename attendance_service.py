"""
MODULE DỊCH VỤ ĐIỂM DANH
=========================
Module này chứa logic nghiệp vụ chính:
- AttendanceService: Xử lý điểm danh
- RegistrationService: Xử lý đăng ký nhân viên
"""

import cv2
import time

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
        """Chạy nhận diện khuôn mặt realtime qua camera."""
        recognition_counter = {}
        last_attendance_time = {}  # Lưu thời gian điểm danh cuối của mỗi người
        frame_count = 0
        last_result = None
        
        with CameraManager() as camera:
            if not camera.is_opened:
                return
            
            while True:
                ret, frame = camera.read_frame()
                if not ret or frame is None:
                    break
                
                # Resize frame
                if config.PROCESS_WIDTH and frame.shape[1] > config.PROCESS_WIDTH:
                    scale = config.PROCESS_WIDTH / frame.shape[1]
                    frame = cv2.resize(frame, (config.PROCESS_WIDTH, int(frame.shape[0] * scale)))

                # Tối ưu hóa: Chỉ nhận dạng mỗi N frame
                if frame_count % config.FRAME_SKIP == 0:
                    # Nhận dạng khuôn mặt lớn nhất
                    last_result = self.recognize_face(frame)
                
                result = last_result
                frame_count += 1
                
                # Xử lý kết quả (Guard clauses để giảm nesting)
                if result is None:
                    cv2.imshow("He thong nhan dien - Nhan 'q' de thoat", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'): break
                    continue

                landmarks = result.get("landmarks")
                bbox = result.get("bbox")
                
                # 1. Kiểm tra spoofing
                if result.get("is_spoof", False):
                    self.renderer.draw_spoof_warning(frame, bbox, landmarks)
                    cv2.imshow("He thong nhan dien - Nhan 'q' de thoat", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'): break
                    continue

                # 2. Trường hợp không nhận dạng được
                if not result.get("recognized"):
                    self.renderer.draw_unknown_face(frame, bbox, landmarks)
                    # Reset counter cho mọi người vì không thấy ai quen trong frame này
                    for eid in recognition_counter: recognition_counter[eid] = 0
                    cv2.imshow("He thong nhan dien - Nhan 'q' de thoat", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'): break
                    continue

                # 3. Trường hợp nhận dạng thành công
                emp_id = result["emp_id"]
                name = result["name"]
                
                # Reset counter cho những người KHÁC
                for eid in list(recognition_counter.keys()):
                    if eid != emp_id: recognition_counter[eid] = 0

                # Kiểm tra cooldown
                now = time.time()
                last_time = last_attendance_time.get(emp_id, 0)
                
                if now - last_time < config.ATTENDANCE_COOLDOWN:
                    self.renderer.draw_already_attended(frame, bbox, name)
                else:
                    # Tích lũy counter
                    recognition_counter[emp_id] = recognition_counter.get(emp_id, 0) + 1
                    
                    if recognition_counter[emp_id] >= config.CONFIRM_FRAMES:
                        self.attendance_db.record(emp_id, name, result["department"])
                        last_attendance_time[emp_id] = now
                        recognition_counter[emp_id] = 0
                        #print(f"[INFO] Ghi nhận điểm danh: {name} ({emp_id})")
                    
                    self.renderer.draw_recognized_face(frame, bbox, name, landmarks)

                cv2.imshow("He thong nhan dien - Nhan 'q' de thoat", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'): break


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
