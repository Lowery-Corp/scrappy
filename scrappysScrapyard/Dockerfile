FROM python:3.14-slim

WORKDIR /app

# Install curl for health checks
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources /etc/apt/sources.list 2>/dev/null || true \
 && apt-get update -o Acquire::Retries=5 \
 && apt-get install -y --no-install-recommends curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir -r /app/requirements.txt

COPY . /app