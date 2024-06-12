# Используем базовый образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем все необходимые файлы
COPY . /app

# Устанавливаем зависимости
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2
RUN pip install -r requirements.txt

# Делаем entrypoint.sh исполняемым
RUN chmod +x /app/entrypoint.sh

# Указываем точку входа
ENTRYPOINT ["/app/entrypoint.sh"]