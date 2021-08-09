FROM python:3.9

RUN useradd -d /opt/scoreboard app
RUN install -d -g app -o app /opt/scoreboard

ADD requirements.txt setup.py ./
RUN pip install -r requirements.txt && rm requirements.txt setup.py

ENV PYTHONUNBUFFERED 1

USER app
WORKDIR /opt/scoreboard

EXPOSE 8000
ENTRYPOINT ["./.docker/start", "runserver", "0.0.0.0:8000"]
