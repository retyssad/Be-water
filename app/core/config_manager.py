# -*- coding: utf-8 -*-
"""配置管理模块（报告 2.7 / 4.4.1）"""
from typing import Any, Optional
from app.core.base_module import BaseModule


class ConfigManager(BaseModule):
    """集中管理系统参数与服务配置"""

    def __init__(self):
        super().__init__(module_id="ConfigManager")
        self._config_file: Optional[str] = None
        self._config_data: dict = {}

    def initialize(self) -> bool:
        self.load_config()
        self.set_status("idle")
        self._logger.info("ConfigManager initialized")
        return True

    def shutdown(self) -> None:
        self._config_data.clear()
        self.set_status("idle")

    # ---- 核心方法 ----
    def load_config(self) -> bool:
        from config.settings import settings
        self._config_data = settings.all()
        return True

    def save_config(self) -> bool:
        import json
        try:
            with open(self._config_file or "config/default_config.json", "w",
                      encoding="utf-8") as f:
                json.dump(self._config_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self._logger.error("save config failed: %s", e)
            return False

    def get_config(self, key: str, default: Any = None) -> Any:
        return self._config_data.get(key, default)

    def set_config(self, key: str, value: Any) -> bool:
        self._config_data[key] = value
        self._logger.info("config set: %s = %s", key, value)
        return True

    def reload_config(self) -> bool:
        return self.load_config()

    def get_api_key(self, provider: str) -> Optional[str]:
        key_map = {"baidu": "llm_api_key", "aliyun": "llm_api_key"}
        return self._config_data.get(key_map.get(provider, ""))
