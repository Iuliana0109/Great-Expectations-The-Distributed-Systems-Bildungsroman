# Use official Python image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Install required packages for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY . .

# Expose the Flask port
EXPOSE 5001

# Run the Flask app
CMD ["python", "app.py"]
