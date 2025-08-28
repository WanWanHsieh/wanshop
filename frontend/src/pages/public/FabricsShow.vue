<template>
  <BackButton />
  <h2>布料展示</h2>
  <div class="grid cols-3">
    <div class="card fabric-card" v-for="f in fabrics" :key="f.id">
      <!-- 布料主圖（縮小 + 可放大預覽） -->
      <el-image
        class="fabric-cover"
        :src="coverSrc(f)"
        :preview-src-list="previewList(f)"
        :initial-index="0"
        fit="cover"
        hide-on-click-modal
        :preview-teleported="true"
      />

      <h3>{{ f.name }}</h3>
      <p class="small">{{ f.origin }}</p>
      <p style="margin: 0">
        <b>${{ f.on_clearance ? f.clearance_price : f.price }}</b>
      </p>
      <p class="small">{{ f.description }}</p>

      <!-- 作品展示：Element Plus 跑馬燈 + Motion-blur 切換效果 + 可放大 -->
      <el-carousel
        v-if="f.works?.length"
        class="works-carousel"
        :class="{ blurring: blurringId === f.id }"
        :autoplay="true"
        :interval="2500"
        indicator-position="outside"
        arrow="always"
        height="140px"
        @change="onChange(f.id)"
      >
        <el-carousel-item v-for="(w, i) in f.works" :key="w.id">
          <el-image
            :src="apiBase + w.url"
            class="work-img"
            :preview-src-list="previewList(f)"
            :initial-index="i + 1"
            fit="cover"
            hide-on-click-modal
            :preview-teleported="true"
          />
        </el-carousel-item>
      </el-carousel>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue";
import { api } from "../../api";
import BackButton from "../../components/BackButton.vue";
const fabrics = ref([]);
const apiBase = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

// 圖片來源與預覽清單
const coverSrc = (f) =>
  f.images?.length
    ? apiBase + f.images[0].url
    : "https://via.placeholder.com/800x600?text=Fabric";
const previewList = (f) => [
  coverSrc(f),
  ...(f.works?.map((w) => apiBase + w.url) || []),
];

// Motion blur 的切換效果（切換時短暫加上 blur class）
const blurringId = ref(null);
function onChange(id) {
  blurringId.value = id;
  setTimeout(() => (blurringId.value = null), 260); // 與 CSS 動畫時間對齊
}

async function fetchAll() {
  const res = await api.get("/public/fabrics");
  fabrics.value = res.data;
}
onMounted(fetchAll);
</script>
<style scoped>
/* 讓布料主圖小一點 */
.fabric-cover {
  width: 90%;
  max-height: 200px;
  object-fit: cover;
  border-radius: 8px;
  display: block;
  margin: 0 auto 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}
/* 跑馬燈區域調整 */
.works-carousel {
  width: 70%;
  margin: 10px auto;
}

/* Motion blur：切換時短暫模糊，模擬動態模糊的視覺 */
.works-carousel.blurring .work-img {
  filter: blur(2px);
}
.work-img {
  width: 100%;
  height: 140px;
  object-fit: cover;
  border-radius: 8px;
  transition: filter 0.25s ease;
}
@media (max-width: 768px) {
  .fabric-cover {
    width: 100%;
    max-height: 180px;
  }
  .work-img {
    height: 120px;
  }
}
</style>
