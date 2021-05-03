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
    <div class="restore">
      <el-row>
        <el-col span="24">
          <el-tabs
            v-model="activeName"
            class="tabs"
          >
            <el-tab-pane
              :label="$t('Apps')"
              name="Applications"
            >
              <Applications />
            </el-tab-pane>
            <el-tab-pane
              :label="$t('PVCs')"
              name="Pvcs"
            >
              <Pvcs />
            </el-tab-pane>
            <el-tab-pane
              :label="$t('Backup')"
              name="Backups"
            >
              <Backups />
            </el-tab-pane>
            <el-tab-pane
              :label="$t('Restore')"
              name="Restores"
            >
              <Restores />
            </el-tab-pane>
          </el-tabs>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import Applications from '@/app/Applications'
import Backups from '@/app/Backups'
import Pvcs from '@/app/Pvcs'
import Restores from '@/app/Restores'
export default {
  name: 'Sysk8s',
  components: {
    Restores,
    Pvcs,
    Backups,
    Applications
  },
  data () {
    return {
      activeName: 'Applications',
      paginationData: [],
      currPageTableData: [],
      dataLoading: true,
      tableData: [],
      title: '',
      rlp: sessionStorage.getItem('rlp')
    }
  },
  mounted () {
  },
  computed: {
  },
  methods: {
  }
}
</script>

<style lang='less' scoped>
.restore{
  margin: 0 3%;
  height: 100%;
  background: #fff;
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
