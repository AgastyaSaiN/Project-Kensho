FROM python:3.11-slim

# Install system dependencies for Qt
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libegl1-mesa \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set PYTHONPATH so we can import 'kensho' package
ENV PYTHONPATH=/app/src

# Create directory for persistence
RUN mkdir -p /root/.kensho

# Entry point
CMD ["python", "-m", "kensho.app"]
