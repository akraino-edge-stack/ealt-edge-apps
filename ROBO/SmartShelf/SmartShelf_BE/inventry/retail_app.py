#
# Copyright 2020 Huawei Technologies Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import config
from flask_sslify import SSLify
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from influxdb import InfluxDBClient
import json
import requests
import os
import cv2
import os.path
from os import path
import base64
import time
import sys
import threading
from wsgiref.util import FileWrapper


app = Flask(__name__)
CORS(app)
sslify = SSLify(app)
app.config['JSON_AS_ASCII'] = False
app.config['UPLOAD_PATH'] = '/usr/app/images_result/'
app.config['VIDEO_PATH'] = '/usr/app/test/resources/'
app.config['supports_credentials'] = True
app.config['CORS_SUPPORTS_CREDENTIALS'] = True
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
ALLOWED_VIDEO_EXTENSIONS = {'mp4'}
COUNT = 0
listOfMsgs = []
listOfCameras = []
listOfShelf = []
listOfVideos = []
listOfShelfTables = []
listOfProducts = []
TableIndex = 0


HTTP_URL = "http://"
HTTPS_URL = "https://"
FRONTEND_URL = HTTP_URL + config.FE_SERVICE


class inventory_info:
    """
    Store the data and manage multiple input video feeds
    """
    def __init__(self, status="Needs Filling", time=0):
        self.type = "Shelf_INV1"
        self.labels = "Bottles"
        self.status = status
        self.currentCount = 1
        self.maxCount = 5
        self.time = time

    def setstatus(self, status):
        self.status = status

    def getstatus(self):
        return self.status

    def setcurrentCount(self, count):
        self.currentCount = count

    def getcurrentCount(self):
        return self.currentCount

    def setmaxCount(self, count):
        self.maxCount = count

    def getmaxCount(self):
        return self.maxCount

    def setlabel(self, labels):
        self.labels = labels

    def getlabel(self):
        return self.labels

    def settime(self, time):
        self.labels = time

    def gettime(self):
        return self.time


class shelf_table:
    """
    Shelf details and product info
    """
    def __init__(self, shelfName="Front Shelf", camName='camera01',
                 location='Zone1'):
        self.shelfName = shelfName
        self.location = location
        self.camName = camName

    def setshelfName(self, status):
        self.shelfName = status

    def getshelfName(self):
        return self.shelfName

    def setlocation(self, loc):
        self.location = loc

    def getlocation(self):
        return self.location

    def setcamName(self, camName):
        self.camName = camName

    def getcamName(self):
        return self.camName


class productDetails:
    """
    product info in shelf
    """
    def __init__(self, type="Bottle", maxCount=10,
                 currentCount=3, status='Needs Filling'):
        self.productType = type
        self.maxCount = maxCount
        self.currentCount = currentCount
        self.status = status

    def setproductType(self, productType):
        self.productType = productType

    def getproductType(self):
        return self.productType

    def setmaxCount(self, maxCount):
        self.maxCount = maxCount

    def getmaxCount(self):
        return self.maxCount

    def setcurrentCount(self, currentCount):
        self.currentCount = currentCount

    def getcurrentCount(self):
        return self.currentCount


class shelf_infos:
    """
    Shelf details and product info
    """
    def __init__(self, shelfName="Front Shelf", camName='camera01',
                 location='Zone1', rtspUrl='shelf.mp4'):
        self.shelfName = shelfName
        self.location = location
        self.camName = camName
        self.rtspUrl = rtspUrl

    def setshelfName(self, status):
        self.shelfName = status

    def getshelfName(self):
        return self.shelfName

    def setlocation(self, loc):
        self.location = loc

    def getlocation(self):
        return self.location

    def setcamName(self, camName):
        self.camName = camName

    def getcamName(self):
        return self.camName

    def setrtspUrl(self, rtspUrl):
        self.rtspUrl = rtspUrl

    def getrtspUrl(self):
        return self.rtspUrl


