FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

# Install git (the Microsoft image is Ubuntu-based, so apt-get works exactly the same)
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The Microsoft image already contains the browsers and system dependencies.
# We do not need RUN playwright install or RUN playwright install-deps here.

COPY main.py .

CMD ["python", "main.py"]