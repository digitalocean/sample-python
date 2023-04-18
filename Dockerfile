# official Python base image
FROM python:3.9-slim

# working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app will run on
EXPOSE 8000

# Set environment variables
ENV GOOGLE_APPLICATION_CREDENTIALS /app/path/to/your-gcp-credentials.json
ENV MYSQL_HOST your_mysql_host
ENV MYSQL_USER your_mysql_user
ENV MYSQL_PASSWORD your_mysql_password
ENV MYSQL_DATABASE your_database_name

# Start the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app"]
