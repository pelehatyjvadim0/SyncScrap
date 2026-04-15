FROM python:3.11-slim

WORKDIR /app

COPY root/apps/workers/embedding/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["faststream", "run", "root.apps.workers.embedding.main:faststream_app"]
