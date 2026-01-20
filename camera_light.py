"""
MODULE ĐIỀU KHIỂN ĐÈN CAMERA
=============================
Cung cấp feedback trực quan khi điểm danh thành công.

Nguyên tắc:
- Một hàm duy nhất: flash_light()
- Non-blocking: chạy trong thread
- Fail silently: lỗi thì log, không crash
"""

import requests
from requests.auth import HTTPDigestAuth
import threading
import time


# Cấu hình camera
CAMERA_IP = "187.26.222.251"
CAMERA_USER = "admin"
CAMERA_PASS = "Tlh@2026"
CHANNEL_ID = 1
TIMEOUT = 2  # giây


def _set_ircut_filter(mode):
    """
    Đặt chế độ IR-cut filter (day/night).
    
    Args:
        mode: "day" hoặc "night"
    
    Returns:
        bool: True nếu thành công
    """
    url = f"http://{CAMERA_IP}/ISAPI/Image/channels/{CHANNEL_ID}/ircutFilter"
    
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<IrcutFilter xmlns="http://www.isapi.org/ver20/XMLSchema" version="2.0">
  <IrcutFilterType>{mode}</IrcutFilterType>
</IrcutFilter>
"""
    
    try:
        r = requests.put(
            url,
            data=xml.encode("utf-8"),
            headers={"Content-Type": "application/xml; charset=UTF-8"},
            auth=HTTPDigestAuth(CAMERA_USER, CAMERA_PASS),
            timeout=TIMEOUT,
        )
        return r.status_code == 200
    except Exception as e:
        print(f"[LIGHT] Lỗi khi đặt {mode}: {e}")
        return False


def _flash_worker():
    """
    Worker function để nháy đèn.
    Chạy trong thread riêng để không block.
    """
    try:
        # Tắt đèn (night mode)
        if _set_ircut_filter("night"):
            time.sleep(1)  # Giữ 300ms
            # Bật lại (day mode)
            _set_ircut_filter("day")
    except Exception as e:
        print(f"[LIGHT] Lỗi khi nháy đèn: {e}")


def flash_light():
    """
    Nháy đèn camera một lần.
    
    Hiệu ứng: day → night (300ms) → day
    Chạy trong thread riêng, không block code chính.
    """
    thread = threading.Thread(target=_flash_worker, daemon=True)
    thread.start()
