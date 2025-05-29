VERSION 0.8

ARG GIT_SHA
ARG DOCKER_IMAGE
ARG VERSION

base-img:
    FROM ghcr.io/cloudnative-pg/postgresql:17.4-13-bookworm

deps:
    FROM +base-img
    
    USER root

    ARG DEBIAN_FRONTEND=noninteractive

    RUN apt-get update && apt-get install -y --no-install-recommends \
        wget gnupg lsb-release ca-certificates curl

    # Add TimescaleDB GPG key and repository
    RUN wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | \
        gpg --dearmor -o /etc/apt/trusted.gpg.d/timescaledb.gpg && \
        echo "deb [signed-by=/etc/apt/trusted.gpg.d/timescaledb.gpg] https://packagecloud.io/timescale/timescaledb/debian/ $(lsb_release -cs) main" > /etc/apt/sources.list.d/timescaledb.list

    # Install TimescaleDB and tools
    RUN apt-get update && apt-get install -y --no-install-recommends \
        timescaledb-2-postgresql-17 timescaledb-tools && \
        rm -rf /var/lib/apt/lists/*

    # Save TimescaleDB artifacts
    SAVE ARTIFACT /usr/lib/postgresql/17/lib/timescaledb.so
    SAVE ARTIFACT /usr/share/postgresql/17/extension/timescaledb*

    # Download and save Supabase SQL schemas (auth, storage, etc.)
    # (Removed due to unavailable URLs and not needed for now)

# Build target: Assembles the final image
build:
    FROM +base-img
    
    USER root

    # Copy TimescaleDB artifacts
    COPY +deps/timescaledb.so /usr/lib/postgresql/17/lib/

    COPY +deps/timescaledb* /usr/share/postgresql/17/extension/

    # Add version information
    ARG VERSION
    ARG GIT_SHA
    RUN echo "Version: $VERSION" > /version.txt && \
        echo "Git SHA: $GIT_SHA" >> /version.txt 
    

    USER postgres

    ARG DOCKER_IMAGE

    EXPOSE 5432

    # Save image (push in CI, use --local for local testing)
    SAVE IMAGE $DOCKER_IMAGE











