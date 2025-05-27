VERSION 0.8

ARG GIT_SHA
ARG DOCKER_IMAGE

base-img:
    FROM ghcr.io/cloudnative-pg/postgresql:17.4-13-bookworm

deps:
    FROM +base-img
    
    USER root

    ARG DEBIAN_FRONTEND=noninteractive

    RUN apt-get update && apt-get install -y --no-install-recommends \
        wget gnupg lsb-release && \
        wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | gpg --dearmor -o /etc/apt/trusted.gpg.d/timescaledb.gpg && \
        echo "deb [signed-by=/etc/apt/trusted.gpg.d/timescaledb.gpg] https://packagecloud.io/timescale/timescaledb/debian/ $(lsb_release -cs) main" > /etc/apt/sources.list.d/timescaledb.list

    RUN apt-get update && apt-get install -y --no-install-recommends \
        timescaledb-2-postgresql-17 \
        timescaledb-tools \
        && rm -rf /var/lib/apt/lists/*
    
    SAVE ARTIFACT /usr/lib/postgresql/17/lib/timescaledb.so AS LOCAL ./artifacts/timescaledb.so

    SAVE ARTIFACT /usr/share/postgresql/17/extension/timescaledb* AS LOCAL ./artifacts/

build:
    FROM +base-img
    
    USER root

    COPY +deps/timescaledb.so /usr/lib/postgresql/17/lib/

    COPY +deps/timescaledb* /usr/share/postgresql/17/extension/

    USER postgres

    ARG DOCKER_IMAGE

    ARG GIT_SHA

    EXPOSE 5432
    
    SAVE IMAGE --push ${DOCKER_IMAGE}












