FROM python:3.11-slim

ARG GITHUB_TOKEN=""

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN if [ -n "$GITHUB_TOKEN" ]; then \
      AUTH_TOKEN="$GITHUB_TOKEN"; \
      case "$GITHUB_TOKEN" in \
        github_pat_*) AUTH_TOKEN="x-access-token:${GITHUB_TOKEN}" ;; \
      esac; \
      git config --global url."https://${AUTH_TOKEN}@github.com/".insteadOf "https://github.com/"; \
      git config --global url."https://${AUTH_TOKEN}@github.com/".insteadOf "git+https://github.com/"; \
    fi

COPY requirements.txt .
RUN pip install -v --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["python", "main.py"]
