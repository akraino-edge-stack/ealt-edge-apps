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
    <div class="tableDiv">
      <el-row class="table">
        <el-table
          :data="currPageTableData"
          v-loading="dataLoading"
          class="mt0"
          size="mini"
          :show-header="false"
          style="width: 100%;"
        >
          <el-table-column
            prop="notificationType"
            :label="$t('Type')"
          >
            <template slot-scope="scope">
              <div
                v-if="scope.row.notificationType === 'Partially Filled'"
              >
                <span class="notificationTagPartiallyFilled">  {{ scope.row.notificationType }} </span>
              </div>
              <div
                v-else-if="scope.row.notificationType === 'Mostly Filled'"
              >
                <span class="notificationTagMostlyFilled">  {{ scope.row.notificationType }} </span>
              </div>
              <div
                v-else
              >
                <span class="notificationTag">  {{ scope.row.notificationType }} </span>
              </div>

              <div>
                <span style="font-size: 13px">{{ scope.row.msg }}</span>
              </div>
              <div>
                <i
                  style="margin-right: 8px"
                  class="el-icon-time"
                />
                <span style="font-size: 10px">{{ scope.row.time }} </span>
              </div>
            </template>
          </el-table-column>
          <el-table-column
            width="45px"
            :label="$t('Action')"
          >
            <template slot-scope="scope">
              <el-button
                id="details"
                @click.native.prevent="handleDetail(scope.row)"
                type="text"
                size="mini"
              >
                <img
                  class="cp"
                  src="../assets/images/image_new.svg"
                  alt=""
                  style="width: 20px;"
                >
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-row>
      <div class="pageBar2">
        <pagination
          :page-sizes="[7,14,21,28]"
          :table-data="paginationData"
          @getCurrentPageData="getCurrentPageData"
        />
      </div>
    </div>

    <el-dialog
      :close-on-click-modal="false"
      :title="$t('Latest Customer Action')"
      :visible.sync="dialogVisibleImage"
      width="50%"
    >
      <img
        class="image-src"
        :src="this.image"
        alt=""
        style="width: 100%;padding: 20px 20px;"
      >
    </el-dialog>
  </div>
</template>

<script>
import { robo } from '../tools/request.js'
import pagination from '../components/Pagination.vue'
export default {
  name: 'Alerts',
  props: {
    getShelfAlertNotificationList:
        {
          type: Function,
          required: true
        },
    alertMessagesData:
        {
          type: Array,
          required: true
        }
  },
  components: {
    pagination
  },
  data () {
    return {
      image: {},
      paginationData: [],
      currPageTableData: [],
      dataLoading: true,
      tableData: [],
      dialogVisibleImage: false,
      rlp: sessionStorage.getItem('rlp')
    }
  },
  mounted () {
    this.getShelfAlertNotificationList()
  },
  computed: {
  },
  watch: {
    alertMessagesData (val) {
      if (val.length > 0) {
        this.tableData = this.paginationData = val
        this.dataLoading = false
      } else {
        this.tableData = this.paginationData = []
        this.dataLoading = false
      }
    }
  },
  methods: {
    handleDetail (row) {
      this.getImage(row.msgid)
      this.dialogVisibleImage = true
    },
    filterTableData (val, key) {
      this.paginationData = this.paginationData.filter(item => {
        let itemVal = item[key]
        if (itemVal) return itemVal.toLowerCase().indexOf(val) > -1
      })
    },
    getCurrentPageData (data) {
      this.currPageTableData = data
    },
    getShelfNotificationListInPage () {
      robo.getShelfNotificationList().then(response => {
        this.tableData = this.paginationData = response.data.Notifications
        this.currPageTableData = this.tableData
        this.dataLoading = false
      }).catch((error) => {
        this.dataLoading = false
        if (error.response.status === 404 && error.response.data.details[0] === 'Record not found') {
          this.tableData = this.paginationData = []
        } else {
          this.$message.error(this.$t('failed to get notifications list'))
        }
      })
    },
    getSearchData (data) {
      this.paginationData = this.tableData
      if (this.paginationData && this.paginationData.length > 0) {
        let reset = false
        for (let key in data) {
          if (data[key]) {
            reset = true
            let dataKey = key
            if (key === 'name') {
              dataKey = 'name'
            }
            this.filterTableData(data[key].toLowerCase(), dataKey)
          }
        }
        if (!reset) this.paginationData = this.tableData
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
  height: 100%;
  background: #fff;
  padding: 10px 10px;
  .table {
    margin-top: 10px;
  }
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
  padding: 3px 9px;
  width: 100%;
  background-color: #F56C6C;
  border-color: #F56C6C;
  color: white;
  border-radius: 4px;
  text-align: center;
  font-size: small;
}
.notificationTagPartiallyFilled {
  padding: 3px 9px;
  width: 100%;
  background-color: #e6a23c;
  border-color: #e6a23c;
  color: white;
  border-radius: 4px;
  text-align: center;
  font-size: small;
}
.notificationTagMostlyFilled {
  padding: 3px 9px;
  width: 100%;
  background-color: #67c23a;
  border-color: #67c23a;
  color: white;
  border-radius: 4px;
  text-align: center;
  font-size: small;
}
.el-col{
padding-left:0 !important;
}
</style>
