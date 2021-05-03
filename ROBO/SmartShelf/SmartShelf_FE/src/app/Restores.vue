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
    <div class="pannel">
      <Search
        :status-item="false"
        :affinity-item="false"
        :ip-item="false"
        @getSearchData="getSearchData"
      />
      <p
        class="btn-restore"
      >
        <el-button
          id="disasterBtn"
          type="primary"
          dark
          size="small"
          @click="restore()"
        >
          {{ $t('Restore') }}
        </el-button>
      </p>
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
              prop="name"
              sortable
              :label="$t('Name')"
              header-align="center"
              align="center"
            >
              <template slot-scope="scope">
                <span style="margin-left: 10px">{{ scope.row.name }}</span>
              </template>
            </el-table-column>
            <el-table-column
              prop="backup"
              :label="$t('Backup')"
              header-align="center"
              align="center"
            />
            <el-table-column
              prop="status"
              :label="$t('Status')"
              header-align="center"
              align="center"
            />
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
        :title="title"
        :visible.sync="dialogVisible"
        style="padding-right:30px;"
        width="40%"
      >
        <div class="k8s">
          <el-row>
            <el-form
              label-width="auto"
              :model="currForm"
              ref="currForm"
            >
              <el-form-item
                :label="$t('Restore Name')"
                prop="restoreName"
              >
                <el-input
                  id="restoreName"
                  maxlength="20"
                  v-model="currForm.restoreName"
                />
              </el-form-item>
              <el-form-item
                :label="$t('Backup Name')"
                maxlength="20"
                prop="backupName"
              >
                <el-input
                  id="backupName"
                  v-model="currForm.backupName"
                />
              </el-form-item>
            </el-form>
          </el-row>
        </div>
        <span
          slot="footer"
          class="dialog-footer"
        >
          <el-button
            id="cancelBtn"
            size="small"
            @click="cancel()"
          >{{ $t('common.cancel') }}</el-button>
          <el-button
            id="confirmBtn"
            type="primary"
            size="small"
            @click="confirm('currForm')"
          >{{ $t('common.confirm') }}</el-button>
        </span>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import { robo } from '../tools/request.js'
import pagination from '../components/Pagination.vue'
import Search from '../components/Search.vue'
export default {
  name: 'Restores',
  components: {
    pagination, Search
  },
  data () {
    return {
      paginationData: [],
      currPageTableData: [],
      dataLoading: true,
      tableData: [],
      dialogVisible: false,
      currForm: {
        restoreName: '',
        backupName: ''
      },
      title: '',
      rlp: sessionStorage.getItem('rlp')
    }
  },
  mounted () {
    this.getRestoreListInPage()
  },
  computed: {
  },
  methods: {
    confirm (form) {
      robo.createRestore(this.currForm).then(response => {
        this.showMessage('success', this.$t('tip.sucToRegNode'), 1500)
        this.getBackupListInPage()
        this.dialogVisible = false
      }).catch((error) => {
        this.handleError(error)
      })
    },
    handleError (error) {
      this.dialogVisible = false
      if (error.response.status === 404 && error.response.data.details[0] === 'Record not found') {
        this.$message.error(error.data.details[0])
      } else if (error.status === 403) {
        this.$message.error(this.$t('tip.loginOperation'))
      } else {
        this.$message.error(error.data)
      }
    },
    cancel () {
      this.dialogVisible = false
      this.resetForm()
    },
    resetForm () {
      this.currForm = {
        restoreName: '',
        backupName: ''
      }
    },
    restore () {
      this.title = this.$t('Restore')
      this.dialogVisible = true
      this.resetForm()
    },
    filterTableData (val, key) {
      this.paginationData = this.paginationData.filter(item => {
        let itemVal = item[key]
        if (itemVal) return itemVal.toLowerCase().indexOf(val) > -1
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
    getCurrentPageData (data) {
      this.currPageTableData = data
    },
    getRestoreListInPage () {
      robo.getBackupList().then(response => {
        this.tableData = this.paginationData = response.data.restoresData
        this.dataLoading = false
      }).catch((error) => {
        this.dataLoading = false
        if (error.response.status === 404 && error.response.data.details[0] === 'Record not found') {
          this.tableData = this.paginationData = []
        } else {
          this.$message.error(this.$t('failed to get restore list'))
        }
      })
    }
  }
}
</script>

<style lang='less' scoped>
.restore{
  margin: 0 3%;
  height: 100%;
  background: #fff;
  padding: 10px 10px;
  .table {
    margin-top: 10px;
  }
  .tableDiv {
    margin-top: 10px;
    padding: 0px 30px;
  }
  .btn-add {
    height: 40px;
    padding:8px 8px;
    float: left;
  }
}
.btn-restore {
  margin-left: 30px;
  margin-top: 20px;
}
.el-col{
  padding-left:0 !important;
}
</style>
