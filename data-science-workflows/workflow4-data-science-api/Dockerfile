# Use latest Python runtime as a parent image
FROM python:3.6.5-slim

# Meta-data
LABEL maintainer="Aly Sivji <alysivji@gmail.com>" \
      description="Docker Data Science Workflow #4: Data Science API\
      This image contains a pickled version of the predictive model\
      that can be accessed using a REST API (created in Flask).\
      Fitting and pickling was done at another point in the process"

# Set the working directory to /app
WORKDIR /app


# ensures that the python output is sent to the terminal without buffering
ENV PYTHONUNBUFFERED=TRUE


# Copy the current directory contents into the container at /app
COPY . /app

# make a virtual environment, activate it, upgrade pip, install dependencies
RUN python3 -m venv iris-app && \
      . iris-app/bin/activate && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Make port available to the world outside this container
EXPOSE 5000

# ENTRYPOINT allows us to specify the default executible
ENTRYPOINT ["python"]

# CMD sets default arguments to executable which may be overwritten when using docker run
CMD ["app.py"]
