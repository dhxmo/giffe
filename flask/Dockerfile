# Use the official Python image as the base image
FROM python:3.8.10 as base

# Set the working directory in the container
WORKDIR /app

# Install the required system packages for OpenGL
RUN apt-get update && apt-get install -y libsm6 libxext6 libfontconfig1 libxrender1 libgl1-mesa-glx libglib2.0-0 python3-opencv libgbm1 libasound2

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install Python dependencies and OpenCV
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN playwright install

# Intermediate image with just the installed dependencies
FROM base as intermediate

# Copy the entire Flask project into the container
COPY . .

# Final image with the application code
FROM base

# Copy the application code from the intermediate image
COPY --from=intermediate /app /app

# Command to run Flask application with Hypercorn
CMD ["hypercorn", "-b", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "run:app"]