class product_infos:
    """
    product info in shelf
    """
    def __init__(self, type="Bottle", maxCount=10,
                 currentCount=3, status='Needs Filling'):
        self.productType = type
        self.maxCount = maxCount

    def setproductType(self, productType):
        self.productType = productType

    def getproductType(self):
        return self.productType

    def setmaxCount(self, maxCount):
        self.maxCount = maxCount

    def getmaxCount(self):
        return self.maxCount


# temporary copied capture_frame file to this due to docker issue for module
# import
class VideoCamera(object):
    """
    opneCV to capture frame from a camera
    """
    def __init__(self, url):
        self.video = cv2.VideoCapture(url)

    def delete(self):
        self.video.release()

    def get_frame(self):
        """
        get a frame from camera url
        """
        success, image = self.video.read()
        return success, image

    def reset_frame(self):

        self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)


class VideoFile(object):
    """
    opneCV to capture frame from a video stream
    """
    def __init__(self, video_name):
        self.video = cv2.VideoCapture(app.config['VIDEO_PATH'] + video_name)

    def delete(self):
        self.video.release()

    def get_frame(self):
        """
        get a frane from stream
        """
        success, image = self.video.read()
        return success, image

    def reset_frame(self):
        self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)


def video(video_capture, shelf_info, TableIndex):

    app.logger.info("local video")
    process_this_frame = 0
    count = 0
    while True:
        success, frame = video_capture.get_frame()
        if count == 5:
            break
        if not success:
            video_capture.reset_frame()
            count = count + 1
            continue

        if process_this_frame == 0:
            thread_1 = threading.Thread(target=shelf_inventory, args=(frame, shelf_info,TableIndex))
            thread_1.start()
            thread_1.join(3)

        count = 0
        process_this_frame = process_this_frame + 1
        if process_this_frame == 21:
            process_this_frame = 0

        # _, _ = cv2.imencode('.jpg', frame)
        time.sleep(.01)
    return 'SampleString'


def parse_obj_data(data, shelf_info, TableIndex):

    notifyFlag = 0

    if ('Bottle' == shelf_info['productDetails'][0]['obj']):
        bottelMax = shelf_info['productDetails'][0]['MaxCount']
        carMax = shelf_info['productDetails'][1]['MaxCount']
        bottelIndex = 0

    else:
        carMax = shelf_info['productDetails'][0]['MaxCount']
        bottelMax = shelf_info['productDetails'][1]['MaxCount']
        bottelIndex = 1

    objData = data['objDetails']
    for obj in objData:
        objType = obj['objtype']
        objCount = obj['objcount']
        if (objType == 'bottle') :
            bottleCnt = objCount
            if (objCount >= bottelMax*70/100):
                bottleStatus = "Mostly Filled"
            elif (objCount >= bottelMax*40/100):
                bottleStatus = "Partially Filled"
            else:
                bottleStatus = "Needs Filling"
                notifyFlag = 1

        if (objType == 'car') :
            carCnt = objCount
            if (objCount >= carMax*70/100):
                Carstatus = "Mostly Filled"
            elif (objCount >= carMax*40/100):
                Carstatus = "Partially Filled"
            else:
                Carstatus = "Needs Filling"
                notifyFlag = 2

        if (objType == 'other') :
            notifyFlag = 3

    shelfTable = {'shelfName': shelf_info['shelfName'],
                      'location': shelf_info['location'],
                      'camName': shelf_info['camName'],
                      "productDetails": [
                          {
                               "productType": "bottle",
                               "maxCount": bottelMax,
                               "currentCount": bottleCnt,
                               "status": bottleStatus
                          },
                          {
                                  "productType": "car",
                                  "maxCount": carMax,
                                  "currentCount": carCnt,
                                  "status": Carstatus
                              }

                          ]
                }

    print (shelfTable)
    print (TableIndex)
    if len(listOfShelfTables) > TableIndex :
        listOfShelfTables[TableIndex] = shelfTable
    else :
        listOfShelfTables.insert(TableIndex, shelfTable)
    return notifyFlag


