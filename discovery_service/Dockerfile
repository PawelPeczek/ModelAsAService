FROM python:3.7-alpine

RUN apk update && \
    apk add openssh postgresql-dev gcc linux-headers libc-dev libffi-dev

ARG SERVER_IDENTITY_SERVICE_HOST="127.0.0.1"
ARG SERVER_IDENTITY_SERVICE_PORT=50002
ARG SERVER_IDENTITY_SERVICE_PATH="/v1/server_identity_service/verify_service_identity"
ARG SERVICE_SECRET
ARG DB_USER
ARG DB_SECRET
ARG DB_HOST
ARG DB_NAME="discovery_service_db"

RUN addgroup docker_users
RUN adduser -S docker_user -G docker_users
RUN mkdir project
RUN chown -R docker_user:docker_users project
COPY ./requirements.txt project/requirements.txt
RUN python -m pip install -r project/requirements.txt

ENV SERVER_IDENTITY_SERVICE_HOST=$SERVER_IDENTITY_SERVICE_HOST
ENV SERVER_IDENTITY_SERVICE_PORT=$SERVER_IDENTITY_SERVICE_PORT
ENV SERVER_IDENTITY_SERVICE_PATH=$SERVER_IDENTITY_SERVICE_PATH
ENV SERVICE_SECRET=$SERVICE_SECRET
ENV DB_USER=$DB_USER
ENV DB_SECRET=$DB_SECRET
ENV DB_HOST=$DB_HOST
ENV DB_NAME=$DB_NAME


COPY . project
WORKDIR project

ENTRYPOINT python -m src.app