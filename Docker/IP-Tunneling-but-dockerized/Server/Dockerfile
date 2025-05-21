FROM python:3.8-slim

WORKDIR /app
COPY . /app 
COPY ../common /app/common

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "Server.py"]
