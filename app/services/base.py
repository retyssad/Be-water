# -*- coding: utf-8 -*-
"""外部服务抽象基类"""
from abc import ABC, abstractmethod


class BaseService(ABC):
    """外部 API 服务基类：双引擎冗余"""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self._primary_provider = "baidu"
        self._fallback_provider = "aliyun"
        self._current_provider = self._primary_provider

    @abstractmethod
    def call(self, *args, **kwargs):
        """调用当前服务"""
        ...

    def switch_provider(self):
        self._current_provider = (self._fallback_provider
                                  if self._current_provider == self._primary_provider
                                  else self._primary_provider)

    @abstractmethod
    def health_check(self) -> bool:
        """服务健康检查"""
        ...
