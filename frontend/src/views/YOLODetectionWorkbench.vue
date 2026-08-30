<template>
  <div class="page yolo-page">
    <PageHeader
      title="无人机探测工作台"
      subtitle="支持图片与视频输入，调用本地 YOLO 模型完成无人机目标检测，并输出检测框、置信度、统计指标和智能研判结论。"
      eyebrow="YOLO UAV Detection"
    >
      <template #extra>
        <el-tag :type="status.model_exists ? 'success' : 'danger'">
          模型：{{ status.model_exists ? "已就绪" : "缺失" }}
        </el-tag>
        <el-tag :type="status.ultralytics_ready ? 'success' : 'warning'">
          Ultralytics：{{ status.ultralytics_ready ? "可用" : "异常" }}
        </el-tag>
        <el-tag effect="plain">设备：{{ status.device || "cpu" }}</el-tag>
      </template>
    </PageHeader>

    <div class="yolo-top panel">
      <div class="control-group">
        <span class="control-label">输入类型</span>
        <el-segmented v-model="inputType" :options="inputOptions" @change="resetResult" />
      </div>
      <div class="control-group">
        <span class="control-label">置信度阈值</span>
        <el-slider v-model="confidence" :min="0.05" :max="0.9" :step="0.05" show-input />
      </div>
      <div class="control-group">
        <span class="control-label">IoU 阈值</span>
        <el-slider v-model="iou" :min="0.1" :max="0.9" :step="0.05" show-input />
      </div>
      <div class="control-group compact">
        <el-checkbox v-model="enableLlm">启用 Ollama 智能研判</el-checkbox>
        <el-button type="primary" :loading="loading" @click="runDetection">
          {{ inputType === "video" ? (liveRunning ? "停止实时检测" : "开始实时检测") : "开始检测" }}
        </el-button>
      </div>
    </div>

    <div class="yolo-workbench">
      <div class="panel input-panel">
        <div class="section-title">
          <h3>输入区与本地素材选择</h3>
          <span>{{ inputType === "image" ? "图片检测" : "视频实时检测" }}</span>
        </div>

        <div class="sample-list" v-if="inputType === 'image'">
          <div
            v-for="item in samples.images"
            :key="item.name"
            :class="['sample-card', { active: selectedImage?.name === item.name && !uploadFile }]"
            @click="selectSampleImage(item)"
          >
            <img :src="backendUrl + item.url" />
            <strong>{{ item.name }}</strong>
          </div>
        </div>

        <div class="sample-list video-list" v-else>
          <div
            v-for="item in samples.videos"
            :key="item.name"
            :class="['sample-card', { active: selectedVideo?.name === item.name && !uploadFile }]"
            @click="selectSampleVideo(item)"
          >
            <div class="video-thumb">LIVE</div>
            <strong>{{ item.name }}</strong>
          </div>
        </div>

        <el-divider />
        <el-upload
          drag
          action="#"
          :auto-upload="false"
          :show-file-list="false"
          :on-change="handleUpload"
          :accept="inputType === 'image' ? 'image/*' : 'video/*'"
        >
          <el-icon class="upload-icon"><UploadFilled /></el-icon>
          <div class="el-upload__text">
            拖拽{{ inputType === "image" ? "图片" : "视频" }}到此处，或点击选择本地文件
          </div>
        </el-upload>

        <div class="input-meta">
          <div class="detail-item">
            <div class="detail-label">当前输入</div>
            <div class="detail-value">{{ activeInputName }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">模型路径</div>
            <div class="detail-value">{{ status.model_path || "-" }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">视频检测方式</div>
            <div class="detail-value">
              {{ uploadFile && inputType === "video" ? "本地播放逐帧送检" : "后端实时标注流" }}
            </div>
          </div>
        </div>
      </div>

      <div class="panel result-panel">
        <div class="section-title">
          <h3>检测结果显示区</h3>
          <span>{{ inputType === "video" ? "视频画面与实时标注" : "检测框与置信度" }}</span>
        </div>

        <div v-if="inputType === 'image'" class="image-stage">
          <img v-if="result.annotated_image" :src="result.annotated_image" />
          <img v-else-if="previewUrl" :src="previewUrl" />
          <div v-else class="empty-hint">请选择本地图片或上传图片后开始检测</div>
        </div>

        <div v-else class="video-stage">
          <div class="live-video-box">
            <img
              v-if="liveStreamUrl && !uploadFile"
              class="live-stream"
              :src="liveStreamUrl"
              alt="实时检测视频流"
            />
            <template v-else>
              <video
                ref="videoRef"
                class="source-video"
                :src="videoPreviewUrl"
                crossorigin="anonymous"
                controls
                muted
                @play="startFrameLoop"
                @pause="stopFrameLoop(false)"
                @ended="finishVideoDetection"
              />
              <canvas ref="overlayCanvasRef" class="overlay-canvas"></canvas>
              <canvas ref="captureCanvasRef" class="capture-canvas"></canvas>
            </template>
            <div v-if="!videoPreviewUrl && !liveStreamUrl" class="empty-hint">
              请选择本地视频或上传视频后开始实时检测
            </div>
          </div>

          <div class="live-strip">
            <div class="live-stat">
              <span>实时状态</span>
              <strong>{{ liveRunning ? "检测中" : "待启动" }}</strong>
            </div>
            <div class="live-stat">
              <span>当前帧目标</span>
              <strong>{{ result.detection_count ?? 0 }}</strong>
            </div>
            <div class="live-stat">
              <span>最高置信度</span>
              <strong>{{ formatPercent(result.max_confidence) }}</strong>
            </div>
            <div class="live-stat">
              <span>已检测帧数</span>
              <strong>{{ frameHistory.length }}</strong>
            </div>
          </div>
        </div>
      </div>

      <div class="panel insight-panel">
        <div class="section-title">
          <h3>检测指标与智能研判</h3>
          <span>{{ result.analysis?.provider || "等待检测" }}</span>
        </div>

        <div class="metric-grid">
          <div class="metric-box">
            <span>检测目标数</span>
            <strong>{{ result.detection_count ?? 0 }}</strong>
          </div>
          <div class="metric-box">
            <span>最高置信度</span>
            <strong>{{ formatPercent(result.max_confidence) }}</strong>
          </div>
          <div class="metric-box">
            <span>推理耗时</span>
            <strong>{{ result.runtime_sec ? `${result.runtime_sec}s` : "-" }}</strong>
          </div>
          <div class="metric-box">
            <span>输入分辨率</span>
            <strong>{{ resolutionText }}</strong>
          </div>
        </div>

        <div class="analysis-card">
          <div class="analysis-head">
            <el-tag :type="alarmType">{{ alarmLevel }}</el-tag>
            <span>{{ result.analysis?.fallback ? "规则兜底研判" : "Ollama 智能研判" }}</span>
          </div>
          <p>{{ analysisText }}</p>
        </div>

        <div class="judge-list">
          <div class="analysis-step">
            <div class="step-index">1</div>
            <div>
              <strong>意图识别</strong>
              <p>视觉检测只能说明疑似目标存在，真实意图需结合轨迹、区域和多模态证据。</p>
            </div>
            <el-tag type="info">辅助</el-tag>
          </div>
          <div class="analysis-step">
            <div class="step-index">2</div>
            <div>
              <strong>行为判断</strong>
              <p>视频实时检测可观察目标是否持续出现，但不替代完整跟踪算法。</p>
            </div>
            <el-tag :type="result.detection_count ? 'warning' : 'success'">
              {{ result.detection_count ? "需复核" : "未触发" }}
            </el-tag>
          </div>
          <div class="analysis-step">
            <div class="step-index">3</div>
            <div>
              <strong>告警预估</strong>
              <p>根据目标数和置信度给出视觉告警等级，再由 KG/LLM 融合链路复核。</p>
            </div>
            <el-tag :type="alarmType">{{ alarmLevel }}</el-tag>
          </div>
        </div>
      </div>
    </div>

    <div class="yolo-bottom">
      <div class="panel table-panel">
        <div class="section-title">
          <h3>检测目标表格</h3>
          <span>{{ detectionRows.length }} 条目标记录</span>
        </div>
        <el-table :data="detectionRows" height="100%" size="small">
          <el-table-column prop="id" label="目标编号" width="90" />
          <el-table-column prop="class_name" label="类别" width="120" />
          <el-table-column label="置信度" width="100">
            <template #default="{ row }">{{ formatPercent(row.confidence) }}</template>
          </el-table-column>
          <el-table-column label="中心点" min-width="130">
            <template #default="{ row }">{{ row.center?.join(", ") }}</template>
          </el-table-column>
          <el-table-column label="检测框 xyxy" min-width="220">
            <template #default="{ row }">{{ row.bbox?.join(", ") }}</template>
          </el-table-column>
          <el-table-column prop="area_ratio" label="面积占比" width="110" />
        </el-table>
      </div>

      <div class="panel frame-panel">
        <div class="section-title">
          <h3>实时帧记录</h3>
          <span>最近检测帧</span>
        </div>
        <el-table :data="frameHistory" height="100%" size="small">
          <el-table-column prop="frame_no" label="序号" width="70" />
          <el-table-column prop="detection_count" label="目标数" width="80" />
          <el-table-column label="最高置信度">
            <template #default="{ row }">{{ formatPercent(row.max_confidence) }}</template>
          </el-table-column>
          <el-table-column prop="runtime_sec" label="耗时(s)" width="90" />
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { UploadFilled } from "@element-plus/icons-vue";
import PageHeader from "../components/common/PageHeader.vue";
import {
  analyzeYoloDetection,
  detectYoloFrame,
  detectYoloImage,
  detectYoloVideoFrame,
  getYoloSamples,
  getYoloStatus,
} from "../api/yolo";

const backendUrl = "http://localhost:8000";
const inputType = ref("image");
const inputOptions = [
  { label: "图片输入", value: "image" },
  { label: "视频输入", value: "video" },
];

const status = ref({});
const samples = ref({ images: [], videos: [] });
const selectedImage = ref(null);
const selectedVideo = ref(null);
const uploadFile = ref(null);
const uploadPreview = ref("");
const confidence = ref(0.25);
const iou = ref(0.45);
const enableLlm = ref(true);
const loading = ref(false);
const result = ref({});
const frameHistory = ref([]);
const liveRunning = ref(false);
const liveStreamUrl = ref("");
const sampleFrameIndex = ref(0);
const videoAggregate = ref({ frames: 0, totalDetections: 0, maxConfidence: 0 });
const videoRef = ref(null);
const overlayCanvasRef = ref(null);
const captureCanvasRef = ref(null);
let frameTimer = null;
let frameBusy = false;

const previewUrl = computed(() => {
  if (uploadPreview.value && inputType.value === "image") return uploadPreview.value;
  if (selectedImage.value) return backendUrl + selectedImage.value.url;
  return "";
});

const videoPreviewUrl = computed(() => {
  if (uploadPreview.value && inputType.value === "video") return uploadPreview.value;
  if (selectedVideo.value) return backendUrl + selectedVideo.value.url;
  return "";
});

const activeInputName = computed(() => {
  if (uploadFile.value) return uploadFile.value.name;
  if (inputType.value === "image") return selectedImage.value?.name || "未选择图片";
  return selectedVideo.value?.name || "未选择视频";
});

const detectionRows = computed(() => result.value.detections || []);

const resolutionText = computed(() => {
  const width = result.value.image_width || result.value.video_width;
  const height = result.value.image_height || result.value.video_height;
  return width && height ? `${width}×${height}` : "-";
});

const alarmLevel = computed(() => {
  const count = result.value.detection_count || 0;
  const conf = result.value.max_confidence || 0;
  if (!count) return "低风险";
  if (conf >= 0.75) return "高风险";
  return "中风险";
});

const alarmType = computed(() => {
  if (alarmLevel.value === "高风险") return "danger";
  if (alarmLevel.value === "中风险") return "warning";
  return "success";
});

const analysisText = computed(
  () =>
    result.value.analysis?.conclusion ||
    "完成一次图片或视频检测后，这里会显示 Ollama 或规则兜底生成的意图识别、行为判断、告警预估和处置建议。",
);

function formatPercent(value) {
  if (value === undefined || value === null || value === "") return "-";
  return `${Math.round(Number(value) * 1000) / 10}%`;
}

async function loadMeta() {
  status.value = (await getYoloStatus()).data;
  samples.value = (await getYoloSamples()).data;
  selectedImage.value = samples.value.images?.[0] || null;
  selectedVideo.value = samples.value.videos?.[0] || null;
}

function selectSampleImage(item) {
  inputType.value = "image";
  selectedImage.value = item;
  clearUpload();
  resetResult();
}

function selectSampleVideo(item) {
  inputType.value = "video";
  selectedVideo.value = item;
  clearUpload();
  resetResult();
}

function clearUpload() {
  uploadFile.value = null;
  if (uploadPreview.value) URL.revokeObjectURL(uploadPreview.value);
  uploadPreview.value = "";
}

function resetResult() {
  stopFrameLoop(false);
  result.value = {};
  frameHistory.value = [];
  liveStreamUrl.value = "";
  sampleFrameIndex.value = 0;
  videoAggregate.value = { frames: 0, totalDetections: 0, maxConfidence: 0 };
  clearOverlay();
}

function handleUpload(upload) {
  clearUpload();
  uploadFile.value = upload.raw;
  uploadPreview.value = URL.createObjectURL(upload.raw);
  resetResult();
}

function buildImageForm() {
  const form = new FormData();
  form.append("confidence", confidence.value);
  form.append("iou", iou.value);
  form.append("enable_llm", enableLlm.value);
  if (uploadFile.value) {
    form.append("file", uploadFile.value);
  } else if (selectedImage.value) {
    form.append("sample_name", selectedImage.value.name);
  }
  return form;
}

async function runDetection() {
  if (inputType.value === "image") {
    await runImageDetection();
    return;
  }
  if (liveRunning.value) {
    await finishVideoDetection();
    return;
  }
  await runVideoRealtime();
}

async function runImageDetection() {
  if (!uploadFile.value && !selectedImage.value) {
    ElMessage.warning("请先选择本地图片或上传图片");
    return;
  }
  loading.value = true;
  try {
    const response = await detectYoloImage(buildImageForm());
    result.value = response.data;
    ElMessage.success("检测完成");
  } catch (error) {
    const detail = error.response?.data?.detail || error.message || "检测失败";
    ElMessage.error(String(detail));
  } finally {
    loading.value = false;
  }
}

async function runVideoRealtime() {
  if (!uploadFile.value && !selectedVideo.value) {
    ElMessage.warning("请先选择本地视频或上传视频");
    return;
  }
  resetResult();
  liveRunning.value = true;
  if (!uploadFile.value && selectedVideo.value) {
    liveStreamUrl.value =
      `${backendUrl}/api/yolo/detect/video-stream/${encodeURIComponent(selectedVideo.value.name)}` +
      `?confidence=${confidence.value}&iou=${iou.value}&frame_stride=3&t=${Date.now()}`;
    result.value = {
      detection_count: 0,
      max_confidence: 0,
      analysis: {
        provider: "video-stream",
        conclusion: "视频正在实时检测，检测过程中下方目标表格显示当前帧结果；视频结束后输出智能研判结论。",
      },
    };
    startSampleFrameLoop();
    ElMessage.success("实时标注流已启动");
    return;
  }
  await nextTick();
  if (videoRef.value) {
    await videoRef.value.play();
    startFrameLoop();
  }
}

function startFrameLoop() {
  if (inputType.value !== "video" || !uploadFile.value) return;
  liveRunning.value = true;
  if (frameTimer) clearInterval(frameTimer);
  frameTimer = setInterval(captureAndDetectFrame, 700);
}

function startSampleFrameLoop() {
  if (inputType.value !== "video" || uploadFile.value || !selectedVideo.value) return;
  liveRunning.value = true;
  sampleFrameIndex.value = 0;
  if (frameTimer) clearInterval(frameTimer);
  frameTimer = setInterval(detectSampleVideoFrame, 700);
}

function stopFrameLoop(clearStream = true) {
  liveRunning.value = false;
  if (clearStream) liveStreamUrl.value = "";
  if (frameTimer) {
    clearInterval(frameTimer);
    frameTimer = null;
  }
}

async function finishVideoDetection() {
  stopFrameLoop(true);
  if (videoRef.value && !videoRef.value.paused) videoRef.value.pause();
  if (videoAggregate.value.frames > 0) {
    await runFinalVideoAnalysis();
  }
}

async function detectSampleVideoFrame() {
  if (frameBusy || !selectedVideo.value) return;
  frameBusy = true;
  try {
    const { data } = await detectYoloVideoFrame(selectedVideo.value.name, {
      frame_index: sampleFrameIndex.value,
      confidence: confidence.value,
      iou: iou.value,
    });
    applyFrameResult(data);
    sampleFrameIndex.value += 3;
    if (data.is_end || sampleFrameIndex.value >= (data.frame_count || 0)) {
      await finishVideoDetection();
    }
  } catch (error) {
    stopFrameLoop(true);
    ElMessage.error(error.response?.data?.detail || error.message || "实时视频帧检测失败");
  } finally {
    frameBusy = false;
  }
}

async function captureAndDetectFrame() {
  if (frameBusy || !videoRef.value || !captureCanvasRef.value) return;
  const video = videoRef.value;
  if (video.paused || video.ended || !video.videoWidth || !video.videoHeight) return;
  frameBusy = true;
  try {
    const canvas = captureCanvasRef.value;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.82));
    if (!blob) return;
    const form = new FormData();
    form.append("file", blob, "frame.jpg");
    form.append("confidence", confidence.value);
    form.append("iou", iou.value);
    const { data } = await detectYoloFrame(form);
    applyFrameResult(data);
    drawOverlay(data.detections || [], data.image_width, data.image_height);
  } catch (error) {
    stopFrameLoop();
    ElMessage.error(error.response?.data?.detail || error.message || "实时帧检测失败");
  } finally {
    frameBusy = false;
  }
}

