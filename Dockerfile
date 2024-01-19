# Use the official Python image as the base image
FROM python:latest

# Set metadata for the image
LABEL maintainer="KrisSert"

# Create and set the working directory
WORKDIR /radio-recorder

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the working directory
COPY . .

# Specify the command to run on container start
CMD ["bash"]