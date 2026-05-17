# 水利工程技术语音问答助手 — 使用说明

## 1. 项目概述

基于 DeepSeek 大语言模型 + 百度智能云 ASR/TTS 的水利工程技术语音问答助手。支持文本问答、语音识别、语音合成三大核心功能，覆盖防洪、灌溉、水电、航运、基础处理等水利专业领域。

### 技术栈

| 层 | 技术 |
|---|---|
| Web 框架 | Flask 2.3+ (Blueprint RESTful API) |
| 大模型 | DeepSeek Chat (OpenAI 兼容接口) |
| 语音识别 | 百度智能云短语音识别 (OAuth 2.0) |
| 语音合成 | 百度智能云语音合成 |
| 数据库 | SQLite + SQLAlchemy ORM |
| 向量检索 | Milvus (可选) |
| 前端 | 单页 HTML + Web Audio API |

### 核心模块（报告 8.1）

```
VCL (8.1.1) → ASR (8.1.2) → LLM (8.1.3) → TTS (8.1.4) → VRL (8.1.5)
语音采集      语音识别      核心交互      语音合成      语音响应
```

---

## 2. 环境准备

### 2.1 依赖安装

```bash
cd water_conservancy_assistant
pip install -r requirements.txt
```

### 2.2 配置文件 `.env`

在项目根目录创建 `.env` 文件（已提供 `.env.example` 模板）：

```ini
# 调试模式（开发环境设为 true）
WCA_DEBUG=true

# Flask 密钥
WCA_SECRET_KEY=your-secret-key

# ---- DeepSeek API（必填） ----
WCA_LLM_API_KEY=sk-your-deepseek-key
WCA_LLM_API_BASE=https://api.deepseek.com
WCA_LLM_MODEL=deepseek-chat

# ---- 百度 ASR（语音识别，必填） ----
WCA_ASR_API_KEY=your-baidu-api-key
WCA_ASR_SECRET_KEY=your-baidu-secret-key
WCA_ASR_APP_ID=your-baidu-app-id

# ---- 百度 TTS（语音合成，必填） ----
WCA_TTS_API_KEY=your-baidu-api-key
WCA_TTS_SECRET_KEY=your-baidu-secret-key
WCA_TTS_APP_ID=your-baidu-app-id
```

> **获取 API 密钥**：
> - DeepSeek: <https://platform.deepseek.com/api_keys>
> - 百度智能云 ASR/TTS: <https://console.bce.baidu.com/ai/#/ai/speech/overview/index>

### 2.3 配置项完整列表

| 环境变量 | 默认值 | 说明 |
|---|---|---|
| `WCA_DEBUG` | false | 调试模式，开启后自动重载 |
| `WCA_SECRET_KEY` | — | Flask 应用密钥 |
| `WCA_LLM_API_KEY` | — | DeepSeek API Key |
| `WCA_LLM_API_BASE` | api.deepseek.com | LLM API 地址 |
| `WCA_LLM_MODEL` | deepseek-chat | 模型名称 |
| `WCA_ASR_API_KEY` | — | 百度 ASR API Key |
| `WCA_ASR_SECRET_KEY` | — | 百度 ASR Secret Key |
| `WCA_ASR_APP_ID` | — | 百度 ASR App ID |
| `WCA_TTS_API_KEY` | — | 百度 TTS API Key |
| `WCA_TTS_SECRET_KEY` | — | 百度 TTS Secret Key |
| `WCA_TTS_APP_ID` | — | 百度 TTS App ID |
| `WCA_DATABASE_PATH` | data/water_knowledge.db | SQLite 数据库路径 |
| `WCA_SESSION_TTL_MINUTES` | 30 | 会话过期时间 |
| `WCA_MAX_HISTORY_ROUNDS` | 10 | 最大对话轮数 |
| `WCA_RAG_TOP_K` | 5 | RAG 检索返回条数 |
| `WCA_RATE_LIMIT_PER_MINUTE` | 60 | 每分钟请求限额 |

---

## 3. 启动运行

### 3.1 开发模式

```bash
cd water_conservancy_assistant
python main.py
```

服务默认监听 `http://0.0.0.0:5000`，浏览器打开 <http://localhost:5000> 即可看到测试页面。

