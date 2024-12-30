# Use a lightweight Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory's contents into the container
COPY . /app

# Expose the proxy server port
EXPOSE 5000

# Run the main script
CMD ["python", "main.py"]