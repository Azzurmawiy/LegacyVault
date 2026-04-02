FROM python:3.13-slim

# Prevent .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Collect static files into staticfiles/ so WhiteNoise can serve them
# SECRET_KEY is only needed by Django's settings loader at build time
RUN SECRET_KEY=build-phase-placeholder \
    DATABASE_URL=sqlite:///tmp/build.db \
    python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "legacyvault.wsgi", "--bind", "0.0.0.0:8000", "--log-file", "-"]
