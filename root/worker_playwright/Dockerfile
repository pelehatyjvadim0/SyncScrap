# Образ с браузерными зависимостями для Playwright (Chromium).
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

COPY root/worker_playwright/requirements.txt /app/requirements-worker-playwright.txt
RUN pip install --no-cache-dir -r /app/requirements-worker-playwright.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["faststream", "run", "root.worker_playwright.main:faststream_app"]
