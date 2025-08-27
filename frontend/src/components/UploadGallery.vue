<template>
  <div class="wgallery">
    <el-upload
      :action="effectiveAction"
      :http-request="doUpload"
      list-type="picture-card"
      :file-list="fileList"
      :on-success="handleSuccess"
      :on-remove="handleRemove"
      :on-preview="handlePreview"
      :multiple="true"
      :auto-upload="true"
      :show-file-list="true"
      :disabled="false"
    >
      <!-- 新增與編輯一致的「選擇圖片」卡（沿用 Element Plus 樣式） -->
      <template #default>
        <div class="el-upload__text">選擇圖片</div>
      </template>
    </el-upload>

    <!-- 使用 Element Plus 的預覽 Viewer -->
    <el-image-viewer
      v-if="viewer.visible"
      :url-list="[viewer.url]"
      @close="viewer.visible = false"
    />
  </div>
</template>

<script setup>
import { ref, watch, computed } from "vue";
import { api } from "../api";
import { ElImageViewer } from "element-plus";

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  uploadUrl: { type: String, required: true },
  scope: { type: String, default: "" }, // 'products' | 'fabrics'
  entityId: { type: Number, default: 0 },
  kind: { type: String, default: "" }, // 'image' | 'work'
});
const emit = defineEmits(["update:modelValue"]);

/* ----- 解析 scope / id / kind ----- */
function parseFromUploadUrl() {
  try {
    const u = new URL(props.uploadUrl, window.location.origin);
    const m = u.pathname.match(/\/api\/upload\/(fabrics|products)\/(\d+)/);
    const scope = props.scope || (m ? m[1] : "");
    const id = props.entityId || (m ? Number(m[2]) : 0);
    const kindQ = u.searchParams.get("kind");
    const kind =
      props.kind || kindQ || (scope === "products" ? "image" : "image");
    return { scope, id, kind };
  } catch {
    return {
      scope: props.scope || "",
      id: props.entityId || 0,
      kind: props.kind || "image",
    };
  }
}
function parseFromModelValue() {
  const urls = props.modelValue || [];
  const first = urls.find((u) => !!u && !String(u).startsWith("blob:"));
  if (!first) return { scope: "", id: 0, kind: props.kind || "image" };
  try {
    const u = new URL(first, window.location.origin);
    const m = u.pathname.match(
      /\/static\/uploads\/(fabrics|products)\/(\d+)\//
    );
    if (m) {
      const scope = props.scope || m[1];
      const id = props.entityId || Number(m[2]);
      const kind = props.kind || "image";
      return { scope, id, kind };
    }
  } catch {}
  return {
    scope: props.scope || "",
    id: props.entityId || 0,
    kind: props.kind || "image",
  };
}
const parsed = computed(() => {
  const a = parseFromUploadUrl();
  if (a.id) return a;
  const b = parseFromModelValue();
  return {
    scope: a.scope || b.scope,
    id: b.id || a.id,
    kind: a.kind || b.kind,
  };
});

/* ----- 真實 action（供 UI 顯示；實際上傳走 doUpload） ----- */
const effectiveAction = computed(() => {
  const { scope, id, kind } = parsed.value;
  if (scope && id) {
    if (scope === "fabrics")
      return `/api/upload/fabrics/${id}?kind=${kind || "image"}`;
    if (scope === "products") return `/api/upload/products/${id}`;
  }
  return props.uploadUrl;
});

/* ----- 端點 + 欄位名 fallback 上傳 ----- */
async function doUpload(options) {
  const { file, onSuccess, onError } = options;
  const { scope, id, kind } = parsed.value;

  if (!id || !scope) {
    onError(new Error("無法推斷 id 或 scope"));
    return;
  }

  const ep =
    scope === "fabrics" ? (kind === "work" ? "works" : "images") : "images";
  const endpoints = [
    `upload/${scope}/${id}${
      scope === "fabrics" ? "?kind=" + (kind || "image") : ""
    }`,
    `${scope}/${id}/${ep}`,
  ];
  const fieldNames = ["files", "file"];

  for (let e = 0; e < endpoints.length; e++) {
    for (let f = 0; f < fieldNames.length; f++) {
      const fd = new FormData();
      fd.append(fieldNames[f], file);
      try {
        const resp = await api.post(endpoints[e], fd);
        onSuccess(resp.data); // 後續 handleSuccess 會抽出 URL
        return;
      } catch (err) {
        const status = err?.response?.status;
        const detail = err?.response?.data?.detail;
        const needFiles =
          Array.isArray(detail) &&
          detail.some((d) => String(d?.loc)?.includes("files"));
        const needFile =
          Array.isArray(detail) &&
          detail.some((d) => String(d?.loc)?.includes("file"));
        const canTryNextField =
          status === 422 &&
          ((fieldNames[f] === "file" && needFiles) ||
            (fieldNames[f] === "files" && needFile));
        const canTryNextEndpoint = status === 404;
        if (canTryNextField || canTryNextEndpoint) continue;
        onError(err);
        return;
      }
    }
  }
  onError(new Error("上傳失敗：端點或欄位名不相容"));
}

