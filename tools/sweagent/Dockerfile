FROM python:3.12-slim
ARG DEBIAN_FRONTEND=noninteractive
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends git patch && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
ENV PYTHONUNBUFFERED=1
CMD ["python", "-u", "app.py"]
