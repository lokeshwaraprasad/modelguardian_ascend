FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY monitor_service.py .

# Expose port
EXPOSE 5001

# Run application
CMD ["python", "monitor_service.py"]
