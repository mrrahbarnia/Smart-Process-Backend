FROM python:3.12-bullseye as builder
LABEL maintainer="mrrahbarnia@gmail.com"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY ./requirements/base.txt /tmp/base.txt
COPY ./requirements/prod.txt /tmp/prod.txt

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r /tmp/prod.txt

RUN apt-get update && \
    apt-get install -y gcc libpq-dev curl && \
    apt clean && \
    rm -rf /tmp && \
    rm -rf /var/cache/apt/*

FROM python:3.12-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
EXPOSE 8000

COPY . /app
WORKDIR /app
EXPOSE 8000
