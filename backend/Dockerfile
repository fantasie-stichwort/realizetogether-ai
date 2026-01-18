# 1. Python Image nutzen (WICHTIG: Upgrade auf 3.11!)
FROM python:3.11-slim

# 2. Arbeitsverzeichnis setzen
WORKDIR /app

# 3. System-Abhängigkeiten
RUN apt-get update && apt-get install -y \
    build-essential \
    libpoppler-cpp-dev \
    pkg-config \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Requirements kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Restlichen Code kopieren
COPY . .

# 6. Port freigeben
EXPOSE 8000

# 7. Start-Befehl
CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT"]