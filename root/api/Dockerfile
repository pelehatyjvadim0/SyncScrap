FROM python:3.11-slim

WORKDIR /app

COPY root/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "root.api.main:app", "--host", "0.0.0.0", "--port", "8000"]