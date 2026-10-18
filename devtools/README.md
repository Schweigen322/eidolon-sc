# 本机开发者工具

在自己的项目副本上调整好感度、礼物背包、抽奖次数、重置卡及角色人设。不需要 Windows 安装 Python；通过 Docker 启动独立工具。

## 安装与启动

把本分支新增的 `devtools/` 文件夹、`docker-compose.devtools.yml`、`start-devtools.cmd`、`stop-devtools.cmd` 和 `restart-backend.cmd` 放到你现有的项目根目录。保留原来的 `.env`、`characters/` 和 Compose 项目目录，避免换一个目录后连到新的数据卷。

先运行原项目并登录一次，再双击 `start-devtools.cmd`。等待首次下载 Python 镜像，打开 http://localhost:8766 。如果打开过早，几秒后刷新。必须使用 localhost 或 127.0.0.1。

先选用户、角色，修改后点保存；数据库修改马上生效，聊天页面需刷新。请在没有进行中通话、回复和送礼时修改。抽奖次数保持原玩法的 0–7，上调库存不改变自然发放规则。

人设保存会修改主机 `characters/sheets/` 中的对应文件，并在 Docker 数据卷中自动备份原内容。保存后双击 `restart-backend.cmd`，再新建对话测试。此启动器仅重启后端，不会自动编辑 `.env`。

停止工具双击 `stop-devtools.cmd`。它不停止聊天项目。

## 限制与恢复

- 修改数值不启用好感度功能。原项目仍需配置 Jev 或 Cloudflare 判断模型；同时满足检索依赖后才能使用长期记忆。
- 工具只发布到电脑的 127.0.0.1，另外检查 Host、Origin 和随机请求令牌。不要通过 Tailscale Serve 或其他代理公开这个工具。
- 每次数据修改前用 SQLite 在线备份保存完整数据库；恢复按钮仅恢复所选用户的三个玩法表，不覆盖聊天、配置、其他用户。
- 完整备份位于同一个数据卷的 `/data/devtools-backups`，包含私人数据。人设备份在其 `sheets/` 子目录，可通过 Docker Desktop 查看卷文件并取出。备份不会自动删除，注意磁盘容量。
- 当前版本不修改服务密钥、模型地址、全局概率和玩法规则，也不解除原项目中的功能依赖。
- 来源许可及角色权利沿用原仓库。

## 验证

`python -m unittest discover -s devtools -p 'test_*.py'`
