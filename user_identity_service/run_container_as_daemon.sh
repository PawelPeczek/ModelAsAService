#!bash
sudo docker rm -f discovery_service_container
sudo -E docker run --network host --name user_identity_service_container -d user_identity_service