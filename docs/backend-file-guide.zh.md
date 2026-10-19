# backend 文件用途索引

以源码提交 `854d427c19eafbf279a98da66f6e2ae8a7c49a11` 为基准，共 **256 个受 Git 跟踪的 backend 文件**：101 个 src 文件、142 个测试及测试数据文件、13 个其他文件。本表按文件职责整理，不代表每个文件都经过完整审计，也不代表相关测试已运行通过。

先读根目录 [AGENTS.md](../AGENTS.md) 和 [CODEX_HANDOFF.md](../CODEX_HANDOFF.md)。角色设定在根目录 `characters/sheets/`，前端在 `frontend/`，服务密钥通常在未提交的根目录 `.env`。

## 建议阅读顺序

| 想调整的行为 | 先看 |
| --- | --- |
| 角色共同规则、回复行为 | engine.py、reply_format.py、producer.py，再看角色设定 |
| 好感度变化和判断 | affinity.py、affinity_judge.py、judge.py |
| 长期记忆 | 下方“记忆与检索”组，并检查实际配置、日志和数据库 |
| 网页开发者工具 | developer_api.py、developer_data.py，以及 frontend 中 DeveloperSettings.tsx |
| 通话、麦克风、语音生成 | 下方“语音通话”组；浏览器输入、媒体连接、STT、TTS 要分别定位 |
| 启动、环境变量、路由 | __main__.py、config.py、app.py |

## 构建与工具

| 文件 | 作用 |
| --- | --- |
| [.dockerignore](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/.dockerignore) | 排除无需进入 Docker 构建上下文的本地文件，减小构建输入。 |
| [.gitignore](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/.gitignore) | 列出 backend 目录中不应提交到 Git 的生成文件。 |
| [.python-version](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/.python-version) | uv 等工具使用的 Python 版本声明：当前为 3.11。 |
| [Dockerfile](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/Dockerfile) | 构建后端镜像，安装 uv 与锁定依赖、复制 src/eval，设置容器数据库与素材路径并启动 eidolon。 |
| [pyproject.toml](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/pyproject.toml) | Python 项目元数据、依赖、eidolon 命令入口，以及 pytest、ruff、pyright 等工具配置。 |
| [scripts/photo_tags.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/scripts/photo_tags.py) | 维护者脚本：查询标签建议并生成照片标签词表；运行时照片流程读取其生成的 JSON。 |
| [uv.lock](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/uv.lock) | uv 生成的精确依赖锁定文件，用于复现安装版本；一般随依赖管理命令更新。 |

## 评测数据

| 文件 | 作用 |
| --- | --- |
| [eval/judge.toml](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/eval/judge.toml) | 判断模型的标注评测样例：检索、好感度、越界、照片、情绪等判断场景。 |
| [eval/memory-baseline.json](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/eval/memory-baseline.json) | 已保存的记忆评测基线结果，供新评测对照；不保存实际部署的用户长期记忆。 |
| [eval/memory.toml](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/eval/memory.toml) | 记忆提炼、更新和召回的标注评测案例。 |
| [eval/rerank-calibration.toml](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/eval/rerank-calibration.toml) | 重排阈值校准的问题、候选与相关性标注。 |

## 启动与配置

| 文件 | 作用 |
| --- | --- |
| [src/eidolon/__init__.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/__init__.py) | Python 包入口标记；本版本为空，没有独立业务逻辑。 |
| [src/eidolon/__main__.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/__main__.py) | eidolon 命令行入口：启动服务，管理用户，导入/同步剧情与世界观，处理立绘、备份、恢复和评测。 |
| [src/eidolon/app.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/app.py) | 创建 FastAPI 应用并注册主要 HTTP 接口；把网页的聊天、角色、档案、记忆、通话等请求交给业务模块。 |
| [src/eidolon/assembly.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/assembly.py) | 根据配置组装数据库、角色、模型、检索、记忆、好感度和通话服务；决定功能启用条件并管理启动、关闭。 |
| [src/eidolon/clock.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/clock.py) | 统一提供当前时间，测试时可以替换时钟。 |
| [src/eidolon/config.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/config.py) | 读取和校验环境变量，定义各类服务配置、默认模型、开关、限额和路径。 |
| [src/eidolon/live_config.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/live_config.py) | 合并 .env 与管理后台覆盖值，管理可运行时修改的配置、模型切换和客户端租用。 |
| [src/eidolon/randomness.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/randomness.py) | 统一提供随机数来源，抽奖等功能使用；测试时可以替换。 |
| [src/eidolon/service_clients.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/service_clients.py) | 创建部署者使用的聊天、后台和判断等服务客户端，并配合动态配置替换、释放连接。 |

## 账号与会话

| 文件 | 作用 |
| --- | --- |
| [src/eidolon/account_api.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/account_api.py) | 开发登录、OAuth 登录回调、退出、账号设置及绑定登录方式等接口。 |
| [src/eidolon/accounts.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/accounts.py) | 用户与外部身份的对应规则、注册和登录资格、封禁及删除账号后的身份处理。 |
| [src/eidolon/admission.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/admission.py) | 统一控制对话/通话开始前的冷却、服务租用、密钥选择和限额占用，并在结束后结算。 |
| [src/eidolon/identity.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/identity.py) | GitHub、Google OAuth 适配，生成授权地址并通过授权码获取外部身份。 |
| [src/eidolon/own_keys.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/own_keys.py) | 验证和使用用户自带 LLM、后台模型、STT、TTS 与生图密钥，选择本轮密钥来源及限额豁免，不静默回退。 |
| [src/eidolon/sessions.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/sessions.py) | 登录 Cookie、会话续期与跨站请求来源校验；此前“请求来自其他网站，已拒绝”的提示来自这里。 |
| [src/eidolon/usage.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/usage.py) | 每用户滑动小时限额、用量记录、失败返还以及自带密钥豁免规则。 |

