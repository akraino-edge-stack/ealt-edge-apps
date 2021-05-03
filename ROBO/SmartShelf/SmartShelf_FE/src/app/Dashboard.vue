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
      <el-col :span="16">
        <div class="sysk8s">
          <el-row>
            <el-col :span="16">
              <h1
                style="font-weight: 600;
                   margin-bottom: 10px;"
              >
                {{ $t('Shelf Management') }}
              </h1>
            </el-col>
            <el-col :span="8">
              <p
                class="btn-add"
              >
                <el-button
                  id="addShelf"
                  type="primary"
                  @click="addShelf()"
                >
                  {{ $t('Add shelf') }}
                </el-button>
              </p>
              <p
                class="btn-add"
              >
                <el-button
                  id="uploadVideo"
                  type="primary"
                  @click="uploadFile()"
                >
                  {{ $t('Upload video') }}
                </el-button>
              </p>
            </el-col>
          </el-row>
          <el-row>
            <el-col :span="16">
              <el-tabs
                v-model="activeName"
              >
                <el-tab-pane>
                  <span slot="label"><i class="el-icon-shopping-cart-full" /> All Inventory</span>
                </el-tab-pane>
                <el-tab-pane>
                  <span slot="label"><i class="el-icon-shopping-cart-1" /> Low Inventory</span>
                </el-tab-pane>
              </el-tabs>
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
                  :label="$t('Name')"
                  width="110px"
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
                  width="110px"
                  header-align="center"
                  align="center"
                />
                <el-table-column
                  prop="camName"
                  :label="$t('Camera')"
                  width="110px"
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
                  width="110px"
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
                    :label="$t('Shelf Name')"
                    prop="shelfName"
                  >
                    <el-input
                      id="shelfName"
                      maxlength="20"
                      v-model="currForm.shelfName"
                    />
                  </el-form-item>
                  <el-form-item
                    :label="$t('Location')"
                    prop="location"
                  >
                    <el-input
                      id="location"
                      v-model="currForm.location"
                    />
                  </el-form-item>
                  <el-form-item
                    :label="$t('Camera Name')"
                    prop="camName"
                  >
                    <el-input
                      id="camName"
                      v-model="currForm.camName"
                    />
                  </el-form-item>
                  <el-form-item
                    :label="$t('rtspUrl')"
                    prop="rtspUrl"
                  >
                    <el-input
                      id="rtspUrl"
                      v-model="currForm.rtspUrl"
                    />
                  </el-form-item>
                  <el-form-item
                    v-for="(product,index) in currForm.productDetails"
                    :label="'Product'+(index+1) "
                    :key="index"
                    style="display:inline-block;"
                  >
                    <el-form-item
                      label="Name"
                      :prop="`productDetails[${index}].obj`"
                      style="display:inline-block;"
                    >
                      <el-input v-model="product.obj" />
                    </el-form-item>
                    <el-form-item
                      label="Max Count"
                      :prop="`productDetails[${index}].MaxCount`"
                      style="display:inline-block;"
                    >
                      <el-input-number v-model="product.MaxCount" />
                    </el-form-item>
                    <el-form-item style="display:inline-block;">
                      <el-button
                        icon="el-icon-delete"
                        @click="delProductDetail(index)"
                      />
                    </el-form-item>
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
                id="addProductBtn"
                size="small"
                @click="addProductDetail()"
              >{{ $t('Add Product') }}</el-button>
              <el-button
                id="confirmBtn"
                type="primary"
                size="small"
                @click="confirm('currForm')"
              >{{ $t('common.confirm') }}</el-button>
            </span>
          </el-dialog>
          <el-dialog
            :close-on-click-modal="false"
            :title="$t('Upload Video')"
            :visible.sync="dialogVisibleUpload"
            width="30%"
          >
            <el-upload
              id="upload"
              class="upload-demo"
              drag
              action=""
              :http-request="submitUpload"
              :before-upload="beforeUpload"
              :file-list="fileList"
              :multiple="false"
              accept=""
              :limit="1"
            >
              <em class="el-icon-upload" />
              <div class="el-upload__text">
                {{ $t('system.edgeNodes.howToUpload') }}
              </div>
            </el-upload>
          </el-dialog>
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
      </el-col>
      <el-col :span="8">
        <Notifications
          @onChange="getShelfListInPage"
        />
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { robo } from '../tools/request.js'
import pagination from '../components/Pagination.vue'
import Camerapannel from './image.vue'
import Notifications from '@/app/Notifications'
export default {
  name: 'Sysk8s',
  components: {
    Notifications,
    pagination,
    Camerapannel
  },
  data () {
    return {
      formData: {
        name: '',
        location: '',
        rtspurl: ''
      },
      liveVideo: {},
      image: {},
      cameraList: [],
      flvPlayer: null,
      activeName: 'All Inventory',
      paginationData: [],
      currPageTableData: [],
      dataLoading: true,
      tableData: [],
      dialogVisible: false,
      dialogVisibleUpload: false,
      dialogVisibleLiveVideo: false,
      dialogVisibleImage: false,
      fileList: [],
      currForm: {
        shelfName: '',
        location: '',
        camName: '',
        rtspUrl: '',
        productDetails: [{
          obj: '',
          MaxCount: ''
        }]
      },
      title: '',
      fileConfirm: true,
      rlp: sessionStorage.getItem('rlp')
    }
  },
  mounted () {
    this.getShelfListInPage()
    this.getLiveVideo('FrontShelf')
  },
  computed: {
  },
  methods: {
    deleteCamera (cameraname) {
      console.log()
    },
    delProductDetail (num) {
      console.log('delete product', num)
      let index = this.currForm.productDetails.indexOf(num)
      console.log('index', index)
      if (num !== -1) {
        this.currForm.productDetails.splice(num, 1)
      }
    },
    addProductDetail () {
      console.log('add product detail length -> ', this.currForm.productDetails.length)
      this.currForm.productDetails.push({
        obj: '',
        MaxCount: ''
      })
    },
    handleLiveVideo (row) {
      this.getLiveVideo(row.shelfName)
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
    cancel (row) {
      this.dialogVisible = false
      this.resetForm()
    },
    resetForm () {
      this.currForm = {
        shelfName: '',
        location: '',
        camName: '',
        rtspUrl: '',
        productDetails: []
      }
    },
    beforeDelete (row) {
      console.log('details')
    },
    addShelf () {
      this.title = this.$t('Add Shelf')
      this.resetForm()
      this.dialogVisible = true
    },
    beforeUpload (file) {
      console.log(file)
    },
    uploadFile () {
      console.log('upload File')
      this.fileList = []
      this.dialogVisibleUpload = true
    },
    async submitUpload (content) {
      let params = new FormData()
      params.append('file', content.file)
      robo.uploadVideo(params).then(response => {
        this.showMessage('success', this.$t('tip.uploadSuc'), 1500)
        this.dialogVisibleUpload = false
      }).catch((error) => {
        console.log(error)
        this.fileList = []
        this.dialogVisibleUpload = false
      })
    },
    getShelfListInPage () {
      robo.getShelfList().then(response => {
        this.tableData = this.paginationData = response.data.shelfDetails
        this.dataLoading = false
      }).catch((error) => {
        this.dataLoading = false
        if (error.response.status === 404 && error.response.data.details[0] === 'Record not found') {
          this.tableData = this.paginationData = []
        } else {
          this.$message.error(this.$t('failed to shelf list'))
        }
      })
    },
    confirm (form) {
      robo.addShelf(this.currForm).then(response => {
        this.showMessage('success', this.$t('Added shelf successfully'), 1500)
        this.getShelfListInPage()
        this.dialogVisible = false
      }).catch((error) => {
        this.handleError(error)
      })
      this.dialogVisible = false
    },
    handleError (error) {
      this.dialogVisible = false
      if (error.response.status === 404 && error.response.data.details[0] === 'Record not found') {
        this.$message.error(error.data.details[0])
      } else {
        this.$message.error(error.data)
      }
    },
    getLiveVideo (shelfName) {
      robo.getLiveVideo(shelfName).then(response => {
        if (response.status === 200) {
          let obj = {
            name: 'shlef1.mp4',
            type: 'video/mp4',
            location: '',
            src: 'http://0.0.0.0:9995/v1/shelf/video/FrontShelf',
            rtspurl: 'shlef1.mp4'
          }
          this.liveVideo = obj
        }
      }).catch((error) => {
        this.handleError(error)
      })
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
