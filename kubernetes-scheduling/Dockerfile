FROM python:3.8.12-slim

RUN pip install pipenv

# ensures that the python output is sent to the terminal without buffering
ENV PYTHONUNBUFFERED=TRUE

WORKDIR /app

COPY ["Pipfile", "Pipfile.lock", "matmulsched.py", "./"]

RUN pipenv install --deploy --system && \
    rm -rf /root/.cache

CMD ["python", "matmulsched.py"]
