#!/bin/sh
set -e

echo "==> Running database migrations (alembic upgrade head)..."
alembic upgrade head

echo "==> Starting backend server..."
exec "$@"
