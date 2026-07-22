FROM python:3.11-slim

ARG GITHUB_TOKEN=""

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install rpa-core SDK with token authentication
RUN if [ -n "$GITHUB_TOKEN" ]; then \
      AUTH_TOKEN="$GITHUB_TOKEN"; \
      case "$GITHUB_TOKEN" in \
        github_pat_*) AUTH_TOKEN="x-access-token:${GITHUB_TOKEN}" ;; \
      esac; \
      pip install --no-cache-dir "rpa-core @ git+https://${AUTH_TOKEN}@github.com/currentlib/lattice-rpa-core-sdk.git"; \
    else \
      pip install --no-cache-dir "rpa-core @ git+https://github.com/currentlib/lattice-rpa-core-sdk.git"; \
    fi

COPY main.py .

CMD ["python", "main.py"]
