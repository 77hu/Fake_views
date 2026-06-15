# Fake_views
AI虚假评论检测Web系统，基于Django + Random Forest实现电商评论真实性判断。  
本项目针对电商虚假评论场景，使用Django 5.2.5开发Web平台，集成预训练RF模型（1.75MB .pkl文件）实现评论实时真假分类，提供VADER情感分析、Plotly.js情绪热力图、vis-network网络传播可视化等辅助分析功能。  
项目支持用户注册登录、历史记录管理、数据统计面板，适合电商平台内容审核和评论质量评估场景。

# 时间表
#### 2025.08.27
初版项目搭建，确定Django + Random Forest技术路线  
#### 2025.08.28
完成ReviewAnalysis数据模型和ReviewForm表单开发  
#### 2025.08.30
集成Random Forest模型（E:\fake_review_rf_model.pkl），完成预测管线  
#### 2025.09.01
集成NLTK VADER情感分析，开发情绪热力图（Plotly.js）  
#### 2025.09.03
完成8个HTML页面开发（主页/登录/注册/面板/历史/详情/热力图/网络图）  
#### 2025.09.05
实现访客日志中间件和用户反馈系统  
#### 2025.09.10
完成MySQL数据库迁移和AJAX异步删除功能

# 目录
<a href="#1-项目介绍">1 项目介绍</a>  
- <a href="#关于虚假评论检测">1.1 关于虚假评论检测</a>  
- <a href="#目录结构">1.2 目录结构</a>  
- <a href="#依赖">1.3 依赖</a>  
- <a href="#系统架构">1.4 系统架构</a>  

<a href="#如何使用">2 如何使用</a>  
- <a href="#安装依赖">2.1 安装依赖</a>  
- <a href="#配置数据库">2.2 配置数据库</a>  
- <a href="#启动服务">2.3 启动服务</a>  
- <a href="#使用说明">2.4 使用说明</a>  
- <a href="#情感热力图">2.5 情感热力图</a>  

<a href="#统计数据">3 统计数据</a>  
- <a href="#模型信息">3.1 模型信息</a>  

<a href="#开发说明">4 开发说明</a>  

<a href="#已知问题">5 已知问题</a>  


# 1 项目介绍
## 1.1 关于虚假评论检测
电商平台上的虚假评论严重影响消费者决策和平台信誉。准确识别虚假评论是平台运营的核心挑战之一。

目前常见的解决方案对比：

| 方法名称 | 相关要点 |
| ------ | ------ |
| 人工审核 | 准确率高但成本极高，无法规模化 |
| 规则引擎（关键词匹配） | 速度快但容易被绕过，误判率高 |
| 付费API（如AWS Comprehend） | 使用简单但成本高，数据隐私有风险 |
| 机器学习分类器 | 本项目采用的方案，兼顾准确率和成本，可自定义训练 |

本项目使用**Django Web + Random Forest模型 + NLTK情感分析**方案，用户输入评论信息（评分、购买验证、产品类别、标题、正文），系统即可实时判断评论真假，支持：
- 实时真假分类（Random Forest模型）
- 置信度概率输出（fake/real概率）
- VADER情感分析（compound分数 -1到+1）
- Plotly.js情绪热力图（品类 × 评分维度）
- 用户历史分析记录管理
- 风险评论自动标注

## 1.2 目录结构
### 1.2.1 基本配置
| 序号 | 文件名称 | 说明 |
| ------ | ------ | ------ |
| 1 | `manage.py` | Django CLI入口 |
| 2 | `db.sqlite3` | SQLite数据库（开发用） |
| 3 | `Fake_views/` | Django项目配置包 |
| 4 | `app1/` | 主应用目录（活跃） |

### 1.2.2 核心应用
| 序号 | 文件名称 | 说明 |
| ------ | ------ | ------ |
| 1 | `app1/models.py` | ReviewAnalysis数据模型（12字段） |
| 2 | `app1/forms.py` | ReviewForm表单定义 |
| 3 | `app1/views.py` | 核心业务逻辑（319行） |
| 4 | `app1/urls.py` | 应用路由（10个URL路由） |
| 5 | `app1/admin.py` | 管理后台注册 |
| 6 | `app1/load_models.py` | 数据加载stub |

