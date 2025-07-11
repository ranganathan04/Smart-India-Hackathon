# Use an official Python image
FROM python:3.10-slim

# Install system packages (including tesseract)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port
EXPOSE 5000

# Run the Flask app
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
