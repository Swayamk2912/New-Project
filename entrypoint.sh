#!/bin/sh

# Wait for Redis to be available
/app/wait-for-redis.sh redis 6379 -- echo "Redis is up and running!"
sleep 5 # Give DNS a moment to settle

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Start Gunicorn
exec "$@"