/* ----- 縮圖顯示 base（517x → 8000） ----- */
function computeAssetBase() {
  const env = (import.meta.env && import.meta.env.VITE_ASSET_BASE) || "";
  if (env) return env.replace(/\/$/, "");
  const { protocol, hostname, port } = window.location;
  if (/^517\d$/.test(port)) return `${protocol}//${hostname}:8000`;
  return `${protocol}//${hostname}${port ? ":" + port : ""}`;
}
const ASSET_BASE = computeAssetBase();
function absUrl(u) {
  if (!u) return u;
  try {
    return new URL(u, ASSET_BASE).toString();
  } catch {
    return u;
  }
}
function stripHost(s) {
  return (s || "").replace(/^https?:\/\/[^/]+/i, "");
}
function isGoodUrl(u) {
  return !!u && !String(u).startsWith("blob:");
}

/* ----- file-list 與 v-model 同步 ----- */
const fileList = ref([]);
function toFileList(urls) {
  return (urls || []).filter(isGoodUrl).map((u, i) => ({
    uid: `uf_${Date.now()}_${i}`,
    name: u.split("/").pop() || `img_${i + 1}`,
    url: absUrl(u),
    status: "success",
    percentage: 100,
  }));
}
watch(
  () => props.modelValue,
  (v) => {
    fileList.value = toFileList(v);
  },
  { immediate: true }
);

function pushUrl(url) {
  const rel = stripHost(url);
  if (!isGoodUrl(rel)) return;
  const next = [...(props.modelValue || [])];
  if (!next.includes(rel)) {
    next.push(rel);
    emit("update:modelValue", next);
  }
}
function removeFromModel(url) {
  const rel = stripHost(url);
  const next = (props.modelValue || []).filter((u) => stripHost(u) !== rel);
  emit("update:modelValue", next);
}

/* 從後端回應中找第一個可用的 URL（遞迴掃描） */
function firstServerUrl(o) {
  const ok = (s) =>
    typeof s === "string" &&
    !s.startsWith("blob:") &&
    (/^https?:\/\//.test(s) || s.startsWith("/static/"));
  if (ok(o)) return o;
  if (Array.isArray(o)) {
    for (const v of o) {
      const r = firstServerUrl(v);
      if (r) return r;
    }
  } else if (o && typeof o === "object") {
    for (const k of Object.keys(o)) {
      const r = firstServerUrl(o[k]);
      if (r) return r;
    }
  }
  return null;
}

function handleSuccess(resp, file) {
  const url = firstServerUrl(resp);
  if (url) {
    if (file) file.url = absUrl(url); // 立刻把卡片換成最終 URL
    pushUrl(url); // 寫回 v-model（DB 儲存由父層負責）
  }
}

async function handleRemove(file) {
  const url = file?.url || "";
  if (!url) return;
  removeFromModel(url);
  const { scope, id, kind } = parsed.value;
  if (scope && id) {
    const send = stripHost(url) || url;
    try {
      if (scope === "products") {
        await api.delete(`products/${id}/images`, { data: [send] });
      } else if (scope === "fabrics") {
        const ep = kind === "work" ? "works" : "images";
        await api.delete(`fabrics/${id}/${ep}`, { data: [send] });
      }
    } catch (e) {
      console.error("刪除圖片失敗", e);
    }
  }
}

/* 預覽（點縮圖預覽） */
const viewer = ref({ visible: false, url: "" });
function handlePreview(file) {
  viewer.value = { visible: true, url: file?.url || "" };
}
</script>

<style scoped>
/* 不覆蓋 Element Plus 預設，僅細微調整容器寬度以避免不同頁面不一致 */
.wgallery {
  width: 100%;
}
</style>
