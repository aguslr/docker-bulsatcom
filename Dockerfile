ARG BASE_IMAGE=library/debian:stable-slim

FROM docker.io/${BASE_IMAGE}

RUN \
  apt-get update && \
  env DEBIAN_FRONTEND=noninteractive \
  apt-get install -y python-is-python3 python3-pyaes python3-requests \
  -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" \
  && apt-get clean && rm -rf /var/lib/apt/lists/* /var/lib/apt/lists/*

COPY src /src
COPY entrypoint.sh /entrypoint.sh

WORKDIR /data

VOLUME /data

ENTRYPOINT ["/entrypoint.sh"]
CMD ["--debug"]
