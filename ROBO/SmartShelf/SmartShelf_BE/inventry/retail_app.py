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
listOfAlertsMsgs = []
listOfCameras = []
listOfShelf = []
listOfVideos = []
listOfShelfTables = []
listOfProducts = []
TableIndex = 0
listOfObj = ['Bottle', 'ToyCar', 'Chair', 'TvMonitor', 'Table', 'Sofa']
lastObj1Cnt = 0
lastObj2Cnt = 0
firstFrame = 1
listOfTableIndex = {}
listOfObjStatus = {}

listOfLocation = ['Aisle_01', 'Aisle_02', 'Aisle_03', 'Aisle_04', 'Aisle_05',
                  'Aisle_06', 'Aisle_07', 'Aisle_08', 'Aisle_09', 'Aisle_10']

DictofCamera = {'Aisle_01': "cam01.mp4", 'Aisle_02': "cam01.mp4",
                'Aisle_03': "cam01.mp4", 'Aisle_04': "cam01.mp4",
                'Aisle_05': "cam01.mp4",  'Aisle_06': "cam01.mp4",
                'Aisle_07': "cam01.mp4", 'Aisle_08': "cam01.mp4",
                'Aisle_09': "cam01.mp4", 'Aisle_10': "cam01.mp4"}

DictDetectionStatus = {}
HTTP_URL = "http://"
HTTPS_URL = "https://"
FRONTEND_URL = HTTP_URL + config.FE_SERVICE
DicMisMatchStatus = {}

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
    key = shelf_info['shelfName'] + shelf_info['location']
    print('[video]Deletion key is', key)
    time.sleep(1.1)

    while True:
        success, frame = video_capture.get_frame()
        if count == 5:
            break
        if not success:
            video_capture.reset_frame()
            count = count + 1
            #time.sleep(.3)
            continue

        if DictDetectionStatus[key] == 0 :
            print('[video]Deletion is triggered')
            return

        if process_this_frame == 0:
            thread_1 = threading.Thread(target=shelf_inventory, args=(frame, shelf_info,TableIndex))
            thread_1.start()
            thread_1.join(1)

        count = 0
        process_this_frame = process_this_frame + 1
        if process_this_frame == 10:
            process_this_frame = 0

        # _, _ = cv2.imencode('.jpg', frame)
        #time.sleep(.01)
        time.sleep(.015)
    return 'SampleString'


