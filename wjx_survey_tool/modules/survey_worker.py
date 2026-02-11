# 问卷填写工作器
import time
import traceback
import logging
import random
from selenium.webdriver.common.by import By

from modules.browser_manager import BrowserManager
from modules.question_processor import QuestionProcessor
from config.settings import settings

class SurveyWorker:
    def __init__(self, config_manager, position_x=0, position_y=0):
        self.config = config_manager
        self.browser_manager = BrowserManager(position_x, position_y)
        self.question_processor = QuestionProcessor(config_manager)
        self.worker_id = f"Worker_{position_x}_{position_y}"
    
    def process_survey(self, global_stats):
        """处理单个问卷"""
        driver = None
        try:
            # 创建浏览器驱动
            driver = self.browser_manager.create_driver()
            
            # 获取问卷链接
            url = self.config.get_url()
            if not url:
                logging.error("问卷链接未设置")
                return False
            
            # 打开问卷
            driver.get(url)
            original_url = driver.current_url
            
            # 检测题目
            try:
                q_list = self.question_processor.detect_questions(driver)
            except Exception as e:
                logging.warning(f"{self.worker_id}: 页面加载失败，跳过当前问卷")
                global_stats.increment_skip()
                if global_stats.skip_count >= settings.get("skip_threshold", 10):
                    logging.critical('跳过次数过多，程序将强制停止，请检查代码是否正确')
                    global_stats.set_stop(True)
                return False
            
            # 初始化题目计数器
            single_num = 0
            vacant_num = 0
            droplist_num = 0
            multiple_num = 0
            matrix_num = 0
            scale_num = 0
            current = 0
            
            # 遍历每一页
            for j in q_list:
                for k in range(1, j + 1):
                    current += 1
                    
                    # 判断题型
                    try:
                        q_type = driver.find_element(By.CSS_SELECTOR, f'#div{current}').get_attribute("type")
                    except:
                        logging.warning(f"{self.worker_id}: 第{current}题加载失败，跳过当前问卷")
                        global_stats.increment_skip()
                        if global_stats.skip_count >= settings.get("skip_threshold", 10):
                            logging.critical('跳过次数过多，程序将强制停止，请检查代码是否正确')
                            global_stats.set_stop(True)
                        return False
                    
                    # 根据题型处理题目
                    if q_type == "1" or q_type == "2":  # 填空题
                        self.question_processor.process_vacant(driver, current, vacant_num)
                        vacant_num += 1
                    elif q_type == "3":  # 单选
                        self.question_processor.process_single(driver, current, single_num)
                        single_num += 1
                    elif q_type == "4":  # 多选
                        self.question_processor.process_multiple(driver, current, multiple_num)
                        multiple_num += 1
                    elif q_type == "5":  # 量表题
                        self.question_processor.process_scale(driver, current, scale_num)
                        scale_num += 1
                    elif q_type == "6":  # 矩阵题
                        matrix_num = self.question_processor.process_matrix(driver, current, matrix_num)
                    elif q_type == "7":  # 下拉框
                        self.question_processor.process_droplist(driver, current, droplist_num)
                        droplist_num += 1
                    elif q_type == "8":  # 滑块题
                        score = random.randint(1, 100)
                        driver.find_element(By.CSS_SELECTOR, f'#q{current}').send_keys(score)
                    elif q_type == "11":  # 排序题
                        self.question_processor.process_reorder(driver, current)
                    else:
                        logging.warning(f"{self.worker_id}: 第{k}题为不支持题型！")
                
                time.sleep(0.5)
                
                # 翻页或提交
                try:
                    driver.find_element(By.CSS_SELECTOR, '#divNext').click()
                    time.sleep(0.5)
                except:
                    try:
                        driver.find_element(By.XPATH, '//*[@id="ctlNext"]').click()
                    except:
                        logging.warning(f"{self.worker_id}: 提交按钮加载失败，跳过当前问卷")
                        global_stats.increment_skip()
                        if global_stats.skip_count >= settings.get("skip_threshold", 10):
                            logging.critical('跳过次数过多，程序将强制停止，请检查代码是否正确')
                            global_stats.set_stop(True)
                        return False
            
            # 提交问卷
            self.question_processor.submit_survey(driver)
            
            # 等待页面跳转
            time.sleep(4)
            new_url = driver.current_url
            
            # 检查是否提交成功
            if original_url != new_url:
                global_stats.increment_success()
                logging.info(f"{self.worker_id}: 已填写{global_stats.success_count}份 - 失败{global_stats.fail_count}次 - 跳过{global_stats.skip_count}次")
                
                # 检查是否达到上限
                if global_stats.success_count >= settings.get("max_count", 20):
                    global_stats.set_stop(True)
                
                return True
            else:
                return False
                
        except Exception as e:
            logging.error(f"{self.worker_id}: 问卷处理失败 - {str(e)}")
            traceback.print_exc()
            global_stats.increment_fail()
            print(f"当前失败次数: {global_stats.fail_count}")
            
            return False
            
        finally:
            if driver:
                self.browser_manager.close_driver()