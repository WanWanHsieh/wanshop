<template>
  <BackButton/>
  <h2>商品展示</h2>
  <div class="grid cols-3">
    <div class="card" v-for="c in categories" :key="c.id">
      <h3>{{ c.name }}</h3>
      <el-button type="primary" @click="selectCat(c)">查看</el-button>
    </div>
  </div>

  <div v-if="current" style="margin-top:10px">
    <h3>類別：{{ current.name }}</h3>
    <div class="grid cols-3">
      <div class="card" v-for="p in products" :key="p.id">
        <img class="img" :src="firstImg(p)" alt="img"/>
        <h4>{{ p.name }}</h4>
        <p>{{ p.description }}</p>
        <p><b>${{ p.promo_price>0?p.promo_price:p.price }}</b></p>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../api'
import BackButton from '../../components/BackButton.vue'
const categories = ref([])
const current = ref(null)
const products = ref([])
const apiBase = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'
const firstImg = p => (p.images?.length? (apiBase + p.images[0].url) : 'https://via.placeholder.com/800x600?text=Product')
async function fetchCats() {
  const res = await api.get('/public/categories')
  categories.value = res.data
}
async function selectCat(c) {
  current.value = c
  const res = await api.get(`/public/products/by_category/${c.id}`)
  products.value = res.data
}
onMounted(fetchCats)
</script>
