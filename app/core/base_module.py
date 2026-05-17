# -*- coding: utf-8 -*-
"""BaseModule - 所有功能模块的抽象基类（报告 4.1）"""
from abc import ABC, abstractmethod
from typing import Any, Optional
import logging


class BaseModule(ABC):
    """模块基类：定义统一的生命周期管理接口"""

    def __init__(self, module_id: str):
        self._module_id = module_id
        self._status = "idle"  # idle | processing | error
        self._config: dict = {}
        self._logger = logging.getLogger(module_id)

    # ---- 属性 ----
    @property
    def module_id(self) -> str:
        return self._module_id

    @property
    def status(self) -> str:
        return self._status

    def set_status(self, status: str):
        self._status = status
        self._logger.debug("status -> %s", status)

    # ---- 生命周期 ----
    @abstractmethod
    def initialize(self) -> bool:
        """初始化模块，返回是否成功"""
        ...

    @abstractmethod
    def shutdown(self) -> None:
        """关闭模块，释放资源"""
        ...

    # ---- 配置 ----
    def get_config(self, key: Optional[str] = None) -> Any:
        if key:
            return self._config.get(key)
        return self._config

    def update_config(self, config: dict) -> bool:
        self._config.update(config)
        self._logger.info("config updated: %s", config)
        return True
