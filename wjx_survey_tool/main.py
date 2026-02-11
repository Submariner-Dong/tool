#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
问卷星自动填写工具 - 图形界面版
作者: SubmarinerD
版本: 1.0
时间: 2026年2月
"""

import os
import sys
import logging

# 添加模块路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('survey_tool.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def main():
    """主函数"""
    try:
        from ui.main_window import MainWindow
        
        print("=" * 50)
        print("问卷星自动填写工具")
        print("版本: 1.0")
        print("作者: SubmarinerD")
        print("=" * 50)
        
        # 启动图形界面
        app = MainWindow()
        app.run()
        
    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保所有依赖包已正确安装")
        input("按回车键退出...")
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")

if __name__ == "__main__":
    main()