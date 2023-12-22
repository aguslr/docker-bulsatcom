ARG BASE_IMAGE=library/debian:buster-slim

FROM docker.io/${BASE_IMAGE}

RUN \
  apt-get update && \
  env DEBIAN_FRONTEND=noninteractive \
  apt-get install -y python2 python-pyaes python-requests python-xmltv \
  -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" \
  && apt-get clean && rm -rf /var/lib/apt/lists/* /var/lib/apt/lists/* && \
  mkdir -p /data && chown -R www-data:www-data /data

COPY src /src
COPY entrypoint.sh /entrypoint.sh

WORKDIR /data

VOLUME /data

USER www-data
ENTRYPOINT ["/entrypoint.sh"]
CMD ["--debug"]