## 数据与管理

| 文件 | 作用 |
| --- | --- |
| [src/eidolon/activity.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/activity.py) | 记录单轮、通话及外部服务调用的结果、耗时、用量和判断数据，为后台统计提供依据。 |
| [src/eidolon/admin_api.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/admin_api.py) | 管理员接口的公共入口与权限检查；未授权用户访问通常表现为 404。 |
| [src/eidolon/admin_backup_api.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/admin_backup_api.py) | 后台备份状态、历史与立即发起备份等接口。 |
| [src/eidolon/admin_config_api.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/admin_config_api.py) | 后台配置读取、修改、恢复 .env 默认及密钥掩码等 HTTP 接口。 |
| [src/eidolon/admin_prices_api.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/admin_prices_api.py) | 后台模型价格查询、手动定价和刷新价格目录等接口。 |
| [src/eidolon/admin_users_api.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/admin_users_api.py) | 后台用户列表、详情、封禁/解封、删除和个人用量/限额等管理接口。 |
| [src/eidolon/announcements.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/announcements.py) | 公告草稿、发布、撤回、编辑及删除的数据库业务逻辑。 |
| [src/eidolon/announcements_api.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/announcements_api.py) | 管理员编辑公告和普通用户获取已发布公告的 HTTP 接口。 |
| [src/eidolon/billing.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/billing.py) | 接收服务自身报告的 token、缓存命中等计费用量，并传给活动记录；不会实际扣款或充值。 |
| [src/eidolon/dashboard.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/dashboard.py) | 汇总后台看板的运行记录、调用量、错误、好感度判断及相关使用情况。 |
| [src/eidolon/database.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/database.py) | 统一打开 SQLite，维护各表的数据归属与删除/匿名化规则，以及安全删除用户或历史对话的公共机制。 |
| [src/eidolon/developer_api.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/developer_api.py) | 网页内开发者工具 API：按指定用户 ID 授权，读取和修改好感度、礼物库存与抽取资源；备份、恢复及编辑角色设定，并更新内存中的角色文本。 |
| [src/eidolon/developer_data.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/developer_data.py) | 开发者工具的数据层：校验参数，对现有 SQLite 中指定用户的游戏数据执行修改；修改前备份，支持限定范围恢复，并约束角色设定路径。 |
| [src/eidolon/price_catalog.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/price_catalog.py) | 获取 models.dev、OpenRouter 的价格与模型信息，用于后台费用估算和能力提示。 |
| [src/eidolon/prices.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/prices.py) | 管理服务价格默认值、目录价格和管理员覆盖值，供费用估算；不会改变服务商真实账单。 |
| [src/eidolon/stats.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/stats.py) | 用户自己的聊天、通话、礼物、认识天数、活跃日期与好感度档位统计。 |
| [src/eidolon/store.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/store.py) | 用户、会话、档案、聊天、事件、照片和通话记录等关系数据存储；记忆和限额另有模块。 |

## 判断与好感度

| 文件 | 作用 |
| --- | --- |
| [src/eidolon/affinity.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/affinity.py) | 好感度数值、档位、每日上涨上限、恢复、冷却、警告与主动结束规则；生成相关态度提示。 |
| [src/eidolon/affinity_judge.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/affinity_judge.py) | 定义好感度五档评分、越界和操纵判断问题及标准，并把模型概率转换成判断结果。 |
| [src/eidolon/emotion.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/emotion.py) | 逐段判断通话回复的情绪、点头或摇头，用于立绘表情与动作。 |
| [src/eidolon/gift_catalog.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/gift_catalog.py) | 读取并校验礼物目录、稀有度与角色喜欢的礼物配置。 |
| [src/eidolon/gifts.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/gifts.py) | 每日抽奖机会、抽取概率、礼物背包、赠送、好感度奖励及重置卡等业务逻辑。 |
| [src/eidolon/gifts_api.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/gifts_api.py) | 礼物目录、背包、抽奖、赠送、使用重置卡和管理员发卡等 HTTP 接口。 |
| [src/eidolon/judge.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/judge.py) | 封装判断服务协议和模型阈值，组织判断输入；原版 turn_state 提供角色名、最近四条消息与最新用户话语。 |

## 维护与评测

