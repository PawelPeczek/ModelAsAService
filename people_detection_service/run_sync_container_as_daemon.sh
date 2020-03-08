#!bash
sudo docker rm -f user_identity_service_container
sudo -E docker run --network host --name people_detection_service_container -d people_detection_service