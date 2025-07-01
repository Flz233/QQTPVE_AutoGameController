import pyautogui
import time
import ctypes
import sys
import win32api
import win32con

# ===== 配置区 =====
LOOP_INTERVAL = 25      # 完整循环间隔(秒)
STARTUP_DELAY = 5       # 启动等待时间(秒)
KEY_HOLD_TIME = [0.75, 1.75, 1.5]  # 方向键持续时间(秒)
CLICK_DELAY = 3.5       # 点击后等待时间(秒)

# ===== 防检测设置 =====
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.3

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

# ===== 新增功能：点击位置校准 =====
def calibrate_click_position():
    """获取用户指定的点击位置"""
    print("请将鼠标移动到目标位置，5秒后获取坐标...")
    time.sleep(5)
    x, y = pyautogui.position()
    print(f"已获取点击位置: X={x}, Y={y}")
    return x, y

# ===== 精准点击函数 =====
def precise_click(x, y, click_delay=0.1):
    """更可靠的点击函数"""
    # 记录原始鼠标位置
    original_pos = pyautogui.position()
    
    # 分段移动鼠标（模拟人手）
    pyautogui.moveTo(x-50, y, duration=0.2)
    time.sleep(0.05)
    pyautogui.moveTo(x, y, duration=0.1)
    
    # 执行点击（按下+释放分开）
    pyautogui.mouseDown()
    time.sleep(click_delay)
    pyautogui.mouseUp()
    
    # 返回原位置（可选）
    pyautogui.moveTo(original_pos, duration=0.1)

# ===== 增强型方向键控制 =====
def press_direction(key, duration=1.75):
    """按住方向键指定时间"""
    if key not in VK_CODE:
        raise ValueError(f"无效方向键: {key}")
    
    print(f"  按下 {key} 方向键...")
    win32api.keybd_event(VK_CODE[key], 0, 0, 0)
    time.sleep(duration)
    win32api.keybd_event(VK_CODE[key], 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.2)

# ===== 主操作函数 =====
def perform_actions(click_x, click_y):
    """执行完整操作序列"""
    # 1. 精准点击
    print(f"[{time.strftime('%H:%M:%S')}] 正在点击 ({click_x}, {click_y})")
    precise_click(click_x, click_y)
    
    # 2. 等待点击响应
    time.sleep(CLICK_DELAY)

    # 3. 方向键组合
    press_direction('up', duration=KEY_HOLD_TIME[0])
    press_direction('right', duration=KEY_HOLD_TIME[1])
    press_direction('up', duration=KEY_HOLD_TIME[2])

# ===== 主循环 =====
if __name__ == "__main__":
    # 获取点击位置
    print("=== 点击位置校准 ===")
    CLICK_X, CLICK_Y = calibrate_click_position()
    
    print(f"""\n=== 游戏控制脚本 ===
操作流程：
1. 鼠标点击 ({CLICK_X}, {CLICK_Y})
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
            perform_actions(CLICK_X, CLICK_Y)
            
            # 循环等待
            print(f"\n下次操作将在 {LOOP_INTERVAL} 秒后...")
            for i in range(LOOP_INTERVAL, 0, -1):
                print(f"\r倒计时: {i:2d}秒", end="")
                time.sleep(1)
            print("\r" + " " * 20 + "\r", end="")
            
    except KeyboardInterrupt:
        print("\n脚本已安全停止")