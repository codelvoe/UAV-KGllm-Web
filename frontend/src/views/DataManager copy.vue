<template>
  <div class="page data-page">
    <PageHeader
      title="多模态数据管理工作台"
      subtitle="查看各模态标准化记录、字段含义和记录摘要，为融合候选生成提供结构化输入。"
      eyebrow="DATA WORKBENCH"
    />

    <div class="data-shell">
      <aside class="panel modality-panel">
        <div class="section-title">
          <h3>模态筛选</h3>
          <span>{{ modalities.length }} 类数据</span>
        </div>
        <div class="modality-list">
          <button
            v-for="item in modalities"
            :key="item.source"
            :class="['modality-item', { active: item.source === source }]"
            @click="changeSource(item.source)"
          >
            <strong>{{ modalityName(item.source) }}</strong>
            <span>{{ item.records || 0 }} 条</span>
          </button>
        </div>

        <div class="modality-note">
          <strong>融合输入数据</strong>
          <p>{{ modalityRole }}</p>
        </div>
      </aside>

      <main class="panel records-panel">
        <div class="records-head">
          <div>
            <h3>{{ modalityName(source) }}标准化记录</h3>
            <p>当前共 {{ total }} 条记录，点击表格行查看右侧摘要。</p>
          </div>
          <div class="toolbar">
            <el-input
              v-model="keyword"
              clearable
              placeholder="搜索记录编号、轨迹编号或目标类别"
              @keyup.enter="load"
              @clear="load"
            />
            <el-button type="primary" @click="load">查询</el-button>
          </div>
        </div>

        <div class="records-table">
          <el-table
            :data="records"
            height="100%"
            highlight-current-row
            @row-click="selectRecord"
          >
            <el-table-column
              fixed
              prop="record_id"
              label="记录编号"
              min-width="150"
              show-overflow-tooltip
            />
            <el-table-column prop="source" label="来源" min-width="90" />
            <el-table-column
              prop="track_id"
              label="轨迹编号"
              min-width="180"
              show-overflow-tooltip
            />
            <el-table-column
              prop="time"
              label="时间"
              min-width="170"
              show-overflow-tooltip
            />
            <el-table-column prop="target_type" label="目标类别" min-width="100" />
            <el-table-column prop="model" label="机型" min-width="110" />
            <el-table-column prop="azimuth" label="方位角" min-width="90" />
            <el-table-column prop="distance" label="距离" min-width="90" />
            <el-table-column prop="altitude" label="高度" min-width="90" />
            <el-table-column prop="speed" label="速度" min-width="90" />
            <el-table-column prop="confidence" label="置信度" min-width="90" />
            <el-table-column prop="snr" label="信噪比" min-width="90" />
          </el-table>
        </div>

        <el-pagination
          v-model:current-page="page"
          layout="total, prev, pager, next"
          :total="total"
          :page-size="20"
          @current-change="load"
        />
      </main>

      <aside class="panel detail-panel">
        <div class="section-title">
          <h3>记录摘要</h3>
          <el-tag v-if="current.record_id" size="small">
            {{ modalityName(current.source) }}
          </el-tag>
        </div>

        <div v-if="current.record_id" class="detail-scroll">
          <div class="detail-card">
            <span>记录编号</span>
            <strong>{{ current.record_id }}</strong>
          </div>
          <div class="detail-card">
            <span>轨迹编号</span>
            <strong>{{ current.track_id || "-" }}</strong>
          </div>
          <div class="detail-grid">
            <div v-for="item in detailItems" :key="item.key" class="detail-card">
              <span>{{ item.label }}</span>
              <strong>{{ formatValue(current[item.key]) }}</strong>
            </div>
          </div>
          <div class="usage-box">
            <strong>数据作用</strong>
            <p>{{ modalityRole }}</p>
          </div>
        </div>

        <div v-else class="empty-hint">请选择一条记录查看摘要。</div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import PageHeader from "../components/common/PageHeader.vue";
import { getModalities, getRecords } from "../api/data";

const modalities = ref([]);
const records = ref([]);
const total = ref(0);
const page = ref(1);
const source = ref("radar");
const keyword = ref("");
const current = ref({});

const detailItems = [
  { key: "time", label: "观测时间" },
  { key: "target_type", label: "目标类别" },
  { key: "model", label: "机型" },
  { key: "azimuth", label: "方位角" },
  { key: "distance", label: "距离" },
  { key: "altitude", label: "高度" },
  { key: "speed", label: "速度" },
  { key: "confidence", label: "置信度" },
  { key: "snr", label: "信噪比" },
];

