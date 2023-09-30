FROM python:3.11.5-slim

ENV PYTHONNUNBUFFERED 1
ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH='./'

WORKDIR /usr/src

COPY ./app /usr/src/app
COPY ./.env /usr/src/
COPY ./poetry.lock /usr/src/poetry.lock
COPY ./pyproject.toml /usr/src/pyproject.toml
COPY ./logging.conf /usr/src/logging.conf
COPY ./alembic.ini /usr/src/alembic.ini



RUN apt-get update -y && apt-get install curl -y \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && poetry config virtualenvs.create false \
    && poetry install \
    && apt-get remove curl -y



