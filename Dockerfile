# Use official Python base image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Install Tesseract and required libraries
RUN apt-get update && \
    apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    pkg-config \
    poppler-utils \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the port (optional)
EXPOSE 5000

# Command to run the app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
