# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt /app/

# Install gcc and other necessary system packages
RUN apt-get update && \
    apt-get install -y gcc && \
    rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 8080 available outside this container
EXPOSE 8080

# Run main.py when the container launches
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080", "--timeout-keep-alive", "120"]
