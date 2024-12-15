import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/home'
import Upload from '@/components/upload'
import Result from '@/components/result'
import Preprocess from '@/components/preprocess'
import TermExtraction from '@/components/termExtraction'
import AttiInference from '@/components/attiInference'
import IncomReport from '@/components/incomReport'

Vue.use(Router)


const myRouter = new Router({
  mode: 'history',
  base: 'lidetector',
  hashbang: true,
  history: false,
  saveScrollPosition: true,
  suppressTransitionError: true,
  routes: [
    {
      path: '/',
      redirect: '/home'
    },
    {
      path: '/home',
      component: Home
    },
    {
      path: '/upload',
      component: Upload,
    },
    {
      path: '/result',
      component: Result,
      children: [
        // {
        //   path: '/',
        //   redirect: '/preprocess'
        // },
        {
          path: '/result/preprocess',
          component: Preprocess,
        },
        {
          path: '/result/termExtraction',
          component: TermExtraction,
        },
        {
          path: '/result/attiInference',
          component: AttiInference,
        },
        {
          path: '/result/incomReport',
          component: IncomReport,
        }
      ]
    },
  ]
})



export default myRouter