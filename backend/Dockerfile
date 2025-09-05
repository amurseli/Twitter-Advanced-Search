FROM python:3.11-slim

WORKDIR /app

# Install ALL system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    fonts-liberation \
    fonts-unifont \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
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
    lsb-release \
    xdg-utils \
    libxshmfence1 \
    libdrm2 \
    libatspi2.0-0 \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and browsers
RUN pip install playwright==1.40.0
RUN playwright install chromium


# Copy project files
COPY . .

# Make entrypoint executable
COPY docker-entrypoint.sh /docker-entrypoin-robust.sh
RUN chmod +x /docker-entrypoint-robust.sh

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production
ENV PORT=6060

EXPOSE 6060

ENTRYPOINT ["/docker-entrypoint-robust.sh"]
CMD gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-6060} --workers 1 --timeout 300 --worker-class sync
