# 🚀 快速启动指南

## 📋 前置要求

1. **Python 3.8+** 已安装
2. **AI模型 API Key** （选择其一）：
   - 阿里云百炼平台 API Key（推荐）
   - OpenAI API Key（可选）

## ⚡ 快速启动（推荐）

```bash
# 1. 进入项目目录
cd Hypertension_agent

# 2. 首次设置
python run.py setup

# 3. 启动开发服务器
python run.py dev
```

## 🔗 访问应用

- **Web界面**: http://localhost:8501
- **API文档**: http://localhost:8000/docs

## 🛠️ 详细安装步骤

### 步骤1: 环境设置

```bash
# 创建虚拟环境（可选但推荐）
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 步骤2: 安装依赖

```bash
pip install -r requirements.txt
```

### 步骤3: 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，添加你的API Key
# 推荐使用阿里云：
# DASHSCOPE_API_KEY=your_dashscope_api_key_here
# LLM_PROVIDER=qwen-plus
#
# 或使用OpenAI：
# OPENAI_API_KEY=your_openai_api_key_here
# LLM_PROVIDER=openai
```

### 步骤4: 初始化数据库

```bash
python scripts/db_manager.py
# 选择: 1. 初始化数据库
# 选择: 2. 创建示例数据（可选）
```

### 步骤5: 启动服务

```bash
# 方法1: 使用运行脚本（推荐）
python run.py dev

# 方法2: 手动启动
# 终端1 - 启动API服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 终端2 - 启动Web界面
streamlit run web/app.py --server.port 8501
```

## 🧪 测试和验证

```bash
# 运行所有测试
python run.py test

# 系统功能验证
python run.py validate

# 错误检查
python scripts/fix_errors.py
```

## 📝 使用说明

### 1. 患者管理
- 创建患者档案
- 记录基本信息和病史
- 管理血压测量记录

### 2. AI智能咨询
- 与AI医疗助手对话
- 获取个性化医疗建议
- 风险评估和药物推荐

### 3. 血压监测
- 记录血压数据
- 可视化趋势分析
- 统计分析功能

### 4. 知识库查询
- 搜索医学知识
- 查看诊疗指南
- 药物信息查询

## ❗ 常见问题

### Q: 无法启动AI功能？
**A**: 检查.env文件中的API Key是否设置正确：
- 阿里云：`DASHSCOPE_API_KEY` 和 `LLM_PROVIDER=qwen-plus`
- OpenAI：`OPENAI_API_KEY` 和 `LLM_PROVIDER=openai`

没有API Key时，其他功能仍可正常使用。

### Q: 数据库错误？
**A**: 运行 `python scripts/db_manager.py` 重新初始化数据库。

### Q: 端口冲突？
**A**: 修改.env文件中的端口配置：
```
API_PORT=8001  # 修改API端口
WEB_PORT=8502  # 修改Web端口
```

### Q: 导入错误？
**A**: 确保在项目根目录下运行，并检查Python路径设置。

## 🆘 获取帮助

```bash
# 查看帮助信息
python run.py help

# 数据库管理工具
python scripts/db_manager.py

# 系统验证工具
python scripts/system_validator.py
```

## ⚠️ 重要提醒

- 本系统仅供学习和研究使用
- 不能替代专业医生的诊断和治疗
- AI生成的建议需要专业医生审核
- 紧急情况请立即就医

## 🔄 更新和维护

```bash
# 更新依赖
pip install -r requirements.txt --upgrade

# 备份数据库
python scripts/db_manager.py
# 选择: 4. 备份数据库

# 查看系统状态
python scripts/system_validator.py
```

---

**祝您使用愉快！如遇问题请参考README.md或提交Issue。**