VERSION 0.8

ARG CLOUDNATIVEPG_VERSION
ARG GIT_SHA
ARG DOCKER_IMAGE_TIMESCALE
ARG DOCKER_IMAGE_SUPABASE
ARG VERSION
ARG POSTGRES_VERSION
ARG TIMESCALE_VERSION
ARG PG_VERSION
ARG PG_MAJOR

# TimescaleDB image based on CloudNativePG PostgreSQL
timescale-build:
    FROM ghcr.io/cloudnative-pg/postgresql:${CLOUDNATIVEPG_VERSION}
    USER root
    ARG POSTGRES_VERSION
    ARG TIMESCALE_VERSION
    ARG PG_MAJOR
    RUN --no-cache test -n "$POSTGRES_VERSION" || (echo "POSTGRES_VERSION is required" && exit 1)
    RUN --no-cache test -n "$TIMESCALE_VERSION" || (echo "TIMESCALE_VERSION is required" && exit 1)
    RUN --no-cache test -n "$PG_MAJOR" || (echo "PG_MAJOR is required" && exit 1)

    # Install TimescaleDB
    RUN set -eux && \
        apt-get update && \
        apt-get install -y --no-install-recommends curl && \
        . /etc/os-release && \
        echo "deb https://packagecloud.io/timescale/timescaledb/debian/ $VERSION_CODENAME main" > /etc/apt/sources.list.d/timescaledb.list && \
        curl -Lsf https://packagecloud.io/timescale/timescaledb/gpgkey | gpg --dearmor > /etc/apt/trusted.gpg.d/timescale.gpg && \
        apt-get update && \
        apt-get install -y --no-install-recommends timescaledb-2-postgresql-${PG_MAJOR}=${TIMESCALE_VERSION}~debian11 && \
        apt-get purge -y curl && \
        rm /etc/apt/sources.list.d/timescaledb.list /etc/apt/trusted.gpg.d/timescale.gpg && \
        rm -rf /var/cache/apt/*

    # Install barman-cloud
    COPY requirements.txt /
    RUN set -xe && \
        apt-get update && \
        apt-get install -y --no-install-recommends \
            build-essential python3-dev libsnappy-dev \
            python3-pip \
            python3-psycopg2 \
            python3-setuptools && \
        pip3 install --upgrade pip && \
        pip3 install --no-deps -r requirements.txt && \
        apt-get remove -y --purge --autoremove \
            build-essential \
            python3-dev \
            libsnappy-dev && \
        rm -rf /var/lib/apt/lists/*

    # Common setup
    RUN set -xe && \
        mkdir -p /etc/postgresql-custom && \
        chmod 777 /var/run/postgresql && \
        chown -R postgres:postgres /var/run/postgresql && \
        chmod 777 /etc/postgresql-custom

    # Copy and set version information
    COPY VERSION ./version-info
    ARG VERSION
    ARG GIT_SHA
    RUN echo "Version: $VERSION" > /version.txt && \
        echo "Git SHA: $GIT_SHA" >> /version.txt && \
        echo "Component versions:" >> /version.txt && \
        cat version-info >> /version.txt

    USER postgres
    ARG DOCKER_IMAGE_TIMESCALE
    EXPOSE 5432

    SAVE IMAGE ${DOCKER_IMAGE_TIMESCALE}

# Supabase image based on Supabase PostgreSQL
supabase-build:
    FROM supabase/postgres:${PG_MAJOR}
    USER root
    ARG POSTGRES_VERSION
    ARG DEBIAN_FRONTEND=noninteractive

    # Install PostgreSQL common and additional extensions
    RUN apt-get update && apt-get install -y postgresql-common && /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y

    # Install additional extensions
    RUN set -xe && \
        apt-get update && \
        apt-get install -y --no-install-recommends postgresql-${PG_MAJOR}-pg-failover-slots && \
        rm -fr /tmp/* && \
        rm -rf /var/lib/apt/lists/*

    # Install barman-cloud
    COPY requirements.txt /
    RUN set -xe && \
        apt-get update && \
        apt-get install -y --no-install-recommends \
            build-essential python3-dev libsnappy-dev \
            python3-pip \
            python3-psycopg2 \
            python3-setuptools && \
        pip3 install --upgrade pip && \
        pip3 install --no-deps -r requirements.txt && \
        apt-get remove -y --purge --autoremove \
            build-essential \
            python3-dev \
            libsnappy-dev && \
        rm -rf /var/lib/apt/lists/*

    # Common setup
    RUN set -xe && \
        mkdir -p /etc/postgresql-custom && \
        chmod 777 /var/run/postgresql && \
        chown -R postgres:postgres /var/run/postgresql && \
        chmod 777 /etc/postgresql-custom

    # Copy and set version information
    COPY VERSION ./version-info
    ARG VERSION
    ARG GIT_SHA
    RUN echo "Version: $VERSION" > /version.txt && \
        echo "Git SHA: $GIT_SHA" >> /version.txt && \
        echo "Component versions:" >> /version.txt && \
        cat version-info >> /version.txt

    USER postgres
    ARG DOCKER_IMAGE_SUPABASE
    EXPOSE 5432

    SAVE IMAGE ${DOCKER_IMAGE_SUPABASE}

# Build both images in sequence
all:
    BUILD +timescale-build
    BUILD +supabase-build


















