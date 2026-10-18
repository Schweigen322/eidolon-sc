# 网页内置设置

新增「设置 → 角色人设」「设置 → 开发者工具」，沿用原项目设置页：左侧分类，右侧居中表单、分区分隔线，手机自动切换为二级页面。

## 给已有本地部署安装

1. 下载本 PR 分支的 ZIP，解压到**另一个文件夹**。原项目、Docker 和网站保持运行。
2. 在刚解压的文件夹双击 `install-web-devtools.cmd`，输入**原项目**的完整目录（其中有你的 `.env`）。
3. 安装器列出用户后，复制你自己账号的 32 位 ID，粘贴并回车。等待 Docker 完成重建。
4. 原地址刷新网页，进入设置。手机/iPad 登录同一个账号，也能使用。

安装器备份原文件，再复制 9 个相关代码文件；只在原 `.env` 添加/更新 `EIDOLON_DEVELOPER_USER`。API 密钥、人设原文件、聊天数据库和此前修改过的 `sessions.py` 不覆盖。Compose 会新增人设文件夹的可写挂载，原 Compose 自定义内容可从备份找回。无需移动原项目或新建数据卷。安装后要还原旧代码可从打印的备份文件夹复制回原位置，再重建。

也可手动合入本分支代码，在原 `.env` 配置 `EIDOLON_DEVELOPER_USER=你的用户ID`，执行 `docker compose up -d --build`。用户 ID 用 `docker compose exec backend eidolon user list` 查看。默认没有授权任何账号；其他账号不会看到入口，直接请求接口也会被拒绝。不要把密钥或 `.env` 上传 GitHub。

## 保存与生效

- **角色人设**：选择角色，编辑 Markdown，点保存。服务端与主机文件同时更新，新回复使用新人设，无需重启。进行中的通话请结束后重拨，建议新建对话验证。人设影响本部署所有用户，不改变独立的世界知识库或检索事实。
- **玩法数据**：可调整自己账号的角色好感度、冷却、礼物库存、抽奖次数（0–7）和重置卡。保存后刷新聊天页查看。修改前结束回复、通话、抽奖或送礼操作，避免并发覆盖。
- **备份**：每次数据修改前自动备份，恢复仅覆盖自己账号的好感度/背包三个表。人设每次保存前也备份；位置为 Docker `eidolon-data` 卷中的 `/data/devtools-backups/sheets/`，可通过 Docker Desktop 取出并粘贴回编辑器。备份不会自动清理。
- 调整数值不会启用尚未配置的判断模型、记忆检索，也不会更改全局概率或自然增长规则。
- 多设备同时编辑同一人设，较旧的版本会收到冲突提示；重新加载页面后再编辑。离开页面前请保存。

原独立 localhost:8766 工具保留为可选入口，使用方法见 [README.md](README.md)，不需要同时启动。

## 验证

后端：`cd backend` 后运行 `uv run pytest -q tests/test_developer_api.py`。
前端：`cd frontend` 后运行 `npm run build`、`npm run test -- --run src/lib/settingsCategory.test.ts` 与 `sh scripts/check-discipline.sh`。
