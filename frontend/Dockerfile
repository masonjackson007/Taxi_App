FROM python:3.12-slim
WORKDIR /Taxi_App/frontend

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY frontend_requirements.txt .
RUN pip install --no-cache-dir -r frontend_requirements.txt
COPY . .
CMD ["streamlit", "run", "frontend.py"]