| 文件 | 作用 |
| --- | --- |
| [src/eidolon/backup.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/backup.py) | 一致性复制 SQLite，检查、压缩、age 加密并上传备份，清理过期备份并记录运行状态。 |
| [src/eidolon/judge_eval.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/judge_eval.py) | eidolon eval judge：用标注样例评估检索、好感度、照片和情绪判断及阈值效果。 |
| [src/eidolon/memory_eval.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/memory_eval.py) | eidolon eval memory：评估记忆提炼、更新、召回等能力，使用隔离的测试数据库。 |
| [src/eidolon/proxy.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/proxy.py) | 按服务和配置决定哪些外部请求走代理、哪些直连，支持管理员运行时调整。 |
| [src/eidolon/rerank_eval.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/rerank_eval.py) | eidolon eval rerank：用标注问题校准候选资料的重排分数与筛选阈值。 |
| [src/eidolon/restore.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/restore.py) | 检查并恢复已解密的数据库备份，处理原数据库、WAL 和中断的备份任务记录。 |
| [src/eidolon/retry.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/retry.py) | 外部请求短暂失败时的有限重试规则，避免无限等待。 |
| [src/eidolon/s3.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/s3.py) | S3 兼容存储访问与签名，支持素材、语音和备份对象的列举、上传与删除。 |

## 语音通话

| 文件 | 作用 |
| --- | --- |
| [src/eidolon/bailian.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/bailian.py) | 阿里云百炼/DashScope 实时语音识别适配：音频分包、识别结果、地域试探、热词和静音保活。 |
| [src/eidolon/call.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/call.py) | WebRTC 信令与通话生命周期；串接语音识别、对话引擎、Fish Audio 合成、字幕、表情及通话控制。 |
| [src/eidolon/call_outcome.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/call_outcome.py) | 通话接通、失败、超时、冷却或挂断等结局与限额、时长、运行记录的结算。 |
| [src/eidolon/delivery_cues.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/delivery_cues.py) | 解析并过滤配音语气标记，使界面显示的台词与送去合成的内容各取所需。 |
| [src/eidolon/hot_words.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/hot_words.py) | 从角色、中文名、读音和世界观生成语音识别热词，减少人物名和组合名识别错误。 |
| [src/eidolon/reading_draft.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/reading_draft.py) | 生成/补齐读音配置草稿，借助 pyopenjtalk 生成音素供人工检查。 |
| [src/eidolon/readings.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/readings.py) | 读取姓名与专有名词读音，构造 Fish Audio 发音词典，保留显示文本的原始写法。 |
| [src/eidolon/turn_taking.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/turn_taking.py) | 通话轮次状态机：用户补充、打断、角色说话、停止播放与只看文字等行为规则。 |
| [src/eidolon/windows_udp.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/windows_udp.py) | 修补 Windows 原生 Python 3.11/3.12 的 UDP 关闭问题，避免 ICE 连接关闭卡住；Docker 内 Linux 不走此 Windows 修补。 |

## 对话与提示词

| 文件 | 作用 |
| --- | --- |
| [src/eidolon/characters.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/characters.py) | 读取 characters.toml 和角色人设等文件，校验角色配置，提供角色列表、头像、音色和立绘等元数据。 |
| [src/eidolon/engine.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/engine.py) | 组织一轮文字或语音对话：读取状态、判断与检索、拼提示词、调用模型和工具、解析并保存回复。 |
| [src/eidolon/producer.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/producer.py) | 用户称呼、性别、生日与时区档案；生成制作人背景及每轮当前时间、文字/通话状态提示。 |
| [src/eidolon/reply_format.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/reply_format.py) | 定义日语和中文字幕、回复长度、情绪配音提示；流式解析标签、文字、语音与照片事件。 |
| [src/eidolon/titles.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/titles.py) | 使用后台模型，根据对话初期内容异步生成历史对话标题；标题不作为角色记忆。 |
| [src/eidolon/turn_outcome.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/turn_outcome.py) | 记录单轮成功、失败、取消等结局，决定这一轮如何结算活动记录和限额。 |

## 记忆与检索

| 文件 | 作用 |
| --- | --- |
| [src/eidolon/corpus.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/corpus.py) | 剧情正文、剧集目录及其向量索引的存取和查询。 |
| [src/eidolon/embedded_texts.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/embedded_texts.py) | 缓存来自配置文件的文本向量，按范围、文本内容和模型区分，供角色与作品资料检索。 |
| [src/eidolon/embedding.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/embedding.py) | 调用硅基流动 Qwen3 或 Google Gemini 向量化接口，把查询、剧情和记忆转成向量。 |
| [src/eidolon/facts.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/facts.py) | 把角色资料文件作为可检索参考来源，与角色每轮必读的人设文件分开。 |
| [src/eidolon/memory.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/memory.py) | 后台抽取用户事实、保存长期记忆、处理事实更新/取代、检索和删除；同一用户不同角色共享记忆并区分来源。 |
| [src/eidolon/reembed.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/reembed.py) | 更换向量服务、模型或维度后，用已有正文重新生成剧情、资料及记忆向量，无需重新下载剧情。 |
| [src/eidolon/references.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/references.py) | 定义剧情、角色资料、作品资料这些检索来源的统一接口与结果结构。 |
| [src/eidolon/rerank.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/rerank.py) | 调用硅基流动重排模型，对候选文本重新打分并提供筛选阈值。 |
| [src/eidolon/retrieval.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/retrieval.py) | 判断本轮是否需要检索，将剧情、角色资料、作品资料和用户记忆组织为回复上下文，并实现回忆剧情工具。 |
| [src/eidolon/work_facts.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/work_facts.py) | 把歌曲、唱片、演出日期等作品事实变成所有角色共享的检索来源。 |

## 照片与立绘

