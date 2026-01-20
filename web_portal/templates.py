"""
WEB PORTAL TEMPLATES
Contains all HTML strings for the web dashboard.
"""

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔐 Đăng Nhập - Hệ Thống Điểm Danh</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            width: 100%;
            max-width: 400px;
        }
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .login-header h1 {
            color: #667eea;
            font-size: 2em;
            margin-bottom: 10px;
        }
        .login-header p {
            color: #666;
            font-size: 0.9em;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn-login {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn-login:hover {
            transform: translateY(-2px);
        }
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #f5c6cb;
        }
        .footer-info {
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 0.85em;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1>🔐 Đăng Nhập</h1>
            <p>Hệ Thống Điểm Danh Khuôn Mặt</p>
        </div>
        
        {% if error %}
        <div class="error-message">
            ⚠️ {{ error }}
        </div>
        {% endif %}
        
        <form method="POST">
            <div class="form-group">
                <label for="username">Tên đăng nhập</label>
                <input type="text" id="username" name="username" required autofocus>
            </div>
            
            <div class="form-group">
                <label for="password">Mật khẩu</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="btn-login">Đăng Nhập</button>
        </form>
        
        <div class="footer-info">
            © 2026 Face Recognition Attendance System
        </div>
    </div>
</body>
</html>
'''

EMPLOYEES_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>👥 Quản Lý Nhân Viên</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2em; margin-bottom: 10px; }
        
        .nav-buttons {
            padding: 15px 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
        }
        .nav-buttons a {
            display: inline-block;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        }
        .nav-buttons a:hover { background: #764ba2; }
        .btn-refresh {
            background: #ffc107 !important;
            color: #333 !important;
        }
        .btn-refresh:hover { background: #e0a800 !important; }
        
        .content {
            padding: 30px;
        }
        .toolbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .btn-add {
            padding: 12px 24px;
            background: #28a745;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .btn-add:hover { background: #218838; }
        
        table { 
            width: 100%; 
            border-collapse: collapse;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border-radius: 10px;
            overflow: hidden;
        }
        thead {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        th { 
            padding: 15px; 
            text-align: left;
            font-weight: 600;
        }
        td { 
            padding: 12px 15px; 
            border-bottom: 1px solid #f0f0f0;
        }
        tr:hover { background: #f8f9fa; }
        
        .badge {
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
        }
        .badge-success { background: #d4edda; color: #155724; }
        .badge-warning { background: #fff3cd; color: #856404; }
        
        .actions {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .btn-edit, .btn-delete, .btn-register {
            padding: 6px 12px;
            border-radius: 4px;
            text-decoration: none;
            font-size: 0.9em;
            font-weight: bold;
            border: none;
            cursor: pointer;
        }
        .btn-edit { background: #17a2b8; color: white; }
        .btn-edit:hover { background: #138496; }
        .btn-delete { background: #dc3545; color: white; }
        .btn-delete:hover { background: #c82333; }
        .btn-register { background: #28a745; color: white; }
        .btn-register:hover { background: #218838; }
        
        .no-data {
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
        }
        .stat-info {
            background: #e7f3ff;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👥 QUẢN LÝ NHÂN VIÊN</h1>
            <p>Thêm, sửa, xóa thông tin nhân viên</p>
        </div>
        
        <div class="nav-buttons">
            <a href="javascript:location.reload()" class="btn-refresh">🔄 Làm mới</a>
            <a href="/monthly">📅 Tổng quan</a>
            <a href="/daily">🗓 Xem theo ngày</a>
            <a href="/employees" style="background: #17a2b8;">👥 Quản lý NV</a>
            <a href="/logout" style="background: #dc3545;">🚪 Đăng xuất</a>
        </div>
        
        <div class="content">
            <div class="toolbar">
                <div class="stat-info">
                    <span>📊 Tổng số nhân viên: <strong>{{ employees|length }}</strong></span>
                </div>
                <a href="/employees/add" class="btn-add">➕ Thêm nhân viên</a>
            </div>
            
            {% if employees %}
            <table>
                <thead>
                    <tr>
                        <th>STT</th>
                        <th>Mã NV</th>
                        <th>Họ tên</th>
                        <th>Phòng ban</th>
                        <th>Số ảnh</th>
                        <th>Thao tác</th>
                    </tr>
                </thead>
                <tbody>
                    {% for emp_id, info in employees.items() %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td><strong>{{ emp_id }}</strong></td>
                        <td>{{ info.name }}</td>
                        <td>{{ info.department }}</td>
                        <td>
                            {% if info.num_photos > 0 %}
                            <span class="badge badge-success">{{ info.num_photos }} ảnh</span>
                            {% else %}
                            <span class="badge badge-warning">Chưa có ảnh</span>
                            {% endif %}
                        </td>
                        <td class="actions">
                            <a href="/employees/register/{{ emp_id }}" class="btn-register">📹 Đăng ký mặt</a>
                            <a href="/employees/edit/{{ emp_id }}" class="btn-edit">✏️ Sửa</a>
                            <form action="/employees/delete/{{ emp_id }}" method="POST" style="display:inline;" 
                                  onsubmit="return confirm('Bạn có chắc muốn xóa nhân viên {{ info.name }}?');">
                                <button type="submit" class="btn-delete">🗑️ Xóa</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <div class="no-data">
                <h2>📭 Chưa có nhân viên</h2>
                <p>Hãy thêm nhân viên mới để bắt đầu</p>
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

EMPLOYEE_FORM_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% if action == 'add' %}➕ Thêm{% else %}✏️ Sửa{% endif %} Nhân Viên</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }
        .form-container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            width: 100%;
            max-width: 500px;
        }
        .form-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .form-header h1 {
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 10px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .form-group input:disabled {
            background: #f5f5f5;
            color: #666;
        }
        .btn-submit {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
            margin-bottom: 15px;
        }
        .btn-submit:hover {
            transform: translateY(-2px);
        }
        .btn-cancel {
            display: block;
            text-align: center;
            padding: 12px;
            color: #667eea;
            text-decoration: none;
            font-weight: bold;
        }
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #f5c6cb;
        }
        .info-box {
            background: #e7f3ff;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #0066cc;
            font-size: 0.9em;
            color: #004085;
        }
    </style>
</head>
<body>
    <div class="form-container">
        <div class="form-header">
            <h1>{% if action == 'add' %}➕ Thêm Nhân Viên Mới{% else %}✏️ Sửa Thông Tin{% endif %}</h1>
        </div>
        
        {% if error %}
        <div class="error-message">
            ⚠️ {{ error }}
        </div>
        {% endif %}
        
        {% if action == 'add' %}
        <div class="info-box">
            💡 <strong>Bước tiếp theo:</strong> Sau khi nhấn thêm, bạn sẽ được chuyển đến trang <strong>đăng ký khuôn mặt</strong> để thu thập 20 ảnh khuôn mặt từ các góc khác nhau.
        </div>
        {% endif %}
        
        <form method="POST">
            <div class="form-group">
                <label for="emp_id">Mã nhân viên *</label>
                {% if action == 'add' %}
                <input type="text" id="emp_id" name="emp_id" required placeholder="VD: EMP001">
                {% else %}
                <input type="text" id="emp_id" value="{{ employee.emp_id }}" disabled>
                {% endif %}
            </div>
            
            <div class="form-group">
                <label for="name">Họ tên *</label>
                <input type="text" id="name" name="name" required 
                       placeholder="VD: Nguyễn Văn A"
                       value="{{ employee.name if employee else '' }}">
            </div>
            
            <div class="form-group">
                <label for="department">Phòng ban</label>
                <input type="text" id="department" name="department" 
                       placeholder="VD: Phòng IT"
                       value="{{ employee.department if employee else '' }}">
            </div>
            
            <button type="submit" class="btn-submit">
                {% if action == 'add' %}➕ Thêm & Đăng ký khuôn mặt{% else %}💾 Lưu thay đổi{% endif %}
            </button>
            <a href="/employees" class="btn-cancel">← Quay lại danh sách</a>
        </form>
    </div>
</body>
</html>
'''

VIDEO_REGISTER_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📹 Đăng Ký Khuôn Mặt - {{ employee.name }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container { 
            max-width: 900px; 
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            text-align: center;
        }
        .header h1 { font-size: 1.8em; margin-bottom: 8px; }
        .header p { opacity: 0.9; }
        
        .content { padding: 30px; }
        
        .employee-info {
            background: #f8f9fa;
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .employee-info strong { color: #667eea; }
        
        .video-container {
            background: #000;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 20px;
            position: relative;
        }
        .video-container img {
            width: 100%;
            display: block;
        }
        
        .status-indicator {
            position: absolute;
            top: 15px;
            left: 15px;
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
            display: none;
        }
        .status-indicator.capturing {
            background: #28a745;
            color: white;
            display: block;
            animation: pulse 1.5s infinite;
        }
        .status-indicator.no-face {
            background: #dc3545;
            color: white;
            display: block;
        }
        .status-indicator.blurry {
            background: #ffc107;
            color: #333;
            display: block;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .status-message {
            text-align: center;
            font-size: 1.1em;
            color: #333;
            margin-bottom: 15px;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 8px;
            min-height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .status-message.success { background: #d4edda; color: #155724; }
        .status-message.warning { background: #fff3cd; color: #856404; }
        .status-message.error { background: #f8d7da; color: #721c24; }
        
        .progress-section {
            margin-bottom: 20px;
        }
        .progress-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        .progress-container {
            width: 100%;
            height: 25px;
            background: #e0e0e0;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        }
        .progress-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            width: 0%;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 0.85em;
        }
        .progress-bar-fill.processing {
            background: linear-gradient(90deg, #667eea, #764ba2);
            animation: shimmer 2s infinite linear;
            background-size: 200% 100%;
        }
        @keyframes shimmer {
            0% { background-position: 200% 0; }
            100% { background-position: 0 0; }
        }
        
        .controls {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-bottom: 20px;
        }
        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .btn-start { background: #28a745; color: white; }
        .btn-stop { background: #dc3545; color: white; }
        .btn-back { background: #6c757d; color: white; text-decoration: none; }
        
        .instructions {
            background: #e7f3ff;
            padding: 15px 20px;
            border-radius: 10px;
            border-left: 4px solid #0066cc;
        }
        .instructions h3 { color: #004085; margin-bottom: 10px; }
        .instructions ul { margin-left: 20px; color: #004085; }
        .instructions li { margin-bottom: 5px; }
        
        .legend {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.9em;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }
        .legend-color.green { background: #28a745; }
        .legend-color.orange { background: #ffc107; }
        .legend-color.red { background: #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📹 ĐĂNG KÝ KHUÔN MẶT</h1>
            <p>Lấy 20 ảnh khuôn mặt từ các góc khác nhau</p>
        </div>
        
        <div class="content">
            <div class="employee-info">
                <div>
                    <strong>{{ employee.name }}</strong> ({{ emp_id }})
                    <br><small>{{ employee.department }}</small>
                </div>
                <div>
                    {% if employee.num_photos > 0 %}
                    <span style="color: #28a745;">✓ Đã có {{ employee.num_photos }} ảnh</span>
                    {% else %}
                    <span style="color: #ffc107;">⚠ Chưa đăng ký</span>
                    {% endif %}
                </div>
            </div>
            
            <div class="video-container">
                <img id="video-feed" src="/api/video-feed" alt="Video Feed">
                <div id="status-indicator" class="status-indicator"></div>
            </div>
            
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color green"></div>
                    <span>Khuôn mặt rõ nét</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color orange"></div>
                    <span>Ảnh bị mờ</span>
                </div>
            </div>
            
            <div id="status-message" class="status-message" style="margin-top: 15px;">
                Nhấn "Bắt đầu" để đăng ký khuôn mặt. Hãy đảm bảo ánh sáng tốt và đưa mặt vào camera.
            </div>
            
            <div class="progress-section" id="progress-section" style="display: none;">
                <div class="progress-label">
                    <span>Tiến độ thu thập ảnh</span>
                    <span id="progress-text">0 / 20 ảnh</span>
                </div>
                <div class="progress-container">
                    <div id="progress-bar-fill" class="progress-bar-fill"></div>
                </div>
            </div>
            
            <div class="controls">
                <button id="btn-start" class="btn btn-start" onclick="startCapture()">
                    ▶️ Bắt đầu
                </button>
                <button id="btn-stop" class="btn btn-stop" onclick="stopCapture()" style="display: none;">
                    ⏹️ Dừng lại
                </button>
                <a href="/employees" class="btn btn-back">← Quay lại</a>
            </div>
            
            <div class="instructions">
                <h3>📋 Hướng dẫn:</h3>
                <ul>
                    <li>Đảm bảo <strong>ánh sáng đủ</strong> và khuôn mặt <strong>rõ nét</strong></li>
                    <li>Nhìn thẳng vào camera, sau đó <strong>quay trái/phải</strong> nhẹ để lấy nhiều góc</li>
                    <li>Hệ thống sẽ tự động lấy ảnh khi phát hiện khuôn mặt rõ nét</li>
                    <li>Mỗi ảnh cách nhau <strong>0.5 giây</strong>, tổng cộng lấy <strong>20 ảnh</strong></li>
                    <li>Khung <span style="color:#28a745;font-weight:bold;">xanh</span> = OK, khung <span style="color:#ffc107;font-weight:bold;">cam</span> = ảnh mờ</li>
                </ul>
            </div>
        </div>
    </div>
    
    <script>
        const empId = "{{ emp_id }}";
        let capturing = false;
        let progressInterval = null;
        
        function updateProgress() {
            fetch('/api/recording-progress')
                .then(r => r.json())
                .then(data => {
                    const statusMsg = document.getElementById('status-message');
                    const statusIndicator = document.getElementById('status-indicator');
                    const progressText = document.getElementById('progress-text');
                    const progressFill = document.getElementById('progress-bar-fill');
                    
                    if (data.recording) {
                        const count = data.count;
                        const total = data.total;
                        const mode = data.mode;
                        const percent = Math.min((count / total) * 100, 100);
                        
                        progressText.textContent = `${count} / ${total} ảnh`;
                        progressFill.style.width = percent + '%';
                        
                        if (mode === 'capturing') {
                            statusMsg.textContent = data.message || 'Đang thu thập ảnh...';
                            statusMsg.className = 'status-message';
                            progressFill.classList.remove('processing');
                            
                            // Cập nhật indicator
                            if (!data.face_detected) {
                                statusIndicator.textContent = '❌ Không thấy mặt';
                                statusIndicator.className = 'status-indicator no-face';
                                statusMsg.className = 'status-message warning';
                            } else if (data.is_blurry) {
                                statusIndicator.textContent = '⚠️ Ảnh mờ';
                                statusIndicator.className = 'status-indicator blurry';
                                statusMsg.className = 'status-message warning';
                            } else {
                                statusIndicator.textContent = '✓ Đang lấy ảnh';
                                statusIndicator.className = 'status-indicator capturing';
                            }
                            
                        } else if (mode === 'saving') {
                            statusMsg.textContent = '⏳ Đang xử lý và lưu dữ liệu...';
                            statusMsg.className = 'status-message';
                            progressFill.classList.add('processing');
                            statusIndicator.style.display = 'none';
                            document.getElementById('btn-stop').style.display = 'none';
                            
                        } else if (mode === 'done') {
                            statusMsg.textContent = data.message || '✓ Hoàn thành!';
                            statusMsg.className = 'status-message success';
                            progressFill.style.width = '100%';
                            progressFill.classList.remove('processing');
                            statusIndicator.style.display = 'none';
                        }
                        
                    } else if (capturing) {
                        // Quá trình kết thúc
                        capturing = false;
                        clearInterval(progressInterval);
                        
                        // Hiển thị thông báo hoàn thành và chuyển trang
                        statusMsg.textContent = '✓ Hoàn thành! Đang chuyển trang...';
                        statusMsg.className = 'status-message success';
                        
                        setTimeout(() => {
                            window.location.href = '/employees';
                        }, 1000);
                    }
                })
                .catch(err => {
                    console.error('Error fetching progress:', err);
                });
        }
        
        function startCapture() {
            fetch('/api/start-recording', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({emp_id: empId})
            }).then(r => r.json()).then(data => {
                if (data.status === 'success') {
                    capturing = true;
                    document.getElementById('btn-start').style.display = 'none';
                    document.getElementById('btn-stop').style.display = 'inline-block';
                    document.getElementById('progress-section').style.display = 'block';
                    document.getElementById('status-message').textContent = 'Đang chuẩn bị...';
                    progressInterval = setInterval(updateProgress, 200);
                } else {
                    document.getElementById('status-message').textContent = '❌ ' + data.message;
                    document.getElementById('status-message').className = 'status-message error';
                }
            });
        }
        
        function stopCapture() {
            if (!capturing) return;
            
            document.getElementById('status-message').textContent = '⏳ Đang dừng và xử lý...';
            document.getElementById('btn-stop').style.display = 'none';
            
            fetch('/api/stop-recording', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({emp_id: empId})
            }).then(r => r.json()).then(data => {
                // Tiếp tục theo dõi progress cho đến khi hoàn tất
            });
        }
    </script>
</body>
</html>
'''

MONTHLY_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Tổng Quan 31 Ngày</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2em; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        
        .nav-buttons {
            padding: 15px 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
        }
        .nav-buttons a {
            display: inline-block;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        }
        .nav-buttons a:hover { background: #764ba2; }
        .btn-refresh {
            background: #ffc107 !important;
            color: #333 !important;
        }
        .btn-refresh:hover { background: #e0a800 !important; }
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }
        .summary-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            text-align: center;
        }
        .summary-card .icon { font-size: 2.5em; margin-bottom: 10px; }
        .summary-card .value { 
            font-size: 2.2em; 
            font-weight: bold; 
            color: #667eea;
            margin: 10px 0;
        }
        .summary-card .label { 
            color: #6c757d; 
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .daily-table {
            padding: 30px;
        }
        .daily-table h2 {
            margin-bottom: 20px;
            color: #333;
        }
        table { 
            width: 100%; 
            border-collapse: collapse;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border-radius: 10px;
            overflow: hidden;
        }
        thead {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        th { 
            padding: 15px; 
            text-align: left;
            font-weight: 600;
        }
        td { 
            padding: 12px 15px; 
            border-bottom: 1px solid #f0f0f0;
        }
        tr:hover { background: #f8f9fa; }
        tr:last-child td { border-bottom: none; }
        
        .badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            display: inline-block;
        }
        .badge-success { background: #28a745; color: white; }
        .badge-warning { background: #ffc107; color: #333; }
        .badge-danger { background: #dc3545; color: white; }
        
        .date-link {
            color: #667eea;
            text-decoration: none;
            font-weight: bold;
        }
        .date-link:hover {
            text-decoration: underline;
        }
        
        .progress-bar {
            height: 8px;
            background: #f0f0f0;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }
        
        .no-data {
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
        }
        .no-data h2 { margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 TỔNG QUAN ĐIỂM DANH 31 NGÀY</h1>
            <p>Thống kê và phân tích xu hướng điểm danh</p>
        </div>
        
        <div class="nav-buttons">
            <a href="javascript:location.reload()" class="btn-refresh">🔄 Làm mới</a>
            <a href="/monthly">📅 Tổng quan</a>
            <a href="/monthly-detail">📋 Chi tiết 31 ngày</a>
            <a href="/daily">🗓 Xem theo ngày</a>
            {% if session.get('role') == 'admin' %}
            <a href="/employees" style="background: #17a2b8;">👥 Quản lý NV</a>
            {% endif %}
            <a href="/export-excel?days=31" style="background: #28a745;">📥 Xuất Excel 31 ngày</a>
            <a href="/logout" style="background: #dc3545;">🚪 Đăng xuất</a>
        </div>
        
        {% if data.daily_stats %}
        <div class="summary-cards">
            <div class="summary-card">
                <div class="icon">📅</div>
                <div class="value">{{ data.summary.total_days }}</div>
                <div class="label">Ngày có dữ liệu</div>
            </div>
            <div class="summary-card">
                <div class="icon">👥</div>
                <div class="value">{{ data.summary.total_employees }}</div>
                <div class="label">Tổng nhân viên</div>
            </div>
            <div class="summary-card">
                <div class="icon">📊</div>
                <div class="value">{{ data.summary.total_records }}</div>
                <div class="label">Lượt điểm danh</div>
            </div>
            <div class="summary-card">
                <div class="icon">✅</div>
                <div class="value">{{ "%.1f"|format(data.summary.avg_on_time_percent) }}%</div>
                <div class="label">Trung bình đúng giờ</div>
            </div>
        </div>
        
        <div class="daily-table">
            <h2>📈 Chi tiết từng ngày ({{ data.daily_stats|length }} ngày gần nhất)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Ngày</th>
                        <th style="text-align: center;">Tổng NV</th>
                        <th style="text-align: center;">Đúng giờ</th>
                        <th style="text-align: center;">Có vấn đề</th>
                        <th>Tỷ lệ đúng giờ</th>
                        <th style="text-align: center;">Đánh giá</th>
                    </tr>
                </thead>
                <tbody>
                    {% for day in data.daily_stats %}
                    <tr>
                        <td>
                            <a href="/daily?date={{ day.date }}" class="date-link">
                                📆 {{ day.date }}
                            </a>
                        </td>
                        <td style="text-align: center;"><strong>{{ day.total }}</strong></td>
                        <td style="text-align: center;">✅ {{ day.on_time }}</td>
                        <td style="text-align: center;">⚠️ {{ day.issues }}</td>
                        <td>
                            <div>{{ "%.1f"|format(day.on_time_percent) }}%</div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {{ day.on_time_percent }}%"></div>
                            </div>
                        </td>
                        <td style="text-align: center;">
                            {% if day.on_time_percent >= 90 %}
                            <span class="badge badge-success">Xuất sắc</span>
                            {% elif day.on_time_percent >= 75 %}
                            <span class="badge badge-warning">Khá</span>
                            {% else %}
                            <span class="badge badge-danger">Cần cải thiện</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <div class="no-data">
            <h2>📭 Chưa có dữ liệu</h2>
            <p>Hệ thống chưa ghi nhận dữ liệu điểm danh nào</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

DAILY_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Dashboard Điểm Danh</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2em; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        
        .nav-buttons {
            padding: 15px 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
        }
        .nav-buttons a {
            display: inline-block;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        }
        .nav-buttons a:hover { background: #764ba2; }
        .btn-refresh {
            background: #ffc107 !important;
            color: #333 !important;
        }
        .btn-refresh:hover { background: #e0a800 !important; }
        
        .date-selector {
            padding: 20px 30px;
            background: #fff;
            border-bottom: 1px solid #dee2e6;
        }
        .date-selector select {
            padding: 10px 15px;
            border: 2px solid #667eea;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            background: white;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            text-align: center;
        }
        .stat-card h3 { 
            color: #6c757d; 
            font-size: 0.9em; 
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stat-card .number { 
            font-size: 2.5em; 
            font-weight: bold;
            margin: 10px 0;
        }
        .stat-card.success .number { color: #28a745; }
        .stat-card.warning .number { color: #ffc107; }
        .stat-card.danger .number { color: #dc3545; }
        
        .table-container { 
            padding: 30px;
            overflow-x: auto;
        }
        table { 
            width: 100%; 
            border-collapse: collapse;
            background: white;
        }
        th { 
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }
        td { 
            padding: 15px;
            border-bottom: 1px solid #dee2e6;
        }
        tr:hover { background: #f8f9fa; }
        
        .badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            display: inline-block;
        }
        .badge-success { background: #d4edda; color: #155724; }
        .badge-danger { background: #f8d7da; color: #721c24; }
        .badge-warning { background: #fff3cd; color: #856404; }
        
        .emp-link {
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }
        .emp-link:hover {
            text-decoration: underline;
        }
        
        .no-data {
            text-align: center;
            padding: 60px;
            color: #6c757d;
        }
        .no-data h2 { margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 DASHBOARD ĐIỂM DANH CHI TIẾT</h1>
            <p>Xem chi tiết theo từng ngày</p>
        </div>
        
        <div class="nav-buttons">
            <a href="javascript:location.reload()" class="btn-refresh">🔄 Làm mới</a>
            <a href="/monthly">📅 Tổng quan 31 ngày</a>
            <a href="/daily">📋 Chi tiết theo ngày</a>
            {% if session.get('role') == 'admin' %}
            <a href="/employees" style="background: #17a2b8;">👥 Quản lý NV</a>
            {% endif %}
            <a href="/logout" style="background: #dc3545;">🚪 Đăng xuất</a>
        </div>
        
        <div class="date-selector">
            <label for="date-select"><strong>Chọn ngày:</strong></label>
            <select id="date-select" onchange="location.href='/daily?date=' + this.value">
                {% for d in available_dates %}
                <option value="{{ d }}" {% if d == date %}selected{% endif %}>
                    {{ d }}
                </option>
                {% endfor %}
            </select>
        </div>
        
        {% if stats.total > 0 %}
        <div class="stats">
            <div class="stat-card">
                <h3>Tổng số nhân viên</h3>
                <div class="number">{{ stats.total }}</div>
            </div>
            <div class="stat-card success">
                <h3>Đúng giờ</h3>
                <div class="number">{{ stats.on_time }}</div>
                <small>{{ "%.1f"|format(stats.on_time_percent) }}%</small>
            </div>
            <div class="stat-card danger">
                <h3>Có vấn đề</h3>
                <div class="number">{{ stats.issues }}</div>
                <small>{{ "%.1f"|format(100 - stats.on_time_percent) }}%</small>
            </div>
        </div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>STT</th>
                        <th>Mã NV</th>
                        <th>Họ và tên</th>
                        <th>Phòng ban</th>
                        <th>Check-in</th>
                        <th>Check-out</th>
                        <th>Tổng giờ</th>
                        <th>Trạng thái</th>
                    </tr>
                </thead>
                <tbody>
                    {% for emp_id, info in employees.items() %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td><strong>{{ emp_id }}</strong></td>
                        <td>
                            <a href="/employee/{{ emp_id }}" class="emp-link">
                                {{ info.name }}
                            </a>
                        </td>
                        <td>{{ info.department }}</td>
                        <td>{{ info.check_in or '--:--:--' }}</td>
                        <td>{{ info.check_out or '--:--:--' }}</td>
                        <td><strong>{{ info.duration }}</strong></td>
                        <td>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                {% if info.status == 'Đúng giờ' %}
                                <span class="badge badge-success">✅ {{ info.status }}</span>
                                {% elif info.status == 'Đi muộn' %}
                                <span class="badge badge-danger">🕒 {{ info.status }}</span>
                                {% elif info.status == 'Về sớm' %}
                                <span class="badge badge-danger">🏃 {{ info.status }}</span>
                                {% elif info.status == 'Nghỉ' %}
                                <span class="badge" style="background: #e9ecef; color: #6c757d;">💤 {{ info.status }}</span>
                                {% elif info.status == 'Nghỉ có phép' %}
                                <span class="badge badge-warning">📝 {{ info.status }}</span>
                                {% elif info.status == 'Nghỉ không phép' %}
                                <span class="badge badge-danger">❌ {{ info.status }}</span>
                                {% elif info.status == 'Xin về sớm' %}
                                <span class="badge badge-warning">🚪 {{ info.status }}</span>
                                {% elif info.status == 'Công tác' %}
                                <span class="badge badge-success">💼 {{ info.status }}</span>
                                {% elif info.status == 'Làm việc từ xa' %}
                                <span class="badge badge-success">🏠 {{ info.status }}</span>
                                {% else %}
                                <span class="badge badge-danger">⚠️ {{ info.status }}</span>
                                {% endif %}
                                
                                {% if session.get('role') == 'admin' %}
                                <button onclick="editStatus('{{ emp_id }}', '{{ info.name }}', '{{ info.status }}')" 
                                        style="border: none; background: none; cursor: pointer; font-size: 1.2em;" title="Chỉnh sửa trạng thái">
                                    ✏️
                                </button>
                                {% endif %}
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <div class="no-data">
            <h2>📭 Không có dữ liệu</h2>
            <p>Chưa có dữ liệu điểm danh cho ngày {{ date }}</p>
        </div>
        {% endif %}
    </div>

    <!-- Modal chỉnh sửa trạng thái -->
    <div id="statusModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; justify-content: center; align-items: center;">
        <div style="background: white; padding: 30px; border-radius: 10px; width: 400px; box-shadow: 0 5px 20px rgba(0,0,0,0.2);">
            <h3 id="modalTitle" style="margin-bottom: 20px;">Chỉnh sửa trạng thái</h3>
            <p style="margin-bottom: 10px; color: #666;">Chọn trạng thái cho nhân viên:</p>
            <select id="statusSelect" style="width: 100%; padding: 10px; margin-bottom: 20px; border-radius: 5px; border: 1px solid #ddd;">
                <option value="Đúng giờ">Đúng giờ</option>
                <option value="Nghỉ">Nghỉ</option>
                <option value="Nghỉ có phép">Nghỉ có phép</option>
                <option value="Nghỉ không phép">Nghỉ không phép</option>
                <option value="Xin về sớm">Xin về sớm</option>
                <option value="Công tác">Công tác</option>
                <option value="Làm việc từ xa">Làm việc từ xa</option>
            </select>
            <div style="display: flex; gap: 10px; justify-content: flex-end;">
                <button onclick="closeModal()" style="padding: 10px 20px; border: none; border-radius: 5px; background: #6c757d; color: white; cursor: pointer;">Hủy</button>
                <button onclick="saveStatus()" style="padding: 10px 20px; border: none; border-radius: 5px; background: #667eea; color: white; cursor: pointer;">Lưu</button>
            </div>
        </div>
    </div>

    <script>
        let currentEmpId = '';
        const selectedDate = '{{ date }}';

        function editStatus(empId, empName, currentStatus) {
            currentEmpId = empId;
            document.getElementById('modalTitle').textContent = 'Chỉnh sửa: ' + empName;
            document.getElementById('statusSelect').value = currentStatus;
            document.getElementById('statusModal').style.display = 'flex';
        }

        function closeModal() {
            document.getElementById('statusModal').style.display = 'none';
        }

        function saveStatus() {
            const newStatus = document.getElementById('statusSelect').value;
            fetch('/api/update-status', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    emp_id: currentEmpId,
                    date: selectedDate,
                    status: newStatus
                })
            })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success') {
                    location.reload();
                } else {
                    alert('Lỗi: ' + data.message);
                }
            });
        }
    </script>
</body>
</html>
'''

EMPLOYEE_DETAIL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ emp_name }} - Lịch sử điểm danh</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container { 
            max-width: 1000px; 
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
        }
        .header h1 { font-size: 2em; margin-bottom: 5px; }
        .header p { opacity: 0.9; }
        .back-link {
            display: inline-block;
            margin-top: 15px;
            color: white;
            text-decoration: none;
            padding: 8px 15px;
            background: rgba(255,255,255,0.2);
            border-radius: 5px;
        }
        .back-link:hover { background: rgba(255,255,255,0.3); }
        .btn-refresh {
            display: inline-block;
            margin-top: 15px;
            margin-left: 10px;
            background: #ffc107;
            color: #333;
            text-decoration: none;
            padding: 8px 15px;
            border-radius: 5px;
            font-weight: bold;
        }
        .btn-refresh:hover { background: #e0a800; }
        
        .info-section {
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }
        .info-section h3 { margin-bottom: 15px; color: #495057; }
        .info-grid {
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 10px 20px;
        }
        .info-label { font-weight: 600; color: #6c757d; }
        
        .table-container { padding: 30px; }
        table { width: 100%; border-collapse: collapse; }
        th { 
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }
        td { 
            padding: 15px;
            border-bottom: 1px solid #dee2e6;
        }
        tr:hover { background: #f8f9fa; }
        
        .badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            display: inline-block;
        }
        .badge-success { background: #d4edda; color: #155724; }
        .badge-danger { background: #f8d7da; color: #721c24; }
        
        .no-data {
            text-align: center;
            padding: 60px;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👤 {{ emp_name }}</h1>
            <p>Lịch sử điểm danh 7 ngày gần nhất</p>
            <a href="/" class="back-link">← Quay lại Dashboard</a>
            <a href="javascript:location.reload()" class="btn-refresh">🔄 Làm mới</a>
        </div>
        
        <div class="info-section">
            <h3>Thông tin nhân viên</h3>
            <div class="info-grid">
                <div class="info-label">Mã NV:</div>
                <div>{{ emp_id }}</div>
                <div class="info-label">Họ tên:</div>
                <div>{{ emp_name }}</div>
                <div class="info-label">Phòng ban:</div>
                <div>{{ emp_dept }}</div>
            </div>
        </div>
        
        {% if history %}
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Ngày</th>
                        <th>Check-in</th>
                        <th>Check-out</th>
                        <th>Tổng giờ</th>
                        <th>Trạng thái</th>
                    </tr>
                </thead>
                <tbody>
                    {% for record in history %}
                    <tr>
                        <td><strong>{{ record.date }}</strong></td>
                        <td>{{ record.check_in or '--:--:--' }}</td>
                        <td>{{ record.check_out or '--:--:--' }}</td>
                        <td><strong>{{ record.duration }}</strong></td>
                        <td>
                            {% if record.status == 'Đúng giờ' %}
                            <span class="badge badge-success">✓ {{ record.status }}</span>
                            {% else %}
                            <span class="badge badge-danger">⚠ {{ record.status }}</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <div class="no-data">
            <h2>📭 Không có dữ liệu</h2>
            <p>Nhân viên này chưa có lịch sử điểm danh</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

MONTHLY_DETAIL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📋 Chi Tiết {{ days }} Ngày - Tất Cả Nhân Viên</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container { 
            max-width: 100%; 
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow-x: auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2em; margin-bottom: 10px; }
        
        .nav-buttons {
            padding: 15px 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
        }
        .nav-buttons a {
            display: inline-block;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        }
        .nav-buttons a:hover { background: #764ba2; }
        .btn-refresh {
            background: #ffc107 !important;
            color: #333 !important;
        }
        .btn-refresh:hover { background: #e0a800 !important; }
        
        .detail-table {
            padding: 30px;
            overflow-x: auto;
        }
        .detail-table h2 {
            margin-bottom: 20px;
            color: #333;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            min-width: 1200px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border: 1px solid #dee2e6;
        }
        th {
            background: #667eea;
            color: white;
            font-weight: bold;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        .sticky-col {
            position: sticky;
            left: 0;
            background: white;
            z-index: 5;
        }
        .sticky-col.header {
            background: #667eea;
            z-index: 15;
        }
        tbody tr:hover { background: #f8f9fa; }
        
        .badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75em;
            font-weight: bold;
            display: inline-block;
            white-space: nowrap;
        }
        .badge-success { background: #28a745; color: white; }
        .badge-danger { background: #dc3545; color: white; }
        .badge-gray { background: #e9ecef; color: #666; }
        
        .time-cell {
            font-size: 0.9em;
            text-align: center;
        }
        .absent { background: #f8f9fa; color: #999; }
        
        .info-box {
            background: #e7f3ff;
            padding: 15px;
            margin: 20px 30px;
            border-left: 4px solid #0066cc;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 CHI TIẾT {{ days }} NGÀY - TẤT CẢ NHÂN VIÊN</h1>
            <p>Bảng tổng hợp chi tiết điểm danh của tất cả nhân viên</p>
        </div>
        
        <div class="nav-buttons">
            <a href="javascript:location.reload()" class="btn-refresh">🔄 Làm mới</a>
            <a href="/monthly">📅 Tổng quan</a>
            <a href="/monthly-detail">📋 Chi tiết {{ days }} ngày</a>
            <a href="/daily">🗓 Xem theo ngày</a>
            {% if session.get('role') == 'admin' %}
            <a href="/employees" style="background: #17a2b8;">👥 Quản lý NV</a>
            {% endif %}
            <a href="/export-excel?days={{ days }}" style="background: #28a745;">📥 Xuất Excel {{ days }} ngày</a>
            <a href="/logout" style="background: #dc3545;">🚪 Đăng xuất</a>
        </div>
        
        <div class="info-box">
            <strong>💡 Hướng dẫn:</strong> Cuộn ngang để xem tất cả các ngày. 
            Màu xanh = Đúng giờ, Màu đỏ = Có vấn đề, Xám = Không điểm danh.
        </div>
        
        {% if employees %}
        <div class="detail-table">
            <h2>👥 Danh sách {{ employees|length }} nhân viên × {{ dates|length }} ngày</h2>
            <table>
                <thead>
                    <tr>
                        <th class="sticky-col header">STT</th>
                        <th class="sticky-col header" style="left: 60px;">Mã NV</th>
                        <th class="sticky-col header" style="left: 150px;">Họ tên</th>
                        <th class="sticky-col header" style="left: 300px;">Phòng ban</th>
                        {% for date in dates %}
                        <th colspan="3" style="text-align: center; background: #5a67d8;">{{ date }}</th>
                        {% endfor %}
                    </tr>
                    <tr style="background: #e9ecef;">
                        <th class="sticky-col header">&nbsp;</th>
                        <th class="sticky-col header" style="left: 60px;">&nbsp;</th>
                        <th class="sticky-col header" style="left: 150px;">&nbsp;</th>
                        <th class="sticky-col header" style="left: 300px;">&nbsp;</th>
                        {% for date in dates %}
                        <th style="font-size: 0.85em;">Vào</th>
                        <th style="font-size: 0.85em;">Ra</th>
                        <th style="font-size: 0.85em;">Trạng thái</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for emp_id, info in employees.items() %}
                    <tr>
                        <td class="sticky-col">{{ loop.index }}</td>
                        <td class="sticky-col" style="left: 60px;"><strong>{{ emp_id }}</strong></td>
                        <td class="sticky-col" style="left: 150px;">{{ info.name }}</td>
                        <td class="sticky-col" style="left: 300px;">{{ info.department }}</td>
                        
                        {% for date in dates %}
                            {% if date in employee_data[emp_id] %}
                                {% set day_info = employee_data[emp_id][date] %}
                                <td class="time-cell">{{ day_info.check_in or '--' }}</td>
                                <td class="time-cell">{{ day_info.check_out or '--' }}</td>
                                <td style="text-align: center;">
                                    {% if day_info.status == 'Đúng giờ' %}
                                    <span class="badge badge-success">✓</span>
                                    {% elif day_info.status == 'Nghỉ' %}
                                    <span class="badge badge-gray">-</span>
                                    {% else %}
                                    <span class="badge badge-danger" title="{{ day_info.status }}">⚠</span>
                                    {% endif %}
                                </td>
                            {% else %}
                                <td class="absent">--</td>
                                <td class="absent">--</td>
                                <td class="absent"><span class="badge badge-gray">-</span></td>
                            {% endif %}
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <div style="text-align: center; padding: 60px 20px; color: #6c757d;">
            <h2>📭 Chưa có dữ liệu</h2>
            <p>Hệ thống chưa ghi nhận dữ liệu điểm danh nào</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''
