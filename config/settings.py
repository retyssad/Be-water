# -*- coding: utf-8 -*-
"""全局配置：支持环境变量 + JSON 配置文件双层加载"""
import json, os
from pathlib import Path
from typing import Optional

def _load_dotenv():
    """Load .env file into os.environ (no external dependency)."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip()
            if key not in os.environ:
                os.environ[key] = value

_load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PREFIX = "WCA_"  # Water Conservancy Assistant


class Settings:
    def __init__(self):
        self._config_file = BASE_DIR / "config" / "default_config.json"
        self._data: dict = {}
        self._load_json()
        self._override_from_env()

    def _load_json(self):
        if self._config_file.exists():
            with open(self._config_file, "r", encoding="utf-8") as f:
                self._data = json.load(f)

    def _override_from_env(self):
        for key in os.environ:
            if key.startswith(ENV_PREFIX):
                config_key = key[len(ENV_PREFIX):].lower()
                self._data[config_key] = os.environ[key]

    @property
    def debug(self) -> bool:
        return str(self._data.get("debug", False)).lower() == "true"

    @property
    def secret_key(self) -> str:
        return self._data.get("secret_key", "change-me-in-production")

    @property
    def jwt_secret(self) -> str:
        return self._data.get("jwt_secret", self.secret_key)

    @property
    def jwt_expire_hours(self) -> int:
        return int(self._data.get("jwt_expire_hours", 24))

    @property
    def database_path(self) -> str:
        return str(BASE_DIR / self._data.get("database_path", "data/water_knowledge.db"))

    @property
    def redis_url(self) -> Optional[str]:
        return self._data.get("redis_url")

    @property
    def log_dir(self) -> str:
        return str(BASE_DIR / self._data.get("log_dir", "data/logs"))

    @property
    def log_level(self) -> str:
        return self._data.get("log_level", "INFO")

    @property
    def milvus_host(self) -> Optional[str]:
        return self._data.get("milvus_host")

    @property
    def milvus_port(self) -> int:
        return int(self._data.get("milvus_port", 19530))

    # --- LLM ---
    @property
    def llm_provider(self) -> str:
        return self._data.get("llm_provider", "deepseek")

    @property
    def llm_api_key(self) -> Optional[str]:
        return self._data.get("llm_api_key") or os.environ.get("WCA_LLM_API_KEY")

    @property
    def llm_api_base(self) -> str:
        return self._data.get("llm_api_base", "https://api.deepseek.com")

    @property
    def llm_model(self) -> str:
        return self._data.get("llm_model", "deepseek-chat")

    @property
    def llm_app_id(self) -> Optional[str]:
        return self._data.get("llm_app_id")

    # --- ASR ---
    @property
    def asr_provider(self) -> str:
        return self._data.get("asr_provider", "baidu")

    @property
    def asr_api_key(self) -> Optional[str]:
        return self._data.get("asr_api_key") or os.environ.get("WCA_ASR_API_KEY")

    @property
    def asr_secret_key(self) -> Optional[str]:
        return self._data.get("asr_secret_key") or os.environ.get("WCA_ASR_SECRET_KEY")

    @property
    def asr_app_id(self) -> Optional[str]:
        return self._data.get("asr_app_id")

    # --- TTS ---
    @property
    def tts_provider(self) -> str:
        return self._data.get("tts_provider", "baidu")

    @property
    def tts_api_key(self) -> Optional[str]:
        return self._data.get("tts_api_key") or os.environ.get("WCA_TTS_API_KEY")

    @property
    def tts_secret_key(self) -> Optional[str]:
        return self._data.get("tts_secret_key") or os.environ.get("WCA_TTS_SECRET_KEY")

    @property
    def tts_app_id(self) -> Optional[str]:
        return self._data.get("tts_app_id")

    # --- Session ---
    @property
    def session_ttl_minutes(self) -> int:
        return int(self._data.get("session_ttl_minutes", 30))

    @property
    def max_history_rounds(self) -> int:
        return int(self._data.get("max_history_rounds", 10))

    # --- Audio ---
    @property
    def default_sample_rate(self) -> int:
        return int(self._data.get("default_sample_rate", 16000))

    @property
    def default_bit_depth(self) -> int:
        return int(self._data.get("default_bit_depth", 16))

    # --- RAG ---
    @property
    def rag_top_k(self) -> int:
        return int(self._data.get("rag_top_k", 5))

    @property
    def similarity_threshold(self) -> float:
        return float(self._data.get("similarity_threshold", 0.75))

    @property
    def embedding_model(self) -> str:
        return self._data.get("embedding_model", "text-embedding-v1")

    # --- Rate Limit ---
    @property
    def rate_limit_per_minute(self) -> int:
        return int(self._data.get("rate_limit_per_minute", 60))

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value):
        self._data[key] = value

    def all(self) -> dict:
        return dict(self._data)


settings = Settings()