| 文件 | 作用 |
| --- | --- |
| [src/eidolon/greetings.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/greetings.py) | 合成角色招呼等配置语音并上传素材存储，避免重复生成已有音频。 |
| [src/eidolon/image_generation.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/image_generation.py) | 调用 NovelAI 官方或 OpenAI 图像兼容接口，校验返回图片并转换为照片存储格式。 |
| [src/eidolon/photo_judge.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/photo_judge.py) | 定义用户是否明确要求照片的判断问题，并按阈值解析判断结果。 |
| [src/eidolon/photo_prompt.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/photo_prompt.py) | 解析角色写出的照片标签，结合固定外貌和画风生成生图提示词，并规范化、过滤标签。 |
| [src/eidolon/photo_tags.json](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/photo_tags.json) | 运行时本地照片标签词表：已知标签、写法改写、允许项和过滤项，由 scripts/photo_tags.py 生成。 |
| [src/eidolon/photos.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/photos.py) | 决定本轮能否发照片，构造照片提示，处理排队、生成、状态、限额和保存等生命周期。 |
| [src/eidolon/photos_api.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/photos_api.py) | 查询照片生成状态及读取已生成图片的 HTTP 接口，检查所属用户权限。 |
| [src/eidolon/stand_fetch.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/stand_fetch.py) | eidolon stand fetch：从 ShinyColorsDB 下载衣装 Spine 数据、纹理和清单，保留已成功下载内容。 |
| [src/eidolon/stand_outfits.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/stand_outfits.py) | eidolon stand outfits：整理每角色卡片和私服/演出服清单，过滤缺文件及重复衣装，写 outfits JSON。 |
| [src/eidolon/stand_upload.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/stand_upload.py) | 把立绘资源、缩略图和衣装清单增量上传到 S3 兼容存储；缩略图实际渲染脚本位于 frontend。 |

## 世界观与同步

| 文件 | 作用 |
| --- | --- |
| [src/eidolon/live_sync.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/live_sync.py) | 同步演出及各演出日的出演者，核对缺席等来源信息。 |
| [src/eidolon/mirror.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/mirror.py) | 访问 ShinyColorsDB 的剧本、卡片和立绘 API/CDN，供剧情同步及立绘下载使用。 |
| [src/eidolon/release_sync.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/release_sync.py) | 同步唱片发行和歌曲信息，从发行网站及补充来源整理演唱成员等数据。 |
| [src/eidolon/roster.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/roster.py) | 把不同来源的人物、声优和组合名字对应到统一人物与组合列表。 |
| [src/eidolon/script_cache.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/script_cache.py) | 维护下载剧本与镜像元数据缓存，决定哪些需要重下，哪些可直接复用。 |
| [src/eidolon/setlist_sync.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/setlist_sync.py) | 同步演出日歌单和各曲演唱成员，整理翻唱、共同出演等情况。 |
| [src/eidolon/sheet_draft.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/sheet_draft.py) | 根据剧情库用后台模型生成角色人设草稿；材料过长时分批做笔记，保留人工审核标记。 |
| [src/eidolon/story_import.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/story_import.py) | 解析剧情 CSV/JSON，识别剧本编号、出场角色和标题；处理译文替换原文及应排除的分支。 |
| [src/eidolon/story_sync.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/story_sync.py) | eidolon story sync：先导入汉化剧情，再补齐镜像原文剧情，利用缓存续做并报告进度与失败。 |
| [src/eidolon/sync_tools.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/sync_tools.py) | 世界观同步模块共用的抓取、文本和读音规范化等工具。 |
| [src/eidolon/world.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/world.py) | 加载事务所、组合、人物、歌曲和演出等世界观数据，生成与当前角色和日期有关的提示与作品条目。 |
| [src/eidolon/world_sync.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/world_sync.py) | eidolon world sync 总流程：汇集人物、组合、发行、歌曲和演出数据，写入世界观文件并报告差异。 |

## 模型接口

| 文件 | 作用 |
| --- | --- |
| [src/eidolon/llm/__init__.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/llm/__init__.py) | 定义统一的模型消息、流式输出、工具调用、推理事件及模型组合接口。 |
| [src/eidolon/llm/anthropic.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/llm/anthropic.py) | 适配 Anthropic Messages 协议，转换消息、工具、流式事件等。 |
| [src/eidolon/llm/openai_compat.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/llm/openai_compat.py) | 适配 OpenAI 兼容 Chat Completions 协议，可连接 DeepSeek 等兼容服务。 |
| [src/eidolon/llm/providers.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/llm/providers.py) | 按配置选择协议适配器，并检查聊天模型是否支持项目需要的流式回复和工具调用。 |
| [src/eidolon/llm/responses.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/llm/responses.py) | 适配 OpenAI Responses 协议，处理文本、推理与工具调用事件。 |
| [src/eidolon/llm/sse.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/src/eidolon/llm/sse.py) | 读取模型服务返回的 SSE 流，拆分事件并解析 JSON。 |

## 测试辅助

