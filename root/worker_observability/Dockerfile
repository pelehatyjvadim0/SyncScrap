FROM python:3.11-slim

WORKDIR /app

COPY root/worker_observability/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["faststream", "run", "root.worker_observability.main:faststream_app"]
