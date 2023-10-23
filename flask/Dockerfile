#FROM ubuntu:latest
LABEL authors="dhruv"

ENTRYPOINT ["top", "-b"]

# Use the official Python image as the base image
FROM python:3.8.10

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the entire Flask project into the container
COPY . .

# Command to run Flask application with Gunicorn
CMD ["hypercorn", "-b", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "run:app"]
