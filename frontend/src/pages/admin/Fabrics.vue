<template>
  <BackButton />
  <h2>布料紀錄</h2>
  <el-button type="primary" @click="openForm()">新增布料</el-button>

  <el-table :data="fabrics" style="width: 100%; margin-top: 10px">
    <el-table-column label="#" width="60" type="index" />
    <el-table-column label="圖片" width="120">
      <template #default="s">
        <img
          v-if="firstImg(s.row)"
          :src="firstImg(s.row)"
          style="
            width: 80px;
            height: 60px;
            object-fit: cover;
            border-radius: 6px;
          "
        />
        <span v-else class="small">無</span>
      </template>
    </el-table-column>
    <el-table-column label="名稱" prop="name" />
    <el-table-column label="產地" prop="origin" width="100" />
    <el-table-column label="價格" prop="price" width="100" />
    <el-table-column label="出清" width="80">
      <template #default="s">{{ s.row.on_clearance ? "✔" : "" }}</template>
    </el-table-column>
    <el-table-column label="建立時間" width="180">
      <template #default="s">{{
        new Date(s.row.created_at).toLocaleString()
      }}</template>
    </el-table-column>
    <el-table-column label="操作" width="240">
      <template #default="s">
        <el-button size="small" @click="openForm(s.row)">編輯</el-button>
        <el-button size="small" type="danger" @click="delRow(s.row)"
          >刪除</el-button
        >
      </template>
    </el-table-column>
  </el-table>

  <el-dialog
    v-model="show"
    width="60%"
    :title="form.id ? '編輯布料' : '新增布料'"
    destroy-on-close
    append-to-body
    top="10vh"
  >
    <el-form :model="form" label-width="120">
      <el-form-item label="名稱"><el-input v-model="form.name" /></el-form-item>
      <el-form-item label="產地">
        <el-select v-model="form.origin" placeholder="選擇產地">
          <el-option label="美國" value="美國" />
          <el-option label="日本" value="日本" />
          <el-option label="韓國" value="韓國" />
          <el-option label="台灣" value="台灣" />
        </el-select>
      </el-form-item>
      <el-form-item label="價格"
        ><el-input-number v-model="form.price" :min="0" :step="10"
      /></el-form-item>
      <el-form-item label="尺寸"
        ><el-input v-model="form.size" placeholder="例如：110x90cm"
      /></el-form-item>
      <el-form-item label="描述"
        ><el-input type="textarea" v-model="form.description"
      /></el-form-item>
      <el-form-item label="是否出清"
        ><el-switch v-model="form.on_clearance"
      /></el-form-item>
      <el-form-item label="出清價格">
        <el-input-number
          v-model="form.clearance_price"
          :min="0"
          :step="10"
          :disabled="!form.on_clearance"
        />
      </el-form-item>

      <el-divider>圖片</el-divider>

      <template v-if="!form.id">
        <div class="card" style="margin-bottom: 8px">
          <p class="small">布料圖片（可多選）</p>
          <el-upload
            list-type="picture-card"
            :auto-upload="false"
            :file-list="pendingImagesList"
            :on-change="onImageChange"
            :on-remove="onImageChange"
            multiple
            accept="image/*"
          >
            <template #default>選擇圖片</template>
          </el-upload>
        </div>

        <div class="card">
          <p class="small">作品圖片（可多選）</p>
          <el-upload
            list-type="picture-card"
            :auto-upload="false"
            :file-list="pendingWorksList"
            :on-change="onWorkChange"
            :on-remove="onWorkChange"
            multiple
            accept="image/*"
          >
            <template #default>選擇圖片</template>
          </el-upload>
        </div>
      </template>

      <template v-else>
        <UploadGallery
          v-model="form.images_urls"
          :upload-url="`/api/upload/fabrics/${form.id}?kind=image`"
          title="布料圖片"
        />
        <UploadGallery
          v-model="form.works_urls"
          :upload-url="`/api/upload/fabrics/${form.id}?kind=work`"
          title="作品圖片"
        />
      </template>
    </el-form>

    <template #footer>
      <div style="flex: 1; text-align: right">
        <el-button @click="show = false">取消</el-button>
        <el-button type="primary" @click="save">儲存</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { api, fileUpload } from "../../api";
