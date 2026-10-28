# Phygital Memory Server

The files to run Phygital Memory on your own server. The guide is [Run it on your own server](../docs/server.md).

| File | What it is |
|---|---|
| [`compose.yaml`](compose.yaml) | Docker Compose: the server, and Caddy in front of it for HTTPS |
| [`.env.example`](.env.example) | The one setting Compose needs (your domain). Copy it to `.env` |
| [`Dockerfile`](Dockerfile) | How the image is built. Each release builds it on GitHub as `ghcr.io/phygital-brain/phygital-memory` |
| [`Dockerfile.dockerignore`](Dockerfile.dockerignore) | What the build may read from the repository |

The Render file is [`render.yaml`](../render.yaml) at the top of the repository, because the Deploy to Render button looks for it there.

To build the image yourself, from the top of the repository:

```bash
docker build -f server/Dockerfile -t phygital-memory .
```
