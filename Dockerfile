FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Removed the unsupported flag. This will now install 'requests' cleanly.
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["python", "main.py"]