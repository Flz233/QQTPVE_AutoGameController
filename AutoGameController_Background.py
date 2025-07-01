import time
import ctypes
import sys
import win32api
import win32con
import win32gui
import pyautogui

# ===== 配置区 =====
WINDOW_TITLE = "QQTPVE"  # 修改为你的游戏窗口标题
LOOP_INTERVAL = 25      # 完整循环间隔(秒)
STARTUP_DELAY = 5       # 启动等待时间(秒)
KEY_HOLD_TIME = [0.75, 1.75, 1.5]  # 方向键持续时间(秒)
CLICK_DELAY = 3.5       # 点击后等待时间(秒)

# ===== 虚拟键码映射 =====
VK_CODE = {
    'up': win32con.VK_UP,
    'right': win32con.VK_RIGHT,
    'down': win32con.VK_DOWN,
    'left': win32con.VK_LEFT
}

# ===== Windows管理员权限检查 =====
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit()

# ===== 窗口操作函数 =====
def find_game_window(title):
    """查找游戏窗口句柄"""
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and title in win32gui.GetWindowText(hwnd):
            hwnds.append(hwnd)
        return True
    
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds[0] if hwnds else None

def get_client_relative_position(hwnd, screen_x, screen_y):
    """计算屏幕坐标对应的客户区相对坐标"""
    # 获取窗口客户区在屏幕上的位置
    client_left, client_top, _, _ = win32gui.GetClientRect(hwnd)
    client_left, client_top = win32gui.ClientToScreen(hwnd, (client_left, client_top))
    
    # 计算相对坐标
    rel_x = screen_x - client_left
    rel_y = screen_y - client_top
    
    return rel_x, rel_y

def calibrate_click_position():
    """校准点击位置"""
    print("请将鼠标移动到目标位置，5秒后获取坐标...")
    time.sleep(5)
    x, y = pyautogui.position()
    print(f"获取的屏幕坐标: X={x}, Y={y}")
    return x, y

def send_mouse_click(hwnd, rel_x, rel_y):
    """向指定窗口发送鼠标点击事件（使用相对坐标）"""
    # 创建lParam参数 (低位是X坐标，高位是Y坐标)
    lParam = win32api.MAKELONG(rel_x, rel_y)
    
    # 发送鼠标移动消息
    win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, lParam)
    time.sleep(0.05)
    
    # 发送鼠标按下消息
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    time.sleep(0.1)
    
    # 发送鼠标释放消息
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)
    time.sleep(0.05)

def send_key_press(hwnd, key, duration=1.0):
    """按住方向键指定时间"""
    if key not in VK_CODE:
        raise ValueError(f"无效方向键: {key}")
    
    print(f"  按下 {key} 方向键...")
    
    """向指定窗口发送按键事件"""
    vk_code = VK_CODE[key]
    
    # 发送按键按下
    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)
    time.sleep(duration)
    
    # 发送按键释放
    win32gui.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, 0)
    time.sleep(0.1)

# ===== 主操作函数 =====
def perform_actions(hwnd, rel_x, rel_y):
    """执行完整操作序列（后台模式）"""
    # 1. 发送鼠标点击
    print(f"[{time.strftime('%H:%M:%S')}] 后台点击 (相对坐标: {rel_x}, {rel_y})")
    send_mouse_click(hwnd, rel_x, rel_y)
    
    # 2. 等待点击响应
    time.sleep(CLICK_DELAY)

    # 3. 发送方向键组合
    send_key_press(hwnd, 'up', KEY_HOLD_TIME[0])
    send_key_press(hwnd, 'right', KEY_HOLD_TIME[1])
    send_key_press(hwnd, 'up', KEY_HOLD_TIME[2])

# ===== 主程序 =====
if __name__ == "__main__":
    # 查找游戏窗口
    game_hwnd = find_game_window(WINDOW_TITLE)
    if not game_hwnd:
        print(f"错误：找不到标题包含 '{WINDOW_TITLE}' 的窗口")
        sys.exit(1)
    
    # 获取窗口信息
    window_title = win32gui.GetWindowText(game_hwnd)
    print(f"找到游戏窗口：{window_title}")
    
    # 检查窗口状态
    if win32gui.IsIconic(game_hwnd):
        print("警告：窗口处于最小化状态，请恢复窗口后继续...")
        # 等待窗口恢复
        while win32gui.IsIconic(game_hwnd):
            time.sleep(1)
    
    # 获取窗口位置信息
    window_rect = win32gui.GetWindowRect(game_hwnd)
    print(f"窗口位置: {window_rect}")
    
    # 校准点击位置
    print("\n===== 点击位置校准 =====")
    screen_x, screen_y = calibrate_click_position()
    
    # 计算相对坐标
    rel_x, rel_y = get_client_relative_position(game_hwnd, screen_x, screen_y)
    print(f"计算得到的相对坐标: X={rel_x}, Y={rel_y}")
    
    # 验证坐标
    client_rect = win32gui.GetClientRect(game_hwnd)
    print(f"客户区大小: 宽度={client_rect[2]}, 高度={client_rect[3]}")
    
    if rel_x < 0 or rel_y < 0 or rel_x > client_rect[2] or rel_y > client_rect[3]:
        print("警告：相对坐标超出客户区范围，点击可能无效！")
    
    print(f"""\n=== 游戏控制脚本 ===
操作流程：
1. 鼠标点击 (相对坐标: {rel_x}, {rel_y})
2. 上方向键 {KEY_HOLD_TIME[0]}秒
3. 右方向键 {KEY_HOLD_TIME[1]}秒
4. 上方向键 {KEY_HOLD_TIME[2]}秒
循环间隔: {LOOP_INTERVAL}秒
========================
""")
    
    print(f"{STARTUP_DELAY}秒后开始执行...")
    time.sleep(STARTUP_DELAY)
    
    try:
        # 初始化：释放所有方向键
        for key in VK_CODE.values():
            win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        while True:
            print(f"\n----- 新一轮操作开始 -----")
            perform_actions(game_hwnd, rel_x, rel_y)
            
            # 循环等待
            print(f"\n下次操作将在 {LOOP_INTERVAL} 秒后...")
            for i in range(LOOP_INTERVAL, 0, -1):
                print(f"\r倒计时: {i:2d}秒", end="")
                time.sleep(1)
            print("\r" + " " * 20 + "\r", end="")
            
    except KeyboardInterrupt:
        print("\n脚本已安全停止")