function applyFrameResult(data) {
  result.value = {
    ...data,
    video_width: data.video_width || data.image_width,
    video_height: data.video_height || data.image_height,
    analysis: {
      provider: "实时逐帧检测",
      conclusion: `当前帧检测到 ${data.detection_count || 0} 个疑似目标，最高置信度 ${formatPercent(data.max_confidence)}。视频结束后将基于累计结果输出智能研判。`,
    },
  };
  videoAggregate.value = {
    frames: videoAggregate.value.frames + 1,
    totalDetections: videoAggregate.value.totalDetections + (data.detection_count || 0),
    maxConfidence: Math.max(videoAggregate.value.maxConfidence || 0, data.max_confidence || 0),
  };
  frameHistory.value.unshift({
    frame_no: frameHistory.value.length + 1,
    detection_count: data.detection_count || 0,
    max_confidence: data.max_confidence || 0,
    runtime_sec: data.runtime_sec || 0,
  });
  frameHistory.value = frameHistory.value.slice(0, 20);
}

async function runFinalVideoAnalysis() {
  const summary = {
    input_type: "video_realtime",
    input_name: activeInputName.value,
    detected_frames: videoAggregate.value.frames,
    total_detections: videoAggregate.value.totalDetections,
    max_confidence: videoAggregate.value.maxConfidence,
    latest_detections: result.value.detections || [],
  };
  if (!enableLlm.value) {
    result.value = {
      ...result.value,
      analysis: {
        provider: "规则研判",
        fallback: true,
        conclusion: `视频检测结束。累计检测 ${summary.detected_frames} 帧，累计目标 ${summary.total_detections} 个，最高置信度 ${formatPercent(summary.max_confidence)}。`,
      },
    };
    return;
  }
  try {
    const { data } = await analyzeYoloDetection(summary);
    result.value = {
      ...result.value,
      analysis: data,
    };
  } catch (error) {
    result.value = {
      ...result.value,
      analysis: {
        provider: "规则研判",
        fallback: true,
        conclusion: `视频检测结束。累计检测 ${summary.detected_frames} 帧，累计目标 ${summary.total_detections} 个，最高置信度 ${formatPercent(summary.max_confidence)}。Ollama 研判调用失败：${error.message}`,
      },
    };
  }
}

