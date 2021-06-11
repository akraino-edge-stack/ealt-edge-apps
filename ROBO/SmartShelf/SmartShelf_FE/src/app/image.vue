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
export default {
  name: 'Camerapannel',
  props: {
    data: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      flvPlayer: null,
      videoData: ''
    }
  },
  methods: {
    playVideo() {
      console.log('playvideo')
      if (flvjs.isSupported()) {
        console.log('vid id', this.vidId)
        console.log('videoData', this.videoData)
        var videoElement = document.getElementById(this.vidId)
        console.log('data -> ', this.data)
        console.log('videoElement', videoElement)
        videoElement.crossOrigin = 'anonymous'
        this.flvPlayer = flvjs.createPlayer({
          type: 'mp4',
          isLive: true,
          url: 'http://localhost:30995/v1/shelf/video/' + this.data
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
      return this.data + 'videoElement'
    }
  },
  watch: {
    data (val) {
      console.log('in watch of image ', val)
      this.data = val
      this.videoData = val
      console.log(this.data)
      this.playVideo()
    }
  },
  mounted () {
    console.log('in image mounted', this.data)
    this.videoData = this.data
    console.log('in image mounted video data', this.videoData)
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