def send_notification_msg(shelf_name, notifyFlag, COUNT):
    """
        This method is to send notification message
    """
    global NOW

    url = FRONTEND_URL + "/notify"
    if len(listOfMsgs) >= 100:
        listOfMsgs.pop()

    if (notifyFlag == 1):
        notification_type = "Needs Filling"
        msg = "Product Bottle needs filling in " + shelf_name
    elif (notifyFlag == 2):
        notification_type = "Needs Filling"
        msg = "Product ToyCar needs filling in " + shelf_name
    else:
        notification_type = "Product Mismatch"
        msg = "Product are mismatched in " + shelf_name

    time_sec = time.time()
    local_time = time.ctime(time_sec)

    newdict = {"msgid": COUNT, "time": local_time,
               "notificationType": notification_type,
               "msg": msg}
    listOfMsgs.insert(0, newdict)
    requests.post(url, json=newdict)

def shelf_inventory(frame, shelf_info, TableIndex):
    """
    shelf_inventory
    """
    notifyFlag = 0
    url = config.detection_url + "detect"
    url_get = config.detection_url + "image"

    global COUNT

    COUNT = COUNT + 1
    if COUNT > 100 :
        COUNT = 0

    print('detection url is', url)
    imencoded = cv2.imencode(".jpg", frame)[1]
    file = {'file': (
            'image.jpg', imencoded.tostring(), 'image/jpeg',
            {'Expires': '0'})}
    res = requests.post(url, files=file)
    data = json.loads(res.text)

    # get image
    response = requests.get(url_get)

    file = open(app.config['UPLOAD_PATH'] + "image_" + str(COUNT) + ".jpg",
                                                           "wb")
    file.write(response.content)
    file.close()

    notifyFlag = parse_obj_data(data, shelf_info, TableIndex)

    if (notifyFlag != 0):
        send_notification_msg(shelf_info['shelfName'], notifyFlag, COUNT)

    # return ''


def db_drop_table(inven_info):
    """
    cleanup measrurment before new trigger

    :param inven_info: inven_info object
    :return: None
    """
    global db_client
    db_client.drop_measurement(inven_info.type)


def store_info_db(inven_info):
    """
    Send "shelf" data to InfluxDB

    :param inven_info: Inventry object
    :return: None
    """
    global db_client
    json_body = [
        {
            "measurement": inven_info.type,
            "tags": {
                "object": "bottles",
            },
            "fields": {
                "time": inven_info.time,
                "status": inven_info.status,
                "currentCount": inven_info.currentCount,
                "maxCount": inven_info.maxCount,
            }
        }]
    db_client.write_points(json_body)


def retrive_info_db():
    """
    Send "shelf" data to InfluxDB

    :param inven_info: Inventry object
    :return: None
    """
    global db_client

    # get data last n data points from DB
    result = db_client.query('select * from Shelf_INV1 order by desc limit '
                             '1;')

    # Get points and iterate over each record
    points = result.get_points(tags={"object": "bottles"})

    # clear the msg list
    # listOfMsgs.clear()
    del listOfMsgs[:]

    # iterate points and fill the records and insert to list
    for point in points:
        print("status: %s,Time: %s" % (point['status'], point['time']))
        newdict = {"shelfName": 'Shelf_INV1', "ObjType": "bottles",
                   "status": point['status'],
                   "currentCount": point['currentCount'],
                   "maxCount": point['maxCount'],
                   "time": point['time']}
        listOfMsgs.insert(0, newdict)


def create_database():
    """
    Connect to InfluxDB and create the database

    :return: None
    """
    global db_client
    proxy = {"http": "http://{}:{}".format(config.IPADDRESS, config.PORT)}
    db_client = InfluxDBClient(host=config.IPADDRESS, port=config.PORT,
                               proxies=proxy, database=config.DATABASE_NAME)
    db_client.create_database(config.DATABASE_NAME)


#@app.route('/v1/shelf/table', methods=['GET'])
def shelf_table_old():
    """
    return inventry table

    :return: inventry table
    """
    retrive_info_db()
    table = {"InventryData": listOfMsgs}
    return jsonify(table)


