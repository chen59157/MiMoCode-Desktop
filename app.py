"""
MiMo Code Desktop - AI 编程助手桌面客户端
基于 pywebview (Edge WebView2) 封装 Web UI 为原生桌面应用
"""

import os
import sys
import json
import time
import socket
import signal
import shutil
import subprocess
import threading
import tempfile
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

import webview

# ── 配置 ──────────────────────────────────────────────
APP_TITLE = "MiMo Code"
APP_WIDTH = 1400
APP_HEIGHT = 900
APP_MIN_WIDTH = 900
APP_MIN_HEIGHT = 600
API_PORT = 3456
API_HOST = "127.0.0.1"

# ── 路径解析 ───────────────────────────────────────────
def get_base_dir():
    """获取应用根目录（支持 PyInstaller 打包后运行）"""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent

BASE_DIR = get_base_dir()
PROJECT_ROOT = BASE_DIR  # app.py 在项目根目录

# ── 全局状态 ───────────────────────────────────────────
mimo_process = None
api_ready = False


def find_mimo_exe():
    """查找 mimo.exe 的位置"""
    candidates = [
        PROJECT_ROOT / "bin" / "mimo.exe",
        PROJECT_ROOT / "mimo.exe",
    ]
    for p in candidates:
        if p.exists():
            return p.resolve()
    mimo_in_path = shutil.which("mimo")
    if mimo_in_path:
        return Path(mimo_in_path)
    return None


def find_web_ui():
    """查找 index.html 的位置"""
    candidates = [
        PROJECT_ROOT / "index.html",
    ]
    for p in candidates:
        if p.exists():
            return p.resolve()
    return None


def is_port_in_use(port, host="127.0.0.1"):
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(1)
            s.connect((host, port))
            return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            return False


def wait_for_api(port, host="127.0.0.1", timeout=30):
    """等待 API 服务就绪"""
    global api_ready
    start = time.time()
    while time.time() - start < timeout:
        if is_port_in_use(port, host):
            api_ready = True
            return True
        time.sleep(0.5)
    return False


def start_mimo_server(cwd=None):
    """启动 mimo.exe 作为 API 服务"""
    global mimo_process

    # 如果端口已被占用，说明服务已在运行
    if is_port_in_use(API_PORT):
        print(f"[MiMo Desktop] API 已在端口 {API_PORT} 运行")
        api_ready = True
        return True

    mimo_path = find_mimo_exe()
    if not mimo_path:
        print("[MiMo Desktop] 错误: 找不到 mimo.exe")
        print(f"  搜索路径: {PROJECT_ROOT / 'bin' / 'mimo.exe'}")
        return False

    work_dir = cwd or str(PROJECT_ROOT)
    print(f"[MiMo Desktop] 启动 mimo serve: {mimo_path}")
    print(f"[MiMo Desktop] 工作目录: {work_dir}")
    print(f"[MiMo Desktop] API 地址: http://{API_HOST}:{API_PORT}")

    try:
        mimo_process = subprocess.Popen(
            [str(mimo_path), "serve", "--port", str(API_PORT), "--hostname", API_HOST],
            cwd=work_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0,
        )
        print(f"[MiMo Desktop] mimo.exe PID: {mimo_process.pid}")

        # 等待 API 就绪
        if wait_for_api(API_PORT, API_HOST):
            print("[MiMo Desktop] API 就绪 ✓")
            return True
        else:
            print("[MiMo Desktop] 错误: API 启动超时")
            stop_mimo_server()
            return False
    except Exception as e:
        print(f"[MiMo Desktop] 启动失败: {e}")
        return False


def stop_mimo_server():
    """停止 mimo.exe 进程"""
    global mimo_process
    if mimo_process:
        print(f"[MiMo Desktop] 停止 mimo.exe (PID: {mimo_process.pid})")
        try:
            if sys.platform == 'win32':
                mimo_process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                mimo_process.terminate()
            mimo_process.wait(timeout=5)
        except Exception:
            try:
                mimo_process.kill()
            except Exception:
                pass
        mimo_process = None
        print("[MiMo Desktop] mimo.exe 已停止")


