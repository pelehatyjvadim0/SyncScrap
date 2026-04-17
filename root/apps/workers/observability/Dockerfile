FROM python:3.11-slim

WORKDIR /app

COPY root/apps/workers/observability/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["faststream", "run", "root.apps.workers.observability.main:faststream_app"]
