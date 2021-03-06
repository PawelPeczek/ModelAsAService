FROM python:3.7-buster

ARG SERVER_IDENTITY_SERVICE_HOST
ARG SERVER_IDENTITY_SERVICE_PORT
ARG SERVER_IDENTITY_SERVICE_PATH
ARG DISCOVERY_SERVICE_HOST
ARG DISCOVERY_SERVICE_PORT
ARG DISCOVERY_SERVICE_PATH
ARG SERVICE_SECRET
ARG AGE_ESTIMATION_CHANNEL
ARG AGE_ESTIMATION_SERVICE_NAME

RUN groupadd docker_users
RUN useradd docker_user -g docker_users
RUN mkdir project project/weights
RUN chown -R docker_user:docker_users project
RUN  wget --no-check-certificate \
   'https://docs.google.com/uc?export=download&id=1u8ZIHHWkXqpfp_HT-Jzr8R6MrozdDn7A' \
   -O project/weights/weights.pth
RUN git clone https://github.com/PawelPeczek/AgeEstimator.git
WORKDIR AgeEstimator
RUN python -m pip install .
WORKDIR /
RUN git clone https://github.com/PawelPeczek/ModelAsAService.git
WORKDIR ModelAsAService/pipeline_sdk
RUN pip install .
WORKDIR /
COPY ./requirements.txt project/requirements.txt
RUN python -m pip install -r project/requirements.txt

ENV SERVER_IDENTITY_SERVICE_HOST=$SERVER_IDENTITY_SERVICE_HOST
ENV SERVER_IDENTITY_SERVICE_PORT=$SERVER_IDENTITY_SERVICE_PORT
ENV SERVER_IDENTITY_SERVICE_PATH=$SERVER_IDENTITY_SERVICE_PATH
ENV DISCOVERY_SERVICE_HOST=$DISCOVERY_SERVICE_HOST
ENV DISCOVERY_SERVICE_PORT=$DISCOVERY_SERVICE_PORT
ENV DISCOVERY_SERVICE_PATH=$DISCOVERY_SERVICE_PATH
ENV SERVICE_SECRET=$SERVICE_SECRET
ENV AGE_ESTIMATION_CHANNE=$AGE_ESTIMATION_CHANNEL
ENV AGE_ESTIMATION_SERVICE_NAME=$AGE_ESTIMATION_SERVICE_NAME


COPY . project
RUN chmod ugo+x project/run_app.sh

WORKDIR project

RUN chmod ugo+x *.sh

ENTRYPOINT ./run_app.sh