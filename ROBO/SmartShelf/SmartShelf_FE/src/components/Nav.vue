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
  <div class="navgation">
    <el-row :gutter="10">
      <el-col
        :lg="6"
        :md="12"
        :sm="12"
        :xs="12"
      >
        <div
          class="logo"
          @click="jumpLogoTo"
        >
          <img
            class="cp"
            src="../assets/images/AK.png"
            alt=""
            style="width: 40px;"
          >
          <h1 class="project-header">Smart Shelf</h1>
        </div>
      </el-col>
      <el-col
        :lg="12"
        class="hidden-md-and-down"
      >
        <div>
          <Topbar
            v-if="!smallMenu"
            :json-data="jsonData"
          />
        </div>
      </el-col>
      <el-col
        :lg="6"
        :md="12"
        :sm="12"
        :xs="12"
      >
        <div class="nav-tabs">
          <div class="btn rt hidden-lg-and-up">
            <em
              class="el-icon-s-unfold"
              @click="openNav"
            />
          </div>
        </div>
      </el-col>
    </el-row>

    <el-collapse-transition>
      <div
        v-if="smallMenu"
        id="menu-div"
      >
        <Topbarsmall
          :json-data="jsonData"
          @closeMenu="closeMenu"
        />
      </div>
    </el-collapse-transition>
  </div>
</template>

<script>
import NavData from '../data/NavData.js'
import Topbar from '../components/Topbar'
import Topbarsmall from '../components/Topbarsmall'
export default {
  name: 'Navgation',
  components: {
    Topbar,
    Topbarsmall
  },
  data () {
    return {
      jsonData: [],
      language: 'en',
      lang: 'English',
      smallMenu: false
    }
  },
  watch: {
    $route (to) {
      sessionStorage.setItem('before_route', to.path)
    }
  },
  mounted () {
    this.jsonData = NavData
    this.language = localStorage.getItem('language') || 'en'
    this.$i18n.locale = this.language
    if (!localStorage.getItem('language')) {
      localStorage.setItem('language', 'en')
    }
  },
  methods: {
    jumpTo (path) {
      this.$router.push(path)
    },
    os () {
      let UserAgent = navigator.userAgent.toLowerCase()
      return {
        isWindows: /windows/.test(UserAgent),
        isMac: /mac/.test(UserAgent)
      }
    },
    openNav () {
      this.smallMenu = !this.smallMenu
    },
    closeMenu (data) {
      this.smallMenu = data
    },
    jumpLogoTo () {
      this.$router.push('/')
    }
  }
}
</script>

<style lang="less" scoped>
.project-header {
  display: inline-block;
  color: white;
  font-size: x-large;
  font-weight: 600;
  margin-inline-start: inherit;
}
.navgation {
  background: #282b33;
  height: 65px;
  top: 0px;
  width: 100%;
  position: fixed;
  z-index: 12;
  .logo {
    height: 65px;
    width: 430px;
    line-height: 65px;
    margin-left: 17px;
    display: flex;
    align-items: center;
    img {
      position: relative;
      top: 0px;
      width: 150px;
    }
    span {
      position: relative;
      top: -28px;
      font-size: 18px;
      color: #ffffff;
      left: 20px;
      cursor: pointer;
    }
    span.blue {
      color: #409eff;
    }
  }
  .language {
    display: inline-block;
    line-height: 65px;
    font-size: 14px;
    color: #6c92fa;
    span {
      width: 60px !important;
      top: 3px !important;
    }
    span:hover {
      text-decoration: underline;
    }
  }
  .user {
    display: inline-block;
    line-height: 65px;
    font-size: 14px;
    color: #6c92fa;
    span {
      width: 100%;
      top: 3px !important;
    }
    span:hover {
      text-decoration: underline;
    }
  }
  .nav-tabs {
    height: 100%;
    font-size: 20px;
    line-height: 50px;
    margin-right: 10px;
    span {
      height: 24px;
      margin-right: 10px;
      position: relative;
      top: 8px;
      cursor: pointer;
      color: #f5f5f5;
    }
    span.el-icon-user-solid.blue {
      color: #409eff;
    }
  }
  // 移动端
  .el-icon-s-unfold {
    color: #ffffff;
    line-height: 65px;
    top: 3px;
    position: relative;
  }
  .menu-div {
    overflow-y: auto;
  }
}
</style>
