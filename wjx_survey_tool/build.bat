@echo off
echo 开始构建问卷星自动填写工具...
echo.

REM 切换到当前脚本所在目录
cd /d "%~dp0"

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 安装依赖包
echo 安装依赖包...
pip install -r requirements.txt

REM 使用PyInstaller打包
echo.
echo 开始打包程序...
pyinstaller build.spec --noconfirm

if errorlevel 1 (
    echo.
    echo 打包失败！
    pause
    exit /b 1
)

echo.
echo 打包完成！
echo 可执行文件位于 dist 目录下
echo.
pause