#!/bin/bash

# Необходимо подождать, чтобы PostgreSQL запустился и произошло создание бд
sleep 5

# Запуск Python telegram_helper программы в фоновом режиме
python telegram_helper.py &

# Запуск Python telegram_manager программы в фоновом режиме
python telegram_manager.py
