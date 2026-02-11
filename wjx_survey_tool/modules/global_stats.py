# 全局统计管理器
import threading
import time

class GlobalStats:
    def __init__(self):
        self._success_count = 0
        self._fail_count = 0
        self._skip_count = 0
        self._stop = False
        self._lock = threading.Lock()
        self._start_time = time.time()
        self._last_success_time = time.time()
    
    def increment_success(self):
        with self._lock:
            self._success_count += 1
            self._last_success_time = time.time()
    
    def increment_fail(self):
        with self._lock:
            self._fail_count += 1
    
    def increment_skip(self):
        with self._lock:
            self._skip_count += 1
    
    def set_stop(self, value):
        with self._lock:
            self._stop = value
    
    def should_stop(self):
        with self._lock:
            return self._stop
    
    def get_elapsed_time(self):
        return time.time() - self._start_time
    
    def get_idle_time(self):
        """获取空闲时间（距离上次成功的时间）"""
        return time.time() - self._last_success_time
    
    def get_stats(self):
        with self._lock:
            return {
                'success_count': self._success_count,
                'fail_count': self._fail_count,
                'skip_count': self._skip_count,
                'stop': self._stop,
                'elapsed_time': self.get_elapsed_time(),
                'idle_time': self.get_idle_time()
            }
    
    @property
    def success_count(self):
        with self._lock:
            return self._success_count
    
    @property
    def fail_count(self):
        with self._lock:
            return self._fail_count
    
    @property
    def skip_count(self):
        with self._lock:
            return self._skip_count