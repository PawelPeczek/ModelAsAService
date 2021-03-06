FROM python:3.7-alpine

RUN apk update && \
    apk add openssh postgresql-dev gcc linux-headers libc-dev libffi-dev

ARG DB_USER
ARG DB_SECRET
ARG DB_HOST
ARG USER_IDENTITY_DB_NAME
ARG SERVER_IDENTITY_SERVICE_HOST
ARG SERVER_IDENTITY_SERVICE_PORT
ARG SERVER_IDENTITY_SERVICE_PATH
ARG DISCOVERY_SERVICE_HOST
ARG DISCOVERY_SERVICE_PORT
ARG DISCOVERY_SERVICE_PATH
ARG USER_IDENTITY_SERVICE_SECRET
ARG ADMIN_IDENTITY_RESOURCES_JWT_SECRET
ARG USER_IDENTITY_SERVICE_NAME

RUN addgroup docker_users
RUN adduser -S docker_user -G docker_users
RUN mkdir project
RUN chown -R docker_user:docker_users project
COPY ./requirements.txt project/requirements.txt
RUN python -m pip install -r project/requirements.txt

ENV DB_USER=$DB_USER
ENV DB_SECRET=$DB_SECRET
ENV DB_HOST=$DB_HOST
ENV USER_IDENTITY_DB_NAME=$USER_IDENTITY_DB_NAME
ENV SERVER_IDENTITY_SERVICE_HOST=$SERVER_IDENTITY_SERVICE_HOST
ENV SERVER_IDENTITY_SERVICE_PORT=$SERVER_IDENTITY_SERVICE_PORT
ENV SERVER_IDENTITY_SERVICE_PATH=$SERVER_IDENTITY_SERVICE_PATH
ENV DISCOVERY_SERVICE_HOST=$DISCOVERY_SERVICE_HOST
ENV DISCOVERY_SERVICE_PORT=$DISCOVERY_SERVICE_PORT
ENV DISCOVERY_SERVICE_PATH=$DISCOVERY_SERVICE_PATH
ENV USER_IDENTITY_SERVICE_SECRET=$USER_IDENTITY_SERVICE_SECRET
ENV ADMIN_IDENTITY_RESOURCES_JWT_SECRET=$ADMIN_IDENTITY_RESOURCES_JWT_SECRET
ENV USER_IDENTITY_SERVICE_NAME=$USER_IDENTITY_SERVICE_NAME

COPY . project
WORKDIR project

RUN chmod ugo+x *.sh

ENTRYPOINT python -m src.app
