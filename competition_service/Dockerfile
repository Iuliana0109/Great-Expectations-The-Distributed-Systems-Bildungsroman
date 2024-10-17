FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for PostgreSQL and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install Flask==2.1.1
RUN pip install Flask-SQLAlchemy==2.5.1
RUN pip install Flask-Bcrypt==1.0.1
RUN pip install Flask-JWT-Extended==4.3.1
RUN pip install tenacity==8.0.1
RUN pip install psycopg2-binary==2.9.3
RUN pip install python-dotenv==0.19.2
RUN pip install Flask-SocketIO==5.3.2
RUN pip install eventlet==0.33.0
RUN pip install dnspython==1.16.0
RUN pip install Werkzeug==1.0.1
RUN pip install SQLAlchemy==1.3.24
RUN pip install requests==2.26.0
RUN pip install redis==4.0.2
RUN pip install websockets==10.1

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 5001

# Run the application
CMD ["python", "app.py"]