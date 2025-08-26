<template>
  <div class="card">
    <p class="small">{{ title }}</p>
    <el-upload
      list-type="picture-card"
      :auto-upload="true"
      :file-list="fileList"
      :http-request="doUpload"
      :on-remove="onRemove"
      multiple
      accept="image/*"
    >
      <template #default>選擇圖片</template>
    </el-upload>
    <p class="tiny" style="color:#777">提示：每張縮圖右上角的「×」即可移除；新增圖片會立即上傳並加入清單。</p>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { fileUpload } from '../api'

const props = defineProps({
  uploadUrl: { type: String, required: true },
  title: { type: String, default: '上傳圖片' },
  modelValue: { type: Array, default: () => [] }, // e.g. ['/uploads/abc.jpg', ...]（相對於 API base）
})
const emit = defineEmits(['update:modelValue'])

const apiBase = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

const fileList = ref([]) // Element Plus 使用的清單（可含 url/raw）

function rebuildFromModel() {
  // 把 v-model 的既有圖片轉成已上傳項目，讓刪除鈕出現
  fileList.value = (props.modelValue || []).map((u, i) => ({
    name: u.split('/').pop() || `image_${i}`,
    url: (u.startsWith('http') ? u : apiBase + u),
    status: 'success',
    uid: `exist_${i}_${Math.random().toString(36).slice(2,7)}`,
  }))
}
watch(() => props.modelValue, rebuildFromModel, { immediate: true, deep: true })

async function doUpload(options) {
  const { file, onSuccess, onError } = options
  try {
    const r = await fileUpload(props.uploadUrl, [file])
    const saved = r.data.saved || []
    if (saved.length) {
      const next = [...props.modelValue, ...saved]
      emit('update:modelValue', next)
      // 追加到檔案清單（顯示為已上傳）
      for (const u of saved) {
        fileList.value.push({
          name: u.split('/').pop() || file.name,
          url: (u.startsWith('http') ? u : apiBase + u),
          status: 'success',
          uid: `new_${Date.now()}_${Math.random().toString(36).slice(2,7)}`,
        })
      }
    }
    onSuccess && onSuccess({}, file)
  } catch (e) {
    onError && onError(e)
  }
}

function onRemove(file, files) {
  if (file && file.url) {
    const relative = file.url.startsWith(apiBase) ? file.url.slice(apiBase.length) : file.url
    const prev = props.modelValue || []
    const next = prev.filter(u => u !== relative && u !== file.url)
    emit('update:modelValue', next)
  }
  // fileList 由 Element Plus 自己維護（這裡不用手動設置）
}
</script>
