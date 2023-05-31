# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Metadata
LABEL authors="fresh-milkshake"

# Set the working directory in the container to /app
WORKDIR /app

# Copy only requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application
COPY . /app

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable
#ENV name value

# Run main.py when the container launches
CMD ["python3", "main.py"]
