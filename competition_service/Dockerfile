FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for PostgreSQL and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies in a single command for reduced layers
RUN pip install Flask Flask-SQLAlchemy Flask-Bcrypt Flask-JWT-Extended \
    tenacity psycopg2-binary python-dotenv Flask-SocketIO eventlet \
    dnspython Werkzeug SQLAlchemy requests redis websockets gunicorn

# Copy the current directory contents into the container at /app
COPY . /app

# Expose the ports the app and websocket use
EXPOSE 5001
EXPOSE 6480

# Run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "--timeout", "30", "app:app"]