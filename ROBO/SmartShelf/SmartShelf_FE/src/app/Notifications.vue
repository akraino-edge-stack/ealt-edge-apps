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
<template>
  <div class="notifications">
    <el-row>
      <el-col :span="6">
        <h1
          style="font-weight: 600;
                   margin-bottom: 10px;"
        >
          {{ $t('Events') }}
        </h1>
      </el-col>
      <el-col :span="18">
        <Search
          :status-item="false"
          :affinity-item="false"
          :ip-item="false"
          @getSearchData="getSearchData"
        />
      </el-col>
    </el-row>
    <el-tabs
      v-model="activeName"
    >
      <el-tab-pane name="All">
        <span slot="label"><i class="el-icon-message-solid" />
          All</span>

        <AllEvents
          :get-shelf-notification-list="getShelfNotificationListInPage"
          :all-messages-data="allMessages"
        />
      </el-tab-pane>
      <el-tab-pane name="Alert">
        <span slot="label"><i class="el-icon-warning" />Alert</span>
        <Alerts
          :get-shelf-alert-notification-list="getShelfAlertNotificationListInPage"
          :alert-messages-data="alertMessages"
        />
      </el-tab-pane>
    </el-tabs>
    <el-dialog
      :close-on-click-modal="false"
      :title="$t('Latest Customer Action')"
      :visible.sync="dialogVisibleImage"
      width="55%"
    >
      <img
        class="image-src"
        :src="this.image"
        alt=""
      >
    </el-dialog>
  </div>
</template>

<script>
import { robo } from '../tools/request.js'
import Search from '../components/Search2.vue'
import io from 'socket.io-client'
import AllEvents from './AllEvents.vue'
import Alerts from './Alerts.vue'
export default {
  name: 'Notifications',
  props: {
  },
  components: {
    AllEvents,
    Alerts,
    Search
  },
  data () {
    return {
      image: {},
      activeName: 'All',
      allMessages: [],
      alertMessages: [],
      dataLoading: true,
      dialogVisibleImage: false,
      rlp: sessionStorage.getItem('rlp')
    }
  },
  mounted () {
    this.getShelfNotificationListInPage()
    this.getShelfAlertNotificationListInPage()
  },
  computed: {
  },
  created () {
    // Client receives the message:
    const socket = io.connect('http://localhost:5000/')
    socket.on('notify', (data) => {
      this.getShelfNotificationListInPage()
      this.getShelfAlertNotificationListInPage()
      this.$emit('onChange')
      this.$emit('OnChangeLowList')
    })
  },
  methods: {
    handleDetail (row) {
      this.getImage(row.msgid)
      this.dialogVisibleImage = true
    },
    filterTableData (val, key) {
      console.log('filtertable data', val, key)
      this.alertMessages = this.alertMessages.filter(item => {
        let itemVal = item[key]
        console.log(itemVal)
        console.log(itemVal.toLowerCase().indexOf(val) > -1)
        if (itemVal) return itemVal.toLowerCase().indexOf(val) > -1
      })
      this.allMessages = this.allMessages.filter(item => {
        let itemVal = item[key]
        console.log(itemVal)
        console.log(itemVal.toLowerCase().indexOf(val) > -1)
        if (itemVal) return itemVal.toLowerCase().indexOf(val) > -1
      })
    },
    getCurrentPageData (data) {
      this.currPageTableData = data
    },
    getShelfNotificationListInPage () {
      robo.getShelfNotificationList().then(response => {
        this.allMessages = response.data.Notifications
        this.dataLoading = false
      }).catch((error) => {
        this.dataLoading = false
        if (error.response.status === 404 && error.response.data.details[0] === 'Record not found') {
          this.allMessages = []
        } else {
          this.$message.error(this.$t('failed to get notifications list'))
        }
      })
    },
    getShelfAlertNotificationListInPage () {
      robo.getShelfAlertNotificationList().then(response => {
        this.alertMessages = response.data.Notifications
        this.dataLoading = false
      }).catch((error) => {
        this.dataLoading = false
        if (error.response.status === 404 && error.response.data.details[0] === 'Record not found') {
          this.alertMessages = []
        } else {
          this.$message.error(this.$t('failed to get notifications list'))
        }
      })
    },
    getSearchData (data) {
      this.paginationData = this.tableData
      let reset = false
      if (this.allMessages && this.allMessages.length > 0) {
        for (let key in data) {
          if (data[key]) {
            reset = true
            let dataKey = 'msg'
            if (key === 'shelfName') {
              dataKey = 'msg'
            }
            this.filterTableData(data[key].toLowerCase(), dataKey)
          }
        }
      }
      if (!reset) {
        console.log('reset is false')
        this.getShelfNotificationListInPage()
        this.getShelfAlertNotificationListInPage()
      }
    },
    handleError (error) {
      this.dialogVisible = false
      if (error.response.status === 404 && error.response.data.details[0] === 'Record not found') {
        this.$message.error(error.data.details[0])
      } else {
        this.$message.error(error.data)
      }
    },
    async getImage (msgId) {
      console.log('get image method', msgId)
      await robo.getImage(msgId).then(response => {
        if (response.status === 200) {
          this.image = 'data:image/jpeg;base64,' + response.data.image
        }
      }).catch((error) => {
        this.handleError(error)
      })
      return this.image
    }
  }
}
</script>

<style scoped lang="less">
.box-card {
  width: 80px;
  height: 20px;
  color: green;
  padding: 0px !important;
}
.image-src {
  margin-bottom: 20px;
}
.sysk8s{
  margin: 0 3%;
  height: 100%;
  background: #fff;
  padding: 10px 10px;
  .table {
    margin-top: 10px;
  }
  .tableDiv {
    margin-top: 10px;
  }
  .btn-add {
    height: 40px;
    padding:8px 8px;
    float: left;
  }
}
.notifications{
  margin-right: 5%;
  height: 95%;
  background: #fff;
  .el-dialog__body {
    padding: 30px 20px;
    color: #606266;
    font-size: 14px;
    word-break: break-all;
    display: flex;
    justify-content: center;
  }
}
.notificationTag {
  width: 100px;
  background-color: #fef0f0;
  border-color: #fde2e2;
  color: #f56c6c;
  border-radius: 4px;
  text-align: center;
  font-size: small;
}
.el-col{
padding-left:0 !important;
}
</style>
