#!bash
sudo docker rm -f discovery_service_container
sudo -E docker run --network host --name discovery_service_container -d discovery_service