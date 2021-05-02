/*
 *  Copyright 2020 Huawei Technologies Co., Ltd.
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


const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const app = express();
app.use(cors());
const path = require('path');
const socket = require("socket.io");

const env=process.env
const port = 5000;

console.log(env)
app.use('/static', express.static(path.join(__dirname, './public')));
app.use(bodyParser.json());

app.get('/', function(req, res) {
  res.send('connected to server successfully');
})

app.post('/notify', (req, res) => {
  io.sockets.emit('notify', req.body);
  res.send("Notify Successfully.");
})

const server = app.listen(port, '0.0.0.0', () => {
  console.log(`Server is running on http://node-proxy:${port}`)
})

const io = socket(server)
