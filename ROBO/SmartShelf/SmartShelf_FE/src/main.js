import Vue from 'vue'
import App from './App.vue'
import router from './router/router.js'
import ElementUI from 'element-ui'
import '../src/assets/style/common.less'
import locale from 'element-ui/lib/locale/lang/en'
import 'element-ui/lib/theme-chalk/index.css'
import 'element-ui/lib/theme-chalk/display.css'
import i18n from './locales/i18n.js'

Vue.use(ElementUI, { locale })
Vue.config.productionTip = false

new Vue({
  router,
  i18n,
  render: (h) => h(App)
}).$mount('#app')
