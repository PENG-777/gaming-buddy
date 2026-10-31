<template>
  <div class="upload-wrapper">
    <!-- 图片卡片列表 -->
    <div class="flex flex-wrap gap-2">
      <div v-for="(file, idx) in fileList" :key="file.uid || idx" class="relative w-[100px] h-[100px] rounded-lg border border-gray-200 overflow-hidden group">
        <img :src="file.url" class="w-full h-full object-cover" alt=""/>
        <!-- 操作按钮 -->
        <div class="absolute inset-0 bg-black/40 flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <button type="button" @click="handlePreview(file)" class="w-7 h-7 flex items-center justify-center rounded bg-white/80 hover:bg-white transition-colors">
            <svg class="w-3.5 h-3.5 text-gray-700" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="3"/><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/></svg>
          </button>
          <button type="button" @click="handleRemove(idx)" class="w-7 h-7 flex items-center justify-center rounded bg-white/80 hover:bg-white transition-colors">
            <svg class="w-3.5 h-3.5 text-red-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
          </button>
        </div>
      </div>

      <!-- 添加上传按钮 -->
      <div v-if="fileList.length < limit" @click="triggerUpload" class="w-[100px] h-[100px] rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center cursor-pointer hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] transition-colors text-gray-400">
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
      </div>
    </div>

    <input ref="uploadInput" type="file" :accept="acceptStr" multiple class="hidden" @change="handleFileChange"/>

    <!-- 提示信息 -->
    <div v-if="showTip" class="mt-2 text-xs text-gray-400">
      请上传<span v-if="fileSize">大小不超过 <b class="text-red-500">{{ fileSize }}MB</b></span>
      <span v-if="fileType"> 格式为 <b class="text-red-500">{{ fileType.join("/") }}</b></span> 的文件
    </div>

    <!-- 预览弹窗 -->
    <Teleport to="body">
      <Transition name="preview-fade">
        <div v-if="previewOpen" class="fixed inset-0 z-[9999] bg-black/80 flex items-center justify-center" @click="previewOpen = false">
          <img :src="previewUrl" class="max-w-[90vw] max-h-[90vh] object-contain rounded-lg shadow-2xl" @click.stop alt="Preview"/>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { getToken } from "@/utils/auth";
import { ElMessage } from "@/utils/toast.js";
import axios from "axios";

const props = defineProps({
  modelValue: [String, Array],
  limit: { type: Number, default: 1 },
  fileSize: { type: Number, default: 5 },
  fileType: { type: Array, default: () => ["png", "jpg", "jpeg"] },
  isShowTip: { type: Boolean, default: true },
});

const emit = defineEmits(["update:modelValue"]);

const baseUrl = import.meta.env.VITE_APP_BASE_API;
const uploadUrl = `${baseUrl}/file/upload`;
const headers = { Authorization: "Bearer " + getToken() };

const fileList = ref([]);
const previewOpen = ref(false);
const previewUrl = ref("");
const uploadInput = ref(null);

const showTip = computed(() => props.isShowTip && (props.fileType || props.fileSize));
const acceptStr = computed(() => props.fileType.map(t => '.' + t).join(','))

const triggerUpload = () => { uploadInput.value?.click() }

watch(() => props.modelValue, (val) => {
  if (!val) { fileList.value = []; return }
  const list = Array.isArray(val) ? val : val.split(",");
  fileList.value = list.map(url => {
    let fullUrl = url;
    if (url && !url.startsWith("http") && !url.startsWith("blob:")) fullUrl = baseUrl + url;
    return { name: url, url: fullUrl, uid: Date.now() + Math.random() };
  });
}, { immediate: true, deep: true });

const emitChange = () => {
  const urls = fileList.value.map(file => {
    let url = file.responseUrl || file.url;
    return url.replace(baseUrl, "");
  });
  emit("update:modelValue", urls.join(","));
};

const handleFileChange = async (e) => {
  const files = Array.from(e.target.files)
  for (const file of files) {
    if (fileList.value.length >= props.limit) { ElMessage.warning(`最多只能上传 ${props.limit} 张图片`); break }

    const isTypeOk = props.fileType.some(type => file.type.includes(type) || file.name.endsWith(type));
    if (!isTypeOk) { ElMessage.error(`格式必须为 ${props.fileType.join("/")}`); continue }

    const isSizeOk = file.size / 1024 / 1024 < props.fileSize;
    if (!isSizeOk) { ElMessage.error(`大小不能超过 ${props.fileSize}MB`); continue }

    const tempUrl = URL.createObjectURL(file)
    const tempFile = { name: file.name, url: tempUrl, uid: Date.now() + Math.random(), status: 'uploading' }
    fileList.value.push(tempFile)

    const formData = new FormData()
    formData.append("file", file)

    try {
      const res = await axios.post(uploadUrl, formData, { headers: { ...headers, 'Content-Type': 'multipart/form-data' } })
      if (res.data.code === 200) {
        const idx = fileList.value.findIndex(f => f.uid === tempFile.uid)
        if (idx !== -1) {
          fileList.value[idx].url = baseUrl + res.data.data.fileName
          fileList.value[idx].responseUrl = baseUrl + res.data.data.fileName
          fileList.value[idx].status = 'success'
          URL.revokeObjectURL(tempUrl)
        }
        emitChange()
      } else {
        ElMessage.error(res.data.msg || "上传失败")
        fileList.value = fileList.value.filter(f => f.uid !== tempFile.uid)
      }
    } catch {
      ElMessage.error("图片上传接口异常")
      fileList.value = fileList.value.filter(f => f.uid !== tempFile.uid)
    }
  }
  e.target.value = ''
}

const handlePreview = (file) => { previewUrl.value = file.url; previewOpen.value = true }
const handleRemove = (idx) => { fileList.value.splice(idx, 1); emitChange() }
</script>

<style scoped>
.preview-fade-enter-active, .preview-fade-leave-active { transition: opacity 0.25s ease; }
.preview-fade-enter-from, .preview-fade-leave-to { opacity: 0; }
</style>