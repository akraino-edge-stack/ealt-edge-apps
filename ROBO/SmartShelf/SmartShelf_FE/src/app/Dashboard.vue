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
            <el-col :span="18">
              <h1
                style="font-weight: 600;
                   margin-bottom: 10px;"
              >
                {{ $t('Shelf Management') }}
              </h1>
            </el-col>
            <el-col :span="6">
              <div style="float: right">
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
              </div>
            </el-col>
          </el-row>
          <el-row>
            <el-col :span="24">
              <el-tabs
                v-model="activeName"
              >
                <el-tab-pane name="All Inventory">
                  <span slot="label"><i class="el-icon-shopping-cart-full" /> All Inventory</span>
                  <AllInventory
                    :get-shelf-list="getShelfListInPage"
                    :shelf-data="shelfData"
                  />
                </el-tab-pane>
                <el-tab-pane name="Low Inventory">
                  <span slot="label"><i class="el-icon-shopping-cart-1" /> Low Inventory</span>
                  <LowInventory
                    :get-low-shelf-list="getLowShelfListInPage"
                    :low-shelf-data="lowShelfData"
                  />
                </el-tab-pane>
              </el-tabs>
            </el-col>
          </el-row>
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
                    :label="$t('Camera Url')"
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
                      <el-select
                        id="productName"
                        v-model="product.obj"
                        :placeholder="$t('Name')"
                        style="display:inline-block;"
                      >
                        <el-option
                          v-for="(item, i) in productList"
                          :key="i"
                          :label="item"
                          :value="item"
                        />
                      </el-select>
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
                {{ $t('Drag the file here，or click to upload') }}
              </div>
            </el-upload>
          </el-dialog>
        </div>
      </el-col>
      <el-col :span="8">
        <Notifications
          @onChange="getShelfListInPage"
          @OnChangeLowList="getLowShelfListInPage"
        />
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { robo } from '../tools/request.js'
import AllInventory from './AllInventory.vue'
import LowInventory from './LowInventory.vue'
import Notifications from '@/app/Notifications'
export default {
  name: 'Sysk8s',
  components: {
    Notifications,
    AllInventory,
    LowInventory
  },
  data () {
    return {
      productList: ['Bottle', 'ToyCar'],
      shelfData: [],
      lowShelfData: [],
      activeName: 'All Inventory',
      dataLoading: true,
      dialogVisible: false,
      dialogVisibleUpload: false,
      fileList: [],
      currForm: {
        shelfName: '',
        location: '',
        camName: 'Camera01',
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
    this.getLowShelfListInPage()
  },
  computed: {
  },
  methods: {
    deleteCamera (cameraname) {
      console.log()
    },
    delProductDetail (num) {
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
    filterTableData (val, key) {
      this.paginationData = this.paginationData.filter(item => {
        let itemVal = item[key]
        if (itemVal) return itemVal.toLowerCase().indexOf(val) > -1
      })
    },
    cancel (row) {
      this.dialogVisible = false
      this.resetForm()
    },
    resetForm () {
      this.currForm = {
        shelfName: '',
        location: '',
        camName: 'camera01',
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
      this.getProductList()
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
        this.showMessage('success', this.$t('Uploaded file successfully'), 1500)
        this.dialogVisibleUpload = false
      }).catch((error) => {
        console.log(error)
        this.fileList = []
        this.dialogVisibleUpload = false
      })
    },
    getShelfListInPage () {
      robo.getShelfList().then(response => {
        this.shelfData = response.data.shelfDetails
        this.dataLoading = false
      }).catch((error) => {
        this.dataLoading = false
        if (error.response.status === 404 && error.response.data.details[0] === 'Record not found') {
          this.shelfData = []
        } else {
          this.$message.error(this.$t('failed to shelf list'))
        }
      })
    },
    getLowShelfListInPage: function () {
      robo.getShelfList().then(response => {
        let shelfDetails = response.data.shelfDetails
        this.lowShelfData = []
        for (let i = 0; i < shelfDetails.length; i++) {
          let lowShelfEntry = false
          for (let j = 0; j < shelfDetails[i].productDetails.length; j++) {
            if (shelfDetails[i].productDetails[j].status === 'Needs Filling') {
              lowShelfEntry = true
            }
          }
          if (lowShelfEntry) {
            this.lowShelfData.push(shelfDetails[i])
          }
        }
        this.dataLoading = false
      }).catch((error) => {
        this.dataLoading = false
        if (error.response.status === 404 && error.response.data.details[0] === 'Record not found') {
          this.lowShelfData = []
        } else {
          this.$message.error(this.$t('failed to shelf list'))
        }
      })
    },
    getProductList () {
      robo.getProductList().then(response => {
        this.productList = response.data.ObjList
      }).catch((error) => {
        this.dataLoading = false
        if (error.response.status === 404 && error.response.data.details[0] === 'Record not found') {
          this.productList = []
        } else {
          this.$message.error(this.$t('failed to product list'))
        }
      })
    },
    confirm (form) {
      robo.addShelf(this.currForm).then(response => {
        if (response.data.responce === 'failure') {
          this.showMessage('error', this.$t('Failed to add shelf'), 1500)
        } else {
          this.showMessage('success', this.$t('Added shelf successfully'), 1500)
        }
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
