#!bash
sudo -E docker run \
    --network  host \
    --env RUN_SYNC_APP=false \
    people_detection_service