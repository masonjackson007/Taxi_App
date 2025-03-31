FROM python:3.12-slim
WORKDIR /Taxi_App/backend
COPY backend_requirements.txt .
RUN pip install --no-cache-dir -r backend_requirements.txt
COPY . .
CMD ["python", "backend.py"]