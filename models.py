"""
MODULE QUẢN LÝ MÔ HÌNH AI - DeepFace
=====================================
Module này chứa các lớp wrapper cho mô hình AI dựa trên DeepFace.
- FaceDetector: Phát hiện khuôn mặt (YuNet - nhanh, ổn định)
- FaceRecognizer: Nhận dạng khuôn mặt (SFace - 128 dims, OpenCV ONNX)
- FaceAntiSpoof: Chống giả mạo (FasNet)

Tối ưu cho CPU: Sử dụng YuNet cho detection và SFace cho recognition.
"""
import os
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Tuple, List

import numpy as np

import config

# Thêm thư mục deepface vào path để có thể import package deepface
base_dir = Path(__file__).resolve().parent
deepface_path = base_dir / "deepface"
if deepface_path.exists() and str(deepface_path) not in sys.path:
    sys.path.insert(0, str(deepface_path))

# Thiết lập môi trường trước khi import DeepFace
os.environ["TF_USE_LEGACY_KERAS"] = "1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["yunet_score_threshold"] = "0.6"  # Hạ thấp ngưỡng để YuNet nhạy hơn


@dataclass
class Face:
    """Đối tượng khuôn mặt được phát hiện."""
    bbox: Tuple[int, int, int, int]  # (x, y, w, h)
    landmarks: Optional[dict]  # Landmark points
    confidence: float
    aligned_img: Optional[np.ndarray] = None  # Ảnh khuôn mặt đã aligned (từ DeepFace)


class FaceDetector:
    """
    Wrapper cho YuNet - detector nhanh và hiệu quả của OpenCV.
    Sử dụng qua module detection của DeepFace.
    """
    
    def __init__(self, detector_backend: str = "yunet"):
        """Khởi tạo YuNet detector."""
        self.backend = detector_backend
    
    def detect(self, image: np.ndarray, max_num: int = 1, align: bool = True) -> Optional[Face]:
        """
        Phát hiện khuôn mặt trong ảnh bằng YuNet.
        
        Args:
            image: Ảnh BGR
            max_num: Số khuôn mặt tối đa (1 = lấy lớn nhất)
            align: Có căn chỉnh khuôn mặt hay không (mặc định True)
        
        Returns:
            Face object (có aligned_img nếu align=True) hoặc None
        """
        from deepface.modules import detection
        
        # Sử dụng detect_faces - DeepFace tự xử lý alignment
        img_objs = detection.detect_faces(
            detector_backend=self.backend,
            img=image,
            align=align,  # DeepFace sẽ trả về ảnh đã aligned trong DetectedFace.img
            expand_percentage=0,
            max_faces=max_num
        )
        
        if not img_objs:
            return None
        
        detected = img_objs[0]
        fa = detected.facial_area
        
        return Face(
            bbox=(fa.x, fa.y, fa.w, fa.h),
            landmarks={"left_eye": fa.left_eye, "right_eye": fa.right_eye},
            confidence=detected.confidence or 0.0,
            aligned_img=detected.img if align else None  # Ảnh aligned từ DeepFace
        )


class FaceRecognizer:
    """
    Wrapper cho SFace - model recognition nhanh và hiệu quả (128 dims, OpenCV ONNX).
    Sử dụng represent() của DeepFace để trích xuất embedding.
    """
    
    def __init__(self, similarity_threshold: float = None):
        """Khởi tạo SFace recognizer."""
        self.model_name = "SFace"
        self.similarity_threshold = similarity_threshold or config.SIMILARITY_THRESHOLD
    
    def get_embedding(self, image: np.ndarray, face: Face) -> np.ndarray:
        """
        Trích xuất embedding từ khuôn mặt sử dụng DeepFace.represent().
        Ưu tiên dùng ảnh aligned nếu có.
        
        Args:
            image: Ảnh BGR gốc
            face: Đối tượng Face từ detector (có thể chứa aligned_img)
        
        Returns:
            Vector embedding 128 chiều, đã normalize
        """
        from deepface.modules import representation
        
        # Ưu tiên dùng ảnh aligned từ DeepFace nếu có
        if face.aligned_img is not None and face.aligned_img.size > 0:
            face_img = face.aligned_img
        else:
            # Fallback: Cắt khuôn mặt từ ảnh gốc
            x, y, w, h = face.bbox
            y_min, y_max = max(0, y), min(image.shape[0], y + h)
            x_min, x_max = max(0, x), min(image.shape[1], x + w)
            face_img = image[y_min:y_max, x_min:x_max]
        
        if face_img.size == 0:
            return np.zeros(128)
        
        # Dùng represent() với detector_backend="skip" để bỏ qua detect
        # DeepFace sẽ tự resize, normalize và forward qua model
        result = representation.represent(
            img_path=face_img,
            model_name=self.model_name,
            detector_backend="skip",  # Bỏ qua detect vì đã có ảnh aligned
            enforce_detection=False,
            align=False,  # Đã align rồi, không cần align lại
            normalization="base",
            l2_normalize=True
        )
        
        if not result:
            return np.zeros(128)
        
        embedding = np.array(result[0]["embedding"])
        return embedding
    
    def find_best_match(
        self, 
        embedding: np.ndarray, 
        embedding_matrix: np.ndarray, 
        embedding_map: List
    ) -> Tuple[Optional[str], float]:
        """
        Tìm embedding giống nhất bằng cosine similarity.
        """
        if embedding_matrix is None or len(embedding_map) == 0:
            return None, 0.0
        
        query = embedding.flatten()
        
        # Cosine similarity (embeddings đã được L2 normalize)
        similarities = np.dot(embedding_matrix, query)
        
        best_idx = np.argmax(similarities)
        best_similarity = float(similarities[best_idx])
        best_emp_id = embedding_map[best_idx][0]
        
        return best_emp_id, best_similarity


class FaceAntiSpoof:
    """
    Wrapper cho FasNet (MiniFASNet) - chống giả mạo.
    Đây là model từ minivision-ai/Silent-Face-Anti-Spoofing.
    """
    
    def __init__(self, threshold: float = None):
        """Khởi tạo FasNet anti-spoofing model."""
        from deepface.models.spoofing.FasNet import Fasnet
        
        self.model = Fasnet()
        self.threshold = threshold or config.ANTISPOOF_THRESHOLD
    
    def check(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> Tuple[bool, float]:
        """
        Kiểm tra khuôn mặt thật hay giả.
        
        Args:
            image: Ảnh BGR gốc
            bbox: (x, y, w, h) của khuôn mặt
        
        Returns:
            (is_real, confidence)
        """
        is_real, score = self.model.analyze(image, bbox)
        
        # Áp dụng threshold
        is_real = is_real and score >= self.threshold
        
        return is_real, score
