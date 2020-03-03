FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install -y python3 python3-pip libssl-dev

ARG SERVER_IDENTITY_SERVICE_HOST="127.0.0.1"
ARG SERVER_IDENTITY_SERVICE_PORT=50002
ARG SERVER_IDENTITY_SERVICE_PATH="/v1/server_identity_service/verify_service_identity"
ARG DISCOVERY_SERVICE_HOST="127.0.0.1"
ARG DISCOVERY_SERVICE_PORT=50003
ARG DISCOVERY_SERVICE_PATH="/v1/discovery_service/locate_services"
ARG SERVICE_SECRET
RUN groupadd docker_users
RUN useradd docker_user -g docker_users
RUN mkdir project
RUN chown -R docker_user:docker_users project
COPY ./requirements.txt project/requirements.txt
RUN python3 -m pip install --no-cache-dir Cython
RUN python3 -m pip install -r project/requirements.txt

ENV SERVER_IDENTITY_SERVICE_HOST=$SERVER_IDENTITY_SERVICE_HOST
ENV SERVER_IDENTITY_SERVICE_PORT=$SERVER_IDENTITY_SERVICE_PORT
ENV SERVER_IDENTITY_SERVICE_PATH=$SERVER_IDENTITY_SERVICE_PATH
ENV DISCOVERY_SERVICE_HOST=$DISCOVERY_SERVICE_HOST
ENV DISCOVERY_SERVICE_PORT=$DISCOVERY_SERVICE_PORT
ENV DISCOVERY_SERVICE_PATH=$DISCOVERY_SERVICE_PATH
ENV SERVICE_SECRET=$SERVICE_SECRET

COPY . project
WORKDIR project

ENTRYPOINT python3 -m src.app