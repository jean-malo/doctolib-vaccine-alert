FROM python:3.8-slim-buster

RUN apt-get update && apt-get -qq -y install gcc curl locales locales-all


RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY poetry.lock .
COPY pyproject.toml .

RUN poetry install --no-root --no-dev
RUN python -m playwright install
COPY src src
COPY data data

CMD ["python", "-m", "src.main"]
