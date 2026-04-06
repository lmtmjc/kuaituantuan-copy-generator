# 更新日志 CHANGELOG

## 2026-04-06
- 项目初始化
- 创建 CONTEXT.md 和 CHANGELOG.md
- 导入 WriteWizard AI 开源项目作为基础框架
- 创建 PRD.md 产品需求文档
- 按 PRD 重构为更清晰的单页架构，拆出 `catalog.py` 和 `generation.py`
- 升级 OpenAI 调用到新版 Python SDK 客户端写法
- 新增“开始生成”和“重新生成”交互，并修正品类切换后的标签联动
- 细化 UI/交互：新增欢迎页视觉区、示例试填、准备度面板、结果预览 Tab 和更清晰的表单分区
- API Key 改为仅从环境变量或 `.env` 读取，删除前端输入框并新增 `.env` 模板
- API 提供方切换为 DeepSeek，使用 `https://api.deepseek.com` 和 `deepseek-chat`
- 新增 `.env.example`，统一改为从 `DEEPSEEK_API_KEY` 读取服务端配置
- 新建 `.gitignore` 并忽略 `.env`，避免本地密钥进入版本库
- 前端移除 DeepSeek 服务状态展示，对客户仅保留通用可用性提示
- 更新 README，补充 DeepSeek 配置方式、运行说明和当前交互能力
