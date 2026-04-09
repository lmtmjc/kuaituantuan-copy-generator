# Codex 操作规则

## 文件删除规则
1. 禁止直接删除任何文件
2. 如果需要删除或替换文件，必须先将文件移动到 /Users/xsy/回收站-codex/，再从原位置移除
3. 移动命令格式：mv 原文件路径 /Users/xsy/回收站-codex/文件名
4. 如果回收站内已有同名文件，在文件名后加时间戳区分，例如：文件名_20260409.py

## 每次任务开始前
- 确认回收站文件夹存在：ls /Users/xsy/回收站-codex/
- 不存在则创建：mkdir -p /Users/xsy/回收站-codex/

## Git 规则
- 每次完成关键功能后更新 CONTEXT.md 和 CHANGELOG.md
- 更新后执行 git commit 并 push 到 GitHub
- .env 文件永远不能推送到 GitHub
- API key 永远不能出现在前端代码里
