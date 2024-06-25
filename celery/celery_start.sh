#!/bin/bash

# Запуск Celery worker в фоновом режиме
celery -A tasks worker --loglevel=info --concurrency=4 &

# # Запуск Celery beat программы в фоновом режиме
celery -A celery_app beat --loglevel=info

