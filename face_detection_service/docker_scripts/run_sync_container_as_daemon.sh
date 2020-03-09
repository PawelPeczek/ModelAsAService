#!bash
sudo docker rm -f user_identity_service_container
sudo -E docker run --network host --name face_detection_service_container -d face_detection_service