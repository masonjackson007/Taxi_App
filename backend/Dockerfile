FROM python:3.11-slim
WORKDIR /Taxi_App/backend
COPY backend_requirements.txt .
RUN pip install --no-cache-dir -r backend_requirements.txt
COPY . .
CMD ["python", "backend.py"]