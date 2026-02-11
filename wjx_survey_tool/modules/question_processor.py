# 题目处理器
import random
import numpy
import time
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

class QuestionProcessor:
    def __init__(self, config_manager):
        self.config = config_manager
        self.single_prob = self._normalize_probabilities(list(self.config.get_question_config("single_prob").values()))
        self.droplist_prob = self._normalize_probabilities(list(self.config.get_question_config("droplist_prob").values()))
        self.multiple_prob = list(self.config.get_question_config("multiple_prob").values())
        self.multiple_opts = list(self.config.get_question_config("multiple_opts").values())
        self.matrix_prob = list(self.config.get_question_config("matrix_prob").values())
        self.scale_prob = self._normalize_probabilities(list(self.config.get_question_config("scale_prob").values()))
        self.texts_prob = self._normalize_probabilities(list(self.config.get_question_config("texts_prob").values()))
        self.texts = list(self.config.get_question_config("texts").values())
    
    def _normalize_probabilities(self, prob_list):
        """归一化概率参数"""
        normalized = []
        for prob in prob_list:
            if isinstance(prob, list) and prob != -1:
                prob_sum = sum(prob)
                normalized.append([x / prob_sum for x in prob])
            else:
                normalized.append(prob)
        return normalized
    
    def detect_questions(self, driver):
        """检测页数和每一页的题量"""
        q_list = []
        xpath = '//*[@id="divQuestion"]/fieldset'
        page_num = len(driver.find_elements(By.XPATH, xpath))
        
        for i in range(1, page_num + 1):
            qs = driver.find_elements(By.XPATH, f'//*[@id="fieldset{i}"]/div')
            invalid_item = 0
            for qs_item in qs:
                if qs_item.get_attribute("topic").isdigit() is False:
                    invalid_item += 1
            q_list.append(len(qs) - invalid_item)
        
        return q_list
    
    def process_vacant(self, driver, current, index):
        """处理填空题"""
        content = self.texts[index]
        p = self.texts_prob[index]
        text_index = numpy.random.choice(a=numpy.arange(0, len(p)), p=p)
        driver.find_element(By.CSS_SELECTOR, f'#q{current}').send_keys(content[text_index])
    
    def process_single(self, driver, current, index):
        """处理单选题"""
        xpath = f'//*[@id="div{current}"]/div[2]/div'
        options = driver.find_elements(By.XPATH, xpath)
        p = self.single_prob[index]
        
        # 参数校验
        if isinstance(p, list):
            actual_options = len(options)
            if len(p) != actual_options:
                print(f"⚠️ 第{current}题参数错误：配置了{len(p)}个概率，实际有{actual_options}个选项")
                print("⚠️ 自动修正为均匀分布概率")
                p = [1/actual_options] * actual_options
        
        if p == -1:
            r = random.randint(1, len(options))
        else:
            r = numpy.random.choice(a=numpy.arange(1, len(options) + 1), p=p)
        
        driver.find_element(By.CSS_SELECTOR, f'#div{current} > div.ui-controlgroup > div:nth-child({r})').click()
    
    def process_droplist(self, driver, current, index):
        """处理下拉框题"""
        driver.find_element(By.CSS_SELECTOR, f"#select2-q{current}-container").click()
        time.sleep(0.5)
        options = driver.find_elements(By.XPATH, f"//*[@id='select2-q{current}-results']/li")
        p = self.droplist_prob[index]
        r = numpy.random.choice(a=numpy.arange(1, len(options)), p=p)
        driver.find_element(By.XPATH, f"//*[@id='select2-q{current}-results']/li[{r + 1}]").click()
    
    def process_multiple(self, driver, current, index):
        """处理多选题"""
        xpath = f'//*[@id="div{current}"]/div[2]/div'
        options = driver.find_elements(By.XPATH, xpath)
        probabilities = self.multiple_prob[index]
        
        if probabilities == 0:
            return
        elif probabilities == -1:
            r = random.randint(1, len(options))
            driver.find_element(By.CSS_SELECTOR, f'#div{current} > div.ui-controlgroup > div:nth-child({r})').click()
        else:
            prob_copy = probabilities.copy()
            opts_num = self.multiple_opts[index]
            
            # 处理必选项
            for i, prob in enumerate(prob_copy):
                if prob == 100:
                    driver.find_element(By.CSS_SELECTOR, f'#div{current} > div.ui-controlgroup > div:nth-child({i + 1})').click()
                    prob_copy[i] = 0
            
            # 处理其他选项
            total = sum([num for num in prob_copy])
            if total == 0:
                return
            
            probabilities_norm = [num / total if num != 0 else 0 for num in prob_copy]
            selection_indices = numpy.random.choice(
                range(len(options)),
                size=opts_num,
                replace=False,
                p=probabilities_norm
            )
            
            for i in selection_indices:
                driver.find_element(By.CSS_SELECTOR, f'#div{current} > div.ui-controlgroup > div:nth-child({i + 1})').click()
    
    def process_matrix(self, driver, current, index):
        """处理矩阵题"""
        xpath1 = f'//*[@id="divRefTab{current}"]/tbody/tr'
        rows = driver.find_elements(By.XPATH, xpath1)
        q_num = sum(1 for tr in rows if tr.get_attribute("rowindex") is not None)
        
        xpath2 = f'//*[@id="drv{current}_1"]/td'
        cols = driver.find_elements(By.XPATH, xpath2)
        
        for i in range(1, q_num + 1):
            p = self.matrix_prob[index]
            index += 1
            
            if p == -1:
                opt = random.randint(2, len(cols))
            else:
                opt = numpy.random.choice(a=numpy.arange(2, len(cols) + 1), p=p)
            
            driver.find_element(By.CSS_SELECTOR, f'#drv{current}_{i} > td:nth-child({opt})').click()
        
        return index
    
    def process_scale(self, driver, current, index):
        """处理量表题"""
        xpath = f'//*[@id="div{current}"]/div[2]/div/ul/li'
        options = driver.find_elements(By.XPATH, xpath)
        p = self.scale_prob[index]
        
        if p == -1:
            b = random.randint(1, len(options))
        else:
            b = numpy.random.choice(a=numpy.arange(1, len(options) + 1), p=p)
        
        driver.find_element(By.CSS_SELECTOR, f'#div{current} > div.scale-div > div > ul > li:nth-child({b})').click()
    
    def process_reorder(self, driver, current):
        """处理排序题"""
        xpath = f'//*[@id="div{current}"]/ul/li'
        items = driver.find_elements(By.XPATH, xpath)
        
        for j in range(1, len(items) + 1):
            b = random.randint(j, len(items))
            driver.find_element(By.CSS_SELECTOR, f'#div{current} > ul > li:nth-child({b})').click()
            time.sleep(0.4)
    
    def submit_survey(self, driver):
        """提交问卷"""
        time.sleep(1)
        
        # 确认对话框
        try:
            driver.find_element(By.XPATH, '//*[@id="layui-layer1"]/div[3]/a').click()
            time.sleep(1)
        except:
            pass
        
        # 智能检测
        try:
            driver.find_element(By.XPATH, '//*[@id="SM_BTN_1"]').click()
            time.sleep(3)
        except:
            pass
        
        # 滑块验证
        try:
            slider = driver.find_element(By.XPATH, '//*[@id="nc_1__scale_text"]/span')
            if str(slider.text).startswith("请按住滑块"):
                width = slider.size.get('width')
                ActionChains(driver).drag_and_drop_by_offset(slider, width, 0).perform()
        except:
            pass