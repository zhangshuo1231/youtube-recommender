FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Railway uses dynamic PORT)
EXPOSE 8000

# Run the application - let Python handle the PORT env variable
CMD ["python", "main.py"]
