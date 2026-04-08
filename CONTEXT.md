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

## 技术栈
- 后端：Python + Streamlit（基于WriteWizard AI开源项目改造）
- AI接口：DeepSeek API（OpenAI 兼容 SDK）
- 数据：examples.json（快团团爆款文案案例，few-shot素材）
- 配置：`.env` + `python-dotenv`
- Prompt策略：few-shot 示例按二级品类优先、一级品类兜底匹配

## 版本管理状态
- 本地仓库已完成 Git 初始化
- 当前分支：`main`
- 已配置远程：`origin -> https://github.com/lmtmjc/kuaituantuan-copy-generator.git`
- 当前已建立 `main` 跟踪 `origin/main`

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
