# Claude 交接：从 Cowork 会话转到本地 Claude Code

写于 2026-10-20。本文记录 Cowork 会话里做过的事和当前状态，接手前先读根目录 AGENTS.md、CODEX_HANDOFF.md 和本文。

## 用户偏好

- 全程用中文回答。
- 改完代码后**直接构建并重启**，不要再问；保持简单，不要额外造工具。
  在项目根目录执行：`docker compose up -d --build backend frontend`（只改 .env 时用 `--force-recreate`）。
- 给用户的命令用 PowerShell，可直接复制。
- 不得 `docker compose down -v`，不得删数据库。
- 测试通过、构建重启之后**直接 `git commit`**，不要再问（2026-10-20 用户要求）。只提交本地，不 push，除非用户要求。
  提交信息用中文写清楚做了什么、为什么，方便其他 AI 接手时从 `git log` 看懂；不要提交 `.env` 和 Cowork 留下的临时脚本。

## 通话里的「日语练习」模式（2026-10-20 已测试、构建、重启并提交；真实通话效果待用户试用）

用户用语音通话练日语口语。开启后：她用**自己的口吻和口癖**（绝不能变成老师腔）纠正用户日语，再单独说一遍改好的完整句子，然后停下、自动关麦；用户重新打开麦克风即继续，她接着说已生成好的正常回复。

- 后端
  - `reply_format.py`：`PRACTICE_INSTRUCTIONS` 提示词；解析 `<pause/>`，产生 `PracticePause(after)` 事件（不显示、不朗读，每条回复最多一次）。
  - `engine.py`：`turn(..., practice=False)`，开启时把提示词加进每轮上下文（放在历史之后，不破坏缓存）。
  - `call.py`：`CallOptions/Call.practice`；`CallTurns` 在 `PracticePause` 后把后续 `Voice/FlushVoice` 扣在 `_held`，向浏览器发 `{"type":"practice-pause","reply":n}`；收到客户端消息 `practice-continue` 放行；打断、新回合、打字时丢弃扣住的内容。也支持客户端消息 `practice {on}`。
  - `turn_taking.py`：新增 `voicing`、`text_only` 属性。
  - `app.py`：`CallRequest.practice`；文字回合跳过 `PracticePause`。
  - 测试：新增 `tests/test_practice.py`；`tests/test_call_turns.py` 的 `run/run_frames` 加了 `practice` 参数。
- 前端
  - `lib/callPreferences.ts`：`practice` 偏好（按设备保存）。
  - `lib/call.ts`：offer 带 `practice`；`continuePractice()`。
  - `lib/api.ts`：CallEvent 加 `practice-pause`。
  - `lib/liveConversation.ts`：`practicing` 状态；收到暂停时关麦；重新开麦时发继续。
  - `components/CallSettings.tsx`：设置页开关；`CallLayer.tsx`：练习中提示；`i18n/zh.ts` 文案。
  - 相关测试夹具已补 `practice` 字段，并加了 3 个 liveConversation 测试。

Claude Code 接手后（2026-10-20）：
- 修复：练习关闭时模型若写了 `<pause/>`，后面的语音也会被扣住；现在只在练习开着时扣。
- 新增：暂停消息带 `after`（前几段是纠正）。练习通话里除纠正外字幕默认糊住，点一下显示该句，通话层右上角「字幕」一键全显示；只看文字时不藏。
- 新增：台词卡 ‹ › 按段翻页（她的一条回复一页，整条列出，方便截图），翻看时新句不拉走，「回到最新」回来（`linePacing.ts` 的 `pagesOf`）。
- 修复：练习暂停时台词卡会在 3 秒后按语速把后面的正文播出来；现在 `LineCard.held` 期间不按语速前进。
- 后端 pytest/ruff/pyright、前端 vitest/typecheck/纪律检查均通过。

## 其他

- 移动端「没声音」问题已解决：是手机上开了「只看文字」，不是代码问题。
- Cowork 会话留下的、可删除的文件：`apply-changes.cmd`、`auto-apply-watcher.cmd`、`.apply-request`、`backend/.pytest_cache/_bundle.tgz`；`.gitignore` 末尾加的两行也可以去掉。
- 下一步可能的需求：根据实际试用调整纠正频率与语气；之后还有群聊（见 CODEX_HANDOFF.md，未实现）。
