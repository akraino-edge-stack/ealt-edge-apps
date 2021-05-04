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
    <h1
      style="font-weight: 600;
                   margin-bottom: 10px;"
    >
      {{ $t('Notifications') }}
    </h1>
    <h2
      style="font-weight: 500;
                   margin-bottom: 20px;"
    >
      {{ $t('Latest events and customer actions') }}
    </h2>
    <div class="tableDiv">
      <el-row class="table">
        <el-table
          :data="currPageTableData"
          v-loading="dataLoading"
          class="mt20"
          size="mini"
          :show-header="false"
          style="width: 100%;"
        >
          <el-table-column
            prop="notificationType"
            width="100px"
          >
            <template slot-scope="scope">
              <el-tag
                type="danger"
                v-if="scope.row.notificationType === 'Needs Filling'"
              >
                {{ scope.row.notificationType }}
              </el-tag>
              <el-tag
                type="warning"
                v-else-if="scope.row.notificationType === 'Product Mismatch'"
              >
                {{ scope.row.notificationType }}
              </el-tag>
              <el-tag
                type="warning"
                v-else
              >
                {{ scope.row.notificationType }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            prop="msg"
            width="150px"
          />
          <el-table-column
            prop="time"
            width="80px"
          />
          <el-table-column
            width="55px"
          >
            <template slot-scope="scope">
              <el-button
                id="details"
                @click.native.prevent="handleDetail(scope.row)"
                type="text"
                size="mini"
              >
                {{ $t('Image') }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-row>
      <div class="pageBar2">
        <pagination
          :page-sizes="[10,15,20,25]"
          :table-data="paginationData"
          @getCurrentPageData="getCurrentPageData"
        />
      </div>
    </div>
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
import pagination from '../components/Pagination.vue'
import io from 'socket.io-client'
export default {
  name: 'Notifications',
  props: {
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
    this.getShelfNotificationListInPage()
  },
  computed: {
  },
  created () {
    // Client receives the message:
    const socket = io.connect('http://localhost:5000/')
    socket.on('notify', (data) => {
      this.getShelfNotificationListInPage()
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
  height: 100%;
  background: #fff;
  padding: 10px 10px;
  .table {
    margin-top: 10px;
  }
  .tableDiv {
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
.el-col{
  padding-left:0 !important;
}
</style>
