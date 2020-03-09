#!bash
export $(egrep -v '^#' ../.env | xargs)
sudo -E docker build \
    --build-arg DB_USER=$DB_USER \
    --build-arg DB_SECRET=$DB_SECRET \
    --build-arg DB_HOST=$DB_HOST \
    --build-arg DISCOVERY_SERVICE_DB_NAME=$DISCOVERY_SERVICE_DB_NAME \
    --build-arg DISCOVERY_SERVICE_NAME=$DISCOVERY_SERVICE_NAME \
    --build-arg SERVER_IDENTITY_SERVICE_HOST=$SERVER_IDENTITY_SERVICE_HOST \
    --build-arg SERVER_IDENTITY_SERVICE_PORT=$SERVER_IDENTITY_SERVICE_PORT \
    --build-arg SERVER_IDENTITY_SERVICE_PATH=$SERVER_IDENTITY_SERVICE_PATH \
    --build-arg DISCOVERY_SERVICE_SECRET=$DISCOVERY_SERVICE_SECRET \
    -t discovery_service .