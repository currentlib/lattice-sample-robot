FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

# Added build-essential to compile any C-extensions the SDK might use
RUN apt-get update && apt-get install -y --no-install-recommends git build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip and install core build tools before trying to install the SDK
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Install the dependencies from the public repo
RUN python3 -m pip install --no-cache-dir "git+https://github.com/currentlib/lattice-rpa-core-sdk.git" requests==2.32.3

COPY main.py .

CMD ["python3", "main.py"]