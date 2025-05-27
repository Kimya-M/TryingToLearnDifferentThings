FROM python:3.10-slim
WORKDIR /app
COPY weak_ssh.py .
# Install useful debugging tools:
RUN apt-get update && apt-get install -y procps net-tools lsof
CMD ["python", "-u", "weak_ssh.py"]

