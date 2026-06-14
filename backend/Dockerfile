FROM python:3.12-slim

ENV PYTHONUNBUFFERED 1
RUN mkdir -p /code
RUN mkdir -p /sock
RUN mkdir -p /logs
WORKDIR /code

RUN apt-get -y update
RUN apt -y install binutils gettext make cmake gcc python3-dev g++ \
	&& rm -rf /var/lib/apt/lists/* \
	&& apt autoremove && apt autoclean
