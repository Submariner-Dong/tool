# 问卷管理器
import threading
import time
import logging
from threading import Thread

from modules.survey_worker import SurveyWorker
from modules.global_stats import GlobalStats
from config.settings import settings

class SurveyManager:
    def __init__(self, config_manager):
        self.config = config_manager
        self.global_stats = GlobalStats()
        self.workers = []
        self.threads = []
        self.running = False
        
    def start(self):
        """开始问卷填写"""
        if self.running:
            logging.warning("问卷填写已经在运行中")
            return
        
        self.running = True
        self.global_stats = GlobalStats()
        
        # 创建工作者
        window_count = settings.get("window_count", 2)
        self.workers = []
        self.threads = []
        
        # 设置窗口位置
        positions = [
            (50, 50),    # 窗口1位置
            (650, 50),   # 窗口2位置
            (650, 280),  # 窗口3位置
            (50, 280),   # 窗口4位置
        ]
        
        for i in range(min(window_count, 4)):
            worker = SurveyWorker(self.config, positions[i][0], positions[i][1])
            self.workers.append(worker)
            
            # 创建工作线程
            thread = Thread(target=self.worker_loop, args=(worker,), daemon=True)
            self.threads.append(thread)
            thread.start()
        
        logging.info(f"启动 {len(self.workers)} 个工作线程")
        
        # 等待所有线程完成或停止
        max_idle_time = 60  # 最大空闲时间60秒
        while any(thread.is_alive() for thread in self.threads) and not self.global_stats.should_stop():
            time.sleep(1)
            
            # 检查是否长时间没有成功提交
            stats = self.global_stats.get_stats()
            if stats['idle_time'] > max_idle_time and stats['success_count'] > 0:
                logging.warning(f"检测到{max_idle_time}秒内没有成功提交，自动停止")
                self.stop()
                break
            
            # 检查失败次数是否超过阈值
            if stats['fail_count'] >= settings.get("fail_threshold", 10):
                logging.critical(f'失败次数过多({stats["fail_count"]}次)，程序将强制停止，请检查代码是否正确')
                self.stop()
                break
        
        self.running = False
        logging.info("问卷填写任务完成")
    
    def worker_loop(self, worker):
        """工作者循环"""
        while not self.global_stats.should_stop() and self.running:
            # 检查是否达到最大填写数量
            if self.global_stats.success_count >= settings.get("max_count", 20):
                self.global_stats.set_stop(True)
                break
            
            # 处理单个问卷
            success = worker.process_survey(self.global_stats)
            
            # 如果处理失败，等待一段时间再重试
            if not success:
                time.sleep(2)
            else:
                # 成功提交后短暂休息
                time.sleep(1)
    
    def stop(self):
        """停止问卷填写"""
        self.running = False
        self.global_stats.set_stop(True)
        logging.info("正在停止问卷填写...")
    
    def get_stats(self):
        """获取统计信息"""
        return self.global_stats.get_stats()
    
    def is_running(self):
        """检查是否在运行中"""
        return self.running