# Phygital Memory Server: the app's engine with no window, for your own server (docs/server.md).
# Built from the top of the repository:  docker build -f server/Dockerfile -t phygital-memory .

# ---- the app's screens (the same ones the desktop app shows) ----
FROM node:22-slim AS page
WORKDIR /src/core/frontend
COPY core/frontend/package.json core/frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY core/frontend/ ./
COPY core/languages/ ../languages/
RUN npm run build

# ---- the engine ----
FROM python:3.14-slim
ARG VERSION=dev
# syncthing: Link my computer and sharing. rclone and fuse3: a memory on WebDAV. git: the GitHub backup.
RUN apt-get update \
 && apt-get install -y --no-install-recommends syncthing rclone fuse3 git ca-certificates tini \
 && rm -rf /var/lib/apt/lists/* \
 && useradd --create-home --uid 1000 memory \
 && mkdir -p /data && chown memory:memory /data
COPY --from=ghcr.io/astral-sh/uv:0.11.19 /uv /usr/local/bin/uv
WORKDIR /app
COPY core/pyproject.toml core/uv.lock LICENSE ./core/
RUN cd core && sed -i 's|"\.\./LICENSE"|"LICENSE"|' pyproject.toml \
 && UV_PROJECT_ENVIRONMENT=/app/venv uv sync --frozen --no-dev --no-install-project
COPY core/phygital_memory/ ./core/phygital_memory/
COPY --from=page /src/core/phygital_memory/web/ ./core/phygital_memory/web/
ENV PATH=/app/venv/bin:$PATH \
    PYTHONPATH=/app/core \
    PYTHONUNBUFFERED=1 \
    HOME=/data/home \
    PHYGITAL_MEMORY_SERVER=1 \
    PHYGITAL_MEMORY_VERSION=$VERSION \
    PHYGITAL_MEMORY_DATA=/data \
    PHYGITAL_MEMORY_STATE=/data/state \
    PHYGITAL_MEMORY_PORT=8790 \
    PHYGITAL_MEMORY_SYNC_PORT=22000 \
    PHYGITAL_MEMORY_MAC_NAME="Phygital Memory server" \
    PHYGITAL_MEMORY_TRASH=/data/trash
USER memory
VOLUME /data
EXPOSE 8790 22000/tcp 22000/udp
ENTRYPOINT ["tini", "--"]
CMD ["python", "-m", "phygital_memory.server"]
