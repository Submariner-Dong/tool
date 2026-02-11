# 主窗口界面
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time

from config.settings import settings
from config.question_config import question_config
from modules.survey_manager import SurveyManager

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("问卷星自动填写工具")
        self.root.geometry("800x800")
        
        # 初始化管理器
        self.survey_manager = None
        self.update_thread = None
        self.running = False
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """设置UI界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # IP代理链接设置
        ttk.Label(main_frame, text="IP代理链接:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.proxy_entry = ttk.Entry(main_frame, width=60)
        self.proxy_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 代理链接说明
        proxy_info = ttk.Label(main_frame, text="获取代理ip，使用品赞ip服务: https://www.ipzan.com?pid=ggj6roo98\n注册并实名认证，将公网ip添加到白名单，选择地区，时长1分钟，数据格式txt，提取数量1\n如果不需要ip可不设置，不影响程序直接运行", 
                              foreground="gray", font=("Arial", 8))
        proxy_info.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # 问卷链接设置
        ttk.Label(main_frame, text="问卷链接:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(main_frame, width=60)
        self.url_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 设置框架
        settings_frame = ttk.LabelFrame(main_frame, text="设置", padding="5")
        settings_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        settings_frame.columnconfigure(1, weight=1)
        
        # 最大填写份数
        ttk.Label(settings_frame, text="最大填写份数:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.max_count_var = tk.StringVar(value=str(settings.get("max_count", 20)))
        ttk.Entry(settings_frame, textvariable=self.max_count_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # 窗口数量
        ttk.Label(settings_frame, text="浏览器窗口数量:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.window_count_var = tk.StringVar(value=str(settings.get("window_count", 2)))
        ttk.Entry(settings_frame, textvariable=self.window_count_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # 失败阈值
        ttk.Label(settings_frame, text="失败阈值:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.fail_threshold_var = tk.StringVar(value=str(settings.get("fail_threshold", 10)))
        ttk.Entry(settings_frame, textvariable=self.fail_threshold_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # 跳过阈值
        ttk.Label(settings_frame, text="跳过阈值:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.skip_threshold_var = tk.StringVar(value=str(settings.get("skip_threshold", 10)))
        ttk.Entry(settings_frame, textvariable=self.skip_threshold_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # 无头模式
        self.headless_var = tk.BooleanVar(value=settings.get("headless_mode", True))
        ttk.Checkbutton(settings_frame, text="无头模式", variable=self.headless_var).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # 概率设置按钮
        ttk.Button(main_frame, text="设置题目概率", command=self.open_probability_editor).grid(row=4, column=0, columnspan=2, pady=10)
        
        # 控制按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="开始", command=self.start_survey)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_survey, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 状态显示
        status_frame = ttk.LabelFrame(main_frame, text="状态信息", padding="5")
        status_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
        # 统计信息
        self.stats_text = scrolledtext.ScrolledText(status_frame, height=18, width=80)
        self.stats_text.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.stats_text.config(state=tk.DISABLED)
        
        # 日志输出
        log_frame = ttk.LabelFrame(main_frame, text="日志", padding="5")
        log_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置主框架的行权重
        main_frame.rowconfigure(6, weight=1)
        main_frame.rowconfigure(7, weight=1)
    
    def load_settings(self):
        """加载设置"""
        # 加载代理链接
        self.proxy_entry.delete(0, tk.END)
        self.proxy_entry.insert(0, settings.get("proxy_url", ""))
        
        # 加载问卷链接
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, question_config.get_url())
    
    def save_settings(self):
        """保存设置"""
        try:
            # 保存代理链接
            proxy_url = self.proxy_entry.get().strip()
            if proxy_url:
                settings.set("proxy_url", proxy_url)
                settings.set("proxy_enabled", True)
            else:
                settings.set("proxy_url", "")
                settings.set("proxy_enabled", False)
            
            # 保存问卷链接
            question_config.set_url(self.url_entry.get().strip())
            
            # 保存其他设置
            settings.set("max_count", int(self.max_count_var.get()))
            settings.set("window_count", int(self.window_count_var.get()))
            settings.set("fail_threshold", int(self.fail_threshold_var.get()))
            settings.set("skip_threshold", int(self.skip_threshold_var.get()))
            settings.set("headless_mode", self.headless_var.get())
            
            return True
        except ValueError as e:
            messagebox.showerror("错误", "请输入有效的数字设置")
            return False
    
    def open_probability_editor(self):
        """打开概率编辑器"""
        from ui.probability_editor import ProbabilityEditor
        ProbabilityEditor(self.root, question_config)
    
    def start_survey(self):
        """开始问卷填写"""
        if not self.save_settings():
            return
        
        if not question_config.get_url():
            messagebox.showerror("错误", "请输入有效的问卷链接")
            return
        
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        
        # 启动问卷管理器
        self.survey_manager = SurveyManager(question_config)
        
        # 启动工作线程
        def run_survey():
            try:
                self.survey_manager.start()
            except Exception as e:
                self.log(f"错误: {str(e)}")
            finally:
                self.running = False
                self.root.after(0, self.on_survey_stopped)
        
        survey_thread = threading.Thread(target=run_survey, daemon=True)
        survey_thread.start()
        
        # 启动状态更新线程
        self.update_thread = threading.Thread(target=self.update_status, daemon=True)
        self.update_thread.start()
    
    def stop_survey(self):
        """停止问卷填写"""
        if self.survey_manager:
            self.survey_manager.stop()
        self.running = False
    
    def on_survey_stopped(self):
        """问卷停止时的回调"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log("问卷填写已停止")
    
    def update_status(self):
        """更新状态信息"""
        while self.running:
            if self.survey_manager:
                stats = self.survey_manager.get_stats()
                self.update_stats_display(stats)
                
                # 实时记录失败次数到日志，用于调试
                if stats['fail_count'] > 0:
                    self.log(f"当前失败计数: {stats['fail_count']}")
            time.sleep(0.5)  # 提高更新频率到0.5秒
    
    def update_stats_display(self, stats):
        """更新统计信息显示"""
        stats_text = f"成功填写: {stats['success_count']} 份\n"
        stats_text += f"失败次数: {stats['fail_count']} 次\n"
        stats_text += f"跳过次数: {stats['skip_count']} 次\n"
        stats_text += f"运行时间: {stats['elapsed_time']:.1f} 秒\n"
        stats_text += f"空闲时间: {stats['idle_time']:.1f} 秒\n"
        stats_text += f"状态: {'运行中' if not stats['stop'] else '已停止'}"
        
        self.root.after(0, lambda: self._update_stats_text(stats_text))
    
    def _update_stats_text(self, text):
        """线程安全地更新统计文本"""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, text)
        self.stats_text.config(state=tk.DISABLED)
    
    def log(self, message):
        """添加日志消息"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        def update_log():
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)
        
        self.root.after(0, update_log)
    
    def run(self):
        """运行应用程序"""
        # 设置窗口关闭事件
        def on_closing():
            if self.running:
                if messagebox.askokcancel("退出", "问卷填写正在运行，确定要退出吗？"):
                    self.stop_survey()
                    self.root.destroy()
            else:
                self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        self.root.mainloop()