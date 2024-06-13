FROM python:3.9-slim
WORKDIR /app
COPY ../requirements.txt .

# Установить зависимости
RUN pip install -r requirements.txt
COPY . .
CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info"]