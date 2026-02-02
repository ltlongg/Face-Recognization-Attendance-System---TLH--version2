"""
WEB PORTAL UTILS
Contains business logic and data processing for the web dashboard.
"""

import os
import csv
import json
from datetime import datetime, timedelta

def calculate_work_duration(check_in_str, check_out_str):
    """Tính toán tổng thời gian làm việc (HH:mm:ss)"""
    if not check_in_str or not check_out_str:
        return "--:--:--"
    try:
        t_in = datetime.strptime(check_in_str, "%H:%M:%S")
        t_out = datetime.strptime(check_out_str, "%H:%M:%S")
        diff = t_out - t_in
        if diff.total_seconds() < 0:
            return "00:00:00"
        
        # Format HH:mm:ss
        seconds = int(diff.total_seconds())
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    except:
        return "--:--:--"

def determine_status(check_in_str, check_out_str, manual_overrides=None, emp_id=None):
    """
    Xác định trạng thái: Đúng giờ, Đi muộn, Về sớm, Nghỉ, hoặc Ưu tiên Manual override.
    """
    # 1. Check manual override first
    if manual_overrides and emp_id in manual_overrides:
        return manual_overrides[emp_id]

    if not check_in_str:
        return "Nghỉ"
        
    try:
        t_in = datetime.strptime(check_in_str, "%H:%M:%S").time()
        in_deadline = datetime.strptime("08:00:00", "%H:%M:%S").time()
        
        status_list = []
        if t_in > in_deadline:
            status_list.append("Đi muộn")
            
        if check_out_str:
            t_out = datetime.strptime(check_out_str, "%H:%M:%S").time()
            out_deadline = datetime.strptime("17:30:00", "%H:%M:%S").time()
            if t_out < out_deadline:
                status_list.append("Về sớm")
        
        if not status_list:
            return "Đúng giờ"
        return " + ".join(status_list)
    except:
        return "Lỗi dữ liệu"

class AttendanceReader:
    """Class xử lý đọc và tổng hợp dữ liệu từ CSV và JSON manual overrides"""
    
    def __init__(self, attendance_dir, employees_json_path):
        self.attendance_dir = attendance_dir
        self.employees_json_path = employees_json_path
        
    def get_employees_info(self):
        """Đọc thông tin nhân viên từ JSON"""
        if not os.path.exists(self.employees_json_path):
            return {}
        try:
            with open(self.employees_json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def get_manual_overrides(self, date_str):
        """Đọc các trạng thái do Quản trị viên ghi đè bằng tay từ JSON"""
        manual_path = os.path.join(self.attendance_dir, f"manual_status_{date_str}.json")
        if os.path.exists(manual_path):
            try:
                with open(manual_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def get_records_by_date(self, date_str):
        """Tổng hợp dữ liệu cho một ngày cụ thể (CSV + Manual Override)"""
        csv_path = os.path.join(self.attendance_dir, f"attendance_{date_str}.csv")
        all_employees = self.get_employees_info()
        manual_overrides = self.get_manual_overrides(date_str)
        
        # Kết quả mẫu: {emp_id: {name, check_in, check_out, status, duration}}
        results = {}
        for emp_id, info in all_employees.items():
            results[emp_id] = {
                "name": info.get("name", "Unknown"),
                "department": info.get("department", "N/A"),
                "check_in": None,
                "check_out": None,
                "status": "Nghỉ",
                "duration": "--:--:--"
            }

        # Đọc dữ liệu từ file CSV
        if os.path.exists(csv_path):
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        eid = row.get('Mã NV')
                        if eid and eid in results:
                            time_str = row.get('Giờ')
                            if not results[eid]["check_in"]:
                                results[eid]["check_in"] = time_str
                            results[eid]["check_out"] = time_str
            except Exception as e:
                print(f"Error reading {csv_path}: {e}")

        # Tính toán trạng thái và thời gian
        for eid, info in results.items():
            info["status"] = determine_status(info["check_in"], info["check_out"], manual_overrides, eid)
            info["duration"] = calculate_work_duration(info["check_in"], info["check_out"])
            
        return results

    def get_available_dates(self, max_days=31):
        """Lấy danh sách các ngày có file điểm danh, tối đa 31 ngày gần nhất"""
        if not os.path.exists(self.attendance_dir):
            return []
            
        files = os.listdir(self.attendance_dir)
        dates = []
        for f in files:
            if f.startswith("attendance_") and f.endswith(".csv"):
                date_part = f.replace("attendance_", "").replace(".csv", "")
                dates.append(date_part)
        
        # Sắp xếp giảm dần (mới nhất lên đầu)
        dates.sort(reverse=True)
        return dates[:max_days]

    def get_monthly_summary(self, max_days=31):
        """Tổng hợp thống kê cho 31 ngày gần nhất"""
        dates = self.get_available_dates(max_days)
        all_employees = self.get_employees_info()
        
        daily_stats = []
        total_records = 0
        total_on_time_sum = 0
        
        for d in dates:
            records = self.get_records_by_date(d)
            total = len(records)
            on_time = sum(1 for r in records.values() if r["status"] == "Đúng giờ")
            issues = sum(1 for r in records.values() if r["status"] not in ["Đúng giờ", "Nghỉ"])
            
            percent = (on_time / total * 100) if total > 0 else 0
            total_on_time_sum += percent
            
            daily_stats.append({
                "date": d,
                "total": total,
                "on_time": on_time,
                "issues": issues,
                "on_time_percent": percent
            })
            total_records += sum(1 for r in records.values() if r["check_in"])

        summary = {
            "total_days": len(dates),
            "total_employees": len(all_employees),
            "total_records": total_records,
            "avg_on_time_percent": (total_on_time_sum / len(dates)) if dates else 0
        }
        
        return {"summary": summary, "daily_stats": daily_stats}

    def get_employee_history(self, emp_id, days=31):
        """Lấy lịch sử của 1 nhân viên trong X ngày gần nhất"""
        available_dates = self.get_available_dates(days)
        history = []
        
        for d in available_dates:
            records = self.get_records_by_date(d)
            if emp_id in records:
                # Bao gồm tất cả các ngày, kể cả khi nhân viên nghỉ
                day_data = records[emp_id]
                day_data["date"] = d
                history.append(day_data)
        
        return history
