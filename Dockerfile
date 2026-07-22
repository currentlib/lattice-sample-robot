FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

# Git is required for pip to install the rpa-core repository
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install both dependencies directly, bypassing the requirements.txt file
RUN python3 -m pip install --no-cache-dir "git+https://github.com/currentlib/lattice-rpa-core-sdk.git" requests==2.32.3

COPY main.py .

CMD ["python3", "main.py"]