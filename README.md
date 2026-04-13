# 快团团食品饮料爆款文案生成器

> 面向快团团团长与食品饮料经销商的 AI 文案工具 —— 填完即生成，生成即可用。

## 简介

本项目通过结构化表单 + DeepSeek API + few-shot 爆款案例库，一键生成符合快团团开团格式的：

- 活动标题（30字内）
- 商品标题（8-30字）
- 卖点短句（3条，每条15字内）
- 卖点详细描述（3-5段，总计500字内）
- 卖点标签（3-5个关键词）

文案可直接复制到快团团开团页面，大幅降低手动撰写成本。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端/应用 | Python + Streamlit |
| AI 接口 | DeepSeek API（OpenAI 兼容 SDK） |
| 数据 | `examples.json`（18 条爆款文案案例，few-shot 素材） |
| 配置 | `.env` + `python-dotenv` |
| 版本管理 | Git + GitHub |

## 关键文件说明

- `app.py`：Streamlit 单页入口，负责状态管理、页面展示和交互。
- `catalog.py`：品类、卖点标签、风格和默认模型配置。
- `generation.py`：表单校验、OpenAI 调用和生成结果封装。
- `prompt.py`：核心 Prompt 构建、few-shot 示例加载和输出归一化。
- `examples.json`：爆款案例素材，用于 few-shot 提示。
- `PRD.md`：产品需求文档（所有功能的最终依据）。
- `CHANGELOG.md`：版本更新记录。
- `.env.example`：环境变量模板。

## 环境要求
- Python 3.8 或更高版本
- pip 包管理工具

## 安装

1. 克隆仓库：

```sh
    git clone https://github.com/lmtmjc/kuaituantuan-copy-generator.git
    cd kuaituantuan-copy-generator
```

2. 推荐创建虚拟环境：

```sh
    python3 -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖：

```sh
    python3 -m pip install -r requirements.txt
```

4. 配置API Key：

 ```sh
    cp .env.example .env
    # 编辑 .env，填入 DEEPSEEK_API_KEY=your_key_here
```

## 运行

1. 启动应用：

```sh
    python3 -m streamlit run app.py
```

2. 打开浏览器访问 `http://localhost:8501`。
3. 点击“开始生成”进入表单。
4. 完成产品信息表单并点击“一键生成”。

## 备注

- 当前版本支持单条录入，批量导入为二期功能
- 用户登录与历史记录为二期功能
- 不支持图片/视频生成，仅限文字文案