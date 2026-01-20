from flask import Flask, render_template_string, request, redirect, url_for, session, Response, jsonify
import os
import cv2
import json
import threading
import time
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
import sys
from datetime import datetime
from config import CAMERA_INDEX

# Add parent directory to path to import local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import EmployeeDatabase
from config import (
    USERNAME, PASSWORD, USER_USERNAME, USER_PASSWORD,
    ATTENDANCE_FOLDER, PHOTOS_FOLDER, EMPLOYEES_DB_FILE,
    TOTAL_FRAMES_TO_CAPTURE, FRAME_CAPTURE_INTERVAL, BLUR_THRESHOLD
)
from models import FaceDetector, FaceRecognizer
from attendance_service import VideoRegistrationService
from camera import CameraManager

# Global detectors for web portal
detector = None
recognizer = None

def get_models():
    global detector, recognizer
    if detector is None:
        detector = FaceDetector()
    if recognizer is None:
        recognizer = FaceRecognizer()
    return detector, recognizer

# Import local modules from this folder
try:
    from web_portal.templates import (
        LOGIN_TEMPLATE, EMPLOYEES_TEMPLATE, EMPLOYEE_FORM_TEMPLATE,
        VIDEO_REGISTER_TEMPLATE, MONTHLY_TEMPLATE, DAILY_TEMPLATE,
        EMPLOYEE_DETAIL_TEMPLATE, MONTHLY_DETAIL_TEMPLATE
    )
    from web_portal.utils import AttendanceReader
except ImportError:
    from templates import (
        LOGIN_TEMPLATE, EMPLOYEES_TEMPLATE, EMPLOYEE_FORM_TEMPLATE,
        VIDEO_REGISTER_TEMPLATE, MONTHLY_TEMPLATE, DAILY_TEMPLATE,
        EMPLOYEE_DETAIL_TEMPLATE, MONTHLY_DETAIL_TEMPLATE
    )
    from utils import AttendanceReader

app = Flask(__name__)
app.secret_key = 'super-secret-key-123'

# Global state for video registration
video_registration_state = {
    'active': False,
    'emp_id': None,
    'count': 0,
    'total': TOTAL_FRAMES_TO_CAPTURE,
    'mode': 'idle',  # idle, capturing, saving, done
    'message': '',
    'face_detected': False,
    'is_blurry': False,
    'captured_frames': [],
    'last_capture_time': 0,
}

