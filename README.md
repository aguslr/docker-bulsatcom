[aguslr/docker-bulsatcom][1]
============================

[![publish-docker-image](https://github.com/aguslr/docker-bulsatcom/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/aguslr/docker-bulsatcom/actions/workflows/docker-publish.yml) [![docker-pulls](https://img.shields.io/docker/pulls/aguslr/bulsatcom)](https://hub.docker.com/r/aguslr/bulsatcom) [![image-size](https://img.shields.io/docker/image-size/aguslr/bulsatcom/latest)](https://hub.docker.com/r/aguslr/bulsatcom)


This *Docker* image downloads M3U and EPG files from *Bulsatcom*'s IPTV service.

> **[Bulsatcom][2]** is Bulgarian satellite television, internet & mobile
> operator, founded in 2000 as the first DVB-S operator in the country.

It's a refactoring of Vasil Valchev's [IPTV Kodi add-on for Bulsatcom][3].


Installation
------------

To use *docker-bulsatcom*, follow these steps:

1. Clone and start the container:

       docker run -v ./data:/data \
         -e BULSAT_USERNAME=me@mail.com \
         -e BULSAT_PASSWORD=123456 \
         docker.io/aguslr/bulsatcom:latest --epg

2. Access the files `bulsat.m3u` and  `bulsat.xml` inside `./data` directory.


### Variables

The image is configured using environment variables passed at runtime. All these
variables are prefixed by `BULSAT_`.

| Variable    | Function                                | Default |
| :---------- | :-------------------------------------- | :------ |
| `USERNAME`  | Username for Bulsatcom                  | `test`  |
| `PASSWORD`  | Password for Bulsatcom                  | `test`  |
| `OUTPUT`    | Output directory for files              | `/data` |
| `TIMEOUT`   | Timeout in seconds                      | 10      |
| `WAIT`      | Wait time between updates               | 300     |
| `EPG`       | Download EPG                            | False   |
| `CACHE`     | Enable cache                            | False   |
| `BLOCK`     | Comma separated list of genres to block | EMPTY   |


Build locally
-------------

Instead of pulling the image from a remote repository, you can build it locally:

1. Clone the repository:

       git clone https://github.com/aguslr/docker-bulsatcom.git

2. Change into the newly created directory and use `docker-compose` to build and
   launch the container:

       cd docker-bulsatcom && docker-compose up --build -d


[1]: https://github.com/aguslr/docker-bulsatcom
[2]: https://www.bulsatcom.bg/
[3]: https://github.com/vastril4o/iptv.bsc
