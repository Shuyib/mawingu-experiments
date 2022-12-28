# Use latest Python runtime as a parent image
FROM python:3.9.12-slim-buster


# Meta-data
LABEL maintainer="Shuyib <>" \
      description="Docker Data Science Workflow #3: Data Driven Application\
      makes a matplotlib plot whose data is retrieved from object storage\
      which is then uploaded back to object storage."

# Set the working directory to /app
WORKDIR /app

# ensures that the python output is sent to the terminal without buffering
ENV PYTHONUNBUFFERED=TRUE

# Copy the current directory contents into the container at /app
COPY . /app

# upgrade pip
RUN pip --no-cache-dir install --upgrade pip && \
    pip install --no-cache-dir pipenv && \
    pipenv install --deploy --system && \
    rm -rf /root/.cache/

# Create mountpoint
VOLUME /app/data

# ENTRYPOINT allows us to specify the default executible
ENTRYPOINT ["python"]

# CMD sets default arguments to executable which may be overwritten when using docker run
CMD ["plot_timeseries.py"]
