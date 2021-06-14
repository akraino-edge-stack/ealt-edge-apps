# example-apps aPaaS for obj-detection

#### 介绍
aPaaS based on EdgeGallery

## Build Docker image
1. download smart shelf Obj detetcion code.
git clone git clone "https://gerrit.akraino.org/r/ealt-edge/apps"

Copy model files to below folder:
apps/ROBO/SmartShelf/Obj_Detection_service/model_info

2. download model file from gitlab and copy to above path
git clone git@gitlab.com:gauravagrawal/ealtedge.git

in folder ROBO-Model below 2 files,
MobileNetSSD_deploy.caffemodel
MobileNetSSD_deploy.prototxt

3. build image:
docker build . -t ealtedge/obj-detection:v1.0

4. push to dockerhub
docker push ealtedge/obj-detection:v1.0
