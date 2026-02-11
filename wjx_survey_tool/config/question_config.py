# 问卷配置管理
import json
import os
from typing import Dict, List, Any

class QuestionConfig:
    def __init__(self):
        self.config_file = "question_config.json"
        self.default_config = {
            "url": "https://v.wjx.cn/vm/ripGV4A.aspx",
            "single_prob": {
                "1": [40, 40, 10, 10], 
                "2": [45, 50, 5], 
                "3": [15, 35, 30, 15, 5], 
                "4": [20, 50, 20, 10], 
                "5": [40, 45, 15], 
                "22": [30, 60, 10], 
                "23": [40, 50, 10], 
                "24": [45, 45, 10], 
                "25": [35, 55, 10], 
                "26": [40, 50, 10], 
                "27": [40, 50, 10]
            },
            "droplist_prob": {"1": [1, 1, 1]},
            "multiple_prob": {"5": [40, 35, 50]},
            "multiple_opts": {"7": 1},
            "matrix_prob": {
                "1": [1, 0, 0, 0, 0], "2": -1, "3": [1, 0, 0, 0, 0], 
                "4": [1, 0, 0, 0, 0], "5": [1, 0, 0, 0, 0], "6": [1, 0, 0, 0, 0]
            },
            "scale_prob": {
                "6": [20, 30, 30, 15, 5], 
                "7": [25, 35, 25, 10, 5], 
                "8": [15, 25, 35, 20, 5], 
                "9": [20, 30, 30, 15, 5], 
                "10": [5, 10, 25, 40, 20], 
                "11": [5, 15, 30, 35, 15], 
                "12": [10, 20, 30, 25, 15], 
                "13": [5, 15, 30, 35, 15], 
                "14": [10, 15, 30, 30, 15], 
                "15": [5, 10, 30, 40, 15], 
                "16": [5, 15, 35, 35, 10], 
                "17": [5, 15, 35, 35, 10], 
                "18": [5, 10, 25, 45, 15], 
                "19": [10, 20, 30, 30, 10], 
                "20": [15, 25, 30, 20, 10],
                "21": [85, 5, 5, 0, 0]
            },
            "texts": {
                "18": [
                    "希望延长社区口腔门诊的晚间及周末服务时间，方便上班族和学生群体就诊。",
                    "建议增加老年人和儿童的免费基础口腔检查项目，比如龋齿筛查、牙周病初诊等。",
                    "希望多开展口腔健康知识讲座，尤其是正确刷牙方法、牙线使用演示和预防蛀牙的科普活动。",
                    "设立匿名评价渠道，及时跟进患者对服务态度或技术水平的投诉建议。",
                    "建议开通线上预约系统，减少现场排队时间，并能实时查询医生排班信息。",
                    "1",
                    "sngfjhadfga",
                    "无"
                ]
            },
            "texts_prob": {"18": [1, 1, 1, 1, 1, 1, 1, 1]}
        }
        self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = self.default_config.copy()
            self.save_config()
    
    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get_question_config(self, question_type: str) -> Dict[str, Any]:
        return self.config.get(question_type, {})
    
    def set_question_config(self, question_type: str, config: Dict[str, Any]):
        self.config[question_type] = config
        self.save_config()
    
    def get_url(self) -> str:
        return self.config.get("url", "")
    
    def set_url(self, url: str):
        self.config["url"] = url
        self.save_config()

# 全局问卷配置实例
question_config = QuestionConfig()