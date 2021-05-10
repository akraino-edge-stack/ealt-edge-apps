/*
 *  Copyright 2021 Huawei Technologies Co., Ltd.
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */

import axios from 'axios'
import 'element-ui/lib/theme-chalk/index.css'

let api = 'http://localhost'
let backupApi = 'http://localhost'
let roboApi = backupApi + ':30081' + '/v1/robo'
let shelfApi = api + ':9995' + '/v1/shelf'

axios.interceptors.response.use(
  function (response) {
    return response
  },
  function (error) {
    return Promise.reject(error)
  }
)

function GET (url, params) {
  let headers = {
  }
  return axios.get(url, {
    params: params,
    headers: headers
  })
}

function POST (url, params) {
  let headers = {
  }
  return axios.post(url, params, { headers: headers })
}

function PUT (url, params) {
  let headers = {
  }
  return axios.put(url, params, { headers: headers })
}

function DELETE (url, params) {
  let headers = {
  }
  return axios.delete(url, {
    headers: headers,
    data: params
  })
}

let robo = {
  getAppsList () {
    return GET(roboApi + '/apps-pvcs')
  },
  getBackupList () {
    return GET(roboApi + '/backup-restore')
  },
  createBackup (params) {
    return POST(roboApi + '/backup', params)
  },
  simulateDisaster () {
    return GET(roboApi + '/disaster')
  },
  createRestore (params) {
    return POST(roboApi + '/restore', params)
  },
  addShelf (params) {
    return POST(shelfApi + '/add', params)
  },
  uploadVideo (params) {
    return POST(shelfApi + '/video', params)
  },
  getShelfList () {
    return GET(shelfApi + '/table')
  },
  getProductList () {
    return GET(shelfApi + '/products')
  },
  getShelfNotificationList () {
    return GET(shelfApi + '/messages')
  },
  getShelfAlertNotificationList () {
    return GET(shelfApi + '/AlertsMessages')
  },
  getLiveVideo (shelfName) {
    return GET(shelfApi + '/video/' + shelfName)
  },
  getImage (msgId) {
    return GET(shelfApi + '/image/' + msgId)
  }
}

export {
  GET,
  POST,
  PUT,
  DELETE,
  robo,
  shelfApi
}
