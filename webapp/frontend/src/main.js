// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'

import ElementUI from'element-ui'
import'element-ui/lib/theme-chalk/index.css'
import axios from 'axios'

Vue.prototype.axios = axios
Vue.config.productionTip = false
Vue.use(ElementUI)


import uploader from 'vue-simple-uploader'
Vue.use(uploader)


import {BootstrapVue,BootstrapVueIcons} from 'bootstrap-vue'
Vue.use(BootstrapVue)
Vue.use(BootstrapVueIcons)
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'


/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})






