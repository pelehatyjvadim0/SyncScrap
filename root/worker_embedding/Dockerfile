FROM python:3.11-slim

WORKDIR /app

COPY root/worker_embedding/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["faststream", "run", "root.worker_embedding.main:faststream_app"]