### 1.2.3 前端模板
| 序号 | 文件名称 | 说明 |
| ------ | ------ | ------ |
| 1 | `templates/home.html` | 主页（687行，评论输入+结果展示） |
| 2 | `templates/dashboard.html` | 用户统计面板（467行） |
| 3 | `templates/history.html` | 历史记录（323行） |
| 4 | `templates/heatmap.html` | 情感热力图（377行，Plotly.js） |
| 5 | `templates/analysis_detail.html` | 分析详情（165行） |
| 6 | `templates/fake_review_dynamic.html` | 网络传播图（269行） |
| 7 | `templates/login.html` | 登录页 |
| 8 | `templates/register.html` | 注册页 |

## 1.3 依赖
```
pip install django mysqlclient joblib nltk pandas matplotlib seaborn scikit-learn
python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt'); nltk.download('wordnet')"
```

## 1.4 系统架构
```
用户提交评论表单
    │
    ▼
views.py home()
    ├── 构造特征DataFrame (RATING, VERIFIED_PURCHASE, PRODUCT_CATEGORY, 文本字段)
    ├── loaded_model.predict() → 'fake' 或 'real'
    ├── loaded_model.predict_proba() → 概率分布
    ├── VADER情感分析 → compound分数 [-1, 1]
    └── 存入ReviewAnalysis模型

数据展示:
    ├── dashboard() → 统计面板（总数/虚假比例/真实比例）
    ├── heatmap() → Plotly.js热力图（品类 × 评分）
    └── history() → 历史记录表 + 筛选 + 模态框
```

# 2 如何使用
## 2.1 安装依赖
```
pip install django mysqlclient joblib nltk pandas matplotlib seaborn scikit-learn
```

## 2.2 配置数据库
项目使用MySQL数据库，在`Fake_views/settings.py`中配置：
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fake',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```
注意：RF模型文件路径硬编码为`E:\fake_review_rf_model.pkl`，需确保文件存在。

## 2.3 启动服务
```
python manage.py migrate
python manage.py runserver
```
访问 `http://localhost:8000/home/` 即可使用。

## 2.4 使用说明
1. 注册/登录账号
2. 在主页填写评论信息（评分1-5、是否购买、产品类别、标题、正文）
3. 点击"提交分析"
4. 查看AI检测结果（REAL/FAKE + 概率分布 + 情感分数）
5. 在用户面板查看历史记录和统计数据

## 2.5 情感热力图
访问 `/heatmap/` 查看按产品类别和评分维度聚合的平均情感分数热力图：
- 颜色：红色（-1负面）→ 白色（0中性）→ 绿色（+1正面）
- X轴：评分（1-5星）
- Y轴：产品类别

# 3 统计数据
## 3.1 模型信息
| 项目 | 值 |
| ------ | ------ |
| 模型类型 | Random Forest Classifier |
| 模型文件 | `E:\fake_review_rf_model.pkl`（1.75MB） |
| 训练数据 | `E:\clear_data.csv`（561KB） |
| 特征列 | RATING, VERIFIED_PURCHASE, PRODUCT_CATEGORY, PRODUCT_TITLE, REVIEW_TITLE, REVIEW_TEXT |
| 类别 | fake / real 二分类 |

# 4 开发说明
- 模型在模块级别全局加载（`joblib.load()`），避免重复IO
- 正确处理模型类别顺序不确定性（`classes_`数组映射）
- `ReviewAnalysis.save()`方法自动设置COMPLETED状态
- AJAX异步删除分析记录，提升用户体验
- Bootstrap 5 + Font Awesome 6（CDN）构建响应式界面

# 5 已知问题
1. RF模型文件路径硬编码为`E:\fake_review_rf_model.pkl`，迁移需修改`views.py`
2. NLTK资源（punkt/stopwords/wordnet）下载被注释，需手动`nltk.download()`
3. `preProcess()`预处理函数存在但未接入预测流程
4. `SECRET_KEY`硬编码在`settings.py`中
5. `Fake_app1`应用未激活（settings.py中已注释）
