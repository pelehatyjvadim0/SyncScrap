FROM python:3.11-slim

WORKDIR /app

COPY root/worker_scout/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["faststream", "run", "root.worker_scout.main:faststream_app"]
