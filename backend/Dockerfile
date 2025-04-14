FROM python:3.12-slim
WORKDIR /Taxi_App/backend
COPY backend_requirements.txt .
RUN pip install --no-cache-dir -r backend_requirements.txt
COPY . .
RUN mkdir -p /var/log/gunicorn
CMD ["gunicorn", "--config", "gunicorn.conf.py", "backend:app"]