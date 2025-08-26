import { createRouter, createWebHistory } from 'vue-router'

import AdminFabrics from '../pages/admin/Fabrics.vue'
import AdminProducts from '../pages/admin/Products.vue'
import AdminOrders from '../pages/admin/Orders.vue'
import Clearance from '../pages/public/Clearance.vue'
import FabricsShow from '../pages/public/FabricsShow.vue'
import ProductsShow from '../pages/public/ProductsShow.vue'

const routes = [
  { path: '/', redirect: '/admin/fabrics' },
  { path: '/admin/fabrics', component: AdminFabrics },
  { path: '/admin/products', component: AdminProducts },
  { path: '/admin/orders', component: AdminOrders },
  { path: '/fabrics/clearance', component: Clearance },
  { path: '/fabrics/show', component: FabricsShow },
  { path: '/products/show', component: ProductsShow },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() { return { top: 0 } },
})

export default router
