<template>
  <div class="card">
    <p class="small">{{ title }}</p>
    <input type="file" multiple @change="onFile"/>
    <div class="grid cols-3" style="margin-top:8px">
      <img v-for="(u,i) in modelValue" :key="i" :src="apiBase + u" class="img" />
    </div>
  </div>
</template>

<script setup>
import { fileUpload } from '../api'
const props = defineProps({
  uploadUrl: { type: String, required: true },
  title: { type: String, default: '上傳圖片' },
  modelValue: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue'])
const apiBase = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

async function onFile(e) {
  const files = e.target.files
  if (!files || files.length === 0) return
  const res = await fileUpload(props.uploadUrl, files)
  const saved = res.data.saved || []
  emit('update:modelValue', [...props.modelValue, ...saved])
}
</script>
