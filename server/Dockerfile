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
ARG TARGETARCH
# The same Syncthing (Link my computer, sharing) and rclone (a memory on WebDAV) as the desktop app
# (core/packaging/bundle_server.py), checked against their published SHA-256. procps: pkill. fuse3: the WebDAV drive.
# git: the GitHub backup.
ARG SYNCTHING=2.1.7 RCLONE=1.75.2
RUN apt-get update \
 && apt-get install -y --no-install-recommends procps fuse3 git ca-certificates tini curl unzip \
 && case "$TARGETARCH" in \
      amd64) ST=2edc416e7ed136b7c858ed5f3f02a3b8316589605e54c380228ceea7acbf0142 RC=349ac8fba6ff65d6247043f1750cdcb518ec5d500ef91463a10d37c0ccdf3702 ;; \
      arm64) ST=48e456690cd2b97e7d26b02b5ac35f62a3b36172267b144cfeaf02c993ab955c RC=7e1e8d69654941b7b7df84ee74c5f7fb09cce7d5496947fb7bf16b55ff427d10 ;; \
      *) echo "Unsupported: $TARGETARCH" && exit 1 ;; esac \
 && cd /tmp \
 && curl -fsSLo st.tgz "https://github.com/syncthing/syncthing/releases/download/v$SYNCTHING/syncthing-linux-$TARGETARCH-v$SYNCTHING.tar.gz" \
 && echo "$ST  st.tgz" | sha256sum -c - \
 && tar -xzf st.tgz && mv "syncthing-linux-$TARGETARCH-v$SYNCTHING/syncthing" /usr/local/bin/ \
 && curl -fsSLo rc.zip "https://downloads.rclone.org/v$RCLONE/rclone-v$RCLONE-linux-$TARGETARCH.zip" \
 && echo "$RC  rc.zip" | sha256sum -c - \
 && unzip -q rc.zip && mv "rclone-v$RCLONE-linux-$TARGETARCH/rclone" /usr/local/bin/ \
 && rm -rf /tmp/* && apt-get purge -y curl unzip && apt-get autoremove -y \
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
