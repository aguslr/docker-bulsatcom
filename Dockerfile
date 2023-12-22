ARG BASE_IMAGE=library/debian:buster-slim

FROM docker.io/${BASE_IMAGE}

RUN \
  apt-get update && \
  env DEBIAN_FRONTEND=noninteractive \
  apt-get install -y python2 python-pip \
  -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" \
  && apt-get clean && rm -rf /var/lib/apt/lists/* /var/lib/apt/lists/* && \
  mkdir -p /data && chown -R www-data:www-data /data

COPY bsc.py /usr/local/bin
COPY requirements.txt /
COPY entrypoint.sh /entrypoint.sh

RUN pip install -r /requirements.txt

WORKDIR /data

EXPOSE 8000/tcp

VOLUME /data

HEALTHCHECK --interval=1m --timeout=3s \
  CMD timeout 2 bash -c 'cat < /dev/null > /dev/tcp/127.0.0.1/8000'

USER www-data
ENTRYPOINT ["/entrypoint.sh"]
CMD ["--cache", "--debug", "--epg"]
