 FROM python:3.11-slim

  ENV PYTHONUNBUFFERED=1
  ENV PYTHONDONTWRITEBYTECODE=1

  WORKDIR /app

  # Install system dependencies
  RUN apt-get update && apt-get install -y \
      gcc \
      g++ \
      && rm -rf /var/lib/apt/lists/*

  # Copy requirements and install Python dependencies
  COPY ./requirements.txt /app/requirements.txt
  RUN pip install --no-cache-dir --upgrade pip && \
      pip install --no-cache-dir -r requirements.txt

  # Copy the application code
  COPY . /app

  # Expose port 7860 (Hugging Face default)
  EXPOSE 7860

  # Create a non-root user for security
  RUN useradd --create-home --shell /bin/bash --uid 1000 app && chown -R app:app /app
  USER app

  # Run the application on port 7860
  CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
