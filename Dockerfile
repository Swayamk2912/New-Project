FROM python:3.10-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Workdir points to the actual Django folder
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first if available
COPY FreelancerM/requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy only project (not the outer folder)
COPY FreelancerM /app
COPY wait-for-redis.sh /app/wait-for-redis.sh
RUN chmod +x /app/wait-for-redis.sh

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "FreelancerM.asgi:application"]
