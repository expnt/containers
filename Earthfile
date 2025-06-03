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

# Minimal base image
minimal-base:
    FROM debian:bullseye-slim
    RUN set -xe && \
        apt-get update && \
        apt-get install -y --no-install-recommends \
            ca-certificates \
            wget \
            gnupg \
            lsb-release && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/* && \
        mkdir -p /etc/postgresql-custom /var/run/postgresql && \
        chmod 777 /var/run/postgresql && \
        chmod 777 /etc/postgresql-custom

# Python deps builder - only for building, output won't be in final image
python-builder:
    FROM python:3.9-slim-bullseye
    WORKDIR /build
    COPY requirements.txt .
    
    # Install only what's absolutely necessary for building
    RUN set -xe && \
        pip install --upgrade pip wheel && \
        pip install --no-cache-dir --prefix=/install --no-deps -r requirements.txt

# Base image for TimescaleDB
timescale-base:
    ARG CLOUDNATIVEPG_VERSION
    FROM ghcr.io/cloudnative-pg/postgresql:$CLOUDNATIVEPG_VERSION

# Base image for Supabase
supabase-base:
    ARG PG_VERSION
    FROM supabase/postgres:$PG_VERSION

# TimescaleDB image with minimal footprint
timescale-build:
    FROM +timescale-base AS base
    USER root
    
    # Set up arguments
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

    # Install TimescaleDB in a single layer with proper cleanup
    RUN set -eux && \
        apt-get update && \
        apt-get install -y --no-install-recommends curl && \
        . /etc/os-release && \
        echo "deb https://packagecloud.io/timescale/timescaledb/debian/ $VERSION_CODENAME main" > /etc/apt/sources.list.d/timescaledb.list && \
        curl -Lsf https://packagecloud.io/timescale/timescaledb/gpgkey | gpg --dearmor > /etc/apt/trusted.gpg.d/timescale.gpg && \
        apt-get update && \
        apt-get install -y --no-install-recommends "timescaledb-2-postgresql-$PG_MAJOR=$TIMESCALE_VERSION~debian$VERSION_ID" && \
        apt-get purge -y curl && \
        apt-get clean && \
        apt-get autoremove -y && \
        rm -rf /etc/apt/sources.list.d/timescaledb.list /etc/apt/trusted.gpg.d/timescale.gpg \
               /var/lib/apt/lists/* /tmp/* /var/tmp/* /var/cache/apt/* \
               /usr/share/doc/* /usr/share/man/* /usr/share/info/* && \
        mkdir -p /etc/postgresql-custom /var/run/postgresql && \
        chmod 777 /var/run/postgresql && \
        chmod 777 /etc/postgresql-custom && \
        find /usr -name "*.a" -delete && \
        find /usr -name "*.la" -delete

    # Copy only necessary Python packages from builder
    COPY --from=+python-builder /install /usr/local
    
    # Copy version information
    COPY VERSION ./version-info
    LET VERSION_INFO=$VERSION
    LET GIT_SHA_INFO=$GIT_SHA
    RUN echo "Version: $VERSION_INFO" > /version.txt && \
        echo "Git SHA: $GIT_SHA_INFO" >> /version.txt && \
        echo "Component versions:" >> /version.txt && \
        cat version-info >> /version.txt && \
        chown -R postgres:postgres /var/run/postgresql /etc/postgresql-custom

    USER postgres
    EXPOSE 5432

    # Save the optimized image
    SAVE IMAGE --push $DOCKER_IMAGE_TIMESCALE

# Supabase image with minimal footprint
supabase-build:
    FROM +supabase-base AS base
    USER root
    
    # Set up arguments
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
    RUN if [ -z "$PG_MAJOR" ] && [ -n "$PG_VERSION" ]; then \
        PG_MAJOR=$(echo "$PG_VERSION" | cut -d'.' -f1); \
        echo "Extracted PG_MAJOR=$PG_MAJOR from PG_VERSION=$PG_VERSION"; \
    fi

    # Install extensions in a single layer with aggressive cleanup
    RUN set -xe && \
        apt-get update && \
        apt-get install -y --no-install-recommends postgresql-common && \
        /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y && \
        apt-get update && \
        apt-get install -y --no-install-recommends "postgresql-${PG_MAJOR}-pg-failover-slots" && \
        apt-get clean && \
        apt-get autoremove -y && \
        rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /var/cache/apt/* \
               /usr/share/doc/* /usr/share/man/* /usr/share/info/* && \
        mkdir -p /etc/postgresql-custom /var/run/postgresql && \
        chmod 777 /var/run/postgresql && \
        chmod 777 /etc/postgresql-custom && \
        find /usr -name "*.a" -delete && \
        find /usr -name "*.la" -delete

    # Copy only necessary Python packages from builder
    COPY --from=+python-builder /install /usr/local
    
    # Copy version information
    COPY VERSION ./version-info
    LET VERSION_INFO=$VERSION
    LET GIT_SHA_INFO=$GIT_SHA
    RUN echo "Version: $VERSION_INFO" > /version.txt && \
        echo "Git SHA: $GIT_SHA_INFO" >> /version.txt && \
        echo "Component versions:" >> /version.txt && \
        cat version-info >> /version.txt && \
        chown -R postgres:postgres /var/run/postgresql /etc/postgresql-custom

    USER postgres
    EXPOSE 5432

    # Save the optimized image
    SAVE IMAGE --push $DOCKER_IMAGE_SUPABASE

# Build both images in sequence
all:
    BUILD +timescale-build
    BUILD +supabase-build


