def parse_obj_data(data, shelf_info, TableIndex, shelf_name):

    obj1Cnt = 0
    obj2Cnt = 0

    key = shelf_info['shelfName'] + shelf_info['location']
    if DictDetectionStatus[key] == 0:
        print('[video]Deletion is triggered')
        return

    shelf = shelf_info['shelfName']
    if shelf in listOfObjStatus :
        ObjStatus = listOfObjStatus[shelf]
        lastObj1Cnt = ObjStatus["lastObj1Cnt"]
        lastObj2Cnt = ObjStatus["lastObj2Cnt"]
        firstFrame = ObjStatus["FirstFrame"]

    filledFlagObj1 = 0
    notifyFlagObj1 = 0
    filledFlagObj2 = 0
    notifyFlagObj2 = 0
    productMismatch = 0
    disableProductMismatch = 1

    productCnt = len(shelf_info['productDetails'])
    if productCnt == 1:
        obj1 = shelf_info['productDetails'][0]['obj']
        obj1MaxCount = shelf_info['productDetails'][0]['MaxCount']
    else :
        obj1 = shelf_info['productDetails'][0]['obj']
        obj1MaxCount = shelf_info['productDetails'][0]['MaxCount']
        obj2 = shelf_info['productDetails'][1]['obj']
        obj2MaxCount = shelf_info['productDetails'][1]['MaxCount']

    objData = data['objDetails']
    for obj in objData:
        objType = obj['objtype']
        objCount = obj['objcount']

        if objType == "bottle" :
            objType = 'Bottle'
        elif objType == "car" :
            objType = 'ToyCar'
        elif objType == "chair" :
            objType = 'Chair'
        elif objType == "tvmonitor" :
            objType = 'TvMonitor'
        elif objType == "diningtable" :
            objType = 'Table'
        elif objType == "sofa" :
            objType = 'Sofa'

        if productCnt == 1:

            if ((objType != obj1) and (objType != 'person') ) :
                productMismatch = 1

            if (objType == obj1):
                obj1Cnt = objCount
                if (objCount > obj1MaxCount):
                    obj1Status = "Over Filled"
                    notifyFlagObj1 = 1
                elif (objCount >= obj1MaxCount * 70 / 100):
                    obj1Status = "Mostly Filled"
                    filledFlagObj1 = 1
                elif (objCount > obj1MaxCount * 30 / 100):
                    obj1Status = "Partially Filled"
                    filledFlagObj1 = 1
                else:
                    obj1Status = "Needs Filling"
                    notifyFlagObj1 = 1

        if productCnt == 2:
            if ((objType != obj1) and (objType != obj2) and (objType !=
                                                             'person')):
                productMismatch = 1

            if (objType == obj1):
                obj1Cnt = objCount
                if (objCount > obj1MaxCount):
                    obj1Status = "Over Filled"
                    notifyFlagObj1 = 1
                elif (objCount >= obj1MaxCount * 70 / 100):
                    obj1Status = "Mostly Filled"
                    filledFlagObj1 = 1
                elif (objCount > obj1MaxCount * 30 / 100):
                    obj1Status = "Partially Filled"
                    filledFlagObj1 = 1
                else:
                    obj1Status = "Needs Filling"
                    notifyFlagObj1 = 1

            if (objType == obj2):
                obj2Cnt = objCount
                if (objCount > obj2MaxCount):
                    obj2Status = "Over Filled"
                    notifyFlagObj2 = 1
                elif (objCount >= obj2MaxCount * 70 / 100):
                    obj2Status = "Mostly Filled"
                    filledFlagObj2 = 1
                elif (objCount > obj2MaxCount * 30 / 100):
                    obj2Status = "Partially Filled"
                    filledFlagObj2 = 1
                else:
                    obj2Status = "Needs Filling"
                    notifyFlagObj2 = 1

    if productCnt == 1 :
        if (obj1Cnt == 0):
            obj1Status = "Needs Filling"
            notifyFlagObj1 = 1

        shelfTable = {'shelfName': shelf_info['shelfName'],
                      'location': shelf_info['location'],
                      'camName': shelf_info['camName'],
                      "productDetails": [
                          {
                              "productType": obj1,
                              "maxCount": obj1MaxCount,
                              "currentCount": obj1Cnt,
                              "status": obj1Status
                          }
                      ]
                      }
    if productCnt == 2 :
        if (obj1Cnt == 0):
            obj1Status = "Needs Filling"
            notifyFlagObj1 = 1
        if (obj2Cnt == 0):
            obj2Status = "Needs Filling"
            notifyFlagObj2 = 1

        shelfTable = {'shelfName': shelf_info['shelfName'],
                      'location': shelf_info['location'],
                      'camName': shelf_info['camName'],
                      "productDetails": [
                          {
                              "productType": obj1,
                              "maxCount": obj1MaxCount,
                              "currentCount": obj1Cnt,
                              "status": obj1Status
                          },
                          {
                              "productType": obj2,
                              "maxCount": obj2MaxCount,
                              "currentCount": obj2Cnt,
                              "status": obj2Status
                          }

                      ]
                      }

    #print (shelfTable)
    #print (TableIndex)

    if DictDetectionStatus[key] == 0:
        print('[video]Deletion is triggered')
        return

    #print ('[Parsing] table index ', TableIndex)
    #print ('[Parsing] shelf table before ', listOfShelfTables)
    #if len(listOfShelfTables) > TableIndex :
     #   listOfShelfTables[TableIndex] = shelfTable
    #else :
     #   listOfShelfTables.insert(TableIndex, shelfTable)

    ShelfExist = 0


    for i in range(len(listOfShelfTables)) :
        #print('[parsing] shelf anme', listOfShelfTables[i]['shelfName'])
        #print('[parsing] shelf anme', shelf_info['shelfName'])
        #print('parsing, index', i)
        if listOfShelfTables[i]['shelfName'] == shelf_info['shelfName'] :
            #print("[parsing] inside")
            #listOfShelfTables.insert(i, shelfTable)
            listOfShelfTables[i] = shelfTable
            ShelfExist = 1
            break

    if ShelfExist == 0 :
        listOfShelfTables.append(shelfTable)


    #print ('[Parsing] shelf table after ', listOfShelfTables)

    time_sec = time.time()
    local_time = time.ctime(time_sec)
    url = FRONTEND_URL + "/notify"

    if (notifyFlagObj1 == 1 or notifyFlagObj2 == 1 or productMismatch == 1) :

        if notifyFlagObj1 == 1 :
            msg = "Product " + obj1 + ' ' + obj1Status + " in " + shelf_name
            status = obj1Status

            newdict = {"msgid": COUNT, "time": local_time,
                       "notificationType": status,
                       "msg": msg, "shelf": shelf_name}

            shelfNotify = 0
            for i in range(len(listOfAlertsMsgs)):
                if (listOfAlertsMsgs[i]['shelf'] == shelf_name) :
                    msg = listOfAlertsMsgs[i]['msg']
                    str = msg.split()
                    previousObj = str[1]
                    print ('previous obj is and  obj1:', previousObj, obj1)
                    if (previousObj == obj1):
                        print('[inside]previous obj is and  obj1:',
                              previousObj, obj1)
                        shelfNotify = 1
                        #if (firstFrame == 0 and obj1Cnt != lastObj1Cnt):
                        listOfAlertsMsgs[i] = newdict
                        requests.post(url, json=newdict)

            if (shelfNotify == 0):
                listOfAlertsMsgs.insert(0, newdict)
                requests.post(url, json=newdict)

            if len(listOfMsgs) >= 100:
                listOfMsgs.pop()

            firstNotify = 1
            for i in range(len(listOfMsgs)):
                if (listOfMsgs[i]['shelf'] == shelf_name):
                    print ('last obj1 cnt', lastObj1Cnt)
                    print ('current obj1 cnt', obj1Cnt)
                    firstNotify = 0
                    if ((firstFrame == 0 and obj1Cnt != lastObj1Cnt)):
                        listOfMsgs.insert(0, newdict)
                        requests.post(url, json=newdict)
                    break

            if firstNotify == 1:
                listOfMsgs.insert(0, newdict)
                requests.post(url, json=newdict)

        if notifyFlagObj2 == 1 :
            msg = "Product " + obj2 + ' ' + obj2Status + " in " + shelf_name
            status = obj2Status

            newdict = {"msgid": COUNT, "time": local_time,
                       "notificationType": status,
                       "msg": msg, "shelf": shelf_name}

            shelfNotify = 0
            for i in range(len(listOfAlertsMsgs)):
                if (listOfAlertsMsgs[i]['shelf'] == shelf_name):
                    msg = listOfAlertsMsgs[i]['msg']
                    str = msg.split()
                    previousObj = str[1]
                    if (previousObj == obj2):
                        print('previous obj is: obj 2 is', previousObj, obj2)
                        shelfNotify = 1
                        #if ((firstFrame == 0 and obj2Cnt != lastObj2Cnt)):
                        listOfAlertsMsgs[i] = newdict
                        requests.post(url, json=newdict)

            if (shelfNotify == 0):
                listOfAlertsMsgs.insert(0, newdict)
                requests.post(url, json=newdict)

            if len(listOfMsgs) >= 100:
                listOfMsgs.pop()

            firstNotify = 1
            for i in range(len(listOfMsgs)):
                if (listOfMsgs[i]['shelf'] == shelf_name):
                    firstNotify = 0
                    if ((firstFrame == 0 and obj2Cnt != lastObj2Cnt)):
                        listOfMsgs.insert(0, newdict)
                        requests.post(url, json=newdict)
                    break

            if firstNotify == 1:
                listOfMsgs.insert(0, newdict)
                requests.post(url, json=newdict)

        if (productMismatch == 1):
            status = "Product Mismatch"
            msg = "Product mismatched in " + shelf_name

            newdict = {"msgid": COUNT, "time": local_time,
                       "notificationType": status,
                       "msg": msg, "shelf": shelf_name}

            shelfNotify = 0
            for i in range(len(listOfAlertsMsgs)):
                if (listOfAlertsMsgs[i]['shelf'] == shelf_name):
                    #if ((listOfAlertsMsgs[i]['notificationType'] != status)):
                    if ((listOfAlertsMsgs[i]['notificationType'] == status)):
                        shelfNotify = 1
                        listOfAlertsMsgs[i] = newdict
                        requests.post(url, json=newdict)
                        break

            if (shelfNotify == 0):
                listOfAlertsMsgs.insert(0, newdict)
                requests.post(url, json=newdict)

            if DicMisMatchStatus[key] == 1 :

                DicMisMatchStatus[key] = 0
                if len(listOfMsgs) >= 100:
                    listOfMsgs.pop()
                '''
                firstNotify = 1
                for i in range(len(listOfMsgs)):
                    if (listOfMsgs[i]['shelf'] == shelf_name):
                        firstNotify = 0
                        if ((listOfMsgs[i]['notificationType'] != status)):
                            listOfMsgs.insert(0, newdict)
                            requests.post(url, json=newdict)
                        break
                '''
               # if firstNotify == 1:
                listOfMsgs.insert(0, newdict)
                requests.post(url, json=newdict)

    if (filledFlagObj1 == 1 or filledFlagObj2 == 1) :
        if filledFlagObj1 == 1 :
            for i in range(len(listOfAlertsMsgs)):
                if (listOfAlertsMsgs[i]['shelf'] == shelf_name):
                    status = obj1Status
                    msg = "Product " + obj1Status + " in " + shelf_name
                    newdict = {"msgid": COUNT, "time": local_time,
                               "notificationType": status,
                               "msg": msg, "shelf": shelf_name}

                    msg = listOfAlertsMsgs[i]['msg']
                    str = msg.split()
                    previousObj = str[1]
                    print ('[POP]previous obj is and  obj1:', previousObj,
                           obj1)
                    if ((previousObj == obj1) or (previousObj ==
                                                  'mismatched')):
                        listOfAlertsMsgs.pop(
                            i);  ## TODO: check for pop of same shelf
                        requests.post(url, json=newdict)


            if len(listOfMsgs) >= 100:
                listOfMsgs.pop()

            firstNotify = 1
            ##TODO: handle case for mostly filled and partially filled and
            # different products notifications
            for i in range(len(listOfMsgs)):
                if (listOfMsgs[i]['shelf'] == shelf_name):
                    firstNotify = 0
                    if (listOfMsgs[i]['notificationType'] != obj1Status):
                        status = obj1Status
                        msg = "Product " + obj1 + " " + obj1Status + " in " + \
                              shelf_name
                        newdict = {"msgid": COUNT, "time": local_time,
                                   "notificationType": obj1Status,
                                   "msg": msg, "shelf": shelf_name}
                        listOfMsgs.insert(0, newdict)
                        requests.post(url, json=newdict)
                    break

            if firstNotify == 1:
                msg = "Product " + obj1 + " " + obj1Status + " in " + \
                      shelf_name
                newdict = {"msgid": COUNT, "time": local_time,
                           "notificationType": obj1Status,
                           "msg": msg, "shelf": shelf_name}
                listOfMsgs.insert(0, newdict)
                requests.post(url, json=newdict)

        if filledFlagObj2 == 1 :
            for i in range(len(listOfAlertsMsgs)):
                if (listOfAlertsMsgs[i]['shelf'] == shelf_name):
                    status = obj2Status
                    msg = "Product " + obj2 + " " + obj2Status + " in " + \
                          shelf_name
                    newdict = {"msgid": COUNT, "time": local_time,
                               "notificationType": status,
                               "msg": msg, "shelf": shelf_name}

                    msg = listOfAlertsMsgs[i]['msg']
                    str = msg.split()
                    previousObj = str[1]
                    print ('[POP]previous obj is and  obj2:', previousObj,
                           obj2)
                    if ((previousObj == obj2)  or (previousObj ==
                                                  'mismatched')):
                        listOfAlertsMsgs.pop(
                            i);  ## TODO: check for pop of same shelf
                        requests.post(url, json=newdict)


            if len(listOfMsgs) >= 100:
                listOfMsgs.pop()

            firstNotify = 1
            ##TODO: handle case for mostly filled and partially filled and
            # different products notifications
            for i in range(len(listOfMsgs)):
                if (listOfMsgs[i]['shelf'] == shelf_name):
                    firstNotify = 0
                    if (listOfMsgs[i]['notificationType'] != obj2Status):
                        status = obj2Status
                        msg = "Product " + obj2 + " " + obj2Status + " in " \
                              + shelf_name
                        newdict = {"msgid": COUNT, "time": local_time,
                                   "notificationType": obj2Status,
                                   "msg": msg, "shelf": shelf_name}
                        listOfMsgs.insert(0, newdict)
                        requests.post(url, json=newdict)
                    break

            if firstNotify == 1:
                msg = "Product " + obj2 + " " + obj2Status + " in " + \
                      shelf_name
                newdict = {"msgid": COUNT, "time": local_time,
                           "notificationType": obj2Status,
                           "msg": msg, "shelf": shelf_name}
                listOfMsgs.insert(0, newdict)
                requests.post(url, json=newdict)

    if productMismatch == 0 :
        DicMisMatchStatus[key] == 1

    ObjStatus["lastObj1Cnt"] = obj1Cnt
    ObjStatus["lastObj2Cnt"] = obj2Cnt
    ObjStatus["FirstFrame"] = 0
    lastObj1Type = obj1
    if productCnt == 2 :
        lastObj2Type = obj2
    return


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
    elif (notifyFlag == 3):
        notification_type = "Product Mismatch"
        msg = "Product are mismatched in " + shelf_name
    else:
        notification_type = "Mostly filled"
        msg = "Product are filled in " + shelf_name

    time_sec = time.time()
    local_time = time.ctime(time_sec)

    newdict = {"msgid": COUNT, "time": local_time,
               "notificationType": notification_type,
               "msg": msg, "shelf": shelf_name}
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

    #print('detection url is', url)
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

    notifyFlag = parse_obj_data(data, shelf_info, TableIndex, shelf_info['shelfName'])

    # send_notification_msg(shelf_info['shelfName'], notifyFlag, COUNT)

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
    productCnt = len(shelf_details['productDetails'])
    # print('total products are=',productCnt)

    for shelf in listOfShelf :
        if ((shelf['shelfName'] == shelf_details['shelfName'])
            and (shelf['location'] == shelf_details['location'])) :
            app.logger.info('[Add shelf]shelf alredy exist')
            msg = {"responce": "failure"}
            return jsonify(msg)


    if productCnt == 1 :
        shelf_info = {
        'shelfName': shelf_details['shelfName'],
        'location': shelf_details['location'],
        'camName': shelf_details['camName'],
        'rtspUrl': shelf_details['rtspUrl'],
        'productDetails': [ {'obj': shelf_details['productDetails'][0]['obj'],
                             'MaxCount': shelf_details['productDetails'][0][
                                 'MaxCount']}
                            ]
    }

    if productCnt == 2 :
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


    if productCnt == 3 :
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
                                 'MaxCount']},
                            {'obj': shelf_details['productDetails'][2][
                                'obj'],
                             'MaxCount': shelf_details['productDetails'][2][
                                 'MaxCount']}
                            ]
    }

    global TableIndex
    print ('print index for shelf', TableIndex)

    key = shelf_details['shelfName'] + shelf_details['location']
    print('[Add shelf]Deletion key is', key)
    DictDetectionStatus[key] = 1
    print("[DETECTION]Detection status:")
    print(DictDetectionStatus)

    listOfTableIndex[key] = TableIndex
    ## product mismatch in case product is removed
    DicMisMatchStatus[key] = 1

    ## Add shelf Obj status dict
    shelf = shelf_details['shelfName']
    listOfObjStatus[shelf] = {'lastObj1Cnt' : 0,
                              'lastObj2Cnt' : 0,
                              'FirstFrame': 1}

    Loc = shelf_details['location']
    if Loc in DictofCamera :
       Video = DictofCamera[Loc]
    else :
        app.logger.info('[Add shelf]location is wrong')
        msg = {"responce": "failure"}
        return jsonify(msg)

    listOfShelf.append(shelf_info)

    video_file = VideoFile(Video)
    # video_dict = {camera_info["name"]: video_file}
    # listOfVideos.append(video_dict)
    thread_2 = threading.Thread(target=video,
                                args=(video_file,
                                      shelf_info, TableIndex,))
    thread_2.start()
    thread_2.join(1)

    TableIndex = TableIndex + 1
    print('thread is over')
    msg = {"responce": "success"}
    return jsonify(msg)


