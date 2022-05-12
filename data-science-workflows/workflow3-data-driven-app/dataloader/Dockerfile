FROM python:3.9.12-slim-buster

# Meta-data
LABEL maintainer="Shuyib <>" \
      description="Docker Data Science Workflow #3: Data driven app which simulates streaming data collected at a one minute interval"

# Set the working directory to /app
WORKDIR /app

# ensures that the python output is sent to the terminal without buffering
ENV PYTHONUNBUFFERED=TRUE

# Copy the current directory contents into the container at /app
COPY . /app

# upgrade pip
RUN pip --no-cache-dir install --upgrade pip

# install pipenv
RUN pip install pipenv

# pip install
RUN pipenv install --deploy --system && \
    rm -rf /root/.cache

# Create mountpoint
VOLUME app/data

# ENTRYPOINT allows us to specify the default executible
ENTRYPOINT ["python"]

# CMD sets default arguments to executable which may be overwritten when using docker run
CMD ["main.py"]
