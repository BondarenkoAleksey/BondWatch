#!/bin/bash
set -e

# Выполняем миграции Alembic
echo "🔄 Выполняем миграции Alembic..."
alembic upgrade head

# Запускаем основной процесс
exec "$@"
