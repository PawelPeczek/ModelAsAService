FROM python:3.7-alpine

RUN apk update && \
    apk add openssh postgresql-dev gcc linux-headers libc-dev libffi-dev

ARG SERVER_IDENTITY_TOKEN_SECRET
ARG DB_USER
ARG DB_SECRET
ARG DB_HOST
ARG SERVER_IDENTITY_DB_NAME
ARG SERVER_IDENTITY_SERVICE_NAME

RUN addgroup docker_users
RUN adduser -S docker_user -G docker_users
RUN mkdir project
RUN chown -R docker_user:docker_users project
COPY ./requirements.txt project/requirements.txt
RUN python -m pip install -r project/requirements.txt

ENV SERVER_IDENTITY_TOKEN_SECRET=$SERVER_IDENTITY_TOKEN_SECRET
ENV DB_USER=$DB_USER
ENV DB_SECRET=$DB_SECRET
ENV DB_HOST=$DB_HOST
ENV SERVER_IDENTITY_DB_NAME=$SERVER_IDENTITY_DB_NAME
ENV SERVER_IDENTITY_SERVICE_NAME=$SERVER_IDENTITY_SERVICE_NAME

COPY . project
WORKDIR project

RUN chmod ugo+x *.sh

ENTRYPOINT python -m src.app