| 文件 | 作用 |
| --- | --- |
| [tests/__init__.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/__init__.py) | 测试包标记；本版本为空。 |
| [tests/browser.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/browser.py) | 测试用 WebRTC 浏览器模拟器：提供静音麦克风和 RTVI 数据通道，连接真实后端。 |
| [tests/conftest.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/conftest.py) | pytest 共用准备环境、临时数据库、角色配置、客户端工厂和测试夹具。 |
| [tests/fakes.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/fakes.py) | 外部模型、判断、向量化、语音、时钟及存储等服务的测试替身，避免测试依赖真实付费服务。 |
| [tests/stories.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/stories.py) | 生成符合汉化仓库和原文格式的样例 CSV/JSON 剧情，用于导入与同步测试。 |

## 测试录制数据

| 文件 | 作用 |
| --- | --- |
| [tests/recordings/anthropic_text.sse](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/recordings/anthropic_text.sse) | 录制的 Anthropic 格式普通文本流，供协议适配器测试重放。 |
| [tests/recordings/anthropic_thinking_tool.sse](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/recordings/anthropic_thinking_tool.sse) | 录制的 Anthropic 格式推理与工具调用流，验证推理和对话文本的分离。 |
| [tests/recordings/anthropic_tool.sse](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/recordings/anthropic_tool.sse) | 录制的 Anthropic 格式工具调用流。 |
| [tests/recordings/models_dev.json](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/recordings/models_dev.json) | 模型目录接口的录制样本，供价格、能力和思考强度提示测试。 |
| [tests/recordings/responses_reasoning_tool.sse](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/recordings/responses_reasoning_tool.sse) | 录制的 Responses 格式推理与工具调用流。 |
| [tests/recordings/responses_text.sse](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/recordings/responses_text.sse) | 录制的 Responses 格式普通文本流。 |
| [tests/recordings/responses_tool.sse](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/recordings/responses_tool.sse) | 录制的 Responses 格式工具调用流。 |

## 测试

