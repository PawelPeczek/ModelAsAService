FROM python:3.7-alpine

RUN apk update && \
    apk add openssh postgresql-dev gcc linux-headers libc-dev libffi-dev

ARG TOKEN_SECRET
ARG DB_USER
ARG DB_SECRET
ARG DB_HOST
ARG DB_NAME="server_identity_db"

RUN addgroup docker_users
RUN adduser -S docker_user -G docker_users
RUN mkdir project
RUN chown -R docker_user:docker_users project
COPY ./requirements.txt project/requirements.txt
RUN python -m pip install -r project/requirements.txt

ENV TOKEN_SECRET=$TOKEN_SECRET
ENV DB_USER=$DB_USER
ENV DB_SECRET=$DB_SECRET
ENV DB_HOST=$DB_HOST
ENV DB_NAME=$DB_NAME


COPY . project
WORKDIR project

ENTRYPOINT python -m src.app