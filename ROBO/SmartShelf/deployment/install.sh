#!/bin/bash  
echo "Smart shell App install start"  
pwd

docker login --username=ealtedge --password=Huawei_akraino

docker pull ealtedge/obj-detection
docker pull ealtedge/inventory-be:v1.3
docker pull ealtedge/robo-be
docker pull ealtedge/robo


git clone https://gitlab.com/gauravagrawal/ealtedge
