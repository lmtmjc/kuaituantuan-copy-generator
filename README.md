# 快团团 AI 文案生成器

本项目是一款面向快团团团长与食品饮料经销商的 AI 文案生成工具。用户填写产品信息后，系统会生成符合快团团开团格式的活动标题、商品标题、卖点短句、卖点详细描述和标签。文案可以直接复制到快团团开团页面，减少手写成本。

## 关键文件

- `app.py`：Streamlit 单页入口，负责状态管理、页面展示和交互。
- `catalog.py`：品类、卖点标签、风格和默认模型配置。
- `generation.py`：表单校验、OpenAI 调用和生成结果封装。
- `prompt.py`：核心 Prompt 构建、few-shot 示例加载和输出归一化。
- `examples.json`：爆款案例素材，用于 few-shot 提示。
- `PRD.md`：产品需求文档。
- `CHANGELOG.md`：更新日志。

## 功能

- 结构化产品信息录入
- 动态品类与卖点标签联动
- 文案风格切换（种草风 / 促销风 / 节日风）
- 一键生成并展示活动标题、商品标题、卖点短句、详细描述、卖点标签
- 重新生成备选文案
- 表单清空
- 生成准备度面板与缺失项提示
- DeepSeek API Key 仅从服务端环境变量或 `.env` 读取
- 结果区支持整段预览和逐项复制
- 单条复制和一键复制全部
- 新版 OpenAI Python SDK 调用

## 安装

1. 进入项目目录：

    ```sh
    cd /Users/xsy/Github/streamlit-AI-copywriter-main
    ```

2. 推荐创建虚拟环境：

    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. 安装依赖：

    ```sh
    python3 -m pip install -r requirements.txt
    ```

4. 配置服务端环境变量或 `.env`：
    直接编辑项目根目录的 `.env` 文件，或参考 `.env.example`：

    ```env
    DEEPSEEK_API_KEY=your_api_key_here
    ```

## 运行

1. 启动应用：

    ```sh
    python3 -m streamlit run app.py
    ```

2. 打开浏览器访问 `http://localhost:8501`。
3. 点击“开始生成”进入表单。
4. 完成产品信息表单并点击“一键生成”。

## DeepSeek API

- API 地址为 `https://api.deepseek.com`。
- 模型固定为 `deepseek-chat`。
- 必须在服务端环境变量或项目根目录 `.env` 文件中配置 `DEEPSEEK_API_KEY`。
- 前端页面不会显示 API Key 输入框，用户打开页面即可直接使用。

## 备注

- 当前版本支持单条输入，不支持批量导入。
- 如果生成结果不满意，可直接点击“重新生成”获得第二版文案。
