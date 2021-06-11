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
  <el-card :body-style="{ padding: '0px' }">
    <div class="video-cards">
      <div
        class="video-player vjs-custom-skin"
      >
        <video controls
          muted
          loop
          :id="vidId"
          width="100%"
          height="100%"
          crossOrigin="anonymous"
        />
      </div>
    </div>
  </el-card>
</template>

<script>
import flvjs from 'flv.js'
import { shelfApi } from '../tools/request.js'
export default {
  name: 'Camerapannel',
  props: {
    shelfName: {
      type: String,
      required: true
    },
    inventoryType: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      flvPlayer: null,
    }
  },
  methods: {
    playVideo() {
      console.log('playvideo')
      if (flvjs.isSupported()) {
        console.log('vid id', this.vidId)
        var videoElement = document.getElementById(this.vidId)
        console.log('shelfName -> ', this.shelfName)
        console.log('inventory type -> ', this.inventoryType)
        console.log('videoElement', videoElement)
        videoElement.crossOrigin = 'anonymous'
        let videoUrl = shelfApi + '/video/' + this.shelfName
        this.flvPlayer = flvjs.createPlayer({
          type: 'mp4',
          isLive: true,
          url: videoUrl
        }, {
          enableWorker: false,
          enableStashBuffer: false,
          isLive: true,
          lazyLoad: false,
          stashInitialSize: 0,
          autoCleanupSourceBuffer: true
        })
        this.flvPlayer.attachMediaElement(videoElement)
        this.flvPlayer.load()
        let playPromise = this.flvPlayer.play()
        if (playPromise !== undefined) {
          playPromise.then(() => {
            this.flvPlayer.play()
          }).catch((e) => { console.log(e) })
        }
      }
    }
  },
  computed: {
    vidId: function () {
      return this.shelfName + this.inventoryType + 'videoElement'
    }
  },
  watch: {
  },
  mounted () {
    this.playVideo()
  }
}
</script>

<style scoped lang="less">
.video-cards{
    width: 100%;
    height: 100%;
}
.video-player vjs-custom-skin {
  video {
    margin-bottom: 30px;
  }
}
.camera-details-con {
    display: flex;
    justify-content: space-between;
}
.cd-text{
    font-size: 22px;
    font-weight: bold;
}
</style>
