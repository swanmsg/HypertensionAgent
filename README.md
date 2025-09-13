# 高血压患者医嘱智能体平台

基于LangChain开发的智能医疗咨询平台，专注于高血压患者的个性化医嘱生成和健康管理。

## 功能特性

- 🏥 **智能医嘱生成**: 基于患者信息生成个性化医疗建议
- 📊 **风险评估**: 评估患者高血压风险等级和并发症风险
- 💊 **用药指导**: 智能推荐适合的降压药物和用药方案
- 📈 **健康监测**: 跟踪血压变化趋势和生活方式调整建议
- 🤖 **智能对话**: 支持自然语言交互，回答患者健康咨询

## 技术架构

- **后端**: FastAPI + LangChain + SQLAlchemy
- **前端**: Streamlit Web界面
- **数据库**: SQLite
- **AI模型**: 支持多种模型
  - 阿里云通义千问-Plus（推荐）
  - OpenAI GPT系列模型
- **知识库**: 高血压医学知识库和诊疗指南

## 快速开始

### 方法一：使用运行脚本（推荐）

1. 下载或克隆项目
```bash
cd Hypertension_agent
```

2. 首次设置
```bash
python run.py setup
```

3. 启动开发服务器
```bash
python run.py dev
```

4. 访问应用
- Web界面: http://localhost:8501
- API文档: http://localhost:8000/docs

### 方法二：手动安装

1. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的OpenAI API Key
```

4. 初始化数据库
```bash
python scripts/db_manager.py
# 选择 "1. 初始化数据库" 和 "2. 创建示例数据"
```

5. 启动服务
```bash
# 启动API服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 另开终端启动Web界面
streamlit run web/app.py --server.port 8501
```

## 使用说明

1. 打开浏览器访问 http://localhost:8501
2. 输入患者基本信息（年龄、性别、血压值等）
3. 与智能体对话，获取个性化医疗建议
4. 查看生成的医嘱和风险评估报告

## 项目结构

```
Hypertension_agent/
├── app/                    # 后端API
│   ├── main.py            # FastAPI应用入口
│   ├── models/            # 数据模型
│   │   ├── database.py    # 数据库模型
│   │   └── schemas.py     # API数据模式
│   ├── services/          # 业务逻辑
│   │   ├── patient_service.py      # 患者管理服务
│   │   ├── ai_agent.py            # AI智能体
│   │   ├── knowledge_service.py   # 知识库服务
│   │   └── medical_advice_service.py # 医疗建议服务
│   └── utils/             # 工具函数
│       └── helpers.py     # 辅助函数
├── web/                   # Web界面
│   └── app.py            # Streamlit应用
├── data/                  # 数据和知识库
│   ├── knowledge/         # 医学知识库
│   │   ├── hypertension_guidelines.md # 诊疗指南
│   │   └── medications.md # 药物信息
│   └── rules/            # 医嘱规则
│       └── medical_rules.py # 规则引擎
├── scripts/               # 脚本工具
│   ├── db_manager.py      # 数据库管理
│   └── system_validator.py # 系统验证
├── tests/                 # 测试文件
│   ├── test_patient_service.py # 患者服务测试
│   ├── test_ai_agent.py       # AI智能体测试
│   └── test_api.py           # API接口测试
├── run.py                 # 运行脚本
├── requirements.txt       # 依赖列表
├── .env.example          # 环境变量模板
└── README.md             # 项目说明
```

## 开发和测试

### 运行测试
```bash
# 运行所有测试
python run.py test

# 或手动运行
pytest tests/ -v
```

### 系统验证
```bash
# 验证系统功能
python run.py validate

# 或手动运行
python scripts/system_validator.py
```

### 数据库管理
```bash
# 数据库管理工具
python scripts/db_manager.py
```

## 配置说明

### 环境变量
- `DASHSCOPE_API_KEY`: 阿里云百炼平台API密钥（推荐）
- `LLM_PROVIDER`: 模型提供商（qwen-plus 或 openai）
- `OPENAI_API_KEY`: OpenAI API密钥（可选）
- `DATABASE_URL`: 数据库连接字符串
- `API_HOST`: API服务主机地址
- `API_PORT`: API服务端口
- `WEB_PORT`: Web应用端口

### 数据库
- 默认使用SQLite数据库
- 数据库文件: `hypertension_agent.db`
- 支持备份和恢复功能

## 注意事项

⚠️ **重要提醒**: 本系统仅用于辅助医疗决策，不能替代专业医生的诊断和治疗。患者应在医生指导下使用相关建议。

### 使用限制
- 本系统仅供学习和研究使用
- 请勿用于实际临床诊疗
- AI生成的建议需要专业医生审核
- 紧急情况请立即就医

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 问题反馈

如遇到问题，请通过以下方式反馈：
- 创建 GitHub Issue
- 提供详细的错误信息和复现步骤

## 版本历史

- v1.0.0 - 初始版本
  - 基础患者管理功能
  - AI智能体集成
  - Web界面实现
  - 知识库和规则引擎

## 许可证

MIT License

## 致谢

- 感谢OpenAI提供的强大AI模型
- 感谢LangChain项目提供的AI开发框架
- 感谢中国高血压防治指南提供的医学指导