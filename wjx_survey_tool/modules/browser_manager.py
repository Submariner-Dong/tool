# 浏览器管理器
import random
import time
import traceback
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from config.settings import settings

def get_chrome_version():
    """获取当前系统Chrome版本"""
    import subprocess
    import re
    
    try:
        # 在Windows系统中检测Chrome版本
        result = subprocess.run(['wmic', 'datafile', 'where', 'name="C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"', 'get', 'Version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)
            if version_match:
                return version_match.group(1)
    except:
        pass
    
    # 备用方法：尝试从注册表获取
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
        version, _ = winreg.QueryValueEx(key, "version")
        winreg.CloseKey(key)
        return version
    except:
        pass
    
    # 如果以上方法都失败，尝试从默认安装路径获取
    try:
        import os
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                result = subprocess.run(['wmic', 'datafile', 'where', f'name="{path}"', 'get', 'Version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    version_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)
                    if version_match:
                        return version_match.group(1)
    except:
        pass
    
    return "未知版本"

# 全局WebDriver服务，避免重复初始化
_global_service = None

def get_global_service():
    """获取全局WebDriver服务"""
    global _global_service
    if _global_service is None:
        # 优先检查根目录下的chromedriver.exe
        import os
        import shutil
        import zipfile
        
        # 检查根目录下是否有chromedriver.exe
        root_driver = "chromedriver.exe"
        if os.path.exists(root_driver):
            print("使用根目录下的chromedriver.exe")
            _global_service = Service(root_driver)
        else:
            # 如果根目录没有，检查.wdm目录中是否有缓存的driver
            # 查找.wdm目录中最新版本的chromedriver
            wdm_base_path = ".wdm/drivers/chromedriver/win64"
            if os.path.exists(wdm_base_path):
                # 获取所有版本目录
                versions = [d for d in os.listdir(wdm_base_path) if os.path.isdir(os.path.join(wdm_base_path, d))]
                if versions:
                    # 使用最新版本（按数字排序）
                    latest_version = sorted(versions, key=lambda x: [int(n) for n in x.split('.')])[-1]
                    version_path = os.path.join(wdm_base_path, latest_version)
                    
                    # 检查是否已经有解压的chromedriver.exe
                    wdm_path = os.path.join(version_path, "chromedriver.exe")
                    if os.path.exists(wdm_path):
                        print(f"使用.wdm目录下的chromedriver.exe (版本: {latest_version})")
                        _global_service = Service(wdm_path)
                    else:
                        # 检查是否有zip文件需要解压
                        zip_files = [f for f in os.listdir(version_path) if f.endswith('.zip')]
                        if zip_files:
                            zip_file = os.path.join(version_path, zip_files[0])
                            try:
                                # 解压zip文件
                                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                                    zip_ref.extractall(version_path)
                                print(f"已解压chromedriver.zip文件")
                                
                                # 再次检查解压后的文件
                                if os.path.exists(wdm_path):
                                    print(f"使用.wdm目录下的chromedriver.exe (版本: {latest_version})")
                                    _global_service = Service(wdm_path)
                                else:
                                    # 如果解压后仍找不到，尝试其他方式
                                    _global_service = _fallback_download()
                            except Exception as e:
                                print(f"解压chromedriver.zip失败: {e}")
                                _global_service = _fallback_download()
                        else:
                            # 如果找到目录但没有zip文件，继续检查其他目录
                            _global_service = _fallback_download()
                else:
                    _global_service = _fallback_download()
            else:
                _global_service = _fallback_download()
    
    return _global_service

def _fallback_download():
    """备用下载方案"""
    import os
    import shutil
    
    root_driver = "chromedriver.exe"
    
    # 如果都没有，下载到项目根目录
    print("未找到本地chromedriver，开始下载...")
    try:
        # 直接下载到项目根目录
        driver_path = ChromeDriverManager().install()
        
        # 无论下载到哪里，都复制到根目录
        if driver_path != root_driver:
            shutil.copy2(driver_path, root_driver)
            print(f"已将chromedriver复制到根目录: {root_driver}")
        
        return Service(root_driver)
            
    except Exception as e:
        print(f"下载chromedriver失败: {e}")
        
        # 尝试解压.wdm目录中的zip文件
        import os
        import zipfile
        
        # 检查.wdm目录中是否有zip文件需要解压
        wdm_base_path = ".wdm/drivers/chromedriver/win64"
        if os.path.exists(wdm_base_path):
            # 获取所有版本目录
            versions = [d for d in os.listdir(wdm_base_path) if os.path.isdir(os.path.join(wdm_base_path, d))]
            if versions:
                # 使用最新版本
                latest_version = sorted(versions, key=lambda x: [int(n) for n in x.split('.')])[-1]
                version_path = os.path.join(wdm_base_path, latest_version)
                
                # 检查是否有zip文件需要解压
                zip_files = [f for f in os.listdir(version_path) if f.endswith('.zip')]
                if zip_files:
                    zip_file = os.path.join(version_path, zip_files[0])
                    try:
                        # 解压zip文件
                        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                            zip_ref.extractall(version_path)
                        print(f"已解压chromedriver.zip文件")
                        
                        # 检查解压后的文件
                        wdm_path = os.path.join(version_path, "chromedriver.exe")
                        if os.path.exists(wdm_path):
                            print(f"使用.wdm目录下的chromedriver.exe (版本: {latest_version})")
                            return Service(wdm_path)
                    except Exception as zip_error:
                        print(f"解压chromedriver.zip失败: {zip_error}")
        
        # 如果网络下载失败，检查是否有其他可用的chromedriver
        if os.path.exists(root_driver):
            print("使用根目录下的chromedriver.exe")
            return Service(root_driver)
        else:
            # 最终尝试使用系统PATH中的chromedriver
            try:
                print("尝试使用系统PATH中的chromedriver")
                return Service("chromedriver")
            except:
                chrome_version = get_chrome_version()
                print(f"""无法找到可用的chromedriver，请手动下载并放置在程序根目录
手动下载步骤：
1. 访问 https://chromedriver.chromium.org/downloads
2. 下载与您Chrome版本匹配的chromedriver
3. 将下载的chromedriver.exe文件放在程序根目录
4. 重新运行程序
当前Chrome版本: {chrome_version}""")
                raise

def get_proxy_ip():
    """获取代理IP"""
    proxy_url = settings.get("proxy_url", "")
    if not proxy_url:
        return None
    
    try:
        response = requests.get(proxy_url, timeout=10)
        if response.status_code == 200:
            proxy_ip = response.text.strip()
            if proxy_ip and ":" in proxy_ip:
                return proxy_ip
    except Exception as e:
        print(f"获取代理IP失败: {str(e)}")
    
    return None

class BrowserManager:
    def __init__(self, position_x=0, position_y=0):
        self.position_x = position_x
        self.position_y = position_y
        self.driver = None
    
    def create_driver(self):
        """创建浏览器驱动"""
        try:
            # 浏览器选项设置
            option = Options()
            option.add_argument("--disable-blink-features=AutomationControlled")
            option.add_argument("--disable-infobars")
            option.add_argument("--disable-extensions")
            option.add_argument("--no-sandbox")
            option.add_argument("--disable-dev-shm-usage")
            
            if settings.get("headless_mode", True):
                option.add_argument("--headless=new")
            
            # 设置代理（如果启用）
            if settings.get("proxy_enabled", False):
                proxy_ip = get_proxy_ip()
                if proxy_ip:
                    option.add_argument(f"--proxy-server=http://{proxy_ip}")
                    print(f"使用代理IP: {proxy_ip}")
            
            # 设置随机User-Agent
            user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(90, 120)}.0.0.0 Safari/537.36"
            option.add_argument(f'user-agent={user_agent}')
            
            # 使用全局WebDriver服务，避免重复初始化
            service = get_global_service()
            self.driver = webdriver.Chrome(service=service, options=option)
            
            # 设置窗口大小和位置
            width = settings.get("browser_width", 550)
            height = settings.get("browser_height", 650)
            self.driver.set_window_size(width, height)
            self.driver.set_window_position(x=self.position_x, y=self.position_y)
            
            # 隐藏webdriver特征
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    window.navigator.chrome = {
                        app: {},
                        webstore: {},
                        runtime: {},
                    };
                '''
            })
            
            return self.driver
            
        except Exception as e:
            print(f"创建浏览器驱动失败: {str(e)}")
            # 这里不抛出异常，让调用方处理统计
            if self.driver:
                self.close_driver()
            raise
    
    def close_driver(self):
        """关闭浏览器驱动"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None