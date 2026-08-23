FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ .

# Expose port
EXPOSE 5000

# Environment variables
ENV MODEL_VERSION=v1
ENV MONITOR_SERVICE_URL=http://monitor:5001

# Run application
CMD ["python", "app.py"]
