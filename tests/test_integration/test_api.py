# -*- coding: utf-8 -*-
"""API 集成测试"""
import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health_endpoint(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["status"] == "ok"
    assert data["service"] == "water-conservancy-assistant"
    assert data["version"] == "2.0.0"


def test_terminology_search(client):
    resp = client.get("/api/v1/terminology/search?term=帷幕灌浆")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["term"] == "帷幕灌浆"


def test_terminology_not_found(client):
    resp = client.get("/api/v1/terminology/search?term=不存在")
    assert resp.status_code == 404


def test_terminology_missing_param(client):
    resp = client.get("/api/v1/terminology/search")
    assert resp.status_code == 400


def test_model_config_update(client):
    resp = client.put("/api/v1/model/config",
                      data=json.dumps({"temperature": 0.8}),
                      content_type="application/json")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["status"] == "success"


def test_health_returns_json(client):
    resp = client.get("/api/v1/health")
    assert resp.content_type == "application/json"
