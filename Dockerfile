# Build v2 - Clear cache
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

EXPOSE 5000

CMD gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} app:app