import BackButton from "../../components/BackButton.vue";
import UploadGallery from "../../components/UploadGallery.vue";

const fabrics = ref([]);
const show = ref(false);
const form = reactive({});

const pendingImagesFiles = ref([]);

const pendingImagesList = ref([]); // UploadUserFile[]
const pendingWorksList = ref([]); // UploadUserFile[]

function ensureUid(list) {
  list.forEach((f, i) => {
    if (!f.uid)
      f.uid = `${Date.now()}_${i}_${Math.random().toString(36).slice(2, 7)}`;
  });
}

function onImageChange(_file, files) {
  ensureUid(files);
  pendingImagesList.value = files;
  pendingImagesFiles.value = files.map((f) => f.raw).filter(Boolean);
}

function onWorkChange(_file, files) {
  ensureUid(files);
  pendingWorksList.value = files;
  pendingWorksFiles.value = files.map((f) => f.raw).filter(Boolean);
}

const pendingWorksFiles = ref([]);
const pendingImagesPreviews = ref([]);
const pendingWorksPreviews = ref([]);

const apiBase = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";
const firstImg = (f) => {
  if (f?.images?.length) return apiBase + f.images[0].url;
  return "";
};

function openForm(row) {
  show.value = true;
  Object.assign(form, {
    id: null,
    name: "",
    origin: "台灣",
    price: 0,
    size: "",
    description: "",
    on_clearance: false,
    clearance_price: 0,
    images_urls: [],
    works_urls: [],
  });

  pendingImagesFiles.value = [];
  pendingWorksFiles.value = [];
  pendingImagesPreviews.value = [];
  pendingWorksPreviews.value = [];

  if (row) {
    Object.assign(form, JSON.parse(JSON.stringify(row)));
    form.images_urls = row.images?.map((i) => i.url) || [];
    form.works_urls = row.works?.map((i) => i.url) || [];
  }
}

async function fetchAll() {
  const res = await api.get("/fabrics/");
  fabrics.value = res.data;
}

function onPickPending(e, kind) {
  const files = Array.from(e.target.files || []);
  if (!files.length) return;
  if (kind === "image") {
    pendingImagesFiles.value.push(...files);
    pendingImagesPreviews.value.push(
      ...files.map((f) => URL.createObjectURL(f))
    );
  } else {
    pendingWorksFiles.value.push(...files);
    pendingWorksPreviews.value.push(
      ...files.map((f) => URL.createObjectURL(f))
    );
  }
}

async function save() {
  const payload = {
    name: form.name,
    origin: form.origin,
    price: form.price,
    size: form.size,
    description: form.description,
    images_urls: form.images_urls,
    works_urls: form.works_urls,
    on_clearance: form.on_clearance,
    clearance_price: form.clearance_price,
  };

  if (!form.id) {
    const res = await api.post("/fabrics/", payload);
    const id = res.data.id;

    if (pendingImagesFiles.value.length) {
      const r = await fileUpload(
        `/api/upload/fabrics/${id}?kind=image`,
        pendingImagesFiles.value
      );
      const urls = r.data.saved || [];
      if (urls.length) await api.post(`/fabrics/${id}/images`, urls);
    }
    if (pendingWorksFiles.value.length) {
      const r = await fileUpload(
        `/api/upload/fabrics/${id}?kind=work`,
        pendingWorksFiles.value
      );
      const urls = r.data.saved || [];
      if (urls.length) await api.post(`/fabrics/${id}/works`, urls);
    }
  } else {
    await api.put(`/fabrics/${form.id}`, payload);
    if (form.images_urls?.length)
      await api.post(`/fabrics/${form.id}/images`, form.images_urls);
    if (form.works_urls?.length)
      await api.post(`/fabrics/${form.id}/works`, form.works_urls);
  }

  show.value = false;
  fetchAll();
}

async function delRow(row) {
  await api.delete(`/fabrics/${row.id}`);
  fetchAll();
}

onMounted(fetchAll);
</script>

<style scoped>
.el-upload-list__item-actions {
  opacity: 1 !important;
}
</style>
