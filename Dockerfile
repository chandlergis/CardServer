# --- 基础镜像 ---
FROM python:3.10-slim

# --- 设置环境变量 ---
ENV PYTHONUNBUFFERED=1

# --- 安装系统级依赖 (最终版) ---
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # ... (原有的一长串依赖保持不变) ...
    gconf-service \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libgconf-2-4 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    lsb-release \
    xdg-utils \
    wget \
    fontconfig \
    # ====================【新增】====================
    # 安装 Google Noto Color Emoji 字体库，解决 emoji 显示问题
    fonts-noto-color-emoji && \
    # ===============================================
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# --- 安装自定义字体 ---
# (这部分保持不变)
RUN mkdir -p /usr/share/fonts/truetype/custom
COPY ./fonts/ /usr/share/fonts/truetype/custom/
RUN fc-cache -f -v

# --- 设置工作目录 ---
WORKDIR /app

# --- 安装 Python 依赖 ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- 复制应用程序代码 ---
COPY . .

# --- 暴露端口 ---
EXPOSE 8000

# --- 启动命令 ---
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]