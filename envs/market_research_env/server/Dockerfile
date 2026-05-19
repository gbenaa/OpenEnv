FROM python:3.11-slim

LABEL description="Market Research Environment with BrowserGym for OpenEnv"

WORKDIR /app/env

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libxshmfence1 \
    fonts-liberation \
    xdg-utils && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1
ENV MARKET_RESEARCH_HEADLESS=true
ENV MARKET_RESEARCH_MAX_STEPS=50
ENV ENABLE_WEB_INTERFACE=true

COPY . /app/env

RUN pip install --no-cache-dir -e .
RUN playwright install chromium

RUN chmod +x /app/env/server/start.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["/app/env/server/start.sh"]
