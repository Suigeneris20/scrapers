FROM mcr.microsoft.com/playwright/python:v1.51.0-jammy

# Install additional system dependencies if needed
# RUN apt-get update && apt-get install -y libpq-dev

# Set working directory
WORKDIR /app

# Copy your requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Python script
COPY . .

CMD ["python", "main.py"]

