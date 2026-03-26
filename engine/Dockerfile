FROM python:3.12-slim

WORKDIR /src

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer cache)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy engine source as a package under /src/engine/
COPY . ./engine/

EXPOSE 8001

CMD ["uvicorn", "engine.main:app", "--host", "0.0.0.0", "--port", "8001"]
