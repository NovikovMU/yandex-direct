# Сборка первого образа
docker build -t celery -f celery/Dockerfile .

# Сборка второго образа
docker build -t telegram -f telegram/Dockerfile .