| 文件 | 作用 |
| --- | --- |
| [tests/test_activity_records.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_activity_records.py) | 验证：文字回合及外部服务调用的运行记录、耗时、用量与后台汇总。 |
| [tests/test_admin_backups.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_admin_backups.py) | 验证：后台备份状态、历史、异常提示与手动发起备份。 |
| [tests/test_admin_commands.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_admin_commands.py) | 验证：命令行列用户、封禁/解封、查询用量以及封禁后的会话处理。 |
| [tests/test_admin_delete_user.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_admin_delete_user.py) | 验证：管理员删除普通用户、清理数据与保留被封禁身份的限制。 |
| [tests/test_admin_entry.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_admin_entry.py) | 验证：管理员身份识别、后台访问权限和未授权访问的 404。 |
| [tests/test_admin_users.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_admin_users.py) | 验证：后台用户搜索、详情、封禁/解封及隐私边界。 |
| [tests/test_admission.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_admission.py) | 验证：回合和通话开始、租用服务、选择密钥、限额占用与结算。 |
| [tests/test_affinity.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_affinity.py) | 验证：好感度初值、档位、时间恢复与不同用户/角色之间的隔离。 |
| [tests/test_affinity_cooldown.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_affinity_cooldown.py) | 验证：好感度归零进入冷却、拒绝新对话及恢复后的解冻。 |
| [tests/test_affinity_dashboard.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_affinity_dashboard.py) | 验证：后台好感度判断、越界/操纵和冷却等聚合统计。 |
| [tests/test_affinity_prompt.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_affinity_prompt.py) | 验证：当前好感度档位及本轮判断如何写入角色态度提示。 |
| [tests/test_affinity_stats.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_affinity_stats.py) | 验证：用户统计中按好感度档位展示角色的行为。 |
| [tests/test_affinity_turns.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_affinity_turns.py) | 验证：对话判断如何实际增减好感度，包含每日上涨上限与特殊处罚。 |
| [tests/test_announcements.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_announcements.py) | 验证：公告草稿、发布、编辑、撤回、删除和用户读取。 |
| [tests/test_assembly.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_assembly.py) | 验证：不同配置与服务组合下，组装流程启用/禁用哪些功能。 |
| [tests/test_backup.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_backup.py) | 验证：备份一致性、压缩加密、上传、保留期清理及任务互斥。 |
| [tests/test_bailian_stt.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_bailian_stt.py) | 验证：模拟真实 WebSocket 的百炼识别协议、音频分包、地域与错误处理。 |
| [tests/test_call.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_call.py) | 验证：使用真实 WebRTC 连接、模拟外部模型的端到端通话。 |
| [tests/test_call_emotions.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_call_emotions.py) | 验证：通话逐段情绪和动作判断及发送给浏览器的事件。 |
| [tests/test_call_hot_words.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_call_hot_words.py) | 验证：为通话生成识别热词，并按不同识别服务传入。 |
| [tests/test_call_outcome.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_call_outcome.py) | 验证：接通/失败/结束、限额返还、结束原因和通话记录的结算。 |
| [tests/test_call_photos.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_call_photos.py) | 验证：通话中请求并生成照片，处理异步照片状态通知。 |
| [tests/test_call_records.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_call_records.py) | 验证：通话、内部回合及 STT/TTS/情绪服务的运行记录。 |
| [tests/test_call_stats.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_call_stats.py) | 验证：已接通通话的次数、时长和时间区间统计。 |
| [tests/test_call_turns.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_call_turns.py) | 验证：语音识别结果、通话中输入文字和回复的轮次流程。 |
| [tests/test_characters.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_characters.py) | 验证：角色配置读取、校验、人设、头像、背景、立绘和招呼等接口。 |
| [tests/test_cloudflare_judge.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_cloudflare_judge.py) | 验证：Cloudflare Workers AI 判断模型的协议、配置和启动检查。 |
| [tests/test_consent.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_consent.py) | 验证：新用户同意条款、年龄声明和同意前的功能权限。 |
| [tests/test_conversation_events.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_conversation_events.py) | 验证：聊天以外的对话事件如何保存、排序、显示及进入模型上下文。 |
| [tests/test_conversation_history.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_conversation_history.py) | 验证：每轮发送给模型的历史消息范围与截取规则。 |
| [tests/test_conversation_summaries.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_conversation_summaries.py) | 验证：对话列表每角色最后一句和时间的摘要接口。 |
| [tests/test_conversation_titles.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_conversation_titles.py) | 验证：第三轮后后台生成对话标题，不阻塞回复且不作为角色记忆。 |
| [tests/test_cost_estimate.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_cost_estimate.py) | 验证：后台按服务用量与价格估算成本，区分部署者和用户自带密钥。 |
| [tests/test_database.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_database.py) | 验证：数据库连接规则、表分类和用户数据归属。 |
| [tests/test_delete_account.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_delete_account.py) | 验证：用户删除账号后完整清理个人数据并退出所有设备。 |
| [tests/test_delete_past_conversations.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_delete_past_conversations.py) | 验证：删除历史对话及事件，同时保留已提炼的长期记忆。 |
| [tests/test_delivery_cues.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_delivery_cues.py) | 验证：配音语气标记的解析、过滤、显示与存储。 |
| [tests/test_document_titles.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_document_titles.py) | 验证：向量化文档的来源标题及不同服务的标题传递方式。 |
| [tests/test_dynamic_context.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_dynamic_context.py) | 验证：动态状态放在历史之后，以及分阶段裁剪历史以利用模型缓存。 |
| [tests/test_effort_hints.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_effort_hints.py) | 验证：根据模型目录提供思考强度选项提示，不把提示当硬性能力限制。 |
| [tests/test_embedded_texts.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_embedded_texts.py) | 验证：角色资料与作品资料向量缓存、作用域、迁移和模型切换。 |
| [tests/test_embedding.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_embedding.py) | 验证：硅基流动向量化协议、查询超时及临时失败重试。 |
| [tests/test_embedding_config.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_embedding_config.py) | 验证：部署时选择硅基流动或 Gemini 向量化服务。 |
| [tests/test_emotion_judge.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_emotion_judge.py) | 验证：判断模型如何判断情绪和点头，以及概率返回解析。 |
| [tests/test_exempting_keys.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_exempting_keys.py) | 验证：部署者选择通话需要自带哪些密钥才能免限额。 |
| [tests/test_exemption.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_exemption.py) | 验证：只按用户携带的服务种类预先查询是否免限额，不提交密钥。 |
| [tests/test_fish_segments.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_fish_segments.py) | 验证：逐段把角色回复送给 Fish Audio 合成的行为。 |
| [tests/test_gemini_embedding.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_gemini_embedding.py) | 验证：Gemini 原生批量向量化协议与查询/文档前缀。 |
| [tests/test_gift_backpack.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_gift_backpack.py) | 验证：抽奖生成礼物或重置卡、背包叠加、稀有度和退役礼物。 |
| [tests/test_gift_catalog.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_gift_catalog.py) | 验证：礼物目录及角色喜好礼物的配置校验与公开接口。 |
| [tests/test_gift_draws.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_gift_draws.py) | 验证：按规则补发每日抽奖机会、上限和功能关闭/重开时的处理。 |
| [tests/test_gift_giving.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_gift_giving.py) | 验证：赠礼扣库存、好感度奖励、冷却期间效果和对话事件。 |
| [tests/test_gift_responses.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_gift_responses.py) | 验证：赠礼信息进入上下文，以及角色只在合适的下一轮回应礼物。 |
| [tests/test_greetings.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_greetings.py) | 验证：角色招呼语音合成、增量上传和旧音频清理。 |
| [tests/test_hang_up_from_elsewhere.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_hang_up_from_elsewhere.py) | 验证：其他对话触发冷却后，中断该用户与角色正在进行的通话。 |
| [tests/test_hardening.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_hardening.py) | 验证：日志不泄露用户内容，以及特定公开部署配置的启动提醒。 |
| [tests/test_identity_providers.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_identity_providers.py) | 验证：GitHub/Google 授权地址、授权码交换和外部身份解析。 |
| [tests/test_image_service.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_image_service.py) | 验证：NovelAI/OpenAI 图像格式、模型地址配置、并发与后台生图试用校验。 |
| [tests/test_judge_eval.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_judge_eval.py) | 验证：判断模型评测命令、标注结果对比、长上下文和耗时统计。 |
| [tests/test_judge_thresholds.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_judge_thresholds.py) | 验证：判断模型名称归类、各模型阈值及配置覆盖。 |
| [tests/test_link_sign_in.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_link_sign_in.py) | 验证：为同一用户绑定/解绑登录方式和退出所有设备。 |
| [tests/test_live_config.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_live_config.py) | 验证：后台切换聊天模型、保存覆盖值、回退和已开始任务的旧模型租用。 |
| [tests/test_live_config_limits.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_live_config_limits.py) | 验证：后台修改小时限额、通话长度和历史上下文长度的生效时机。 |
| [tests/test_live_config_services.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_live_config_services.py) | 验证：后台切换其他服务、密钥与判断/重排阈值的行为。 |
| [tests/test_llm_cache_hits.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_llm_cache_hits.py) | 验证：从不同模型协议读取输入缓存命中 token 并记录用量。 |
| [tests/test_llm_config.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_llm_config.py) | 验证：模型协议选择以及不支持流式/工具调用时的启动拒绝。 |
| [tests/test_llm_effort.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_llm_effort.py) | 验证：思考强度、额外请求参数及禁止覆盖关键字段。 |
| [tests/test_llm_protocols.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_llm_protocols.py) | 验证：用录制的 SSE 流验证 Responses 和 Anthropic 适配器。 |
| [tests/test_memories.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_memories.py) | 验证：记忆提炼、跨角色共享、更新、检索、删除与用户隔离。 |
| [tests/test_memory_eval.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_memory_eval.py) | 验证：记忆评测的隔离数据库、重复评测、召回和分类汇总。 |
| [tests/test_memory_management.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_memory_management.py) | 验证：用户通过 API 列出和删除单条或全部记忆，检查数据权限。 |
| [tests/test_openai_compat.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_openai_compat.py) | 验证：用录制流验证 OpenAI 兼容 Chat Completions 适配器。 |
| [tests/test_own_image.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_own_image.py) | 验证：用户自带生图地址、模型和密钥的试用、使用及失败处理。 |
| [tests/test_own_keys.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_own_keys.py) | 验证：统一选择用户/部署者密钥，错误不静默回退，以及豁免规则。 |
| [tests/test_own_keys_in_logs.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_own_keys_in_logs.py) | 验证：用户自带密钥在错误、模型调用及记忆失败时不会泄露到日志。 |
| [tests/test_own_llm.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_own_llm.py) | 验证：验证并使用自带聊天/后台模型，不在服务器保存密钥。 |
| [tests/test_own_llm_no_longer_required.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_own_llm_no_longer_required.py) | 验证：旧“必须自带 LLM”配置移除后的兼容与迁移。 |
| [tests/test_own_speech_keys.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_own_speech_keys.py) | 验证：用户自带语音识别/合成密钥，以及相关限额豁免。 |
| [tests/test_past_conversations.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_past_conversations.py) | 验证：历史对话列表、当前对话、摘要、照片和已结束状态。 |
| [tests/test_photo_all_ages.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_photo_all_ages.py) | 验证：照片标签规范化及内容过滤规则，不合规字段替换与允许项。 |
| [tests/test_photo_failures.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_photo_failures.py) | 验证：生图失败、超时、错误尺寸、排队及失败信息如何影响后续上下文。 |
| [tests/test_photo_limits.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_photo_limits.py) | 验证：照片独立小时限额、生成时计数和并发消耗额度。 |
| [tests/test_photo_records.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_photo_records.py) | 验证：生图活动记录、照片用量与成本估算。 |
| [tests/test_photos.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_photos.py) | 验证：文字回合中请求照片、判断、照片标签及异步生成流程。 |
| [tests/test_price_catalog.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_price_catalog.py) | 验证：外部模型价格目录拉取、价格匹配和管理员定价优先级。 |
| [tests/test_producer_profile.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_producer_profile.py) | 验证：用户档案跨设备保存，并注入称呼、性别、生日与本地时间。 |
| [tests/test_proxy.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_proxy.py) | 验证：各服务和用户自带密钥的代理选择、配置与动态切换。 |
| [tests/test_rate_limit.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_rate_limit.py) | 验证：从 API 验证每用户跨设备共享的文字与通话小时限额。 |
| [tests/test_reading_draft.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_reading_draft.py) | 验证：根据人物和世界观生成、补齐读音音素，保留已有人工配置。 |
| [tests/test_readings.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_readings.py) | 验证：读音配置如何传给 Fish Audio，而显示文本保持原写法。 |
| [tests/test_recall_story.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_recall_story.py) | 验证：聊天模型调用回忆工具后，查到剧情并根据结果回复。 |
| [tests/test_reembed.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_reembed.py) | 验证：从已有正文重建不同来源的向量，成功后再清理旧向量。 |
| [tests/test_rerank_eval.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_rerank_eval.py) | 验证：重排评测命令、标注相关性与候选分数对比。 |
| [tests/test_rerank_thresholds.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_rerank_thresholds.py) | 验证：按重排模型选择阈值及环境变量覆盖。 |
| [tests/test_reset_card_grants.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_reset_card_grants.py) | 验证：管理员统一发放重置卡、发放记录和用户资格。 |
| [tests/test_reset_cards.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_reset_cards.py) | 验证：使用重置卡恢复低好感度角色并解除冷却。 |
| [tests/test_restore.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_restore.py) | 验证：恢复前检查数据库、原子替换、清理 WAL 与失败保持原库。 |
| [tests/test_retrieval.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_retrieval.py) | 验证：对话中的判断、并行查询、候选重排和检索内容注入。 |
| [tests/test_retrieval_services.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_retrieval_services.py) | 验证：判断和重排外部服务的协议与配置。 |
| [tests/test_roster.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_roster.py) | 验证：把来源中的人物、声优和组合名字映射为统一条目。 |
| [tests/test_service_call_models.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_service_call_models.py) | 验证：模型热切换时，服务调用记录仍归属于真正执行该请求的模型。 |
| [tests/test_sessions.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_sessions.py) | 验证：Cookie 登录、会话时效、来源校验及开发登录与公开部署配置约束。 |
| [tests/test_shared_memory.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_shared_memory.py) | 验证：对一位角色说过的事，被另一位角色以转述方式记住。 |
| [tests/test_she_ends_conversation.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_she_ends_conversation.py) | 验证：角色因越界、累计伤害或冷却结束文字对话后的记录和限制。 |
| [tests/test_she_hangs_up.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_she_hangs_up.py) | 验证：角色因越界、累计伤害或冷却主动挂断通话。 |
| [tests/test_sheet_draft.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_sheet_draft.py) | 验证：使用剧情材料生成角色人设草稿的输入和文件输出。 |
| [tests/test_sign_in.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_sign_in.py) | 验证：GitHub/Google 首次注册、再次登录及账号资格/封禁。 |
| [tests/test_stand_fetch.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_stand_fetch.py) | 验证：立绘下载、缓存、缺文件处理和下载命令。 |
| [tests/test_stand_outfits.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_stand_outfits.py) | 验证：生成每角色卡片、私服与演出服衣装清单。 |
| [tests/test_stand_upload.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_stand_upload.py) | 验证：素材增量上传、清单上传顺序及 S3 签名。 |
| [tests/test_stats.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_stats.py) | 验证：认识天数、连续活跃、活跃时段和日期等用户统计。 |
| [tests/test_store_sessions.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_store_sessions.py) | 验证：数据库中过期会话的查拒与清理。 |
| [tests/test_story_import.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_story_import.py) | 验证：汉化剧情 CSV 导入、查询及剧本识别。 |
| [tests/test_story_import_json.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_story_import_json.py) | 验证：游戏原文 JSON 剧本导入与汉化版本的优先关系。 |
| [tests/test_story_sync.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_story_sync.py) | 验证：汉化剧情加镜像原文剧情的增量同步与断点保留。 |
| [tests/test_stt_provider.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_stt_provider.py) | 验证：Soniox/百炼识别服务选择、密钥试用和启动校验。 |
| [tests/test_text_turn.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_text_turn.py) | 验证：文字聊天接口的一轮请求、输出及记录。 |
| [tests/test_tts_models.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_tts_models.py) | 验证：Fish Audio 模型选择、名称校验、付费模型额度试用。 |
| [tests/test_turn_outcome.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_turn_outcome.py) | 验证：回合成功/失败/中断等事件的最终结算。 |
| [tests/test_turn_taking.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_turn_taking.py) | 验证：通话轮次、补充、打断和文字模式的状态机。 |
| [tests/test_turns.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_turns.py) | 验证：对话引擎的流式事件、取消与记录协议。 |
| [tests/test_usage.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_usage.py) | 验证：滑动小时用量、失败返还、自带密钥和用量保留。 |
| [tests/test_user_limits.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_user_limits.py) | 验证：管理员对单个用户设置文字/通话限额及恢复部署默认。 |
| [tests/test_user_recent_usage.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_user_recent_usage.py) | 验证：后台单用户最近 24 小时、7/30 天的使用与拒绝统计。 |
| [tests/test_voice_call.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_voice_call.py) | 验证：通话建立、信令接口与 ICE 服务器配置。 |
| [tests/test_voice_interruption.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_voice_interruption.py) | 验证：用户打断后及时停止角色语音。 |
| [tests/test_windows_udp.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_windows_udp.py) | 验证：Windows UDP 关闭时仍发送连接断开通知，避免 ICE 关闭挂起。 |
| [tests/test_world_retrieval.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_world_retrieval.py) | 验证：歌曲、发行和演出资料与剧情、人物资料一起检索重排。 |
| [tests/test_world_setting.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_world_setting.py) | 验证：每轮注入世界观及校验角色属于世界观名单。 |
| [tests/test_world_sync.py](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/tests/test_world_sync.py) | 验证：从模拟官方/补充来源同步人物、组合、歌曲和演出的数据与报告。 |

## 类型声明

| 文件 | 作用 |
| --- | --- |
| [typings/pyrage/__init__.pyi](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/typings/pyrage/__init__.pyi) | 为缺少类型信息的 pyrage 加密库补充项目用到的函数和异常类型。 |
| [typings/pyrage/x25519.pyi](https://github.com/Schweigen322/eidolon-sc/blob/854d427c19eafbf279a98da66f6e2ae8a7c49a11/backend/typings/pyrage/x25519.pyi) | 补充 age/X25519 公钥接收者和私钥身份等类型声明。 |

## 本地生成的目录

本索引只包含 Git 跟踪文件。`backend/.venv/`、`__pycache__/`、运行数据、下载资源和缓存不属于源码文件清单。曾在 backend 下生成的 `source/` 和 `outfits/` 是立绘处理产物，部署使用的目录已整理到根目录 `corpus/stand/`；不要因为索引里没有就删除这些本地资源。

测试文件描述的是要验证的行为；排查问题时，应结合当前版本的测试结果与运行日志。修改配置读取、会话、数据库或提示词时，应运行相应测试，而不是把完整测试目录逐个当作业务入口阅读。
