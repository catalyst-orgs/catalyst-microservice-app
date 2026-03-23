FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Default: v1
ENV APP_VERSION=v1
ENV APP_COLOR=#2196F3

EXPOSE 8000

USER 1000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
