FROM python:3.11-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source files
COPY . .

# Support Railway port binding (including 3003, 5000, 8080, 80)
ENV PORT=3003
EXPOSE 3003 5000 8080 80

CMD gunicorn app:app --bind 0.0.0.0:${PORT:-3003} --workers 2 --timeout 120
