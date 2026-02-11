# 概率编辑器界面
import tkinter as tk
from tkinter import ttk, messagebox

class ProbabilityEditor:
    def __init__(self, parent, config_manager):
        self.config = config_manager
        self.window = tk.Toplevel(parent)
        self.window.title("题目概率设置")
        self.window.geometry("1000x700")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        self.load_probabilities()
    
    def setup_ui(self):
        """设置UI界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 题目类型选择
        type_frame = ttk.Frame(main_frame)
        type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(type_frame, text="题目类型:").pack(side=tk.LEFT)
        self.question_type = tk.StringVar(value="single_prob")
        type_combo = ttk.Combobox(type_frame, textvariable=self.question_type, state="readonly")
        type_combo['values'] = [
            ("single_prob", "单选题"),
            ("droplist_prob", "下拉框题"),
            ("multiple_prob", "多选题"),
            ("matrix_prob", "矩阵题"),
            ("scale_prob", "量表题"),
            ("texts_prob", "填空题")
        ]
        type_combo.pack(side=tk.LEFT, padx=5)
        type_combo.bind('<<ComboboxSelected>>', self.on_type_changed)
        
        # 题目选择框架
        question_frame = ttk.LabelFrame(main_frame, text="题目选择", padding="5")
        question_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(question_frame, text="题目编号:").pack(side=tk.LEFT)
        self.question_key = tk.StringVar()
        self.question_combo = ttk.Combobox(question_frame, textvariable=self.question_key, state="readonly")
        self.question_combo.pack(side=tk.LEFT, padx=5)
        self.question_combo.bind('<<ComboboxSelected>>', self.on_question_changed)
        
        # 概率设置框架
        prob_frame = ttk.LabelFrame(main_frame, text="概率设置", padding="5")
        prob_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 概率输入区域
        self.prob_frame_inner = ttk.Frame(prob_frame)
        self.prob_frame_inner.pack(fill=tk.BOTH, expand=True)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="保存", command=self.save_probabilities).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="添加题目", command=self.add_question).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除题目", command=self.delete_question).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # 选项数量设置
        options_frame = ttk.Frame(button_frame)
        options_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(options_frame, text="选项数量:").pack(side=tk.LEFT)
        self.options_count = tk.StringVar(value="3")
        ttk.Spinbox(options_frame, from_=2, to=10, textvariable=self.options_count, width=5,
                   command=self.update_probability_inputs).pack(side=tk.LEFT, padx=5)
    
    def load_probabilities(self):
        """加载概率设置"""
        self.on_type_changed()
    
    def on_type_changed(self, event=None):
        """题目类型改变事件"""
        question_type = self.question_type.get()
        config = self.config.get_question_config(question_type)
        
        # 更新题目选择
        keys = list(config.keys())
        self.question_combo['values'] = keys
        if keys:
            self.question_key.set(keys[0])
            self.on_question_changed()
        else:
            self.question_key.set("")
            self.clear_probability_inputs()
    
    def on_question_changed(self, event=None):
        """题目改变事件"""
        question_type = self.question_type.get()
        question_key = self.question_key.get()
        
        if question_key:
            config = self.config.get_question_config(question_type)
            probabilities = config.get(question_key, [])
            
            # 更新选项数量
            if isinstance(probabilities, list):
                self.options_count.set(str(len(probabilities)))
                self.update_probability_inputs(probabilities)
            else:
                self.options_count.set("3")
                self.update_probability_inputs()
    
    def clear_probability_inputs(self):
        """清空概率输入框"""
        for widget in self.prob_frame_inner.winfo_children():
            widget.destroy()
    
    def update_probability_inputs(self, probabilities=None):
        """更新概率输入框"""
        self.clear_probability_inputs()
        
        try:
            count = int(self.options_count.get())
        except:
            count = 3
        
        if count < 2:
            count = 2
        if count > 10:
            count = 10
        
        # 创建输入框
        for i in range(count):
            row_frame = ttk.Frame(self.prob_frame_inner)
            row_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(row_frame, text=f"选项 {i+1} 概率:").pack(side=tk.LEFT)
            
            prob_var = tk.StringVar()
            if probabilities and i < len(probabilities):
                if isinstance(probabilities[i], (int, float)):
                    prob_var.set(str(probabilities[i]))
                else:
                    prob_var.set("")
            
            entry = ttk.Entry(row_frame, textvariable=prob_var, width=10)
            entry.pack(side=tk.LEFT, padx=5)
            
            # 存储变量引用
            if not hasattr(self, 'prob_vars'):
                self.prob_vars = []
            if i >= len(self.prob_vars):
                self.prob_vars.append(prob_var)
            else:
                self.prob_vars[i] = prob_var
    
    def add_question(self):
        """添加新题目"""
        question_type = self.question_type.get()
        config = self.config.get_question_config(question_type)
        
        # 生成新题目编号
        existing_keys = [int(k) for k in config.keys() if k.isdigit()]
        new_key = str(max(existing_keys) + 1) if existing_keys else "1"
        
        # 添加默认概率
        try:
            count = int(self.options_count.get())
            default_prob = [1] * count  # 均匀分布
        except:
            default_prob = [1, 1, 1]
        
        config[new_key] = default_prob
        self.config.set_question_config(question_type, config)
        
        # 更新界面
        self.on_type_changed()
        self.question_key.set(new_key)
        self.on_question_changed()
        
        messagebox.showinfo("成功", f"已添加题目 {new_key}")
    
    def delete_question(self):
        """删除题目"""
        question_type = self.question_type.get()
        question_key = self.question_key.get()
        
        if not question_key:
            messagebox.showwarning("警告", "请先选择要删除的题目")
            return
        
        if messagebox.askyesno("确认", f"确定要删除题目 {question_key} 吗？"):
            config = self.config.get_question_config(question_type)
            if question_key in config:
                del config[question_key]
                self.config.set_question_config(question_type, config)
                
                # 更新界面
                self.on_type_changed()
                
                messagebox.showinfo("成功", f"已删除题目 {question_key}")
    
    def save_probabilities(self):
        """保存概率设置"""
        question_type = self.question_type.get()
        question_key = self.question_key.get()
        
        if not question_key:
            messagebox.showwarning("警告", "请先选择题目")
            return
        
        try:
            # 获取输入的概率值
            probabilities = []
            for prob_var in self.prob_vars:
                value = prob_var.get().strip()
                if value:
                    probabilities.append(float(value))
                else:
                    probabilities.append(1)  # 默认值
            
            # 保存到配置
            config = self.config.get_question_config(question_type)
            config[question_key] = probabilities
            self.config.set_question_config(question_type, config)
            
            messagebox.showinfo("成功", "概率设置已保存")
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")