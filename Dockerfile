# =========================================
# 水利工程技术语音问答助手 - Docker
# =========================================

FROM python:3.11-slim AS base

WORKDIR /app

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# =========================================
FROM base AS production

COPY . .

# 创建数据目录
RUN mkdir -p data/logs data/knowledge_base

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "--timeout", "120", "main:app"]
