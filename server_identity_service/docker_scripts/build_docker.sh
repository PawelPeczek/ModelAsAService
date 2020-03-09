#!bash
export $(egrep -v '^#' ../.env | xargs)
sudo -E docker build \
    --build-arg DB_USER=$DB_USER \
    --build-arg DB_SECRET=$DB_SECRET \
    --build-arg DB_HOST=$DB_HOST \
    --build-arg SERVER_IDENTITY_DB_NAME=$SERVER_IDENTITY_DB_NAME \
    --build-arg SERVER_IDENTITY_TOKEN_SECRET=$SERVER_IDENTITY_TOKEN_SECRET \
    --build-arg SERVER_IDENTITY_SERVICE_NAME=$SERVER_IDENTITY_SERVICE_NAME \
    -t server_identity_service .