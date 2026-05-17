# -*- coding: utf-8 -*-
"""API v1 Blueprint"""
from flask import Blueprint

api_bp = Blueprint("api_v1", __name__)

from app.api.v1 import sessions, voice, knowledge, terminology, model, health, chat
