ARG BASE_IMAGE=library/debian:buster-slim

FROM docker.io/${BASE_IMAGE}

RUN \
  apt-get update && \
  env DEBIAN_FRONTEND=noninteractive \
  apt-get install -y python2 python-pip \
  -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" \
  && apt-get clean && rm -rf /var/lib/apt/lists/* /var/lib/apt/lists/* && \
  mkdir -p /data && chown -R www-data:www-data /data

COPY src/main.py /usr/local/bin/bsc.py
COPY src/requirements.txt /
COPY entrypoint.sh /entrypoint.sh

RUN pip install -r /requirements.txt

WORKDIR /data

VOLUME /data

USER www-data
ENTRYPOINT ["/entrypoint.sh"]
CMD ["--debug"]
