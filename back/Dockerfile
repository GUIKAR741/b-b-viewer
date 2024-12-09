FROM python:3.13.0-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--log-level", "info", "--log-config", "logger.conf", "--worker-class", "gevent", "--timeout", "0", "wsgi:app" ]