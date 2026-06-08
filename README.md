# 🌊 水利工程技术语音问答助手

基于 **DeepSeek 大语言模型** + **百度智能云 ASR/TTS** 的水利工程技术智能问答系统。支持文本对话（SSE 流式）、语音识别、语音合成，覆盖防洪、灌溉、水电、航运、基础处理等水利专业领域。

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green)](https://flask.palletsprojects.com/)
[![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek-purple)](https://platform.deepseek.com/)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

---

## ✨ 核心特性

| 模块 | 能力 |
|---|---|
| 💬 **文本问答** | SSE 流式输出，逐 token 实时渲染，支持客户端打断 |
| 🎤 **语音识别 (ASR)** | 百度短语音识别，浏览器端 16kHz PCM 采集 + 自动增益 |
| 🔊 **语音合成 (TTS)** | 百度语音合成，流式分句播放队列，Web Audio API 驱动 |
| 🔄 **全链路流水线** | VCL→ASR→LLM→TTS→VRL 一键完成语音问答 |
| 📖 **术语库** | 水利专业术语精确/模糊检索 |
| 🔍 **RAG 检索** | Milvus 向量库 + 知识增强生成 |
| 🛡 **熔断保护** | LLM/ASR/TTS 服务熔断 + 无 API Key 兜底应答 |
| 🎨 **前端** | 单页应用，Markdown + KaTeX 渲染，响应式布局 |

---

## 🚀 快速开始

### 1. 克隆 & 安装

```bash
git clone <repo-url>
cd water_conservancy_assistant
pip install -r requirements.txt
```

### 2. 配置 API 密钥

创建 `.env` 文件：

```ini
WCA_LLM_API_KEY=sk-your-deepseek-key
WCA_LLM_API_BASE=https://api.deepseek.com
WCA_LLM_MODEL=deepseek-chat

WCA_ASR_API_KEY=your-baidu-api-key
WCA_ASR_SECRET_KEY=your-baidu-secret-key
WCA_ASR_APP_ID=your-baidu-app-id

WCA_TTS_API_KEY=your-baidu-api-key
WCA_TTS_SECRET_KEY=your-baidu-secret-key
WCA_TTS_APP_ID=your-baidu-app-id
```

### 3. 初始化数据库

```bash
python scripts/init_db.py
python scripts/seed_data.py
```

### 4. 启动

```bash
python main.py
# 打开 http://localhost:5000
```

> 详细配置和部署说明见 **[使用说明.md](使用说明.md)**

---

## 🏗 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    浏览器 (SPA)                              │
│  Web Audio API → PCM采集 → base64 → HTTP POST               │
│  SSE stream ← Markdown/KaTeX 渲染 ← TTS 分句播放            │
└──────────────────────┬──────────────────────────────────────┘
                       │  HTTP / SSE
┌──────────────────────▼──────────────────────────────────────┐
│                 Flask API (api/v1)                           │
│  /chat · /chat/stream · /voice/recognize                    │
│  /voice/synthesize · /voice/process · /voice/status         │
│  /sessions · /terminology · /knowledge · /model             │
└──────┬──────────┬──────────┬──────────┬─────────────────────┘
       │          │          │          │
  ┌────▼──┐ ┌────▼──┐ ┌────▼──┐ ┌────▼──────┐
  │DeepSeek│ │百度ASR│ │百度TTS│ │Milvus RAG │
  │(SSE流) │ │OAuth2 │ │PCM16K │ │向量检索   │
  └────────┘ └───────┘ └───────┘ └───────────┘
```

### 语音流水线

```
VCL (采集) → ASR (识别) → LLM (推理) → TTS (合成) → VRL (播放)
  PCM 16kHz    百度API    DeepSeek API   百度API     Web Audio API
```

---

## 📡 API 概览

Base URL: `http://localhost:5000/api/v1`

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/health` | 健康检查 |
| `POST` | `/chat` | 文本问答（非流式） |
| `POST` | `/chat/stream` | **文本问答（SSE 流式）** 🆕 |
| `POST` | `/voice/recognize` | 语音识别 |
| `POST` | `/voice/synthesize` | 语音合成 |
| `POST` | `/voice/process` | **全链路语音问答** |
| `GET` | `/voice/status` | 模块状态 |
| `POST` / `GET` / `DELETE` | `/sessions` | 会话管理 |
| `GET` | `/terminology/search` | 术语检索 |
| `POST` | `/knowledge/retrieve` | RAG 知识检索 |
| `PUT` | `/model/config` | 模型参数调整 |

---

## 📁 项目结构

```
water_conservancy_assistant/
├── main.py                  # 应用入口
├── .env                     # API 密钥（不入库）
├── requirements.txt         # 依赖
├── config/
│   ├── settings.py          # 全局配置
│   └── default_config.json  # 默认配置模板
├── app/
│   ├── __init__.py          # Flask App Factory
│   ├── api/v1/              # RESTful API 蓝图
│   │   ├── chat.py          # 文本问答 + SSE 流式
│   │   ├── voice.py         # 语音识别/合成/全链路
│   │   ├── sessions.py      # 会话管理
│   │   ├── knowledge.py     # RAG 检索
│   │   ├── terminology.py   # 术语库
│   │   ├── model.py         # 模型参数
│   │   └── health.py        # 健康检查
│   ├── core/                # 业务模块
│   │   ├── voice_assistant.py    # 流水线编排器
│   │   ├── voice_capture.py      # VCL
│   │   ├── speech_recognizer.py  # ASR
│   │   ├── core_interaction.py   # LLM 交互
│   │   ├── speech_synthesizer.py # TTS
│   │   ├── voice_response.py     # VRL
│   │   ├── session_manager.py    # 会话
│   │   ├── config_manager.py     # 配置
│   │   ├── error_handler.py      # 错误处理
│   │   └── rag/                  # RAG 引擎
│   ├── services/            # 外部 API 封装
│   │   ├── llm_service.py   # DeepSeek（SSE 流式）
│   │   ├── asr_service.py   # 百度 ASR
│   │   ├── tts_service.py   # 百度 TTS
│   │   └── circuit_breaker.py # 熔断器
│   ├── models/              # SQLAlchemy 数据模型 (11 表)
│   ├── utils/               # 工具（音频、加密）
│   └── static/index.html    # 前端 SPA
├── database/                # 数据库连接 + DDL
├── scripts/                 # init_db, seed_data
└── tests/                   # 单元测试 + 集成测试
```

---

## 🧪 测试

```bash
pytest tests/ -v                    # 全部测试
pytest tests/test_unit/ -v          # 单元测试
pytest tests/test_integration/ -v   # 集成测试
pytest tests/ --cov=app --cov-report=html  # 覆盖率
```

---

## 📖 详细文档

完整的使用说明、API 细节、配置项列表和常见问题请参阅 **[使用说明.md](使用说明.md)**。

---

## 📄 License

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request。项目尚在开发迭代中，重大变更请先提 Issue 讨论。
