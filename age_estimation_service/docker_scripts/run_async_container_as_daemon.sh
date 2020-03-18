#!bash
sudo docker rm -f user_identity_service_container
sudo -E docker run \
    --network host \
    --env RUN_SYNC_APP=false \
    --name age_estimation_service_container \
    -d age_estimation_service