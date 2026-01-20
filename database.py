"""
MODULE QUẢN LÝ DATABASE
========================
Module này chứa các lớp quản lý dữ liệu:
- EmployeeDatabase: Quản lý thông tin nhân viên
- AttendanceDatabase: Quản lý dữ liệu điểm danh
"""

import os
import json
import csv
import shutil
import re
import unicodedata
import numpy as np
from datetime import datetime

import config
from camera_light import flash_light


class EmployeeDatabase:
    """
    Lớp quản lý database nhân viên.
    
    Dữ liệu được lưu trữ:
    - Thông tin cơ bản: JSON file
    - Embedding: File embeddings.npz
    - Ảnh đăng ký: JPG files
    
    Attributes:
        employees: Dict lưu thông tin nhân viên trong RAM
        _embedding_matrix: Ma trận embedding đã stack (N x 128)
        _embedding_map: List mapping index -> (emp_id, photo_idx)
    """
    
    # File lưu trữ embedding tối ưu
    EMBEDDINGS_FILE = os.path.join(config.DATA_FOLDER, "embeddings.npz")
    
    def __init__(self):
        """
        Khởi tạo database nhân viên.
        """
        self.employees = {}
        # Cache cho vectorized search
        self._embedding_matrix = None  # Shape: (N, 128)
        self._embedding_map = []       # List of (emp_id, photo_idx)
        
        self._create_folders()
        self._load_database()
    
    def _create_folders(self):
        """
        Tạo cấu trúc thư mục lưu trữ.
        
        Cấu trúc:
        employee_data/
        ├── embeddings.npz  # Tất cả embeddings
        ├── photos/         # Ảnh nhân viên
        ├── attendance/     # File CSV điểm danh
        └── employees.json  # Thông tin nhân viên
        """
        folders = [
            config.DATA_FOLDER,
            config.PHOTOS_FOLDER,
            config.ATTENDANCE_FOLDER
        ]
        
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
    
    def _load_database(self):
        """
        Tải database từ file.
        """
        if not os.path.exists(config.EMPLOYEES_DB_FILE):
            return
        
        # Đọc thông tin cơ bản từ JSON
        with open(config.EMPLOYEES_DB_FILE, 'r', encoding='utf-8') as f:
            employees_info = json.load(f)
        
        # Khởi tạo thông tin cơ bản cho tất cả nhân viên
        for emp_id, info in employees_info.items():
            self.employees[emp_id] = {
                "name": info["name"],
                "department": info["department"],
                "embeddings": [],
                "num_photos": info.get("num_photos", 0)
            }
        
        # Load embeddings từ npz và cập nhật vào RAM
        if os.path.exists(self.EMBEDDINGS_FILE):
            self._load_from_npz()
    
    def _load_from_npz(self):
        """
        Load embeddings từ file npz và gán vào các nhân viên tương ứng.
        """
        try:
            data = np.load(self.EMBEDDINGS_FILE, allow_pickle=True)
            self._embedding_matrix = data['matrix']  # Shape: (N, 512)
            self._embedding_map = data['mapping'].tolist()  # List of (emp_id, photo_idx)
            
            # Phân bổ embeddings vào từng nhân viên trong self.employees
            for idx, (emp_id, photo_idx) in enumerate(self._embedding_map):
                if emp_id in self.employees:
                    # Đảm bảo index embedding là hợp lệ
                    embedding = self._embedding_matrix[idx]
                    self.employees[emp_id]["embeddings"].append(embedding)
        except Exception as e:
            print(f"[ERROR] Không thể load embeddings: {e}")
    
    def _sanitize_folder_name(self, name):
        """
        Chuyển đổi tên thành tên thư mục an toàn.
        
        Ví dụ: "Nguyễn Văn A" -> "Nguyen_Van_A"
        
        Args:
            name: Tên gốc
        
        Returns:
            str: Tên đã được làm sạch
        """
        # Bỏ dấu tiếng Việt
        name = unicodedata.normalize('NFD', name)
        name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')
        
        # Thay khoảng trắng bằng dấu gạch dưới
        name = name.replace(' ', '_')
        
        # Bỏ các ký tự đặc biệt, chỉ giữ chữ cái, số và gạch dưới
        name = re.sub(r'[^a-zA-Z0-9_]', '', name)
        
        return name
    
    def _save_database(self):
        """
        Lưu database vào file JSON.
        
        Chỉ lưu thông tin cơ bản, embedding lưu riêng.
        """
        employees_info = {}
        
        for emp_id, info in self.employees.items():
            employees_info[emp_id] = {
                "name": info["name"],
                "department": info["department"],
                "num_photos": info.get("num_photos", 0)
            }
        
        with open(config.EMPLOYEES_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(employees_info, f, ensure_ascii=False, indent=4)
    
    def add_employee(self, emp_id, name, department, embeddings, photos=None, overwrite=False):
        """
        Thêm nhân viên mới vào database.
        
        Args:
            emp_id: Mã nhân viên
            name: Họ tên
            department: Phòng ban
            embeddings: List các vector embedding khuôn mặt
            photos: List ảnh đăng ký (optional)
            overwrite: Cho phép ghi đè nếu đã tồn tại mẫu khuôn mặt
        
        Returns:
            tuple: (success, message)
        """
        # Kiểm tra trùng mã (chỉ báo lỗi nếu không phải chế độ ghi đè)
        if emp_id in self.employees and not overwrite:
            return False, f"{config.MESSAGES['employee_exists']} ({emp_id})"
        
        # Đảm bảo embeddings là list
        if not isinstance(embeddings, list):
            embeddings = [embeddings]
        
        # Lưu ảnh nếu có - tạo thư mục riêng cho mỗi nhân viên
        if photos is not None:
            import cv2
            if not isinstance(photos, list):
                photos = [photos]
            
            # Tạo tên thư mục: EMP001_Nguyen_Van_A
            safe_name = self._sanitize_folder_name(name)
            folder_name = f"{emp_id}_{safe_name}"
            employee_photo_folder = os.path.join(config.PHOTOS_FOLDER, folder_name)
            
            # Nếu ghi đè, xóa thư mục ảnh cũ để tránh lẫn lộn
            if overwrite and os.path.exists(employee_photo_folder):
                shutil.rmtree(employee_photo_folder)
            
            # Tạo thư mục
            if not os.path.exists(employee_photo_folder):
                os.makedirs(employee_photo_folder)
            
            # Lưu từng ảnh vào thư mục
            for i, photo in enumerate(photos):
                photo_file = os.path.join(
                    employee_photo_folder, f"{i+1}.jpg"
                )
                cv2.imwrite(photo_file, photo)
        
        # Thêm vào RAM
        self.employees[emp_id] = {
            "name": name,
            "department": department,
            "embeddings": embeddings,
            "num_photos": len(embeddings)
        }
        
        # Lưu database
        self._save_database()
        
        # Rebuild embedding matrix
        self._rebuild_embedding_matrix()
        
        return True, f"{config.MESSAGES['register_success']} {name} ({emp_id}) - {len(embeddings)} ảnh"
    
    def get_employee(self, emp_id):
        """
        Lấy thông tin nhân viên theo mã.
        
        Args:
            emp_id: Mã nhân viên
        
        Returns:
            dict: Thông tin nhân viên hoặc None
        """
        return self.employees.get(emp_id)
    
    def get_all_employees(self):
        """
        Lấy tất cả nhân viên.
        
        Returns:
            dict: Dictionary chứa tất cả nhân viên
        """
        return self.employees
    
    def get_embedding_matrix(self):
        """
        Lấy embedding matrix và mapping cho vectorized search.
        
        Returns:
            tuple: (matrix, mapping)
                - matrix: np.ndarray shape (N, 128) - tất cả embeddings đã stack
                - mapping: List[(emp_id, photo_idx)] - mapping index -> employee
                
        Trả về (None, []) nếu không có embeddings.
        """
        return self._embedding_matrix, self._embedding_map
    
    def _save_embeddings_npz(self):
        """
        Lưu tất cả embeddings vào 1 file npz tối ưu.
        """
        if self._embedding_matrix is None or len(self._embedding_map) == 0:
            return
        
        np.savez(
            self.EMBEDDINGS_FILE,
            matrix=self._embedding_matrix,
            mapping=np.array(self._embedding_map, dtype=object)
        )
    
    def _rebuild_embedding_matrix(self):
        """
        Rebuild embedding matrix từ employees dict.
        Lưu TOÀN BỘ các mẫu khuôn mặt của từng người để đạt độ chính xác cao nhất.
        """
        all_embeddings = []
        all_mapping = []
        
        for emp_id, info in self.employees.items():
            for i, emb in enumerate(info["embeddings"]):
                all_embeddings.append(emb.flatten())
                all_mapping.append((emp_id, i))
        
        if all_embeddings:
            self._embedding_matrix = np.vstack(all_embeddings).astype(np.float32)
            self._embedding_map = all_mapping
        else:
            self._embedding_matrix = None
            self._embedding_map = []
        
        # Lưu file npz
        self._save_embeddings_npz()
    
    def delete_employee(self, emp_id):
        """
        Xóa nhân viên khỏi database.
        
        Args:
            emp_id: Mã nhân viên cần xóa
        
        Returns:
            tuple: (success, message)
        """
        if emp_id not in self.employees:
            return False, config.MESSAGES['employee_not_found']
        
        name = self.employees[emp_id]["name"]
        
        # Xóa khỏi RAM
        del self.employees[emp_id]  
        
        # Xóa thư mục ảnh của nhân viên
        # Tìm và xóa thư mục có prefix là emp_id
        if os.path.exists(config.PHOTOS_FOLDER):
            for folder in os.listdir(config.PHOTOS_FOLDER):
                if folder.startswith(f"{emp_id}_"):
                    folder_path = os.path.join(config.PHOTOS_FOLDER, folder)
                    if os.path.isdir(folder_path):
                        shutil.rmtree(folder_path)
        
        # Cập nhật database
        self._save_database()
        
        # Rebuild embedding matrix
        self._rebuild_embedding_matrix()
        
        return True, f"Đã xóa nhân viên: {name} ({emp_id})"
    
    def count(self):
        """
        Đếm số lượng nhân viên.
        
        Returns:
            int: Số lượng nhân viên
        """
        return len(self.employees)
    
    def exists(self, emp_id):
        """
        Kiểm tra nhân viên có tồn tại không.
        
        Args:
            emp_id: Mã nhân viên
        
        Returns:
            bool: True nếu tồn tại
        """
        return emp_id in self.employees
    
    def update_employee(self, emp_id, name=None, department=None):
        """
        Cập nhật thông tin nhân viên và đồng bộ tên thư mục ảnh.
        
        Args:
            emp_id: Mã nhân viên
            name: Họ tên mới (optional)
            department: Phòng ban mới (optional)
        
        Returns:
            tuple: (success, message)
        """
        if emp_id not in self.employees:
            return False, config.MESSAGES['employee_not_found']
        
        # Lấy tên cũ trước khi cập nhật
        old_name = self.employees[emp_id].get("name")
        
        # Cập nhật thông tin và đổi tên thư mục nếu tên thay đổi
        if name and name != old_name:
            if os.path.exists(config.PHOTOS_FOLDER):
                new_safe_name = self._sanitize_folder_name(name)
                new_folder_name = f"{emp_id}_{new_safe_name}"
                new_path = os.path.join(config.PHOTOS_FOLDER, new_folder_name)
                
                # Tìm và đổi tên thư mục có prefix là emp_id_
                for folder in os.listdir(config.PHOTOS_FOLDER):
                    if folder.startswith(f"{emp_id}_"):
                        old_path = os.path.join(config.PHOTOS_FOLDER, folder)
                        # Chỉ đổi tên nếu thư mục tồn tại và đường dẫn mới khác đường dẫn cũ
                        if os.path.isdir(old_path) and old_path != new_path:
                            try:
                                # Nếu thư mục đích đã tồn tại (hiếm gặp), xóa nó trước
                                if os.path.exists(new_path):
                                    shutil.rmtree(new_path)
                                os.rename(old_path, new_path)
                            except Exception as e:
                                print(f"[ERROR] Lỗi đổi tên thư mục: {e}")
            
            self.employees[emp_id]["name"] = name
            
        if department:
            self.employees[emp_id]["department"] = department
        
        # Lưu database
        self._save_database()
        
        return True, f"Đã cập nhật thông tin nhân viên: {emp_id}"
    
    def add_employee_info_only(self, emp_id, name, department):
        """
        Thêm nhân viên mới chỉ với thông tin cơ bản (không có embeddings).
        Dùng cho việc thêm nhân viên từ web dashboard.
        
        Args:
            emp_id: Mã nhân viên
            name: Họ tên
            department: Phòng ban
        
        Returns:
            tuple: (success, message)
        """
        # Kiểm tra trùng mã
        if emp_id in self.employees:
            return False, f"{config.MESSAGES['employee_exists']} ({emp_id})"
        
        # Thêm vào RAM (không có embeddings)
        self.employees[emp_id] = {
            "name": name,
            "department": department,
            "embeddings": [],
            "num_photos": 0
        }
        
        # Lưu database
        self._save_database()
        
        return True, f"Đã thêm nhân viên: {name} ({emp_id}) - Chưa có ảnh đăng ký"


class AttendanceDatabase:
    """
    Lớp quản lý dữ liệu điểm danh.
    
    Dữ liệu được lưu vào file CSV theo ngày:
    attendance_YYYY-MM-DD.csv
    """
    
    def __init__(self):
        """
        Khởi tạo database điểm danh.
        """
        # Đảm bảo thư mục tồn tại
        if not os.path.exists(config.ATTENDANCE_FOLDER):
            os.makedirs(config.ATTENDANCE_FOLDER)
    
    def _get_csv_path(self, date_str=None):
        """
        Lấy đường dẫn file CSV theo ngày.
        
        Args:
            date_str: Ngày (format: YYYY-MM-DD), mặc định là hôm nay
        
        Returns:
            str: Đường dẫn file CSV
        """
        if date_str is None:
            date_str = datetime.now().strftime(config.DATE_FORMAT)
        
        return os.path.join(
            config.ATTENDANCE_FOLDER, 
            f"attendance_{date_str}.csv"
        )
    
    def record(self, emp_id, name, department):
        """
        Ghi nhận phát hiện khuôn mặt.
        
        Args:
            emp_id: Mã nhân viên
            name: Họ tên
            department: Phòng ban
        
        Returns:
            dict: Thông tin đã ghi
        """
        now = datetime.now()
        date_str = now.strftime(config.DATE_FORMAT)
        time_str = now.strftime(config.TIME_FORMAT)
        
        csv_file = self._get_csv_path(date_str)
        file_exists = os.path.exists(csv_file)
        
        # Ghi vào file CSV
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Ghi header nếu file mới
            if not file_exists:
                writer.writerow([
                    "Mã NV", "Họ tên", "Phòng ban",
                    "Ngày", "Giờ", "Loại điểm danh"
                ])
            
            writer.writerow([
                emp_id, name, department,
                date_str, time_str, config.ATTENDANCE_DETECT
            ])
        
        record_info = {
            "emp_id": emp_id,
            "name": name,
            "department": department,
            "date": date_str,
            "time": time_str,
            "type": config.ATTENDANCE_DETECT
        }
        
        # Nháy đèn báo điểm danh thành công
        flash_light()
        
        return record_info
    
    def get_records(self, date_str=None):
        """
        Lấy danh sách điểm danh theo ngày.
        
        Args:
            date_str: Ngày cần xem (format: YYYY-MM-DD)
        
        Returns:
            list: Danh sách các bản ghi điểm danh
        """
        csv_file = self._get_csv_path(date_str)
        
        if not os.path.exists(csv_file):
            return []
        
        records = []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
        
        return records
    
    def get_employee_records(self, emp_id, date_str=None):
        """Lấy điểm danh của một nhân viên theo ngày."""
        all_records = self.get_records(date_str)
        return [r for r in all_records if r.get("Mã NV") == emp_id]