### 3.2 生产模式

```bash
# 关闭调试
export WCA_DEBUG=false

# Gunicorn（Linux/Mac）
gunicorn -w 4 -b 0.0.0.0:5000 main:app

# 或 Waitress（Windows）
pip install waitress
waitress-serve --port=5000 main:app
```

### 3.3 Docker

```bash
docker build -t water-assistant .
docker run -p 5000:5000 --env-file .env water-assistant
```

---

## 4. 初始化数据库

```bash
# 建表 + 验证
python scripts/init_db.py

# 导入种子数据（术语库、示例配置等）
python scripts/seed_data.py
```

成功后会在 `data/water_knowledge.db` 创建 11 张表。

---

## 5. API 接口

Base URL: `http://localhost:5000/api/v1`

### 5.1 健康检查

**`GET /health`**

```json
{"status":"ok","service":"water-conservancy-assistant","version":"2.0.0"}
```

### 5.2 文本问答

**`POST /chat`**

请求：
```json
{"question": "什么是帷幕灌浆？"}
```

响应：
```json
{
  "answer": "帷幕灌浆是指在坝基或岸坡中钻孔...",
  "sources": ["SL 570-2013"],
  "confidence": 0.92
}
```

### 5.3 语音识别

**`POST /voice/recognize`**

请求（base64 编码的 PCM 音频）：
```json
{
  "audio_data": "<base64-pcm>",
  "sample_rate": 16000,
  "bit_depth": 16,
  "channels": 1
}
```

响应：
```json
{
  "status": "success",
  "text": "什么是帷幕灌浆",
  "raw_text": "什么是帷幕灌浆",
  "confidence": 0.95
}
```

### 5.4 语音合成

**`POST /voice/synthesize`**

请求：
```json
{"text": "水利工程的主要类型包括防洪工程。"}
```

响应：
```json
{
  "status": "success",
  "audio_data": "<base64-wav>",
  "duration": 2.5,
  "sample_rate": 16000
}
```

> 文本最长 500 字，超过返回 `T002` 错误。

### 5.5 完整语音问答流程

**`POST /voice/process`**

一步完成 VCL → ASR → LLM → TTS → VRL 全链路。

请求：
```json
{
  "audio_data": "<base64-pcm>",
  "session_id": "可选",
  "user_id": "anonymous"
}
```

响应：
```json
{
  "status": "success",
  "question": "什么是帷幕灌浆",
  "answer": "帷幕灌浆是指...",
  "asr_confidence": 0.95,
  "domain": "基础处理",
  "audio_data": "<base64-wav>",
  "audio_duration": 3.1,
  "timeline": {
    "capture": "done",
    "asr": {"text": "什么是帷幕灌浆", "confidence": 0.95},
    "llm": {"domain": "基础处理", "confidence": 0.9},
    "tts": {"duration": 3.1},
    "vrl": {"state": "done", "volume": 70}
  }
}
```

### 5.6 语音系统状态

**`GET /voice/status`**

返回 6 个模块的实时状态：
```json
{
  "vcl": {"state": "idle", "status": "idle"},
  "asr": {"provider": "baidu", "status": "idle"},
  "llm": {"status": "idle"},
  "tts": {"status": "idle"},
  "vrl": {"state": "ready", "status": "idle"},
  "session": {"status": "idle"}
}
```

### 5.7 会话管理

| 方法 | 路径 | 说明 |
|---|---|---|
| `POST` | `/sessions` | 创建会话 |
| `GET` | `/sessions/<id>` | 获取会话信息 |
| `DELETE` | `/sessions/<id>` | 结束会话 |
| `POST` | `/sessions/<id>/messages` | 发送消息 |
| `GET` | `/sessions/<id>/messages` | 获取消息历史 |

### 5.8 其他接口

| 方法 | 路径 | 说明 |
|---|---|---|
| `POST` | `/knowledge/retrieve` | RAG 知识库检索 |
| `GET` | `/terminology/search?term=帷幕灌浆` | 术语库查询 |
| `PUT` | `/model/config` | 调整模型参数（temperature, top_p 等） |

### 5.9 错误码

