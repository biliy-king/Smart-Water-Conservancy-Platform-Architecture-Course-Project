import Vue from 'vue'
import VueRouter from 'vue-router'
import lanhu_androidexpanded3 from '../views/lanhu_androidexpanded3/index.vue'
import lanhu_groupandroidexpanded1 from '../views/lanhu_groupandroidexpanded1/index.vue'
import lanhu_frame3 from '../views/lanhu_frame3/index.vue'
import lanhu_androidexpanded2 from '../views/lanhu_androidexpanded2/index.vue'
import lanhu_androidexpanded4 from '../views/lanhu_androidexpanded4/index.vue'
import lanhu_frame4 from '../views/lanhu_frame4/index.vue'

Vue.use(VueRouter)

const routes = [
    {
    path: '/',
    redirect: "/lanhu_androidexpanded3"
  },
  {
    path: '/lanhu_androidexpanded3',
    name: 'lanhu_androidexpanded3',
    component: lanhu_androidexpanded3
  },
  {
    path: '/lanhu_groupandroidexpanded1',
    name: 'lanhu_groupandroidexpanded1',
    component: lanhu_groupandroidexpanded1
  },
  {
    path: '/lanhu_frame3',
    name: 'lanhu_frame3',
    component: lanhu_frame3
  },
  {
    path: '/lanhu_androidexpanded2',
    name: 'lanhu_androidexpanded2',
    component: lanhu_androidexpanded2
  },
  {
    path: '/lanhu_androidexpanded4',
    name: 'lanhu_androidexpanded4',
    component: lanhu_androidexpanded4
  },
  {
    path: '/lanhu_frame4',
    name: 'lanhu_frame4',
    component: lanhu_frame4
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
