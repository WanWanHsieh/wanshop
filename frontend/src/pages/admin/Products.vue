<template>
  <BackButton/>
  <h2>商品紀錄</h2>
  <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center">
    <el-button type="primary" @click="openForm()">新增商品</el-button>
    <el-input v-model="newCat" placeholder="新增類別名稱" style="max-width:200px"/>
    <el-button @click="addCat">新增類別</el-button>
  </div>

  <el-table :data="products" style="width:100%; margin-top:10px">
    <el-table-column label="#" width="60" type="index"/>
    <el-table-column label="圖片" width="120">
      <template #default="s">
        <img
          v-if="firstImg(s.row)"
          :src="firstImg(s.row)"
          style="width:80px;height:60px;object-fit:cover;border-radius:6px"
        />
        <span v-else class="small">無</span>
      </template>
    </el-table-column>
    <el-table-column label="名稱" prop="name"/>
    <el-table-column label="類別" width="140">
      <template #default="s">{{ catName(s.row.category_id) }}</template>
    </el-table-column>
    <el-table-column label="價格" prop="price" width="100"/>
    <el-table-column label="促銷價" prop="promo_price" width="100"/>
    <el-table-column label="建立時間" width="180">
      <template #default="s">{{ new Date(s.row.created_at).toLocaleString() }}</template>
    </el-table-column>
    <el-table-column label="操作" width="220">
      <template #default="s">
        <el-button size="small" @click="openForm(s.row)">編輯</el-button>
        <el-button size="small" type="danger" @click="delRow(s.row)">刪除</el-button>
      </template>
    </el-table-column>
  </el-table>

  <el-dialog v-model="show" width="60%" :title="form.id ? '編輯商品' : '新增商品'" destroy-on-close append-to-body top="10vh">
    <el-form :model="form" label-width="120">
      <el-form-item label="名稱"><el-input v-model="form.name"/></el-form-item>
      <el-form-item label="類別">
        <el-select v-model="form.category_id" placeholder="選擇類別">
          <el-option v-for="c in categories" :key="c.id" :value="c.id" :label="c.name"/>
        </el-select>
      </el-form-item>
      <el-form-item label="價格"><el-input-number v-model="form.price" :min="0" :step="10"/></el-form-item>
      <el-form-item label="促銷價"><el-input-number v-model="form.promo_price" :min="0" :step="10"/></el-form-item>
      <el-form-item label="尺寸"><el-input v-model="form.size"/></el-form-item>
      <el-form-item label="描述"><el-input type="textarea" v-model="form.description"/></el-form-item>

      <el-divider>商品圖片</el-divider>

      
<template v-if="!form.id">
  <div class="card">
    <p class="small">商品圖片（可多選）</p>
    <el-upload
      list-type="picture-card"
      :auto-upload="false"
      :file-list="pendingList"
      :on-change="onPendingChange"
      :on-remove="onPendingChange"
      multiple
      accept="image/*"
    >
      <template #default>選擇圖片</template>
    </el-upload>
  </div>
</template>


      <template v-else>
        <UploadGallery v-model="form.images_urls" :upload-url="`/api/upload/products/${form.id}`" title="商品圖片"/>
      </template>
    </el-form>

    <template #footer>
      <div style="flex:1; text-align:right">
        <el-button @click="show=false">取消</el-button>
        <el-button type="primary" @click="save">儲存</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { api, fileUpload } from '../../api'
import BackButton from '../../components/BackButton.vue'
import UploadGallery from '../../components/UploadGallery.vue'

const categories = ref([])
const products = ref([])
const show = ref(false)
const form = reactive({})
const newCat = ref('')

const pendingFiles = ref([])

const pendingList = ref([]) // UploadUserFile[] for create mode

function ensureUid(list) {
  list.forEach((f, i) => {
    if (!f.uid) f.uid = `${Date.now()}_${i}_${Math.random().toString(36).slice(2,7)}`
  })
}

function onPendingChange(_file, files) {
  ensureUid(files)
  pendingList.value = files
  pendingFiles.value = files.map(f => f.raw).filter(Boolean)
}

const pendingPreviews = ref([])

const apiBase = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'
const firstImg = (p) => {
  if (p?.images?.length) return apiBase + p.images[0].url
  return ''
}

const catName = (id) => categories.value.find(c => c.id === id)?.name || '-'

function openForm(row) {
  show.value = true
  Object.assign(form, { id: null, name: '', category_id: null, price: 0, promo_price: 0, size: '', description: '', images_urls: [] })

  pendingFiles.value = []
  pendingPreviews.value = []

  if (row) {
    Object.assign(form, JSON.parse(JSON.stringify(row)))
    form.images_urls = row.images?.map(i => i.url) || []
  }
}

async function fetchAll() {
  const [cats, prods] = await Promise.all([
    api.get('/categories/'),
    api.get('/products/')
  ])
  categories.value = cats.data
  products.value = prods.data
}

async function addCat() {
  if (!newCat.value) return
  await api.post('/categories/', { name: newCat.value })
  newCat.value = ''
  fetchAll()
}

function onPickPending(e) {
  const files = Array.from(e.target.files || [])
  if (!files.length) return
  pendingFiles.value.push(...files)
  pendingPreviews.value.push(...files.map(f => URL.createObjectURL(f)))
}

async function save() {
  const payload = {
    name: form.name, category_id: form.category_id, price: form.price,
    promo_price: form.promo_price, size: form.size, description: form.description
  }
  if (!form.id) {
    const res = await api.post('/products/', payload)
    const id = res.data.id
    if (pendingFiles.value.length) {
      const r = await fileUpload(`/api/upload/products/${id}`, pendingFiles.value)
      const urls = r.data.saved || []
      if (urls.length) await api.post(`/products/${id}/images`, urls)
    }
  } else {
    await api.put(`/products/${form.id}`, payload)
    if (form.images_urls?.length) await api.post(`/products/${form.id}/images`, form.images_urls)
  }
  show.value = false
  fetchAll()
}

async function delRow(row) {
  await api.delete(`/products/${row.id}`)
  fetchAll()
}

onMounted(fetchAll)
</script>

<style scoped>
.el-upload-list__item-actions{opacity:1 !important;}
</style>