def admin_required(f):
    def wrap(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

def login_required(f):
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        
        # Check Admin
        if user == USERNAME and pwd == PASSWORD:
            session['logged_in'] = True
            session['role'] = 'admin'
            return redirect(url_for('monthly_dashboard'))
        
        # Check Employee View Only Account
        if user == USER_USERNAME and pwd == USER_PASSWORD:
            session['logged_in'] = True
            session['role'] = 'user'
            return redirect(url_for('monthly_dashboard'))

        return render_template_string(LOGIN_TEMPLATE, error="Sai tài khoản hoặc mật khẩu!")
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return redirect(url_for('monthly_dashboard'))

@app.route('/monthly')
@login_required
def monthly_dashboard():
    reader = AttendanceReader(ATTENDANCE_FOLDER, EMPLOYEES_DB_FILE)
    data = reader.get_monthly_summary(31)
    return render_template_string(MONTHLY_TEMPLATE, data=data)

@app.route('/daily')
@login_required
def daily_dashboard():
    date_str = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    reader = AttendanceReader(ATTENDANCE_FOLDER, EMPLOYEES_DB_FILE)
    
    available_dates = reader.get_available_dates(31)
    if not available_dates and date_str == datetime.now().strftime("%Y-%m-%d"):
        available_dates = [date_str]
    
    records = reader.get_records_by_date(date_str)
    
    # Calculate stats
    total = len(records)
    on_time = sum(1 for r in records.values() if r["status"] == "Đúng giờ")
    issues = sum(1 for r in records.values() if r["status"] not in ["Đúng giờ", "Nghỉ"])
    percent = (on_time / total * 100) if total > 0 else 0
    
    stats = {
        "total": total,
        "on_time": on_time,
        "issues": issues,
        "on_time_percent": percent
    }
    
    return render_template_string(DAILY_TEMPLATE, 
                                 employees=records, 
                                 date=date_str, 
                                 available_dates=available_dates,
                                 stats=stats)

@app.route('/monthly-detail')
@login_required
def monthly_detail():
    days = int(request.args.get('days', 31))
    reader = AttendanceReader(ATTENDANCE_FOLDER, EMPLOYEES_DB_FILE)
    dates = reader.get_available_dates(days)
    dates.sort() # Show chronological order in detail view
    
    employees = reader.get_employees_info()
    employee_data = {}
    
    for emp_id in employees:
        employee_data[emp_id] = {}
        for date in dates:
            day_records = reader.get_records_by_date(date)
            if emp_id in day_records:
                employee_data[emp_id][date] = day_records[emp_id]

    return render_template_string(MONTHLY_DETAIL_TEMPLATE, 
                                 employees=employees, 
                                 dates=dates, 
                                 employee_data=employee_data,
                                 days=days)

@app.route('/employee/<emp_id>')
@login_required
def employee_detail(emp_id):
    reader = AttendanceReader(ATTENDANCE_FOLDER, EMPLOYEES_DB_FILE)
    employees = reader.get_employees_info()
    
    if emp_id not in employees:
        return "Nhân viên không tồn tại", 404
        
    info = employees[emp_id]
    history = reader.get_employee_history(emp_id, 31)
    
    return render_template_string(EMPLOYEE_DETAIL_TEMPLATE,
                                 emp_id=emp_id,
                                 emp_name=info['name'],
                                 emp_dept=info.get('department', 'N/A'),
                                 history=history)

@app.route('/api/update-status', methods=['POST'])
@admin_required
def update_status():
    data = request.json
    emp_id = data.get('emp_id')
    date_str = data.get('date')
    new_status = data.get('status')
    
    if not all([emp_id, date_str, new_status]):
        return jsonify({"status": "error", "message": "Thiếu dữ liệu"}), 400
        
    # Ensure directory exists
    if not os.path.exists(ATTENDANCE_FOLDER):
        os.makedirs(ATTENDANCE_FOLDER)
        
    manual_path = os.path.join(ATTENDANCE_FOLDER, f"manual_status_{date_str}.json")
    
    # Load existing
    overrides = {}
    if os.path.exists(manual_path):
        try:
            with open(manual_path, 'r', encoding='utf-8') as f:
                overrides = json.load(f)
        except:
            pass
            
    # Update
    overrides[emp_id] = new_status
    
    # Save
    with open(manual_path, 'w', encoding='utf-8') as f:
        json.dump(overrides, f, indent=4, ensure_ascii=False)
        
    return jsonify({"status": "success", "message": "Đã cập nhật trạng thái"})

@app.route('/employees')
@admin_required
def list_employees():
    db = EmployeeDatabase()
    employees = db.get_all_employees()
    # Add count of photos for each employee
    for eid in employees:
        # Sử dụng _sanitize_folder_name để tìm đúng thư mục (vì tên có thể có dấu)
        safe_name = db._sanitize_folder_name(employees[eid]['name'])
        emp_dir = os.path.join(PHOTOS_FOLDER, f"{eid}_{safe_name}")
        
        if os.path.exists(emp_dir):
            employees[eid]['num_photos'] = len([f for f in os.listdir(emp_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))])
        else:
            # Thử tìm các thư mục có prefix là eid_ (phòng trường hợp tên thư mục bị lệch)
            found = False
            if os.path.exists(PHOTOS_FOLDER):
                for folder in os.listdir(PHOTOS_FOLDER):
                    if folder.startswith(f"{eid}_"):
                        p = os.path.join(PHOTOS_FOLDER, folder)
                        employees[eid]['num_photos'] = len([f for f in os.listdir(p) if f.lower().endswith(('.jpg', '.png', '.jpeg'))])
                        found = True
                        break
            if not found:
                employees[eid]['num_photos'] = 0
            
    return render_template_string(EMPLOYEES_TEMPLATE, employees=employees)

