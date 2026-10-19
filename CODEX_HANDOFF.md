# Codex 交接：个人自部署定制版

## 基准与工作方式

源码仓库：[Schweigen322/eidolon-sc](https://github.com/Schweigen322/eidolon-sc)，上游 Sallyn0225/eidolon-sc。用户于 2026-10-19 上传了本地定制版本，代码基准提交为 `854d427c19eafbf279a98da66f6e2ae8a7c49a11`；本文仅记录交接时已知状态，不替代实时源码、配置与测试结果。

用户在 Windows 的项目目录为：
`C:\Users\19937\OneDrive\Desktop\eidolon-sc-main\eidolon-sc-main`。
主要通过 Docker Compose 运行，电脑、手机、iPad 使用同一服务。请用中文解释，并给出可直接复制的 PowerShell 命令，不要将提示符一起放入代码块，不要混用 CMD 的 `cd /d`。

先遵循根目录 AGENTS.md；修改前端前阅读 frontend/AGENTS.md 与 DESIGN.md。后端逐文件用途见 [backend 文件用途索引](docs/backend-file-guide.zh.md)。

GitHub 同步的是源码。根目录 .env、API 密钥、SQLite 数据库、聊天、长期记忆、好感度和背包运行数据、剧情语料、下载立绘和缩略图没有随本次提交迁移。云端 Codex 不能据此认定本地运行配置或数据正常。继续使用用户原有本地目录、Compose 项目与数据卷；不得通过删除数据库或 `docker compose down -v` 来“修复”问题。

## 用户希望保留的体验

- 网页内开发者工具，可调好感度、库存和角色设定。
- 自定义角色性格、世界观与关系，让回复自然、有上下文，减少反复催睡。
- 用户希望恋人设定下的普通、自愿亲密互动得到合理判断；应检查关系上下文与判断规则的一致性，避免简单一刀切。
- 长期记忆、剧情检索和衣装立绘可正常使用。
- 后续想加入用户、郁田はるき、鈴木羽那的群聊：自动轮流，回应用户话题；也能有限轮数自行开场互动。**目前没有确认已实现，不要当成现成功能。**

## 本次上传实际包含的定制

| 范围 | 已存在的改动 |
| --- | --- |
| backend/src/eidolon/developer_api.py | 内置网页开发者 API，使用指定用户 ID 授权；读取与修改玩法数据、备份恢复、编辑角色设定 |
| backend/src/eidolon/developer_data.py | SQLite 参数校验与修改，修改前备份；恢复限定于指定用户的玩法表，角色文件路径约束 |
| backend/src/eidolon/app.py、config.py | 注册开发者接口并读取相关配置，以及 Tailscale 开发来源配置 |
| backend/src/eidolon/sessions.py、tests/test_sessions.py | 信任明确配置的开发来源、HTTPS 会话 Cookie 与对应测试 |
| backend/src/eidolon/producer.py | 在时间提示中加入减少反复催睡、优先回应当前话题的软规则 |
| backend/src/eidolon/affinity_judge.py | 修改部分越界判断描述；存在下文所述矛盾 |
| characters/sheets/ | 修改 chiyuki、hana、haruki、juri、kiriko、kogane、mamimi、mano、nichika、rinze；部分角色新增大量文本 |
| frontend/src/components/settings/DeveloperSettings.tsx 及设置导航文件 | 网页内开发者工具入口与界面 |
| devtools/、docker-compose.devtools.yml、根目录 cmd 启动器 | 独立本地开发者面板与相关测试、启动和停止方式 |
| frontend/scripts/stand-thumbnails.mts、docker-compose.yml | 缩略图脚本与本地部署相关适配 |

**本次定制提交未修改 engine.py、judge.py、reply_format.py。** 先前讨论过的额外共同提示词、judge.turn_state 关系信息提取等方案，不能认定已经应用。请阅读实际文件后再判断。

内置角色设定编辑接口保存时，会备份原文件并更新后端内存中的角色文本；应在当前回复或通话结束后，用新对话确认效果。独立 devtools 面板的文件编辑路径不同，其 README 要求保存后重启后端，不要混淆两种行为。玩法数据修改前会创建数据库备份，备份含个人数据，应留在本地。

独立 devtools 面板默认绑定 localhost:8766，含来源和请求令牌检查；不要把它随意代理到外网。内置页面依赖 `EIDOLON_DEVELOPER_USER` 的指定用户授权。现有授权设计应在后续审查中实际验证。

## 本地运行与配置

沿用仓库 README 与配置文档；不要为了云端测试复制用户真实密钥。backend/pyproject.toml 声明 Python >=3.11，当前类型检查目标为 3.11。前端脚本直接运行 .mts，使用支持该方式的 Node（项目部署文档要求应再次核对，建议按现有容器版本对齐）。

在项目根目录 PowerShell 中：
```powershell
docker compose up -d --build
docker compose ps
docker compose logs --tail 100 backend
```

后端代码变更后：
```powershell
docker compose up -d --build backend
```

.env 内容变更后需要重建容器配置，仅 restart 不会重新载入容器环境变量：
```powershell
docker compose up -d --force-recreate backend frontend
```

服务名应以当前 docker-compose.yml 为准。不要在运行剧情同步、下载或渲染任务时无提示重建相关进程。

### Tailscale 与移动设备

已使用 Tailscale Serve 将 HTTPS 根路径代理到 localhost:3000。访问设备需要连接同一 tailnet。自定义开发来源配置示意如下，域名替换为实际设备域名：
```dotenv
EIDOLON_DOMAIN=
EIDOLON_DEV_LOGIN=1
EIDOLON_DEV_ORIGIN=https://<machine>.<tailnet>.ts.net
EIDOLON_DEVELOPER_USER=<32位十六进制用户ID>
```

用户 ID 不是昵称，可用 `docker compose exec backend eidolon user list` 查看。不要直接提交实际 .env。配置 EIDOLON_DOMAIN 同时开启 EIDOLON_DEV_LOGIN=1 时，后端会拒绝启动；此前导致过登录 500。开发登录允许冒充用户，只适用于受控的个人开发环境，不应作为公开部署的登录方案。

本次新增配置尚未同步到 .env.example 的情况需要后续检查并补文档，不要假定示例已经完整。

麦克风需要安全上下文。普通手机局域网 HTTP IP 地址不能代替 HTTPS。Tailscale HTTPS 可解决页面安全上下文问题，但并不保证 WebRTC 音频媒体路径可用。

### 衣装资源

用户已下载约 2192 套资源并生成衣装清单与缩略图。实际运行目录整理到：
- corpus/stand/source
- corpus/stand/outfits
- corpus/stand/webroot

这些产物不在仓库中。曾误生成到 backend/source 和 backend/outfits，不能看到仓库中没有这些文件就重新下载全部资源。

本地资源服务在项目根目录启动：
```powershell
npx.cmd --yes http-server .\corpus\stand\webroot -p 8765 --cors
```

移动端 HTTPS 页面也需要能访问的 HTTPS 资源地址。先前方案是另开 Tailscale HTTPS 8443 代理资源端口：
```powershell
tailscale serve --https=8443 --bg http://localhost:8765
```

然后配置 EIDOLON_STAND_ASSETS_URL 为对应 HTTPS 8443 地址；核对前后端如何消费变量，按需重新创建或构建容器。仅电脑能打开 localhost 资源不代表手机能读到。favicon.ico 的 404 不能据此认定衣装加载失败。

## 待核实的问题

1. **关系判断规则不一致。** affinity_judge.py 的场景文字允许部分角色处于恋人关系，但越界问题描述、判 true 和判 false 的标准对性相关内容存在互相矛盾的表述。原有 judge.turn_state 的上下文有限，未确认注入完整关系设定。应先用代表性输入和测试确认误判来源，再统一规则；同步检查 affinity.py 的阶段态度与角色设定是否冲突。
2. **催睡只有软规则。** producer.py 已加入减少重复提醒、尊重继续聊天的意愿等规则，没有实现每晚计数或硬性冷却。
3. **角色文本体积与优先级。** hana、haruki、kiriko 等文件较大。应检查实际提示拼装、冲突和 token 开销，保留用户自定义内容，不要未经说明大幅压缩覆盖。
4. **iPad 通话中断后无转写。** 曾经通话正常，之后 Chrome/Safari 都出现收不到声音；麦克风指示灯亮、系统备忘录可录音，电脑通话正常。已有日志显示连接后 No audio frame received，但未确认原因。需要分别检查浏览器音轨、音频中断、ICE/媒体路径与服务端接收；不能认定已经证明 STT 额度或 TURN 是原因。用户提出重启 iPad，但没有后续成功记录。
5. **剧情同步与长期记忆。** 剧情同步曾因向量服务 429 TPM 中断，也曾出现同时运行两个同步进程；完整导入与检索效果未确认。不要同时启动重复同步，也不要未经估算执行全库重新向量化。记忆页曾为空，不能凭配置变量存在就宣布记忆已工作。
6. **模型与付费状态不能从 git 确认。** 用户报告使用云端 DeepSeek 和 Fish Audio，曾配置 Jev；具体型号、端点、余额和实时成功调用需要读取脱敏配置或日志后确认。不要将历史口头型号当成当前 .env 事实。生图也未确认实际成功。
7. **群聊尚待实现。** 先审查会话、消息模型与记忆归属，再讨论轮流、角色彼此可见上下文、用户插话、停止条件和费用；不得无限自动生成。

## 验证方式

本次 GitHub 上传核对了提交和文件清单，未在交接过程中运行整套应用测试，不宣称定制版全部通过。

后端在 backend 目录安装锁定依赖后，按改动运行相关 pytest，再运行代码检查：
```powershell
uv sync --frozen
uv run pytest tests/test_sessions.py
uv run ruff check src tests
uv run pyright
```

提示词、好感度、档案或开发者工具改动，应从 tests 中选实际对应测试，并增加有区分能力的回归用例。独立面板测试从项目根目录运行：
```powershell
python -m unittest discover -s devtools -p "test_*.py"
```

前端在 frontend 目录：
```powershell
npm.cmd ci
npm.cmd run test
npm.cmd run typecheck
npm.cmd run build
```

区分离线单元测试、需启动本地服务的浏览器测试与会调用收费 API 的在线评测；先读相关测试/评测说明，避免误启动大量付费调用。报告哪些验证实际执行、哪些未执行以及原因。数据库变更要有可回退备份；新的云环境没有用户本机数据库，不能伪称验证了用户数据。

## 建议的首个 Codex 任务

阅读 AGENTS.md、本文与后端索引，审查现有开发者工具和角色关系判断的实现，先给出可复现问题、对应文件及最小修改建议。基于用户选择处理具体问题；保留已上传的角色设定，避免把所有未来需求一次性改写进系统。

## 最近工作

### 2026-10-20：补记此前 Codex 工作，开始主动消息整合前保存现场

- 本节记录晚于上文的历史基准；当前本地 main 已有 Claude 的 `2bf4bf0e`、`583e3d4d`、`427e5070`，其中包含双方此前成果。后续行为以实际源码、提交和 `CLAUDE_HANDOFF.md` 为准。
- 提示词：修正 `backend/src/eidolon/affinity_judge.py` 的越界描述矛盾；为羽那、はるき、霧子、恋鐘及摩美々、にちか、千雪、結華、凛世补充具体接话示例，保留个性、已有关系和年龄边界；霧子省略号未统一改写。文件为对应 `characters/sheets/*.md`。Claude 后续二创刻画和好感误罚调整已包含在上述提交中，不将其误记为 Codex 独立完成。
- 用户背景：`store.py`、`engine.py`、`tests/test_producer_context.py` 支持每用户共享及角色专属背景，每轮注入；实际私人设定仅存本机数据库，未提交到源码。加入地道日语练习与先纠错再正常回复的偏好；排名未导入。Claude 后续新增的通话练习暂停、字幕隐藏等以其交接为准。
- 主动消息：`proactive.py`、`app.py`、`assembly.py`、`database.py`、`store.py`、`engine.py` 及 `tests/test_proactive.py`，前端 `ProactiveSettings.tsx`、设置入口、列表、轮询、API 和相关测试，实现默认关闭、选角色、固定间隔、每日尝试上限、安静时段、时区、未回复不追发、活跃避让及发送前复核。说明见 `docs/proactive-messages.zh.md`。当时后端相关组 41 项通过（另排除一项原有 developer_data 直接连接数据库纪律问题），前端相关组 215 项通过；完成桌面/移动构建版 Playwright 验收并清理临时验收脚本。
- 名字容错：`name_recognition.py`、`judge.py`、`engine.py`、`hot_words.py`、`tests/test_name_recognition.py`、`tests/test_affinity_turns.py` 及 `docs/name-recognition.zh.md`，覆盖晴樹/晴树、花、桐子、小金等已确认变体。纯称呼评分保护与上下文提示分开，原话保留，未整体放宽其他内容判断；补充名字读音热词。该次相关离线测试 41 项通过，ruff/pyright 通过。
- 以上代码当时均已按授权构建部署并核对健康及数据数量；部署前 SQLite 备份保存在原数据卷的 `/data/profile-import-backups/`、`/data/feature-backups/`。曾按用户要求用はるき执行一次真实主动消息测试，已成功入库；未进行付费批量评测。历史测试结果不代表本轮新代码已验证。40 轮通话上限未改，10 分钟配置是否取消仍需实际核对。
- 语音无声报告已由用户取消排查，未就此修代码。游戏剧情工作原理和二创学习方案仅作解释，没有因此导入新剧情或实现二创检索库。
- 本轮动手前仍有 `.gitignore` 的忽略项和 `apply-changes.cmd`、`auto-apply-watcher.cmd` 未提交；按用户“先检查并保存”要求，已将完整差异及两个文件复制到本机临时目录 `eidolon-before-proactive-20261020-073101`，原文件原样保留，不将临时脚本提交。本次只补记交接，未变更应用代码或重启；下一步整合自然搭话与固定间隔，保留一套调度器，不整体合并上游。