# ── 本地 Web UI 服务器 ──────────────────────────────────
class QuietHandler(SimpleHTTPRequestHandler):
    """静默 HTTP 请求处理器（不输出日志到控制台）"""
    def log_message(self, format, *args):
        pass  # 静默

def find_free_port():
    """查找一个可用端口"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

def start_web_server(web_root, port):
    """启动本地 HTTP 服务器来托管 Web UI"""
    handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(web_root), **kwargs)
    server = HTTPServer(('127.0.0.1', port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"[MiMo Desktop] Web UI 服务器: http://127.0.0.1:{port}")
    return server


class MiMoAPI:
    """暴露给 pywebview JS 调用的 Python API"""

    def get_server_info(self):
        return json.dumps({
            "host": API_HOST,
            "port": API_PORT,
            "ready": api_ready,
            "mimo_pid": mimo_process.pid if mimo_process else None,
        })

    def open_dev_tools(self):
        """打开开发者工具（调试用）"""
        return True

    def get_version(self):
        return "0.1.0"

    def get_platform(self):
        return sys.platform


def on_closing():
    """窗口关闭时的清理"""
    print("[MiMo Desktop] 正在关闭...")
    stop_mimo_server()
    print("[MiMo Desktop] 已退出")


def main():
    print("=" * 50)
    print(f"  {APP_TITLE} Desktop v0.1.0")
    print(f"  开源 AI 编程智能体 · 跨会话记忆")
    print("=" * 50)

    # 1. 启动 mimo API 服务
    if not start_mimo_server():
        print("[MiMo Desktop] 无法启动 mimo 服务，尝试直接加载 Web UI...")

    # 2. 启动本地 Web UI 服务器（解决 file:// 跨域问题）
    web_ui_path = find_web_ui()
    if web_ui_path:
        web_root = web_ui_path.parent
        ui_port = find_free_port()
        web_server = start_web_server(web_root, ui_port)
        web_ui_url = f"http://127.0.0.1:{ui_port}/index.html"
        print(f"[MiMo Desktop] 加载 Web UI: {web_ui_url}")
    else:
        web_server = None
        web_ui_url = f"http://{API_HOST}:{API_PORT}"
        print(f"[MiMo Desktop] 使用内置 Web UI: {web_ui_url}")

    # 3. 创建桌面窗口
    api = MiMoAPI()

    window = webview.create_window(
        title=APP_TITLE,
        url=web_ui_url,
        js_api=api,
        width=APP_WIDTH,
        height=APP_HEIGHT,
        min_size=(APP_MIN_WIDTH, APP_MIN_HEIGHT),
        confirm_close=True,
        background_color='#0A0A0A',
        text_select=True,
    )

    # 4. 设置窗口图标（Windows API）
    def set_window_icon():
        """延迟设置窗口图标"""
        time.sleep(1)
        if sys.platform == 'win32':
            try:
                import ctypes
                icon_path = BASE_DIR / "icon.ico"
                if icon_path.exists():
                    hwnd = ctypes.windll.user32.GetForegroundWindow()
                    if hwnd:
                        WM_SETICON = 0x0080
                        IMAGE_ICON = 1
                        LR_LOADFROMFILE = 0x0010
                        hicon = ctypes.windll.user32.LoadImageW(
                            0, str(icon_path), IMAGE_ICON, 0, 0, LR_LOADFROMFILE
                        )
                        if hicon:
                            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 0, hicon)
                            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 1, hicon)
            except Exception:
                pass

    icon_thread = threading.Thread(target=set_window_icon, daemon=True)
    icon_thread.start()

    # 5. 注册关闭回调
    def cleanup():
        if web_server:
            web_server.shutdown()
        on_closing()

    window.events.closing += lambda: cleanup()

    # 5. 启动 GUI 事件循环
    print(f"[MiMo Desktop] 打开窗口...")
    webview.start(debug=False, gui='edgechromium')


if __name__ == '__main__':
    main()
