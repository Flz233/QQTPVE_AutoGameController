# QQTPVE_AutoGameController 
QQTPVE 抓蜗牛模式，前台、后台自动挂机脚本 (QQTPVE's snail catching mode, foreground and background automatic hang-up scripts)

此为游戏自动化控制脚本，提供前台和后台两种自动化控制方案，适用于需要重复执行特定鼠标点击和键盘操作的游戏场景。

## 脚本功能

- **前台脚本**：需要游戏窗口在前台激活状态
- **后台脚本**：游戏窗口需要在后台运行（最小化）
- 自动校准点击位置
- 可配置操作间隔和持续时间
- 管理员权限自动获取

## 安装依赖

```bash
pip install pyautogui pywin32

# 前台运行
python AutoGameController_Foreground.py
# 后台运行
python AutoGameController_Background.py
