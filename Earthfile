VERSION 0.8

ARG GIT_SHA
ARG DOCKER_IMAGE
ARG VERSION

# Base CNPG PostgreSQL image
base-img:
    FROM ghcr.io/cloudnative-pg/postgresql:17.4-13-bookworm

# TimescaleDB stage
timescale-deps:
    FROM +base-img
    USER root
    ARG DEBIAN_FRONTEND=noninteractive

    # Install only necessary packages and TimescaleDB
    RUN apt-get update && \
        apt-get install -y --no-install-recommends \
            curl gnupg lsb-release ca-certificates && \
        # Add TimescaleDB repository
        curl -s https://packagecloud.io/install/repositories/timescale/timescaledb/script.deb.sh | bash && \
        # Install TimescaleDB and pgvector
        apt-get install -y --no-install-recommends \
            timescaledb-2-postgresql-17 \
            postgresql-17-pgvector && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

    # Save TimescaleDB artifacts
    SAVE ARTIFACT /usr/lib/postgresql/17/lib/timescaledb.so
    SAVE ARTIFACT /usr/share/postgresql/17/extension/timescaledb*
    SAVE ARTIFACT /usr/lib/postgresql/17/lib/vector.so
    SAVE ARTIFACT /usr/share/postgresql/17/extension/vector*

# Supabase extensions stage
supabase-deps:
    FROM +base-img
    USER root
    ARG DEBIAN_FRONTEND=noninteractive

    # Install only necessary build dependencies
    RUN apt-get update && \
        apt-get install -y --no-install-recommends \
            curl build-essential postgresql-server-dev-17 \
            libcurl4-openssl-dev && \
        # Download and build pg_net
        cd /tmp && \
        curl -sL https://github.com/supabase/pg_net/archive/refs/heads/master.tar.gz | tar xz && \
        cd pg_net-master && \
        make && make install && \
        cd .. && \
        rm -rf pg_net-master && \
        # Cleanup
        apt-get clean && \
        rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

    # Save Supabase extension artifacts
    SAVE ARTIFACT /usr/lib/postgresql/17/lib/pg_net.so
    SAVE ARTIFACT /usr/share/postgresql/17/extension/pg_net*

# Final image with all components
build:
    FROM +base-img
    USER root

    # Copy TimescaleDB extensions
    COPY +timescale-deps/timescaledb.so /usr/lib/postgresql/17/lib/
    COPY +timescale-deps/timescaledb* /usr/share/postgresql/17/extension/
    COPY +timescale-deps/vector.so /usr/lib/postgresql/17/lib/
    COPY +timescale-deps/vector* /usr/share/postgresql/17/extension/

    # Copy Supabase extensions
    COPY +supabase-deps/pg_net.so /usr/lib/postgresql/17/lib/
    COPY +supabase-deps/pg_net* /usr/share/postgresql/17/extension/

    # Set up directories and permissions
    RUN mkdir -p /etc/postgresql-custom && \
        chmod 777 /var/run/postgresql && \
        chown -R postgres:postgres /var/run/postgresql && \
        chmod 777 /etc/postgresql-custom

    # Add version information
    ARG VERSION
    ARG GIT_SHA
    RUN echo "Version: $VERSION" > /version.txt && \
        echo "Git SHA: $GIT_SHA" >> /version.txt 

    USER postgres
    ARG DOCKER_IMAGE
    EXPOSE 5432

    # Save final image
     SAVE IMAGE --push ${DOCKER_IMAGE}