@app.route('/employees/add', methods=['GET', 'POST'])
@admin_required
def add_employee():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        name = request.form['name']
        dept = request.form.get('department', '')
        
        db = EmployeeDatabase()
        if db.exists(emp_id):
            return render_template_string(EMPLOYEE_FORM_TEMPLATE, action='add', error="Mã nhân viên đã tồn tại!")
            
        # Create folder and save info
        db.add_employee_info_only(emp_id, name, dept)
        return redirect(url_for('register_video', emp_id=emp_id))
        
    return render_template_string(EMPLOYEE_FORM_TEMPLATE, action='add', employee=None)

@app.route('/employees/edit/<emp_id>', methods=['GET', 'POST'])
@admin_required
def edit_employee(emp_id):
    db = EmployeeDatabase()
    if not db.exists(emp_id):
        return redirect(url_for('list_employees'))
        
    if request.method == 'POST':
        name = request.form['name']
        dept = request.form.get('department', '')
        # Sử dụng update_employee thay vì add_employee_info_only giúp cập nhật thông tin hiện có
        success, message = db.update_employee(emp_id, name, dept)
        if success:
            return redirect(url_for('list_employees'))
        else:
            employee = db.get_employee(emp_id).copy()
            employee['emp_id'] = emp_id
            return render_template_string(EMPLOYEE_FORM_TEMPLATE, action='edit', employee=employee, error=message)
        
    employee = db.get_employee(emp_id).copy()
    employee['emp_id'] = emp_id
    return render_template_string(EMPLOYEE_FORM_TEMPLATE, action='edit', employee=employee)

@app.route('/employees/delete/<emp_id>', methods=['POST'])
@admin_required
def delete_employee(emp_id):
    db = EmployeeDatabase()
    db.delete_employee(emp_id)
    return redirect(url_for('list_employees'))

@app.route('/employees/register/<emp_id>')
@admin_required
def register_video(emp_id):
    db = EmployeeDatabase()
    if emp_id not in db.employees:
        return redirect(url_for('list_employees'))
    
    employee = db.employees[emp_id]
    # Check current photo count
    emp_dir = os.path.join(PHOTOS_FOLDER, f"{emp_id}_{employee['name']}")
    employee['num_photos'] = len(os.listdir(emp_dir)) if os.path.exists(emp_dir) else 0
    
    return render_template_string(VIDEO_REGISTER_TEMPLATE, emp_id=emp_id, employee=employee)

@app.route('/api/video-feed')
@admin_required
def video_feed():
    """Video feed duy nhất - vừa hiển thị, vừa capture frame khi cần.
    Tất cả logic detect, blur check, capture đều chạy trong 1 luồng này.
    """
    def generate():
        det, rec = get_models()
        
        # Sử dụng CameraManager với Threading để giảm lag RTSP
        with CameraManager(CAMERA_INDEX) as camera:
            if not camera.is_opened:
                return

            while True:
                success, frame = camera.read_frame()
                if not success or frame is None:
                    time.sleep(0.01)
                    continue
                
                # Tạo bản copy sạch ngay lập tức để dùng cho tính toán/lưu trữ
                clean_frame = frame.copy()
                
                # Detect face (Sử dụng ảnh sạch)
                face = det.detect(clean_frame)
                video_registration_state['face_detected'] = face is not None
                
                is_sharp = False
                laplacian_var = 0
                
                if face:
                    x, y, w, h = face.bbox
                    
                    # Kiểm tra độ mờ (Sử dụng ảnh sạch)
                    face_region = clean_frame[y:y+h, x:x+w]
                    if face_region.size > 0:
                        gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
                        laplacian_var = cv2.Laplacian(gray_face, cv2.CV_64F).var()
                        is_blurry = bool(laplacian_var < BLUR_THRESHOLD)
                        is_sharp = not is_blurry
                        video_registration_state['is_blurry'] = is_blurry
                        
                        color = (0, 165, 255) if is_blurry else (0, 255, 0)
                    else:
                        color = (0, 255, 0)
                        video_registration_state['is_blurry'] = False
                    
                    # VẼ LÊN FRAME (Chỉ dùng để hiển thị, không dùng để lưu)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                    
                    # Vẽ landmarks lên frame hiển thị
                    if face.landmarks:
                        for part, pos in face.landmarks.items():
                            if isinstance(pos, (list, tuple)) and len(pos) == 2:
                                cv2.circle(frame, (int(pos[0]), int(pos[1])), 3, (0, 255, 255), -1)
                    
                    # === CAPTURE LOGIC (Lưu clean_frame) ===
                    if video_registration_state['mode'] == 'capturing':
                        current_time = time.time()
                        time_ok = (current_time - video_registration_state['last_capture_time']) >= FRAME_CAPTURE_INTERVAL
                        
                        if is_sharp and time_ok:
                            # Lưu bản SẠCH vào danh sách đăng ký
                            video_registration_state['captured_frames'].append(clean_frame)
                            video_registration_state['last_capture_time'] = current_time
                            video_registration_state['count'] = len(video_registration_state['captured_frames'])
                            video_registration_state['message'] = f'Đã lấy {video_registration_state["count"]}/{TOTAL_FRAMES_TO_CAPTURE} ảnh. Quay trái/phải để lấy nhiều góc.'
                            
                            # Đủ số lượng → chuyển sang saving
                            if video_registration_state['count'] >= TOTAL_FRAMES_TO_CAPTURE:
                                video_registration_state['mode'] = 'saving'
                                video_registration_state['message'] = 'Đang xử lý và lưu dữ liệu...'
                                # Chạy save trong thread riêng để không block video feed
                                threading.Thread(target=save_captured_frames, args=(det, rec), daemon=True).start()
                        
                        elif is_blurry:
                            video_registration_state['message'] = f'Ảnh bị mờ (variance: {laplacian_var:.1f}). Giữ yên và đảm bảo ánh sáng tốt.'
                else:
                    video_registration_state['is_blurry'] = False
                    if video_registration_state['mode'] == 'capturing':
                        video_registration_state['message'] = 'Không phát hiện khuôn mặt. Hãy đưa mặt vào camera.'

                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


