# Dockerfile References: https://docs.docker.com/engine/reference/builder/

# Start from python:3.8-alpine base image
FROM python:3.8-slim-buster

# Make dir app
RUN mkdir /app
WORKDIR /app
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

# Copy the source from the current directory to the Working Directory inside the container
COPY . .


COPY . .

# Expose port 5000 to the outside world
EXPOSE 5000

# Run the executable
CMD ["python", "main.py"]