<template>
  <BackButton/>
  <h2>布料展示</h2>
  <div class="grid cols-3">
    <div class="card" v-for="f in fabrics" :key="f.id">
      <img class="img" :src="firstImg(f)" alt="img"/>
      <h3>#{{ f.id.toString().padStart(4,'0') }} {{ f.name }}</h3>
      <div class="grid cols-3">
        <img v-for="w in f.works" :key="w.id" :src="apiBase + w.url" class="img"/>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../api'
import BackButton from '../../components/BackButton.vue'
const fabrics = ref([])
const apiBase = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'
const firstImg = f => (f.images?.length? (apiBase + f.images[0].url) : 'https://via.placeholder.com/800x600?text=Fabric')
async function fetchAll() {
  const res = await api.get('/public/fabrics')
  fabrics.value = res.data
}
onMounted(fetchAll)
</script>
