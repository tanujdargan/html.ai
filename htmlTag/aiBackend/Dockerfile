# 1. Base image
FROM python:3.11-slim

# 2. Workdir
WORKDIR /app

# 3. Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy source
COPY . .

# 5. Run the server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "3000"]