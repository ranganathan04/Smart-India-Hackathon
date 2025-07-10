FROM python:3.10-slim

WORKDIR /app

# Install Tesseract OCR system-wide
RUN apt-get update && apt-get install -y tesseract-ocr

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Start app using gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
