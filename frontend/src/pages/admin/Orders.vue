<template>
  <BackButton/>
  <h2>訂購紀錄</h2>
  <el-button type="primary" @click="openForm()">新增訂單</el-button>
  <el-table :data="orders" style="width:100%; margin-top:10px">
    <el-table-column label="#" width="60" type="index"/>
    <el-table-column label="日期" width="180">
      <template #default="s">{{ new Date(s.row.created_at).toLocaleString() }}</template>
    </el-table-column>
    <el-table-column label="顧客" prop="customer_name"/>
    <el-table-column label="總金額" width="140">
      <template #default="s">{{ total(s.row).toFixed(0) }}</template>
    </el-table-column>
    <el-table-column label="訂單狀態" width="140" prop="order_status"/>
    <el-table-column label="匯款狀態" width="140" prop="payment_status"/>
    <el-table-column label="操作" width="240">
      <template #default="s">
        <el-button size="small" @click="openForm(s.row)">編輯</el-button>
        <el-button size="small" type="danger" @click="delRow(s.row)">刪除</el-button>
      </template>
    </el-table-column>
  </el-table>

  <el-drawer v-model="show" size="80%" :title="form.id ? '編輯訂單' : '新增訂單'">
    <el-form :model="form" label-width="120">
      <el-form-item label="顧客名稱"><el-input v-model="form.customer_name"/></el-form-item>
      <el-form-item label="訂單描述"><el-input v-model="form.description"/></el-form-item>
      <el-form-item label="訂單狀態">
        <el-select v-model="form.order_status">
          <el-option label="尚未處理" value="尚未處理"/>
          <el-option label="已完成" value="已完成"/>
          <el-option label="已寄出" value="已寄出"/>
        </el-select>
      </el-form-item>
      <el-form-item label="匯款狀態">
        <el-select v-model="form.payment_status">
          <el-option label="已匯款" value="已匯款"/>
          <el-option label="貨到付款" value="貨到付款"/>
        </el-select>
      </el-form-item>

      <el-divider>訂單明細</el-divider>
      <div class="card" style="margin-bottom:8px">
        <el-space wrap>
          <el-select v-model="newItem.product_id" placeholder="選擇商品" style="min-width:200px">
            <el-option
              v-for="p in products"
              :key="p.id"
              :label="`${p.name} $${p.promo_price>0?p.promo_price:p.price}`"
              :value="p.id"
            />
          </el-select>
          <el-select v-model="newItem.fabric_id" placeholder="選擇布料(可選)" style="min-width:200px" clearable>
            <el-option v-for="f in fabrics" :key="f.id" :value="f.id" :label="f.name"/>
          </el-select>
          <el-select v-model="newItem.state" placeholder="狀態" style="min-width:140px">
            <el-option label="空白" value="空白"/>
            <el-option label="製作中" value="製作中"/>
            <el-option label="預購中" value="預購中"/>
            <el-option label="已完成" value="已完成"/>
          </el-select>
          <el-input-number v-model="newItem.adjustment" :step="10" :min="-9999" :max="9999" placeholder="調整金額"/>
          <el-input v-model="newItem.description" placeholder="描述" style="min-width:240px"/>
          <el-button @click="addItem">加入</el-button>
        </el-space>
      </div>

      <el-table :data="form.items" size="small">
        <el-table-column label="#" type="index" width="60"/>
        <el-table-column label="商品">
          <template #default="s">{{ productName(s.row.product_id) }}</template>
        </el-table-column>
        <el-table-column label="布料">
          <template #default="s">{{ fabricName(s.row.fabric_id) }}</template>
        </el-table-column>
        <el-table-column label="狀態" prop="state" width="120"/>
        <el-table-column label="原價" width="120">
          <template #default="s">{{ priceOf(s.row.product_id).toFixed(0) }}</template>
        </el-table-column>
        <el-table-column label="調整" prop="adjustment" width="120"/>
        <el-table-column label="小計" width="120">
          <template #default="s">{{ (priceOf(s.row.product_id) + (s.row.adjustment||0)).toFixed(0) }}</template>
        </el-table-column>
      </el-table>
      <div style="text-align:right; margin-top:10px">
        <strong>總金額：{{ form.items.reduce((s,i)=>s+priceOf(i.product_id)+(i.adjustment||0),0).toFixed(0) }}</strong>
      </div>
    </el-form>
    <template #footer>
      <div style="flex:1; text-align:right">
        <el-button @click="show=false">取消</el-button>
        <el-button type="primary" @click="save">儲存</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { api } from '../../api'
import BackButton from '../../components/BackButton.vue'

const orders = ref([])
const products = ref([])
const fabrics = ref([])
const show = ref(false)
const form = reactive({})
const newItem = reactive({ product_id: null, fabric_id: null, state: '空白', adjustment: 0, description: '' })

const productName = id => products.value.find(p=>p.id===id)?.name || '-'
const fabricName = id => fabrics.value.find(f=>f.id===id)?.name || '-'
const priceOf = id => {
  const p = products.value.find(p=>p.id===id)
  if (!p) return 0
  return p.promo_price>0?p.promo_price:p.price
}

function total(order) {
  return order.items.reduce((s,it)=> s + it.final_price, 0)
}

function openForm(row) {
  show.value = true
  Object.assign(form, { id: null, customer_name: '', description: '', order_status: '尚未處理', payment_status: '貨到付款', items: [] })
  if (row) Object.assign(form, JSON.parse(JSON.stringify(row)))
}

async function fetchAll() {
  const [o, p, f] = await Promise.all([
    api.get('/orders/'),
    api.get('/products/'),
    api.get('/fabrics/'),
  ])
  orders.value = o.data
  products.value = p.data
  fabrics.value = f.data
}

function addItem() {
  if (!newItem.product_id) return
  form.items.push(JSON.parse(JSON.stringify(newItem)))
  Object.assign(newItem, { product_id: null, fabric_id: null, state: '空白', adjustment: 0, description: '' })
}

async function save() {
  const payload = {
    customer_name: form.customer_name,
    description: form.description,
    order_status: form.order_status,
    payment_status: form.payment_status,
    items: form.items.map(i => ({ product_id: i.product_id, fabric_id: i.fabric_id, state: i.state, adjustment: i.adjustment, description: i.description }))
  }
  if (!form.id) {
    await api.post('/orders/', payload)
  } else {
    await api.put(`/orders/${form.id}`, {
      customer_name: form.customer_name,
      description: form.description,
      order_status: form.order_status,
      payment_status: form.payment_status,
    })
  }
  show.value = false
  fetchAll()
}

async function delRow(row) {
  await api.delete(`/orders/${row.id}`)
  fetchAll()
}

onMounted(fetchAll)
</script>