function drawOverlay(detections, sourceWidth, sourceHeight) {
  const canvas = overlayCanvasRef.value;
  const video = videoRef.value;
  if (!canvas || !video) return;
  const rect = video.getBoundingClientRect();
  canvas.width = rect.width;
  canvas.height = rect.height;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const scaleX = canvas.width / sourceWidth;
  const scaleY = canvas.height / sourceHeight;
  ctx.lineWidth = 3;
  ctx.font = "13px Microsoft YaHei";
  detections.forEach((det, index) => {
    const [x1, y1, x2, y2] = det.bbox;
    const color = ["#ff4d4f", "#fa8c16", "#1677ff", "#52c41a"][index % 4];
    const left = x1 * scaleX;
    const top = y1 * scaleY;
    const width = (x2 - x1) * scaleX;
    const height = (y2 - y1) * scaleY;
    const label = `${det.class_name} ${formatPercent(det.confidence)}`;
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.strokeRect(left, top, width, height);
    const textWidth = ctx.measureText(label).width + 10;
    ctx.fillRect(left, Math.max(0, top - 24), textWidth, 22);
    ctx.fillStyle = "#fff";
    ctx.fillText(label, left + 5, Math.max(14, top - 8));
  });
}

function clearOverlay() {
  const canvas = overlayCanvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  ctx?.clearRect(0, 0, canvas.width, canvas.height);
}

