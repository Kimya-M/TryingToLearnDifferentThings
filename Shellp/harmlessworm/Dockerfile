FROM ubuntu:20.04

RUN apt update && apt install -y bash coreutils
COPY harmlesswormonlystudyreasons.sh /replicator.sh
RUN chmod +x /replicator.sh

WORKDIR /
CMD ["./replicator.sh"]
