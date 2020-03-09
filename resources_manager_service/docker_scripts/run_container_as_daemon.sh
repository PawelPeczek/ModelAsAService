#!bash
sudo docker rm -f resources_manager_service_container
sudo -E docker run --network host --name resources_manager_service_container -d resources_manager_service