FROM python:3.8.12-slim

RUN pip install pipenv

# ensures that the python output is sent to the terminal without buffering
ENV PYTHONUNBUFFERED=TRUE

WORKDIR /app

COPY ["Pipfile", "Pipfile.lock", "matmulsched.py", "./"]

RUN pipenv install --system --deploy

CMD ["python", "matmulsched.py"]