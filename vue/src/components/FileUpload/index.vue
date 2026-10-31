<template>
  <div class="w-full">
    <!-- 拖拽上传区域 -->
    <div
      class="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-[var(--color-primary)] hover:bg-[var(--color-primary-bg)]/30 transition-colors"
      @click="triggerUpload"
      @dragover.prevent
      @drop.prevent="handleDrop"
    >
      <div class="flex flex-col items-center gap-2">
        <svg class="w-10 h-10 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
        <p class="text-sm text-gray-500">点击或拖拽文件到此处上传</p>
      </div>
      <div class="mt-2 text-xs text-gray-400">
        单个文件最大 {{ fileSizeLimit }}MB 支持格式：{{ accept }}
      </div>
    </div>

    <input ref="uploadInput" type="file" :accept="accept" multiple class="hidden" @change="handleFileChange"/>

    <!-- 文件列表 -->
    <div class="mt-3 space-y-2">
      <div v-for="file in fileList" :key="file.uid" class="flex items-center justify-between px-3 py-2 rounded-lg border border-gray-200 bg-white">
        <div class="flex items-center gap-2 flex-1 min-w-0">
          <svg class="w-5 h-5 text-gray-400 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><polyline points="13 2 13 9 20 9"/></svg>
          <span class="text-sm text-gray-700 truncate">{{ file.name }}</span>
        </div>
        <div class="flex items-center gap-2 flex-shrink-0">
          <!-- 进度条 -->
          <div v-if="file.status === 'uploading'" class="w-20 h-1.5 bg-gray-200 rounded-full overflow-hidden">
            <div class="h-full bg-[var(--color-primary)] rounded-full transition-all duration-300" :style="{ width: (file.percentage || 0) + '%' }"/>
          </div>
          <span v-if="file.status === 'success'" class="text-xs text-green-500">成功</span>
          <button @click="handleRemove(file)" class="text-gray-400 hover:text-red-500 transition-colors">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, computed, watch} from "vue";
import {getToken} from "@/utils/auth";
import {ElMessage} from "@/utils/toast.js";
import axios from "axios";

const props = defineProps({
  modelValue: { type: [String, Array], default: () => [] },
  limit: { type: Number, default: 2 },
  fileSizeLimit: { type: Number, default: 100 },
  accept: { type: String, default: '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.zip,.rar' },
  customAction: { type: String, default: null }
});

const emit = defineEmits(["update:modelValue", "success", "error", "remove", "exceed"]);

const baseUrl = import.meta.env.VITE_APP_BASE_API;
const uploadUrl = ref(props.customAction || `${baseUrl}/file/upload`);
const headers = { Authorization: "Bearer " + getToken() };

const rawFileList = ref([]);
const uploadInput = ref(null);

const fileList = computed({
  get: () => rawFileList.value.map(file => ({ ...file, status: file.status || 'success' })),
  set: (value) => { rawFileList.value = value }
});

watch(() => props.modelValue, (val) => {
  if (!val) { rawFileList.value = []; return }
  const list = Array.isArray(val) ? val : val.split(",");
  rawFileList.value = list.map((item, index) => {
    let fullUrl = item;
    if (item && !item.startsWith("http") && !item.startsWith("blob:")) fullUrl = baseUrl + item;
    return { name: item.split('/').pop() || `file-${index}`, url: fullUrl, uid: Date.now() + index, status: 'success' };
  });
}, { immediate: true, deep: true });

const triggerUpload = () => { uploadInput.value?.click() }

const emitChange = () => {
  const urls = fileList.value
    .filter(file => file.url || file.responseUrl)
    .map(file => {
      let url = file.responseUrl || file.url;
      if (url && url.startsWith(baseUrl)) return url.replace(baseUrl, "");
      return url;
    })
    .filter(Boolean);
  emit("update:modelValue", urls.join(","));
};

const validateFile = (file) => {
  const fileName = file.name.toLowerCase();
  const acceptedTypes = props.accept.toLowerCase().split(',');
  const isTypeValid = acceptedTypes.some(type => fileName.endsWith(type.toLowerCase()));
  if (!isTypeValid) { ElMessage.error(`不支持的文件格式，请上传 ${props.accept} 格式的文件`); return false }

  const isSizeValid = file.size / 1024 / 1024 < props.fileSizeLimit;
  if (!isSizeValid) { ElMessage.error(`文件大小不能超过 ${props.fileSizeLimit}MB`); return false }

  if (fileList.value.length >= props.limit) {
    ElMessage.warning(`最多只能上传 ${props.limit} 个文件`);
    emit("exceed");
    return false
  }
  return true
}

const handleFileChange = async (e) => {
  for (const file of Array.from(e.target.files)) {
    if (!validateFile(file)) continue
    const temp = { name: file.name, url: '', uid: Date.now() + Math.random(), status: 'uploading', percentage: 0 }
    rawFileList.value.push(temp)

    const formData = new FormData()
    formData.append("file", file)

    try {
      const res = await axios.post(uploadUrl.value, formData, {
        headers: { ...headers, 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          const pct = Math.round((e.loaded / e.total) * 100)
          const idx = rawFileList.value.findIndex(f => f.uid === temp.uid)
          if (idx !== -1) rawFileList.value[idx].percentage = pct
        }
      })
      if (res.data.code === 200) {
        const idx = rawFileList.value.findIndex(f => f.uid === temp.uid)
        if (idx !== -1) {
          rawFileList.value[idx].status = 'success'
          rawFileList.value[idx].responseUrl = baseUrl + res.data.fileName
          rawFileList.value[idx].url = baseUrl + res.data.fileName
        }
        ElMessage.success('上传成功')
        emitChange()
        emit("success", res, file)
      } else {
        ElMessage.error(res.data.msg || "上传失败")
        rawFileList.value = rawFileList.value.filter(f => f.uid !== temp.uid)
        emit("error", res, file)
      }
    } catch (err) {
      ElMessage.error("文件上传失败，请重试")
      rawFileList.value = rawFileList.value.filter(f => f.uid !== temp.uid)
      emit("error", err, file)
    }
  }
  e.target.value = ''
}

const handleDrop = (e) => {
  const files = Array.from(e.dataTransfer.files)
  for (const file of files) {
    if (!validateFile(file)) continue
    // reuse file change logic via creating a temp FileList
    const dt = new DataTransfer()
    dt.items.add(file)
    uploadInput.value.files = dt.files
    handleFileChange({ target: { files: dt.files, value: '' } })
  }
}

const handleRemove = (file) => {
  rawFileList.value = rawFileList.value.filter(f => f.uid !== file.uid)
  emitChange()
  emit("remove", file)
}
</script>
