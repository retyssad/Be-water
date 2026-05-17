# -*- coding: utf-8 -*-
"""数据库Schema定义：11张表 + 索引（对应报告第7章）"""

SCHEMA_SQL = """
-- ========== V1.0 基础表 ==========

CREATE TABLE IF NOT EXISTS users (
    user_id         VARCHAR(64) PRIMARY KEY,
    username        VARCHAR(100) NOT NULL UNIQUE,
    password_hash   VARCHAR(256) NOT NULL,
    email           VARCHAR(200),
    phone           VARCHAR(20),
    role            VARCHAR(20) DEFAULT 'user',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login      DATETIME,
    status          VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id      VARCHAR(64) PRIMARY KEY,
    user_id         VARCHAR(64) NOT NULL,
    device_id       VARCHAR(64),
    device_type     VARCHAR(20),
    start_time      DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_active     DATETIME DEFAULT CURRENT_TIMESTAMP,
    expired_at      DATETIME,
    status          VARCHAR(20) DEFAULT 'active',
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS messages (
    message_id      VARCHAR(64) PRIMARY KEY,
    session_id      VARCHAR(64) NOT NULL,
    sender          VARCHAR(20) NOT NULL,
    content         TEXT NOT NULL,
    timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP,
    message_type    VARCHAR(20) DEFAULT 'text',
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

CREATE TABLE IF NOT EXISTS configs (
    config_id       VARCHAR(64) PRIMARY KEY,
    key             VARCHAR(100) NOT NULL UNIQUE,
    value           TEXT,
    type            VARCHAR(20),
    description     VARCHAR(500),
    last_updated    DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by      VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS logs (
    log_id          VARCHAR(64) PRIMARY KEY,
    level           VARCHAR(20) NOT NULL,
    module          VARCHAR(100),
    message         TEXT NOT NULL,
    details         TEXT,
    timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id         VARCHAR(64)
);

-- ========== V2.0 新增表 ==========

CREATE TABLE IF NOT EXISTS knowledge_base (
    doc_id          VARCHAR(64) PRIMARY KEY,
    title           VARCHAR(500) NOT NULL,
    content         TEXT NOT NULL,
    doc_type        VARCHAR(50) NOT NULL,
    category        VARCHAR(100),
    source          VARCHAR(200),
    publish_year    INTEGER,
    embedding_vector BLOB,
    chunk_index     INTEGER DEFAULT 0,
    total_chunks    INTEGER DEFAULT 1,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active       TINYINT DEFAULT 1
);

CREATE TABLE IF NOT EXISTS terminology (
    term_id         VARCHAR(64) PRIMARY KEY,
    term            VARCHAR(100) NOT NULL UNIQUE,
    pinyin          VARCHAR(200),
    definition      TEXT NOT NULL,
    category        VARCHAR(50),
    source          VARCHAR(200),
    synonyms        VARCHAR(500),
    usage_examples  TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS api_logs (
    log_id          VARCHAR(64) PRIMARY KEY,
    session_id      VARCHAR(64),
    user_id         VARCHAR(64),
    api_type        VARCHAR(20) NOT NULL,
    provider        VARCHAR(50),
    request_size    INTEGER,
    response_size   INTEGER,
    latency_ms      INTEGER,
    status_code     INTEGER,
    error_code      VARCHAR(20),
    request_time    DATETIME NOT NULL,
    cost_ms         INTEGER
);

CREATE TABLE IF NOT EXISTS model_evaluation (
    eval_id         VARCHAR(64) PRIMARY KEY,
    session_id      VARCHAR(64),
    question        TEXT NOT NULL,
    answer          TEXT NOT NULL,
    retrieved_docs  TEXT,
    rouge_l         FLOAT,
    bleu_4          FLOAT,
    term_match_rate FLOAT,
    hallucination_score FLOAT,
    user_rating     INTEGER,
    eval_time       DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_feedback (
    feedback_id     VARCHAR(64) PRIMARY KEY,
    session_id      VARCHAR(64),
    message_id      VARCHAR(64),
    user_id         VARCHAR(64),
    rating          INTEGER,
    feedback_type   VARCHAR(50),
    comment         TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_metrics (
    metric_id       VARCHAR(64) PRIMARY KEY,
    metric_name     VARCHAR(100) NOT NULL,
    metric_value    FLOAT NOT NULL,
    metric_unit     VARCHAR(20),
    host            VARCHAR(100),
    recorded_at     DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ========== 索引 ==========
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_kb_doc_type ON knowledge_base(doc_type);
CREATE INDEX IF NOT EXISTS idx_kb_category ON knowledge_base(category);
CREATE INDEX IF NOT EXISTS idx_api_logs_session ON api_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_api_logs_user ON api_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_api_logs_type ON api_logs(api_type);
CREATE INDEX IF NOT EXISTS idx_eval_session ON model_evaluation(session_id);
CREATE INDEX IF NOT EXISTS idx_feedback_session ON user_feedback(session_id);
CREATE INDEX IF NOT EXISTS idx_metrics_name ON system_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_metrics_time ON system_metrics(recorded_at);
"""
