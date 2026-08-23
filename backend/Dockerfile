FROM python:3.11-slim

WORKDIR /app

# Install build dependencies ringan
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU wheel langsung (Hanya ~150MB, selesai dalam hitungan detik)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Salin dan install sisa requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode aplikasi, dataset, dan saved_models
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]