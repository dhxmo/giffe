# Use the official Python image as the base image
FROM python:3.8.10

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN apt-get update && apt-get install -y libsm6 libxext6 ffmpeg libfontconfig1 libxrender1 libgl1-mesa-glx libglib2.0-0 libgl1
RUN apt-get update && apt-get install -y python3-opencv
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the entire Flask project into the container
COPY . .

# Command to run Flask application with Gunicorn
CMD ["hypercorn", "-b", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "run:app"]
