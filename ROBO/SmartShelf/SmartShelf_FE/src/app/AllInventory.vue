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
    <el-row>
      <el-col :span="24">
        <Search
          @getSearchData="getSearchData"
        />
      </el-col>
    </el-row>
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
            width="150px"
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
            width="150px"
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
                  style="width: 80px; height: 20px; background-color: orange; border-radius: 4px; color: white; margin: 4px; padding: 0px; display: inline-block"
                  v-else-if="item.status === 'Partially Filled'"
                >
                  <span style="padding: 0">  {{ item.currentCount }} / {{ item.maxCount }} </span>
                </div>
                <div
                  style="width: 80px; height: 20px; background-color: red; border-radius: 4px; color: white; margin: 4px; padding: 0px; display: inline-block"
                  v-else
                >
                  <span style="padding: 0">  {{ item.currentCount }} / {{ item.maxCount }} </span>
                </div>
              </span>
              <div v-show="dialogVisibleLiveVideo[scope.row.shelfName]" style="width: 50%; margin:auto; margin-top: 5px;">
                <Camerapannel
                  :shelfName=scope.row.shelfName
                  :inventoryType="inventoryType"
                />
              </div>
            </template>
          </el-table-column>
          <el-table-column
            :label="$t('common.operation')"
            width="180px"
            header-align="center"
            align="center"
          >
            <template slot-scope="scope">
              <el-button
                id="hideVideo"
                @click.native.prevent="handleHideVideo(scope.row)"
                type="text"
                size="small"
                v-if=dialogVisibleLiveVideo[scope.row.shelfName]
              >
                {{ $t('Hide video') }}
              </el-button>
              <el-button
                id="liveVideo"
                @click.native.prevent="handleLiveVideo(scope.row)"
                type="text"
                size="small"
                v-else
              >
                {{ $t('Live video') }}
              </el-button>
              <el-button
                  id="deleteButton"
                  @click.native.prevent="showDeleteWarning(scope.row)"
                  type="text"
                  size="small"
              >
                {{ $t('Delete') }}
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
  </div>
</template>

<script>
import { robo } from '../tools/request.js'
import pagination from '../components/Pagination.vue'
import Camerapannel from './image.vue'
import Search from '../components/Search2.vue'
export default {
  name: 'AllInventory',
  props: {
    getShelfList: {
      type: Function,
      required: true
    },
    shelfData: {
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
      inventoryType: 'All',
      flvPlayer: null,
      paginationData: [],
      currPageTableData: [],
      dataLoading: false,
      tableData: [],
      dialogVisible: false,
      dialogVisibleLiveVideo: [],
      title: '',
      searchData: '',
      rlp: sessionStorage.getItem('rlp')
    }
  },
  mounted () {
    this.getShelfList()
  },
  watch: {
    shelfData (val) {
      if (val.length > 0) {
        this.tableData = this.paginationData = val
        if (this.paginationData && this.paginationData.length > 0 && this.searchData) {
          this.filterTableData(this.searchData, 'shelfName')
        }
        this.dataLoading = false
      } else { 
        this.tableData = []
        this.paginationData = []
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
            this.searchData = data[key].toLowerCase()
            this.filterTableData(data[key].toLowerCase(), dataKey)
          }
        }
        if (!reset) {
          this.paginationData = this.tableData
          this.searchData = ''
        }
      }
    },
    handleLiveVideo (row) {
      let tmp = [...this.dialogVisibleLiveVideo]
      tmp[row.shelfName] = true
      this.dialogVisibleLiveVideo = tmp
      console.log(this.dialogVisibleLiveVideo)
    },
    handleHideVideo (row) {
      let tmp = [...this.dialogVisibleLiveVideo]
      tmp[row.shelfName] = false
      this.dialogVisibleLiveVideo = tmp
      console.log(this.dialogVisibleLiveVideo)
    },
    showDeleteWarning (row) {
      console.log('show delete warning')
      this.$confirm('Are you sure, you want to delete this Shelf?', 'Warning', {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        closeOnClickModal: false,
        showClose: false,
        type: 'warning'
      }).then(() => {
        this.deleteShelf(row)
      }).catch(() => {
      })
    },
    deleteShelf (row) {
      robo.deleteShelf(row.shelfName, row.location).then(res => {
        this.getShelfList()
      }).catch(err => {
        console.log(err)
      })
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
    margin-left: 10px;
    margin-right: 10px;
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
