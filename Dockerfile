# Render deploy for the Invoice Manager (Flask + WeasyPrint).
# WeasyPrint needs Pango/Cairo system libraries. Vercel's serverless runtime
# has none of them (and ignores apt.txt), and Render's native Python
# environment does not install apt.txt either - so the only way to run the
# PDF feature is a Docker deploy like this one. The old apt.txt lists the
# same libraries; this Dockerfile is what actually installs them.
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# $PORT is assigned by Render; binding a fixed port means the health check
# never succeeds. (The old render.yaml startCommand "gunicorn app:app"
# bound 127.0.0.1:8000.)
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120"]