@app.route('/v1/shelf/video/<shelfname>', methods=['GET'])
def play_video(shelfname):
    app.logger.info("Received message from ClientIP [" + request.remote_addr
                    + "] Operation [" + request.method + "]" +
                    " Resource [" + request.url + "]")

    print('Shelf name is =' + shelfname)
    for ShelfInfo in listOfShelf:
        if shelfname == ShelfInfo['shelfName']:
            Loc = ShelfInfo['location']
            if Loc in DictofCamera:
                Video = DictofCamera[Loc]
            else:
                app.logger.info('[Add shelf]location is wrong')
                msg = {"responce": "failure"}
                return jsonify(msg)

            videoPath = app.config['VIDEO_PATH'] + Video
            return Response(FileWrapper(open(videoPath, 'rb')),
                            mimetype='video/mp4')


@app.route('/v1/shelf/shelfname/<shelfname>/location/<location>', methods=['DELETE'])
def delete_shelf(shelfname, location):
    shelf_details = request.json
    app.logger.info("Received message from ClientIP [" + request.remote_addr
                    + "] Operation [" + request.method + "]" +
                    " Resource [" + request.url + "]")

    for i in range(len(listOfShelf)) :
        if ((listOfShelf[i]['shelfName'] == shelfname)
            and (listOfShelf[i]['location'] == location)) :
            listOfShelf.pop(i)
            key = shelfname + location
            print('Deletion key is', key)
            DictDetectionStatus[key] = 0
            print("[DETECTION]Detection status:")
            print(DictDetectionStatus)

            break

    if shelfname in listOfObjStatus :
        del listOfObjStatus[shelfname]

    print ('[Delete]Alerts msg list', listOfAlertsMsgs)
    j = 0
    while j < 2 :
        j = j+1
        for i in range(len(listOfAlertsMsgs)):
            print('[Delet]index is', i)
            if (listOfAlertsMsgs[i]['shelf'] == shelfname):
                listOfAlertsMsgs.pop(i)
                break

    newdict = {"msgid": 0, "time": 0,
               "notificationType": 'null',
               "msg": 'null', "shelf": 'null'}

    url = FRONTEND_URL + "/notify"
    requests.post(url, json=newdict)

    for i in range(len(listOfShelfTables)) :
        if listOfShelfTables[i]['shelfName'] == shelfname :
            #listOfShelfTables.insert(i, shelfTable)
            listOfShelfTables.pop(i)

            msg = {"responce": "success"}
            return jsonify(msg)



    msg = {"responce": "failure"}
    print("shel not exist")

    return jsonify(msg)


