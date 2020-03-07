#!bash
sudo docker rm -f server_identity_service_container
sudo -E docker run --network host --name server_identity_service_container -d server_identity_service