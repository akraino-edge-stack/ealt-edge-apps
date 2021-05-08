<!--
  -  Copyright 2021 Huawei Technologies Co., Ltd.
  -
  -  Licensed under the Apache License, Version 2.0 (the "License");
  -  you may not use this file except in compliance with the License.
  -  You may obtain a copy of the License at
  -
  -      http://www.apache.org/licenses/LICENSE-2.0
  -
  -  Unless required by applicable law or agreed to in writing, software
  -  distributed under the License is distributed on an "AS IS" BASIS,
  -  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  -  See the License for the specific language governing permissions and
  -  limitations under the License.
  -->

<template>
  <div>
    <Search
      :status-item="false"
      :affinity-item="false"
      :ip-item="false"
      @getSearchData="getSearchData"
    />
    <div class="tableDiv">
      <el-row class="table">
        <el-table
          :data="currPageTableData"
          v-loading="dataLoading"
          class="mt20"
          border
          size="small"
          style="width: 100%;"
        >
          <el-table-column
            prop="shelfName"
            sortable
            :label="$t('Shelf Name')"
            width="130px"
            header-align="center"
            align="center"
          >
            <template slot-scope="scope">
              <span style="margin-left: 10px">{{ scope.row.shelfName }}</span>
            </template>
          </el-table-column>
          <el-table-column
            prop="location"
            :label="$t('Location')"
            width="120px"
            header-align="center"
            align="center"
          />
          <el-table-column
            :label="$t('Products')"
            header-align="center"
            align="center"
          >
            <template slot-scope="scope">
              <span
                v-for="(item,index) in scope.row.productDetails"
                :key="index"
                style="display: inline-block"
              >
                {{ item.productType }}
                <div
                  style="width: 80px; height: 20px; background-color: green; border-radius: 4px; color: white; margin: 4px; padding: 0px; display: inline-block"
                  v-if="item.status === 'Mostly Filled'"
                >
                  <span style="padding: 0">  {{ item.currentCount }} / {{ item.maxCount }} </span>
                </div>
                <div
                  style="width: 80px; height: 20px; background-color: red; border-radius: 4px; color: white; margin: 4px; padding: 0px; display: inline-block"
                  v-else-if="item.status === 'Needs Filling'"
                >
                  <span style="padding: 0">  {{ item.currentCount }} / {{ item.maxCount }} </span>
                </div>
                <div
                  style="width: 80px; height: 20px; background-color: orange; border-radius: 4px; color: white; margin: 4px; padding: 0px; display: inline-block"
                  v-else-if="item.status === 'Partially Filled'"
                >
                  <span style="padding: 0">  {{ item.currentCount }} / {{ item.maxCount }} </span>
                </div>
              </span>
            </template>
          </el-table-column>
          <el-table-column
            :label="$t('common.operation')"
            width="120px"
            header-align="center"
            align="center"
          >
            <template slot-scope="scope">
              <el-button
                id="liveVideo"
                @click.native.prevent="handleLiveVideo(scope.row)"
                type="text"
                size="small"
              >
                {{ $t('Live video') }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-row>
      <div class="pageBar">
        <pagination
          :page-sizes="[10,15,20,25]"
          :table-data="paginationData"
          @getCurrentPageData="getCurrentPageData"
        />
      </div>
    </div>
    <el-dialog
      :close-on-click-modal="false"
      :title="$t('Live video')"
      :visible.sync="dialogVisibleLiveVideo"
      width="50%"
    >
      <Camerapannel
        :delcamera="deleteCamera"
        :data="liveVideo"
      />
    </el-dialog>
  </div>
</template>

<script>
import { shelfApi } from '../tools/request.js'
import pagination from '../components/Pagination.vue'
import Camerapannel from './image.vue'
import Search from '../components/Search2.vue'
export default {
  name: 'AllInventory',
  props: {
    getShelfList:
        {
          type: Function,
          required: true
        },
    shelfData:
        {
          type: Array,
          required: true
        }
  },
  components: {
    pagination,
    Camerapannel,
    Search
  },
  data () {
    return {
      liveVideo: {},
      flvPlayer: null,
      paginationData: [],
      currPageTableData: [],
      dataLoading: false,
      tableData: [],
      dialogVisible: false,
      dialogVisibleLiveVideo: false,
      title: '',
      rlp: sessionStorage.getItem('rlp')
    }
  },
  mounted () {
    this.getShelfList()
  },
  watch: {
    shelfData (val) {
      if (val.length > 0) {
        console.log('setting data -> ', val)
        this.tableData = this.paginationData = val
        this.dataLoading = false
      }
    }
  },
  computed: {
  },
  methods: {
    getSearchData (data) {
      this.paginationData = this.tableData
      if (this.paginationData && this.paginationData.length > 0) {
        let reset = false
        for (let key in data) {
          if (data[key]) {
            reset = true
            let dataKey = key
            if (key === 'shelfName') {
              dataKey = 'shelfName'
            }
            this.filterTableData(data[key].toLowerCase(), dataKey)
          }
        }
        if (!reset) this.paginationData = this.tableData
      }
    },
    deleteCamera (cameraname) {
      console.log()
    },
    handleLiveVideo (row) {
      this.liveVideo = {
        name: row.shelfName,
        type: 'video/mp4',
        src: shelfApi + '/video/' + row.shelfName
      }
      this.dialogVisibleLiveVideo = true
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
    beforeDelete (row) {
      console.log('details')
    },

    handleError (error) {
      this.dialogVisible = false
      if (error.response.status === 404 && error.response.data.details[0] === 'Record not found') {
        this.$message.error(error.data.details[0])
      } else {
        this.$message.error(error.data)
      }
    }
  }
}
</script>

<style lang='less' scoped>
.box-card {
  width: 80px;
  height: 20px;
  color: green;
  padding: 0px !important;
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
}
.el-col{
  padding-left:0 !important;
}
</style>