@app.route('/v1/shelf/table', methods=['GET'])
def shelf_table():
    app.logger.info("Received message from ClientIP [" + request.remote_addr
                    + "] Operation [" + request.method + "]" +
                    " Resource [" + request.url + "]")

    table = {"shelfDetails": listOfShelfTables}
    return jsonify(table)


@app.route('/v1/shelf/locations', methods=['GET'])
def get_locations():
    app.logger.info("Received message from ClientIP [" + request.remote_addr
                    + "] Operation [" + request.method + "]" +
                    " Resource [" + request.url + "]")

    locations = {"Locations": listOfLocation}
    return jsonify(locations)

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


@app.route('/v1/shelf/AlertsMessages', methods=['GET'])
def alerts_messages():
    """
        This method is used to return list of messages
    """
    app.logger.info("Received message from ClientIP [" + request.remote_addr
                    + "] Operation [" + request.method + "]" +
                    " Resource [" + request.url + "]")
    # TODO: Add shelf table info when sendig notification
    notification = {'Notifications': listOfAlertsMsgs,
        "shelfDetails": listOfShelfTables}
    return jsonify(notification)


@app.route('/v1/shelf/ObjList', methods=['GET'])
def Obj_List():
    """
        This method is used to return list of messages
    """
    app.logger.info("Received message from ClientIP [" + request.remote_addr
                    + "] Operation [" + request.method + "]" +
                    " Resource [" + request.url + "]")
    # TODO: Add shelf table info when sendig notification
    ObjList = {'ObjList': listOfObj}
    return jsonify(ObjList)


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
