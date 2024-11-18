# Define the base image 
FROM python:3.9.18-slim

# Meta-data: Identifying the maintainer of the image and a brief description of the image
LABEL maintainer="Shuyib <>" \
      description="Docker Data Science Workflow #3: Data driven app which simulates streaming data collected at a one minute interval"

# Set the working directory to /app
WORKDIR /app

# ensures that the python output is sent to the terminal without buffering
# buffering can cause delays in the output
ENV PYTHONUNBUFFERED=TRUE

# Copy the current directory contents into the container at /app
COPY . /app

# upgrade pip and install pipenv
RUN pip --no-cache-dir install --upgrade pip && \
    pip install --no-cache-dir pipenv && \
    pipenv install --deploy --system && \   
    rm -rf /root/.cache/

# Add a non-root user and switch to that user
RUN useradd -m myuser
USER myuser

# Create mountpoint
VOLUME /app/data

# ENTRYPOINT allows us to specify the default executable
ENTRYPOINT ["python"]

# CMD sets default arguments to executable which may be overwritten when using docker run
CMD ["main.py"]
