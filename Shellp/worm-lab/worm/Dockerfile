FROM ubuntu:22.04
RUN apt-get update && apt-get install -y bash coreutils netcat
COPY replicator.sh /replicator.sh
RUN chmod +x /replicator.sh
CMD ["/replicator.sh"]

