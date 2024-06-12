celery -A celery_app worker --loglevel=info &
celery -A celery_app beat --loglevel=info &

# Запускаем боты
python /app/telegram_helper.py &
python /app/telegram_manager.py &

# Ждем завершения процессов
wait -n