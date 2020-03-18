#!bash
sudo -E docker run \
    --network  host \
    --env RUN_SYNC_APP=false \
    age_estimation_service