onMounted(loadMeta);
onBeforeUnmount(() => {
  stopFrameLoop(true);
  clearUpload();
});
</script>

<style scoped>
.yolo-page {
  height: calc(100vh - 58px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding-bottom: 12px;
}

.yolo-page :deep(.page-header) {
  flex: 0 0 78px;
  margin-bottom: 10px;
}

.yolo-top {
  flex: 0 0 76px;
  display: grid;
  grid-template-columns: 180px minmax(0, 1fr) minmax(0, 1fr) 250px;
  gap: 14px;
  align-items: center;
  margin-bottom: 12px;
}

.control-group {
  min-width: 0;
}

.control-group.compact {
  display: grid;
  gap: 8px;
}

.control-label {
  display: block;
  color: var(--muted);
  font-size: 12px;
  margin-bottom: 6px;
}

.yolo-workbench {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr) 380px;
  gap: 12px;
}

.input-panel,
.result-panel,
.insight-panel {
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.sample-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.sample-card {
  cursor: pointer;
  border: 1px solid var(--line);
  background: var(--panel-soft);
  border-radius: 8px;
  padding: 7px;
  transition: 0.16s ease;
}

.sample-card.active,
.sample-card:hover {
  border-color: #7db2ff;
  box-shadow: 0 8px 18px rgba(36, 104, 216, 0.12);
}

.sample-card img {
  width: 100%;
  height: 78px;
  object-fit: cover;
  border-radius: 6px;
  display: block;
  margin-bottom: 6px;
}

.sample-card strong {
  display: block;
  font-size: 12px;
  color: var(--text);
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.video-thumb {
  height: 78px;
  border-radius: 6px;
  background: linear-gradient(135deg, #153f8f, #2468d8);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  letter-spacing: 1px;
  margin-bottom: 6px;
}

.upload-icon {
  font-size: 34px;
  color: var(--primary);
}

.input-meta {
  display: grid;
  gap: 8px;
  margin-top: 10px;
}

.result-panel {
  padding: 12px;
}

.image-stage,
.video-stage {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.image-stage img {
  width: 100%;
  height: 100%;
  min-height: 0;
  object-fit: contain;
  background: #101a2b;
  border-radius: 8px;
  border: 1px solid var(--line);
}

.live-video-box {
  position: relative;
  flex: 1;
  min-height: 0;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #101a2b;
}

.live-stream,
.source-video {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
  background: #101a2b;
}

.overlay-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.capture-canvas {
  display: none;
}

.live-strip {
  flex: 0 0 72px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
}

.live-stat {
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel-soft);
}

.live-stat span {
  display: block;
  color: var(--muted);
  font-size: 12px;
}

.live-stat strong {
  display: block;
  margin-top: 5px;
  color: var(--primary-dark);
  font-size: 18px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.metric-box {
  padding: 11px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel-soft);
}

.metric-box span {
  display: block;
  color: var(--muted);
  font-size: 12px;
  margin-bottom: 6px;
}

.metric-box strong {
  font-size: 22px;
  color: var(--primary-dark);
}

.analysis-card {
  margin-top: 12px;
  padding: 12px;
  border: 1px solid #f3d19e;
  background: #fffaf0;
  border-radius: 8px;
}

.analysis-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: var(--muted);
}

.analysis-card p {
  margin: 0;
  line-height: 1.7;
  color: #3d4b5d;
  white-space: pre-wrap;
}

.judge-list {
  margin-top: 12px;
  display: grid;
  gap: 8px;
  overflow-y: auto;
}

.judge-list .analysis-step {
  grid-template-columns: 32px 1fr 72px;
}

.judge-list p {
  margin: 4px 0 0;
  color: var(--muted);
  line-height: 1.5;
}

.yolo-bottom {
  flex: 0 0 190px;
  min-height: 0;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 380px;
  gap: 12px;
  margin-top: 12px;
}

.table-panel,
.frame-panel {
  min-height: 0;
  overflow: hidden;
}

@media (max-width: 1280px) {
  .yolo-page {
    height: auto;
    overflow: visible;
  }

  .yolo-top,
  .yolo-workbench,
  .yolo-bottom {
    grid-template-columns: 1fr;
  }

  .yolo-workbench {
    min-height: 900px;
  }
}
</style>
