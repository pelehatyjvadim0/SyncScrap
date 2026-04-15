FROM python:3.11-slim

WORKDIR /app

COPY root/apps/workers/delta/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["faststream", "run", "root.apps.workers.delta.main:faststream_app"]
