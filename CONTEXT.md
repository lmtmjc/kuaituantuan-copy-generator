# 项目全貌 CONTEXT

## 项目是什么
快团团食品饮料爆款文案生成器。
用户输入产品信息，一键生成符合快团团开团格式的爆款文案，
供团长和经销商直接复制使用。

## 当前进度
- [x] 项目框架搭建
- [x] 产品信息录入表单
- [x] 文案一键生成功能
- [x] 风格切换功能
- [x] 一键复制功能
- [x] 重新生成功能
- [x] UI/交互细化
- [x] DeepSeek API 接入
- [x] `.env` / `.env.example` / `.gitignore` 配置
- [x] GitHub 远程仓库配置与首次备份推送
- [x] Prompt 示例按品类动态匹配
- [x] examples.json 扩充并修复为 18 条可解析案例
- [x] Prompt 强化为快团团资深运营专家人设与高转化语言风格
- [x] Prompt 补充排版规范、价格划算感表达和描述结构约束
- [x] Prompt 强化系统人设（10万单专家）、卖点强制 Emoji 前缀、详细描述禁止说明书体并对齐示例带货节奏
- [x] normalize_output 支持降级处理，不再因卖点/段落/标签数量不足直接失败
- [x] README 主标题与「爆款文案」产品定位对齐（仓库对外展示与 PRD/CONTEXT 一致）
- [x] 生成中 Spinner 提示统一为「正在生成，请稍候...」（无「最多20秒」等附加说明）
- [x] 首页 / 顶栏 UI：浅色全站底、左对齐极简 Header、升级 Slogan 与「快团团专供」副文案
- [x] 首页纯白极简：四列规格网格、黑底 CTA、`details` 折叠说明；欢迎页不再单独展示侧栏使用说明

## 技术栈
- 后端：Python + Streamlit（基于WriteWizard AI开源项目改造）
- AI接口：DeepSeek API（OpenAI 兼容 SDK）
- 数据：examples.json（快团团爆款文案案例，few-shot素材）
- 配置：`.env` + `python-dotenv`
- Prompt策略：few-shot 示例按二级品类优先、一级品类兜底匹配；系统人设为带货超10万单的食品饮料专家（口语化、真实、感染力）；用户指令强调微信风格 Emoji、活动标题震撼符号、卖点每条必须以 Emoji 开头（禁止无 Emoji）；详细描述禁止说明书体、须有画面感与情绪、参考示例语气节奏且每段有钩子或场景代入；有比价时写清省钱与「闭眼入」感；并结合目标人群做场景引导

## 版本管理状态
- 本地仓库已完成 Git 初始化
- 当前分支：`main`
- 已配置远程：`origin -> https://github.com/lmtmjc/kuaituantuan-copy-generator.git`
- 当前已建立 `main` 跟踪 `origin/main`
- 最近文档同步：2026-04-12（`CONTEXT.md` / `CHANGELOG.md` 与仓库当前实现对齐；含首页顶栏极简 UI、Slogan 与生成中 Spinner 等；工作区与 `origin/main` 一致时可视为进度清单有效）

## 关键文件说明
- `app.py` 主程序入口
- `catalog.py` 品类、标签、风格和模型配置
- `generation.py` 表单校验、模型调用和结果封装
- `prompt.py` 核心Prompt逻辑（重要，修改需谨慎）
- `examples.json` 爆款案例数据（当前 18 条，可正常 JSON 解析）
- `.env.example` 环境变量模板
- `.gitignore` 本地密钥忽略规则
- `PRD.md` 产品需求文档（所有功能的最终依据）
- `CHANGELOG.md` 历史修改记录

## 输出字段规范
| 输出字段 | 字数要求 |
|------|------|
| 活动标题 | 30字以内 |
| 商品标题 | 8-30字 |
| 卖点短句 | 每条15字以内，共3条 |
| 卖点详细描述 | 总计500字以内，3-5段 |
| 卖点标签 | 3-5个关键词 |

## 踩过的坑
- 初始版本的 OpenAI SDK 调用方式与依赖版本不匹配，已升级为兼容 SDK 客户端写法
- 前端暴露 API Key 输入和服务状态不适合客户使用，现已全部收口到服务端环境变量
- `.env` 必须加入 `.gitignore`，避免真实密钥被 git 跟踪
- few-shot 如果固定取前两条，容易与当前商品品类偏离，现已改为按品类动态匹配示例
- `examples.json` 在合并大量案例时容易出现转义和结构错误，后续每次更新后都要先做 JSON 解析验证

## 下一步要做的事
- 用真实 DeepSeek key 做一轮完整联调，继续收 Prompt 质量
- 视需要补基础测试（Prompt 归一化、表单校验、输出解析）
- 继续补充更多二级品类示例，提高动态匹配下的 few-shot 质量
- 评估部署方式，确保客户打开页面即可直接使用
