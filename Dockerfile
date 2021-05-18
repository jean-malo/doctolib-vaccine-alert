FROM mcr.microsoft.com/playwright:bionic

RUN apt-get update && apt-get -qq -y install gcc curl locales locales-all

RUN pip install playwright dateparser PyYAML requests

RUN python -m playwright install
COPY src src
COPY config.ini config.ini

CMD ["python", "-m", "src.main"]