| 分类 | 示例 | 说明 |
|---|---|---|
| A (Audio) | A001 | 音频格式无效 |
| R (Recognition) | R001 | 语音识别失败 |
| T (TTS) | T001, T002 | 合成失败 / 文本过长 |
| P (Parameter) | P001 | 参数缺失 |
| S (Session) | S001, S003 | 会话不存在 / 已过期 |
| SYSTEM | SYSTEM001 | 系统内部错误 |

---

## 6. 前端测试页面

访问 <http://localhost:5000>，页面包含三个功能区域：

### 文本问答标签
- 输入水利工程相关问题，DeepSeek 实时作答
- 快捷问题按钮（帷幕灌浆、防洪标准等）
- 回答自动调用 TTS 语音合成播放

### 语音问答标签
- 点击麦克风按钮录音，**观察音量表确认麦克风工作**
- 5 级流水线可视化：采集 → 识别 → 交互 → 合成 → 响应
- 10 秒自动停止，或手动点击停止
- 识别结果和 AI 回答实时显示

### 右侧面板
- **术语库查询**：支持精确/模糊搜索
- **语音合成测试**：输入文本直接合成为语音播放
- **模块状态**：6 个核心模块实时健康检测

---

## 7. 运行测试

```bash
# 全部测试
pytest tests/ -v

# 仅单元测试
pytest tests/test_unit/ -v

# 仅集成测试
pytest tests/test_integration/ -v

# 带覆盖率报告
pytest tests/ --cov=app --cov-report=html
```

---

## 8. 项目结构

```
water_conservancy_assistant/
├── main.py                  # 应用入口
├── .env                     # 环境变量（API 密钥等）
├── requirements.txt         # Python 依赖
├── config/
│   ├── settings.py          # 全局配置（pydantic 风格）
│   └── default_config.json  # 默认配置模板
├── app/
│   ├── __init__.py          # Flask App Factory
│   ├── api/v1/              # RESTful API
│   │   ├── chat.py          # 文本问答
│   │   ├── voice.py         # 语音识别/合成/流程
│   │   ├── sessions.py      # 会话管理
│   │   ├── knowledge.py     # 知识库检索
│   │   ├── terminology.py   # 术语库查询
│   │   ├── model.py         # 模型参数调优
│   │   └── health.py        # 健康检查
│   ├── core/                # 核心业务模块
│   │   ├── voice_capture.py      # VCL 语音采集
│   │   ├── speech_recognizer.py  # ASR 语音识别
│   │   ├── core_interaction.py   # LLM 核心交互
│   │   ├── speech_synthesizer.py # TTS 语音合成
│   │   ├── voice_response.py     # VRL 语音响应
│   │   ├── voice_assistant.py    # 编排器
│   │   ├── session_manager.py    # 会话管理
│   │   ├── config_manager.py     # 配置管理
│   │   ├── error_handler.py      # 错误处理
│   │   └── rag/                  # RAG 引擎
│   ├── services/            # 外部 API 封装
│   │   ├── llm_service.py   # DeepSeek LLM
│   │   ├── asr_service.py   # 百度 ASR
│   │   ├── tts_service.py   # 百度 TTS
│   │   └── circuit_breaker.py # 熔断器
│   ├── models/              # SQLAlchemy 数据模型 (11 表)
│   └── utils/               # 工具（音频处理、加密等）
├── database/                # 数据库连接 + SQL DDL
├── scripts/
│   ├── init_db.py           # 初始化数据库
│   └── seed_data.py         # 导入种子数据
└── tests/
    ├── test_unit/           # 单元测试
    └── test_integration/    # 集成测试
```

---

## 9. 常见问题

**Q: 语音识别一直返回 [R001]？**
1. 确认麦克风工作正常（看录音时页面上的音量表是否有读数）
2. 使用 Chrome 或 Edge 浏览器
3. 查看服务器控制台的百度 ASR 诊断日志（`err_no` / `err_msg`）
4. 确认百度 API 密钥已正确填入 `.env`

**Q: 文本问答无响应？**
1. 确认 DeepSeek API Key 已正确填入 `.env`
2. 检查网络是否能访问 `api.deepseek.com`

**Q: Flask 开发服务器警告？**
正常运行会看到 `WARNING: This is a development server.`，仅开发环境显示，不影响使用。生产环境使用 Gunicorn 部署。
