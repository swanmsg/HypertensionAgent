# 阿里百炼平台配置指南

## 🔧 配置步骤

### 1. 获取API Key

1. 访问 [阿里云百炼平台](https://bailian.console.aliyun.com/)
2. 登录您的阿里云账号
3. 开通百炼服务
4. 在控制台中创建应用
5. 获取API Key

### 2. 配置环境变量

编辑 `.env` 文件：

```bash
# 阿里百炼平台配置（主要使用）
DASHSCOPE_API_KEY=your_dashscope_api_key_here

# 使用的模型类型（qwen-plus 或 openai）
LLM_PROVIDER=qwen-plus

# OpenAI API配置（可选）
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1

# 数据库配置
DATABASE_URL=sqlite:///./hypertension_agent.db

# 应用配置
APP_NAME=高血压患者医嘱智能体平台
APP_VERSION=1.0.0
DEBUG=True

# API配置
API_HOST=0.0.0.0
API_PORT=8000

# Web界面配置
WEB_HOST=0.0.0.0
WEB_PORT=8501
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 📋 支持的模型

### 阿里云通义千问（推荐）
- **模型名称**: qwen-plus
- **提供商**: 阿里云百炼平台
- **特点**: 
  - 中文支持优秀
  - 响应速度快
  - 成本相对较低
  - 数据安全性高

### OpenAI GPT（备选）
- **模型名称**: gpt-3.5-turbo
- **提供商**: OpenAI
- **特点**:
  - 英文能力强
  - 生态完善
  - 需要科学上网

## 🔄 切换模型

通过修改环境变量 `LLM_PROVIDER` 来切换模型：

```bash
# 使用阿里云qwen-plus（推荐）
LLM_PROVIDER=qwen-plus

# 使用OpenAI GPT
LLM_PROVIDER=openai
```

## 🚀 启动服务

```bash
# 快速启动
python run.py dev

# 或手动启动
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
streamlit run web/app.py --server.port 8501
```

## 🔍 验证配置

访问 Web 界面首页，可以看到当前使用的模型信息：
- 🤖 AI模型: 阿里百炼通义千问-Plus模型 (在线) ✅
- 🤖 AI模型: 不可用 ❌（需要检查配置）

## 💡 使用建议

1. **推荐使用qwen-plus**：中文医疗领域表现更好
2. **API Key安全性**：不要将API Key提交到代码库
3. **网络环境**：阿里云模型对网络要求相对宽松
4. **成本控制**：设置合理的调用频率限制

## ❓ 常见问题

### Q: 如何获取阿里云API Key？
A: 
1. 登录 [阿里云控制台](https://ecs.console.aliyun.com/)
2. 搜索"百炼"进入百炼控制台
3. 创建应用获取API Key

### Q: API调用失败怎么办？
A: 
1. 检查API Key是否正确
2. 确认账户余额充足
3. 检查网络连接
4. 查看错误日志

### Q: 能否同时支持多个模型？
A: 目前支持通过环境变量切换，未来版本将支持动态切换

### Q: qwen-plus和gpt-3.5-turbo有什么区别？
A:
- **qwen-plus**: 中文理解更好，医疗术语处理优秀，响应快
- **gpt-3.5-turbo**: 英文能力强，生态丰富，但中文医疗专业性略低

## 📞 技术支持

如需技术支持，请：
1. 查看系统日志
2. 运行 `python scripts/system_validator.py` 进行诊断
3. 提交Issue并附上错误信息