@app.route('/v1/shelf/image/<MsgID>', methods=['GET'])
def detected_image(MsgID):
    """
    detect images with imposed

    :return: result image
    """
    detected_image = app.config['UPLOAD_PATH'] + "image_" + str(MsgID) + ".jpg"
    print('file exits:', str(path.exists(detected_image)))
    status = str(path.exists(detected_image))
    if status == 'True':
        # as base64 string
        with open(detected_image, "rb") as img_file:
            jpeg_bin = base64.b64encode(img_file.read())

        response = {'image': jpeg_bin}
        return jsonify(response)
    else:
        response = {'image': 'null'}
        print('file not exist')
        return jsonify(response)


def allowed_videofile(filename):
    """
    File types to upload:mp4
    param: filename:
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS


@app.route('/v1/shelf/video', methods=['POST'])
def upload_video():
    app.logger.info("Received message from ClientIP [" + request.remote_addr
                    + "] Operation [" + request.method + "]" +
                    " Resource [" + request.url + "]")
    print("videpath:" + app.config['VIDEO_PATH'])
    if 'file' in request.files:
        files = request.files.getlist("file")
        for file in files:
            if allowed_videofile(file.filename):
                file.save(os.path.join(app.config['VIDEO_PATH'],
                                       file.filename))
                print('file path is:', app.config['VIDEO_PATH']
                      + file.filename)
            else:
                raise IOError('video format error')
                msg = {"responce": "failure"}
                return jsonify(msg)
    msg = {"responce": "success"}
    return jsonify(msg)


def hash_func(camera_info):
    hash_string = camera_info["cameraNumber"] + \
                  camera_info["cameraLocation"] + \
                  camera_info["rtspUrl"]
    # readable_hash = hashlib.sha256(str(hash_string).encode(
    # 'utf-8')).hexdigest()
    readable_hash = hash(hash_string)
    if readable_hash < 0:
        readable_hash += sys.maxsize
    print(readable_hash)
    return readable_hash


@app.route('/v1/shelf/add', methods=['POST'])
def add_shelf():
    shelf_details = request.json
    app.logger.info("Received message from ClientIP [" + request.remote_addr
                    + "] Operation [" + request.method + "]" +
                    " Resource [" + request.url + "]")

    shelf_info = {
        'shelfName': shelf_details['shelfName'],
        'location': shelf_details['location'],
        'camName': shelf_details['camName'],
        'rtspUrl': shelf_details['rtspUrl'],
        'productDetails': [ {'obj': shelf_details['productDetails'][0]['obj'],
                             'MaxCount': shelf_details['productDetails'][0][
                                 'MaxCount']},
                            {'obj': shelf_details['productDetails'][1][
                                'obj'],
                             'MaxCount': shelf_details['productDetails'][1][
                                 'MaxCount']}
                            ]
    }

    listOfShelf.append(shelf_info)

    global TableIndex
    print ('print index for shelf', TableIndex)

    if "mp4" in shelf_details["rtspUrl"]:
        video_file = VideoFile(shelf_details['rtspUrl'])
        # video_dict = {camera_info["name"]: video_file}
        # listOfVideos.append(video_dict)
        thread_2 = threading.Thread(target=video,
                                    args=(video_file,
                                          shelf_info,TableIndex,))
        thread_2.start()
        thread_2.join(3)

        TableIndex = TableIndex + 1
        print ('thread is over')
        msg = {"responce": "success"}
        return jsonify(msg)

    msg = {"responce": "failure"}
    return jsonify(msg)


@app.route('/v1/shelf/video/<shelfname>', methods=['GET'])
def play_video(shelfname):
    app.logger.info("Received message from ClientIP [" + request.remote_addr
                    + "] Operation [" + request.method + "]" +
                    " Resource [" + request.url + "]")

    print('Shelf name is =' + shelfname)
    for ShelfInfo in listOfShelf:
        if shelfname == ShelfInfo['shelfName']:
            videoPath = app.config['VIDEO_PATH'] + ShelfInfo['rtspUrl']
            return Response(FileWrapper(open(videoPath, 'rb')),
                            mimetype='video/mp4')


@app.route('/v1/shelf/table', methods=['GET'])
def shelf_table():
    app.logger.info("Received message from ClientIP [" + request.remote_addr
                    + "] Operation [" + request.method + "]" +
                    " Resource [" + request.url + "]")

    table = {"shelfDetails": listOfShelfTables}
    return jsonify(table)


# TODO: scan table and display low entries
@app.route('/v1/shelf/table/empty', methods=['GET'])
def shelf_table_empty():
    app.logger.info("Received message from ClientIP [" + request.remote_addr
                    + "] Operation [" + request.method + "]" +
                    " Resource [" + request.url + "]")

    table = {"shelfDetails": listOfShelfTables}
    return jsonify(table)


@app.route('/v1/shelf/messages', methods=['GET'])
def monitor_messages():
    """
        This method is used to return list of messages
    """
    app.logger.info("Received message from ClientIP [" + request.remote_addr
                    + "] Operation [" + request.method + "]" +
                    " Resource [" + request.url + "]")
    # TODO: Add shelf table info when sendig notification
    notification = {'Notifications': listOfMsgs,
        "shelfDetails": listOfShelfTables}
    return jsonify(notification)

@app.route('/v1/monitor/cameras/<cameraID>', methods=['GET'])
def get_camera(cameraID):
    """
    register camera with location
    """
    app.logger.info("Received message from ClientIP [" + request.remote_addr
                    + "] Operation [" + request.method + "]" +
                    " Resource [" + request.url + "]")
    valid_id = 0
    for camera_info in listOfCameras:
        # cameraID = int(cameraID)
        if cameraID == camera_info["cameraID"]:
            valid_id = 1
            break

    if valid_id == 0:
        app.logger.info("camera ID is not valid")
        msg = {"responce": "failure"}
        return jsonify(msg)

    if "mp4" in camera_info["rtspUrl"]:
        video_file = VideoFile(camera_info["rtspUrl"])
        video_dict = {camera_info["cameraNumber"]: video_file}
        listOfVideos.append(video_dict)
        # return Response(shelf_inventory(video_file, camera_info[
        # "cameraNumber"]),
        #                mimetype='multipart/x-mixed-replace; boundary=frame')
        shelf_inventory(video_file, camera_info["cameraNumber"])
        app.logger.info("get_camera: Added json")
        msg = {"responce": "success"}
        return jsonify(msg)

    else:
        video_file = VideoCamera(camera_info["rtspUrl"])
        video_dict = {camera_info["cameraNumber"]: video_file}
        listOfVideos.append(video_dict)
        return Response(shelf_inventory(video_file,
                        camera_info["cameraNumber"]),
                        mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/v1/monitor/cameras/<camera_name>', methods=['DELETE'])
def delete_camera(camera_name):
    app.logger.info("Received message from ClientIP [" + request.remote_addr
                    + "] Operation [" + request.method + "]" +
                    " Resource [" + request.url + "]")
    for video1 in listOfVideos:
        if camera_name in video1:
            video_obj = video1[camera_name]
            video_obj.delete()
    for camera in listOfCameras:
        if camera_name == camera["cameraNumber"]:
            listOfCameras.remove(camera)
    return Response("success")


@app.route('/v1/monitor/cameras')
def query_cameras():
    app.logger.info("Received message from ClientIP [" + request.remote_addr
                    + "] Operation [" + request.method + "]" +
                    " Resource [" + request.url + "]")
    camera_info = {"roboCamera": listOfCameras}
    return jsonify(camera_info)


@app.route('/', methods=['GET'])
def hello_world():
    app.logger.info("Received message from ClientIP [" + request.remote_addr
                    + "] Operation [" + request.method + "]" +
                    " Resource [" + request.url + "]")
    return Response("Hello MEC Developer")


def start_server(handler):
    app.logger.addHandler(handler)
   # create_database()
    if config.ssl_enabled:
        context = (config.ssl_certfilepath, config.ssl_keyfilepath)
        app.run(host=config.server_address, debug=True, ssl_context=context,
                threaded=True, port=config.server_port)
    else:
        app.run(host=config.server_address, debug=True, threaded=True,
                port=config.server_port)
