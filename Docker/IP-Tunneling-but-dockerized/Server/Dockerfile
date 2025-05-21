FROM python:3.8-slim

WORKDIR /app
COPY . /app 

# Install system dependencies
RUN apt-get update && \
    apt-get install -y libpcap-dev tcpdump && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "Server.py"]
