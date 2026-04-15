FROM python:3.11-slim

WORKDIR /app

COPY root/apps/workers/scout/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["faststream", "run", "root.apps.workers.scout.main:faststream_app"]
