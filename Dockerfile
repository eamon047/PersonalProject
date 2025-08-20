# 选择基础镜像：python 3.11 的瘦身版，支持多架构（含 arm64）
FROM python:3.11-slim

# 基本环境变量：不生成 .pyc；stdout 直刷；pip 安静一点
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 可选：安装编译工具（如果某些依赖需要编译才保留，否则能省就省）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 设定工作目录（之后的相对路径都基于这里）
WORKDIR /app

# 先只拷贝依赖清单，利用 Docker 层缓存：依赖不变就无需重新安装
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 再拷贝项目代码（代码变化才会让这层失效）
COPY . /app

# 创建非 root 用户并设置权限
RUN useradd -m appuser && \
    chown -R appuser:appuser /app

# 切换到非 root 用户
USER appuser

# 暴露服务端口（文档作用；真正的映射在 `-p 宿主:容器`）
EXPOSE 8000

# 启动命令：用 uvicorn 跑你的 FastAPI 应用
# 注意：入口是 app.main:app（你的仓库结构里 main.py 定义了 app）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
