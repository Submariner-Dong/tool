# 问卷星自动填写工具

## 项目简介

这是一个基于Python和Selenium的问卷星自动填写工具，能够模拟人工填写问卷，支持多种题型，并可以按预设概率分布进行智能填写。

**⚠️ 重要提示：使用前必须挂梯子（VPN/代理），因为程序无法自动检测电脑上的Chrome版本，需要手动去Chrome官网下载匹配的WebDriver，而官网访问需要梯子！**

## 技术原理

### 核心机制
- **自动化浏览器控制**：使用Selenium WebDriver控制Chrome浏览器
- **智能题型识别**：通过DOM元素属性自动识别问卷题型（单选、多选、填空、矩阵等）
- **概率分布填写**：根据预设的概率参数进行智能选择，模拟真实用户行为
- **多线程处理**：支持同时打开多个浏览器窗口并行填写
- **IP代理轮换**：自动切换代理IP避免被检测

### 支持的题型
- 单选题（type=3）
- 多选题（type=4）
- 填空题（type=1/2）
- 量表题（type=5）
- 矩阵题（type=6）
- 下拉框题（type=7）
- 滑块题（type=8）
- 排序题（type=11）

## 环境要求

### 必需组件
- Python 3.6+
- Chrome浏览器
- Chrome WebDriver（与Chrome版本匹配）
- 必要的Python包：
  ```bash
  selenium
  numpy
  requests
  ```

### 网络要求
**必须使用VPN/代理/梯子**，原因：
- 程序无法自动检测Chrome版本，需要手动下载WebDriver
- Chrome WebDriver官网（https://chromedriver.chromium.org/）在国内无法直接访问
- 需要梯子才能下载匹配的WebDriver文件

## 安装配置

### 1. 环境准备
```bash
pip install selenium numpy requests
```

### 2. Chrome WebDriver配置（关键步骤）
**注意：这一步必须挂梯子才能完成！**
1. **挂梯子访问**：https://chromedriver.chromium.org/
2. **查看Chrome版本**：在Chrome中打开 `chrome://version/` 查看版本号
3. **下载匹配版本**：在官网下载与Chrome版本完全匹配的WebDriver
4. **放置文件**：将下载的chromedriver.exe放在Python安装目录或系统PATH中

### 3. 代理设置（可选但推荐）
推荐使用品赞IP服务：
1. 注册品赞IP账号并完成实名认证
2. 将本机公网IP添加到白名单
3. 在代码中配置API链接

## 使用方法

### 第一步：修改问卷链接
在代码中找到`url`变量，替换为你的问卷链接：
```python
url = 'https://www.wjx.cn/vm/你的问卷ID.aspx'
```

### 第二步：配置题型概率参数

#### 单选题配置
```python
single_prob = {"1": [30, 70], "2": -1, "3": [20, 30, 50]}
# -1表示随机选择，[30,70]表示3:7的概率分布
```

#### 多选题配置
```python
multiple_prob = {"1": [100, 2, 1, 1]}  # 100表示必选，其他数字表示概率权重
multiple_opts = {"1": 1}  # 表示在必选后额外选择1个选项
```

#### 填空题配置
```python
texts = {"1": ["答案1", "答案2", "答案3"]}
texts_prob = {"1": [1, 1, 1]}  # 每个答案的权重
```

#### 其他题型
- 矩阵题：`matrix_prob`
- 量表题：`scale_prob`
- 下拉框：`droplist_prob`

### 第三步：运行程序
```bash
python wjx(origin).py
```

## 参数说明

### 概率参数规则
- `-1`：完全随机选择
- `[a, b, c]`：按权重比例选择，会自动归一化
- `100`：在多选题中表示必选选项

### 窗口配置
在`main`函数中调整线程数量：
```python
thread_1 = Thread(target=run, args=(50, 50))  # 窗口1坐标
thread_2 = Thread(target=run, args=(650, 50)) # 窗口2坐标
# 可以添加更多线程增加填写速度
```

## 注意事项

### ⚠️ 重要警告
1. **必须使用代理/VPN**：否则会被问卷星检测
2. **概率参数要合理**：确保参数数量与选项数量匹配
3. **不要设置过高频率**：避免触发反爬虫机制
4. **数据仅供参考**：自动填写的数据不具备真实研究的信效度

### 故障排除
- **WebDriver版本不匹配**：下载与Chrome版本对应的WebDriver
- **代理IP失效**：检查品赞IP服务是否正常
- **题型不支持**：某些特殊题型可能无法自动填写
- **验证码出现**：程序会自动处理滑块验证，但复杂验证码需要人工干预

## 项目结构

```
wjx_survey_tool/
├── main.py              # 主程序文件
├── config.json          # 配置文件
├── question_config.json # 题目配置
└── survey_tool.log     # 运行日志
```

## 联系方式

- QQ群：774326264 或 427847187
- 作者：鐘
- 更新时间：2023.11

## 免责声明

本工具仅供学习和研究使用，请勿用于非法用途。使用本工具产生的任何后果由使用者自行承担。

---

**再次强调：使用前务必挂梯子，否则无法正常使用！**