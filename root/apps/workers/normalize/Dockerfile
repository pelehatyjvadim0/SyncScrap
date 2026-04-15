FROM python:3.11-slim

WORKDIR /app

COPY root/apps/workers/normalize/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["faststream", "run", "root.apps.workers.normalize.main:faststream_app"]
