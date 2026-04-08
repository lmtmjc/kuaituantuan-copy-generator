# 更新日志 CHANGELOG

## 2026-04-08
- `prompt.py` 的 few-shot 示例取用逻辑改为按品类动态匹配：优先二级品类，其次一级品类，最后兜底前两条
- 修复 `examples.json` 的格式问题，保留全部案例内容，并确认文件可被 JSON 正常解析
- `examples.json` 当前整理为 18 条案例，覆盖更多食品饮料子品类
- 同步更新 `CONTEXT.md`，记录当前项目进度与示例数据状态

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
- 配置 GitHub 远程仓库 `origin`
- 首次将本地 `main` 分支推送到 `lmtmjc/kuaituantuan-copy-generator`
- 建立本地 `main` 与 `origin/main` 的跟踪关系，便于后续备份