def save_captured_frames(det, rec):
    """Lưu các frame đã capture vào database (chạy trong thread riêng để không block video)."""
    state = video_registration_state
    emp_id = state['emp_id']
    frames = state['captured_frames'].copy()  # Copy để tránh race condition
    
    db = EmployeeDatabase()
    if emp_id not in db.employees:
        state['mode'] = 'done'
        state['message'] = 'Lỗi: Mã NV không hợp lệ'
        time.sleep(1.5)
        state['active'] = False
        return
    
    name = db.employees[emp_id]['name']
    dept = db.employees[emp_id].get('department', '')
    
    service = VideoRegistrationService(det, rec, db)
    success, message = service.register_from_video_frames(emp_id, name, dept, frames)
    
    if success:
        state['mode'] = 'done'
        state['message'] = f'✓ Hoàn thành! Đã đăng ký {len(frames)} ảnh.'
    else:
        state['mode'] = 'done'
        state['message'] = f'Lỗi: {message}'
    
    print(f"[INFO] {message}")
    time.sleep(1.5)
    state['active'] = False


@app.route('/api/start-recording', methods=['POST'])
@admin_required
def start_recording():
    """Bắt đầu capture frame - chỉ set state, video_feed sẽ tự capture."""
    data = request.json
    emp_id = data.get('emp_id')
    
    db = EmployeeDatabase()
    if emp_id not in db.employees:
        return jsonify({'status': 'error', 'message': 'Mã NV không hợp lệ'})
    
    # Reset state
    video_registration_state['active'] = True
    video_registration_state['emp_id'] = emp_id
    video_registration_state['count'] = 0
    video_registration_state['total'] = TOTAL_FRAMES_TO_CAPTURE
    video_registration_state['captured_frames'] = []
    video_registration_state['last_capture_time'] = 0
    video_registration_state['mode'] = 'capturing'
    video_registration_state['message'] = 'Đang chờ phát hiện khuôn mặt...'
    
    return jsonify({'status': 'success'})


@app.route('/api/recording-progress')
@admin_required
def recording_progress():
    """API trả về trạng thái capture hiện tại."""
    # Đảm bảo các giá trị trả về là kiểu dữ liệu chuẩn của Python (để JSON serializable)
    return jsonify({
        'recording': bool(video_registration_state['active']),
        'count': int(video_registration_state['count']),
        'total': int(video_registration_state['total']),
        'mode': str(video_registration_state['mode']),
        'message': str(video_registration_state['message']),
        'face_detected': bool(video_registration_state['face_detected']),
        'is_blurry': bool(video_registration_state['is_blurry'])
    })