const modalityRole = computed(() => {
  const roles = {
    radar: "雷达提供空间位置、运动状态和信号质量，是候选生成的主要空间输入。",
    spectrum: "频谱提供无线电语义、机型、目标类别和信号强度，是跨模态融合的重要语义锚点。",
    recognize: "视觉识别提供目标类别和相似度，可作为辅助证据支持候选确认与冲突判断。",
    pho_status: "光电状态记录设备姿态、视线方向和工作状态，用于解释视觉证据可用性。",
    decrypt: "隐藏标签仅用于最终评价，不进入候选生成、排序或大模型裁决。",
  };
  return roles[source.value] || "多源感知输入记录。";
});

function modalityName(name) {
  return (
    {
      radar: "雷达",
      spectrum: "频谱",
      recognize: "视觉识别",
      pho_status: "光电状态",
      decrypt: "隐藏标签",
    }[name] ||
    name ||
    "-"
  );
}

function formatValue(value) {
  if (value === null || value === undefined || value === "") return "-";
  const number = Number(value);
  if (Number.isFinite(number)) return number.toFixed(3).replace(/\.?0+$/, "");
  return value;
}

async function load() {
  const { data } = await getRecords({
    source: source.value,
    page: page.value,
    page_size: 20,
    keyword: keyword.value,
  });
  records.value = data.items || [];
  total.value = data.total || 0;
  current.value = records.value[0] || {};
}

function changeSource(nextSource) {
  source.value = nextSource;
  page.value = 1;
  keyword.value = "";
  load();
}

function selectRecord(row) {
  current.value = row;
}

onMounted(async () => {
  modalities.value = (await getModalities()).data || [];
  if (!modalities.value.length) {
    modalities.value = [
      { source: "radar", records: 0 },
      { source: "spectrum", records: 0 },
      { source: "recognize", records: 0 },
      { source: "pho_status", records: 0 },
      { source: "decrypt", records: 0 },
    ];
  }
  await load();
});
</script>

<style scoped>
.data-page {
  height: 100%;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.data-shell {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr) 320px;
  gap: 12px;
}

.modality-panel,
.records-panel,
.detail-panel {
  min-height: 0;
  overflow: hidden;
  padding: 14px;
}

.modality-panel,
.records-panel,
.detail-panel {
  display: flex;
  flex-direction: column;
}

.section-title,
.records-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.section-title h3,
.records-head h3 {
  margin: 0;
  color: #17233d;
  font-size: 15px;
}

.section-title span,
.records-head p {
  margin: 4px 0 0;
  color: #708198;
  font-size: 12px;
}

.modality-list {
  display: grid;
  gap: 8px;
}

.modality-item {
  width: 100%;
  padding: 11px 12px;
  border: 1px solid #dfe8f2;
  border-radius: 8px;
  background: #f8fbff;
  color: #263d5d;
  text-align: left;
  cursor: pointer;
}

.modality-item strong {
  display: block;
  margin-bottom: 4px;
}

.modality-item span {
  color: #708198;
  font-size: 12px;
}

.modality-item.active {
  border-color: #409eff;
  background: #edf5ff;
  color: #174ea6;
}

.modality-note {
  margin-top: auto;
  padding: 12px;
  border: 1px solid #dfe8f2;
  border-radius: 8px;
  background: #f8fbff;
}

.modality-note p,
.usage-box p {
  margin: 8px 0 0;
  color: #53677f;
  font-size: 13px;
  line-height: 1.55;
}

.toolbar {
  display: flex;
  gap: 8px;
}

.toolbar .el-input {
  width: 320px;
}

.records-table {
  flex: 1;
  min-height: 0;
  margin-bottom: 10px;
}

.detail-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: grid;
  align-content: start;
  gap: 9px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 9px;
}

.detail-card,
.usage-box {
  min-width: 0;
  padding: 10px;
  border: 1px solid #dfe8f2;
  border-radius: 8px;
  background: #f8fbff;
}

.detail-card span {
  display: block;
  margin-bottom: 5px;
  color: #708198;
  font-size: 12px;
}

.detail-card strong {
  display: block;
  overflow: hidden;
  color: #17233d;
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-hint {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8a9bb0;
}

@media (max-width: 1280px) {
  .data-shell {
    grid-template-columns: 190px minmax(0, 1fr) 280px;
  }
}
</style>
