FROM mcr.microsoft.com/playwright:bionic

RUN apt-get update && apt-get -qq -y install gcc curl locales locales-all


RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY poetry.lock .
COPY pyproject.toml .

RUN pip install dateparser slack-sdk playwright
RUN python -m playwright install
COPY src src
COPY emails.txt emails.txt

CMD ["python", "-m", "src.main"]
