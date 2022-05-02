FROM python:3.9.12-slim-buster

# Meta-data
LABEL maintainer="Aly Sivji <alysivji@gmail.com>" \
      description="Docker Data Science Workflow #3: Data Driven Application\
      This specific use case has the container set up like an executible.\
      Code plus dependencies required to run the program are installed in the\
      container. Data are set up via a mounted folder. Executing\
      docker run with a parameter starts up a dashboard"

# Set the working directory to /app
WORKDIR /app

# ensures that the python output is sent to the terminal without buffering
ENV PYTHONUNBUFFERED=TRUE

# Copy the current directory contents into the container at /app
COPY . /app

# upgrade pip
RUN pip --no-cache-dir install --upgrade pip

# pip install
RUN pipenv install --deploy --system && \
    rm -rf /root/.cache

# Create mountpoint
VOLUME app/data

# ENTRYPOINT allows us to specify the default executible
ENTRYPOINT ["python"]

# CMD sets default arguments to executable which may be overwritten when using docker run
CMD ["main.py"]
