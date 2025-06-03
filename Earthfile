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

# Base image for TimescaleDB
timescale-base:
    ARG CLOUDNATIVEPG_VERSION
    FROM ghcr.io/cloudnative-pg/postgresql:$CLOUDNATIVEPG_VERSION

# Base image for Supabase
supabase-base:
    ARG PG_VERSION
    FROM supabase/postgres:$PG_VERSION

# TimescaleDB image based on CloudNativePG PostgreSQL
timescale-build:
    FROM +timescale-base
    USER root
    ARG POSTGRES_VERSION
    ARG TIMESCALE_VERSION
    ARG PG_MAJOR
    ARG VERSION
    ARG GIT_SHA
    ARG DOCKER_IMAGE_TIMESCALE
    
    # Validate required arguments
    RUN --no-cache test -n "$POSTGRES_VERSION" || (echo "POSTGRES_VERSION is required" && exit 1)
    RUN --no-cache test -n "$TIMESCALE_VERSION" || (echo "TIMESCALE_VERSION is required" && exit 1)
    RUN --no-cache test -n "$PG_MAJOR" || (echo "PG_MAJOR is required" && exit 1)
    RUN --no-cache test -n "$DOCKER_IMAGE_TIMESCALE" || (echo "DOCKER_IMAGE_TIMESCALE is required" && exit 1)

    # Install TimescaleDB
    RUN set -eux && \
        apt-get update && \
        apt-get install -y --no-install-recommends curl && \
        . /etc/os-release && \
        echo "deb https://packagecloud.io/timescale/timescaledb/debian/ $VERSION_CODENAME main" > /etc/apt/sources.list.d/timescaledb.list && \
        curl -Lsf https://packagecloud.io/timescale/timescaledb/gpgkey | gpg --dearmor > /etc/apt/trusted.gpg.d/timescale.gpg && \
        apt-get update && \
        apt-get install -y --no-install-recommends "timescaledb-2-postgresql-$PG_MAJOR=$TIMESCALE_VERSION~debian$VERSION_ID" && \
        apt-get purge -y curl && \
        rm /etc/apt/sources.list.d/timescaledb.list /etc/apt/trusted.gpg.d/timescale.gpg && \
        rm -rf /var/cache/apt/* /var/lib/apt/lists/*

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
    LET VERSION_INFO=$VERSION
    LET GIT_SHA_INFO=$GIT_SHA
    RUN echo "Version: $VERSION_INFO" > /version.txt && \
        echo "Git SHA: $GIT_SHA_INFO" >> /version.txt && \
        echo "Component versions:" >> /version.txt && \
        cat version-info >> /version.txt

    USER postgres
    EXPOSE 5432

    # Save the image with explicit push flag
    SAVE IMAGE --push $DOCKER_IMAGE_TIMESCALE

# Supabase image based on Supabase PostgreSQL
supabase-build:
    FROM +supabase-base
    USER root
    ARG PG_VERSION
    ARG PG_MAJOR
    ARG DEBIAN_FRONTEND=noninteractive
    ARG VERSION
    ARG GIT_SHA
    ARG DOCKER_IMAGE_SUPABASE
    
    # Validate required arguments
    RUN --no-cache test -n "$PG_VERSION" || (echo "PG_VERSION is required" && exit 1)
    RUN --no-cache test -n "$DOCKER_IMAGE_SUPABASE" || (echo "DOCKER_IMAGE_SUPABASE is required" && exit 1)

    # Extract PG_MAJOR from the Supabase version if not provided
    # Supabase images use format like 15.1.0.137 where 15 is the major version
    RUN if [ -z "$PG_MAJOR" ] && [ -n "$PG_VERSION" ]; then \
        PG_MAJOR=$(echo "$PG_VERSION" | cut -d'.' -f1); \
        echo "Extracted PG_MAJOR=$PG_MAJOR from PG_VERSION=$PG_VERSION"; \
    fi

    # Install PostgreSQL common and additional extensions
    RUN apt-get update && apt-get install -y postgresql-common && /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y

    # Install additional extensions
    RUN set -xe && \
        apt-get update && \
        apt-get install -y --no-install-recommends \
            "postgresql-${PG_MAJOR}-pg-failover-slots" && \
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
    LET VERSION_INFO=$VERSION
    LET GIT_SHA_INFO=$GIT_SHA
    RUN echo "Version: $VERSION_INFO" > /version.txt && \
        echo "Git SHA: $GIT_SHA_INFO" >> /version.txt && \
        echo "Component versions:" >> /version.txt && \
        cat version-info >> /version.txt

    USER postgres
    EXPOSE 5432

    # Save the image with explicit push flag
    SAVE IMAGE --push $DOCKER_IMAGE_SUPABASE

# Build both images in sequence
all:
    BUILD +timescale-build
    BUILD +supabase-build


