@app.route('/export-excel')
@login_required
def export_excel():
    days = int(request.args.get('days', 7))
    reader = AttendanceReader(ATTENDANCE_FOLDER, EMPLOYEES_DB_FILE)
    dates = reader.get_available_dates(days)
    dates.sort() # Sắp xếp theo trình tự thời gian
    
    employees = reader.get_employees_info()
    
    # Create Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Diem_Danh_{days}_Ngay"
    
    # Styles
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    center_align = Alignment(horizontal="center", vertical="center")
    border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                   top=Side(style='thin'), bottom=Side(style='thin'))
    
    # Header row 1: Thông tin NV và Các ngày
    ws.merge_cells(start_row=1, start_column=1, end_row=2, end_column=1)
    ws.cell(1, 1).value = "STT"
    ws.merge_cells(start_row=1, start_column=2, end_row=2, end_column=2)
    ws.cell(1, 2).value = "Mã NV"
    ws.merge_cells(start_row=1, start_column=3, end_row=2, end_column=3)
    ws.cell(1, 3).value = "Họ Tên"
    ws.merge_cells(start_row=1, start_column=4, end_row=2, end_column=4)
    ws.cell(1, 4).value = "Phòng Ban"
    
    col_idx = 5
    for d in dates:
        ws.merge_cells(start_row=1, start_column=col_idx, end_row=1, end_column=col_idx+2)
        cell = ws.cell(1, col_idx)
        cell.value = d
        cell.alignment = center_align
        cell.font = header_font
        cell.fill = header_fill
        
        # Sub-header: Vào, Ra, Trạng thái
        ws.cell(2, col_idx).value = "Vào"
        ws.cell(2, col_idx+1).value = "Ra"
        ws.cell(2, col_idx+2).value = "Trạng thái"
        col_idx += 3
        
    # Formatting headers
    for r in [1, 2]:
        for c in range(1, col_idx):
            cell = ws.cell(r, c)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_align
            cell.border = border

    # Data rows
    row_idx = 3
    for emp_id, info in employees.items():
        ws.cell(row_idx, 1).value = row_idx - 2
        ws.cell(row_idx, 2).value = emp_id
        ws.cell(row_idx, 3).value = info['name']
        ws.cell(row_idx, 4).value = info.get('department', 'N/A')
        
        c_idx = 5
        for d in dates:
            day_records = reader.get_records_by_date(d)
            if emp_id in day_records:
                rec = day_records[emp_id]
                ws.cell(row_idx, c_idx).value = rec['check_in'] or "--"
                ws.cell(row_idx, c_idx+1).value = rec['check_out'] or "--"
                status_cell = ws.cell(row_idx, c_idx+2)
                status_cell.value = rec['status']
                
                # Color status
                if rec['status'] == 'Đúng giờ':
                    status_cell.font = Font(color="008000") # Green
                elif rec['status'] != 'Nghỉ':
                    status_cell.font = Font(color="FF0000") # Red
                else:
                    status_cell.font = Font(color="808080") # Gray
            else:
                ws.cell(row_idx, c_idx).value = "--"
                ws.cell(row_idx, c_idx+1).value = "--"
                ws.cell(row_idx, c_idx+2).value = "Nghỉ"
                ws.cell(row_idx, c_idx+2).font = Font(color="808080")
            
            # Auto-align data
            for i in range(3):
                ws.cell(row_idx, c_idx+i).alignment = center_align
                ws.cell(row_idx, c_idx+i).border = border
                
            c_idx += 3
        
        # Border and align for static cols
        for i in range(1, 5):
            ws.cell(row_idx, i).border = border
            ws.cell(row_idx, i).alignment = center_align
            
        row_idx += 1
        
    # Column width adjustments
    ws.column_dimensions['C'].width = 25
    ws.column_dimensions['D'].width = 15
    
    output_filename = f"Bao_Cao_Diem_Danh_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    temp_path = os.path.join(ATTENDANCE_FOLDER, output_filename)
    wb.save(temp_path)
    
    # Function to yield file and then delete
    def stream_and_remove():
        with open(temp_path, 'rb') as f:
            yield from f
        try:
            os.remove(temp_path)
        except:
            pass
            
    return Response(stream_and_remove(), 
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    headers={"Content-Disposition": f"attachment; filename={output_filename}"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
