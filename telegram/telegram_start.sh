#!/bin/bash

# Запуск Python telegram_helper программы в фоновом режиме
python telegram_helper.py &

# Запуск Python telegram_manager программы в фоновом режиме
python telegram_manager.py
