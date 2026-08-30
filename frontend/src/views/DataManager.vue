<template>
  <div class="page data-page">
    <PageHeader
      title="多模态数据管理"
      subtitle="查看各模态标准化记录、字段完整性和选中记录摘要。"
      eyebrow="Data Understanding"
    />

    <!-- 紧凑摘要条：替代无业务价值的六张 KPI 卡片 -->
    <div class="panel data-summary-bar">
      <div class="summary-main">
        <div class="summary-pill">
          <span>当前模态</span>
          <strong>{{ modalityName(source) }}</strong>
        </div>
        <div class="summary-divider"></div>
        <div class="summary-pill">
          <span>记录数</span>
          <strong>{{ total }}</strong>
        </div>
        <div class="summary-divider"></div>
        <div class="summary-pill">
          <span>轨迹数</span>
          <strong>{{ currentModality?.tracks || "-" }}</strong>
        </div>
        <div class="summary-divider"></div>
        <div class="summary-pill summary-role-pill">
          <span>数据角色</span>
          <strong>{{ roleShortName }}</strong>
        </div>
      </div>

      <div class="summary-right">
        <el-tag :type="roleTagType" effect="light">
          {{ source === "decrypt" ? "仅评价使用" : "参与证据组织" }}
        </el-tag>
        <span class="summary-tip">{{ source === "decrypt" ? "不进入 KG 候选与 LLM 裁决" : "点击记录查看证据摘要" }}</span>
      </div>
    </div>

    <div class="data-content">
      <!-- 上方主工作区：自动占满剩余高度 -->
      <div class="data-workbench">
        <!-- 左侧：模态筛选 -->
        <div class="panel filter-panel">
          <div class="section-title">
            <h3>模态筛选</h3>
            <span>证据来源</span>
          </div>

          <el-menu :default-active="source" @select="changeSource">
            <el-menu-item
              v-for="modality in modalities"
              :key="modality.source"
              :index="modality.source"
            >
              <span>{{ modalityName(modality.source) }}</span>
              <span class="muted">（{{ modality.records }}）</span>
            </el-menu-item>
          </el-menu>

          <div class="filter-info" :class="{ warning: source === 'decrypt' }">
            <div class="filter-info-head">
              <span>分析角色</span>
              <el-tag size="small" :type="roleTagType">{{ roleShortName }}</el-tag>
            </div>
            <p>{{ modalityRole }}</p>
          </div>

          <div class="filter-note">
            <span>页面说明</span>
            <p>呈现标准化字段和选中记录摘要，不展开原始 JSON。</p>
          </div>
        </div>

        <!-- 中间：充分展开的记录主表 -->
        <div class="panel table-panel">
          <div class="section-title">
            <h3>标准化记录主表</h3>
            <span>表头固定 · 首列固定 · 支持列显隐</span>
          </div>

          <div class="toolbar">
            <el-input
              v-model="keyword"
              clearable
              placeholder="搜索记录编号 / 轨迹编号 / 目标类型"
              @clear="load"
              @keyup.enter="load"
            />
            <el-button type="primary" @click="load">查询</el-button>

            <el-popover placement="bottom" :width="270" trigger="click">
              <template #reference>
                <el-button>列显隐</el-button>
              </template>
              <el-checkbox-group v-model="visibleColumns" class="column-selector">
                <el-checkbox
                  v-for="column in allColumns"
                  :key="column.prop"
                  :label="column.prop"
                >
                  {{ column.label }}
                </el-checkbox>
              </el-checkbox-group>
            </el-popover>
          </div>

          <div class="table-shell">
            <el-table
              class="table-fill"
              :data="records"
              height="100%"
              highlight-current-row
              @row-click="show"
            >
              <el-table-column
                fixed
                prop="record_id"
                label="记录编号"
                width="126"
                show-overflow-tooltip
              />
              <el-table-column
                v-for="column in activeColumns"
                :key="column.prop"
                :prop="column.prop"
                :label="column.label"
                :width="column.width"
                :min-width="column.minWidth"
                :formatter="column.formatter"
                show-overflow-tooltip
              />
            </el-table>
          </div>

          <el-pagination
            v-model:current-page="page"
            class="table-pagination"
            layout="total, prev, pager, next"
            :total="total"
            :page-size="20"
            @current-change="load"
          />
        </div>

        <!-- 右侧：选中记录详情 -->
        <div class="panel detail-panel">
          <div class="section-title">
            <h3>选中记录摘要</h3>
            <el-tag v-if="current.record_id" size="small" :type="roleTagType">
              {{ modalityName(current.source) }}
            </el-tag>
          </div>

          <div v-if="current.record_id" class="detail-scroll">
            <div class="detail-block">
              <h4>基本信息</h4>
              <div class="field-grid">
                <div class="field-card">
                  <span>记录编号</span>
                  <strong :title="displayValue(current.record_id)">
                    {{ displayValue(current.record_id) }}
                  </strong>
                </div>
                <div class="field-card">
                  <span>来源模态</span>
                  <strong>{{ modalityName(current.source) }}</strong>
                </div>
                <div class="field-card field-full">
                  <span>轨迹编号</span>
                  <strong :title="displayValue(current.track_id)">
                    {{ displayValue(current.track_id) }}
                  </strong>
                </div>
                <div class="field-card field-full">
                  <span>观测时间</span>
                  <strong :title="displayValue(current.time)">
                    {{ displayValue(current.time) }}
                  </strong>
                </div>
              </div>
            </div>

            <div class="detail-block">
              <h4>目标与观测特征</h4>
              <div class="field-grid">
                <div
                  v-for="item in featureDetailItems"
                  :key="item.key"
                  class="field-card"
                >
                  <span>{{ item.label }}</span>
                  <strong :title="String(formatDetailValue(item.key))">
                    {{ formatDetailValue(item.key) }}
                  </strong>
                </div>
              </div>
            </div>

            <div class="detail-block">
              <h4>证据用途提示</h4>
              <div class="usage-list">
                <div v-for="tip in qualityTips" :key="tip.tag" class="usage-row">
                  <span class="usage-tag" :class="{ evaluation: source === 'decrypt' }">
                    {{ tip.tag }}
                  </span>
                  <p>{{ tip.text }}</p>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="empty-hint detail-empty">
            点击表格中的一条记录查看详情
          </div>
        </div>
      </div>

      <!-- 底部分析区：固定留在首屏 -->
      <div class="data-analysis-grid">
        <div class="panel analysis-panel">
          <div class="section-title">
            <h3>字段说明</h3>
            <span>中文口径与算法用途</span>
          </div>

          <div class="guide-list">
            <div v-for="item in fieldGuide" :key="item.name" class="guide-item">
              <div class="guide-title">
                <strong>{{ item.name }}</strong>
                <el-tag size="small" effect="plain">{{ item.tag }}</el-tag>
              </div>
              <p>{{ item.desc }}</p>
            </div>
          </div>
        </div>

        <div class="panel analysis-panel">
          <div class="section-title">
            <h3>当前模态摘要</h3>
            <el-tag size="small" :type="roleTagType">{{ modalityName(source) }}</el-tag>
          </div>

          <div class="modality-metrics">
            <div class="metric-card">
              <span>记录数量</span>
              <strong>{{ total }}</strong>
            </div>
            <div class="metric-card">
              <span>轨迹数量</span>
              <strong>{{ currentModality?.tracks || "-" }}</strong>
            </div>
          </div>

          <div class="modality-role">
            <span>主要作用</span>
            <p>{{ modalityRole }}</p>
          </div>
        </div>

        <div class="panel analysis-panel">
          <div class="section-title">
            <h3>处理链路</h3>
            <span>{{ source === "decrypt" ? "仅评价路径" : "records 到候选池" }}</span>
          </div>

          <div class="pipeline-list">
            <div
              v-for="(step, index) in pipelineSteps"
              :key="step.label"
              class="pipeline-step"
              :class="{ evaluation: source === 'decrypt' }"
            >
              <div class="step-index">{{ index + 1 }}</div>
              <div class="step-text">
                <strong>{{ step.label }}</strong>
                <small>{{ step.desc }}</small>
              </div>
              <el-tag size="small" :type="source === 'decrypt' ? 'danger' : ''">
                {{ step.tag }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
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
const source = ref("radar");
const page = ref(1);
const keyword = ref("");
const current = ref({});

function numberFormatter(_row, _column, value) {
  return formatNumber(value);
}

const allColumns = [
  { prop: "source", label: "来源模态", width: 92 },
  { prop: "track_id", label: "轨迹编号", minWidth: 154 },
  { prop: "time", label: "观测时间", minWidth: 182 },
  { prop: "target_type", label: "目标类别", width: 88 },
  { prop: "model", label: "机型/型号", minWidth: 105 },
  { prop: "azimuth", label: "方位角", minWidth: 102, formatter: numberFormatter },
  { prop: "distance", label: "距离", minWidth: 106, formatter: numberFormatter },
  { prop: "altitude", label: "高度", minWidth: 102, formatter: numberFormatter },
  { prop: "speed", label: "速度", minWidth: 98, formatter: numberFormatter },
  { prop: "confidence", label: "置信度", minWidth: 100, formatter: numberFormatter },
  { prop: "snr", label: "SNR", minWidth: 96, formatter: numberFormatter },
];

const visibleColumns = ref(allColumns.map((item) => item.prop));

const activeColumns = computed(() =>
  allColumns.filter((item) => visibleColumns.value.includes(item.prop)),
);

const featureDetailItems = [
  { key: "target_type", label: "目标类别" },
  { key: "model", label: "机型/型号" },
  { key: "azimuth", label: "方位角" },
  { key: "distance", label: "距离" },
  { key: "altitude", label: "高度" },
  { key: "speed", label: "速度" },
  { key: "confidence", label: "置信度" },
  { key: "snr", label: "SNR" },
];

const currentModality = computed(() =>
  modalities.value.find((item) => item.source === source.value),
);

const roleShortName = computed(() => {
  const roles = {
    radar: "候选生成输入",
    spectrum: "语义锚点证据",
    recognize: "辅助识别证据",
    pho_status: "设备状态证据",
    decrypt: "隐藏评价标签",
  };
  return roles[source.value] || "输入记录";
});

const modalityRole = computed(() => {
  const roles = {
    radar: "空间与运动候选，是覆盖最广但虚警较多的基础输入。",
    spectrum: "无线电语义锚点，提供机型、drone 语义、方位与信号质量。",
    recognize: "视觉辅助证据，用于补充类别与相似度，覆盖范围有限。",
    pho_status: "光电设备状态与视线信息，用于解释视觉可用性。",
    decrypt: "隐藏标签，仅用于最终评价，不进入 KG 候选或 LLM 裁决。",
  };
  return roles[source.value] || "多模态输入记录。";
});

const roleTagType = computed(() => {
  if (source.value === "decrypt") return "danger";
  if (source.value === "spectrum") return "success";
  if (source.value === "recognize") return "warning";
  return "primary";
});

const fieldGuide = computed(() => {
  const guides = {
    radar: [
      { name: "方位角", tag: "matching", desc: "目标相对设备方向，用于 radar-spectrum 方位匹配。" },
      { name: "距离 / 高度 / 速度", tag: "motion", desc: "描述目标运动状态，为轨迹合理性分析提供依据。" },
      { name: "SNR", tag: "quality", desc: "反映雷达回波质量，用于辅助判断证据可信度。" },
    ],
    spectrum: [
      { name: "方位角", tag: "matching", desc: "用于与雷达候选进行方向一致性匹配。" },
      { name: "机型 / 语义", tag: "semantic", desc: "提供 drone 语义与具体机型提示。" },
      { name: "置信度", tag: "quality", desc: "反映频谱识别证据可靠程度。" },
    ],
    recognize: [
      { name: "目标类别", tag: "semantic", desc: "视觉识别类别，用于辅助确认目标属性。" },
      { name: "置信度", tag: "quality", desc: "反映视觉检测可靠程度，不单独形成最终裁决。" },
      { name: "时间覆盖", tag: "coverage", desc: "视觉覆盖有限，缺失时不直接视为反证。" },
    ],
    pho_status: [
      { name: "设备状态", tag: "status", desc: "表示光电设备当前可用状态和工作方向。" },
      { name: "视线方向", tag: "coverage", desc: "用于解释视觉观测边界和缺失原因。" },
      { name: "时间字段", tag: "alignment", desc: "用于与目标观测进行时间对齐。" },
    ],
    decrypt: [
      { name: "身份轨迹", tag: "evaluation", desc: "作为隐藏标签与最终输出对照，不参与融合。" },
      { name: "评价边界", tag: "isolation", desc: "禁止进入候选生成、排序和 LLM 输入。" },
      { name: "结果核验", tag: "metric", desc: "仅用于计算 Precision、Recall、F1 与 FAR。" },
    ],
  };
  return guides[source.value] || guides.radar;
});

const qualityTips = computed(() => {
  if (source.value === "decrypt") {
    return [
      { tag: "label", text: "身份与轨迹字段仅用于最终评价" },
      { tag: "isolated", text: "不得进入候选生成与候选排序" },
      { tag: "LLM", text: "不得进入大模型研判输入" },
    ];
  }
  return [
    { tag: "time", text: "时间字段用于跨模态对齐" },
    { tag: "track", text: "轨迹编号用于形成轨迹级摘要" },
    { tag: "KG", text: "关键证据用于候选检索与解释" },
  ];
});

const pipelineSteps = computed(() => {
  if (source.value === "decrypt") {
    return [
      { label: "Decrypt Records", desc: "身份与位置记录", tag: "records" },
      { label: "Hidden-label Track", desc: "形成评价参照", tag: "label" },
      { label: "Evaluation Only", desc: "核验最终结果", tag: "eval" },
    ];
  }
  return [
    { label: "标准化记录", desc: `${modalityName(source.value)} records`, tag: "records" },
    { label: "轨迹级摘要", desc: "聚合连续证据", tag: "tracks" },
    { label: "KG 候选检索", desc: "进入候选分析", tag: "fusion" },
  ];
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

function displayValue(value) {
  return value === null || value === undefined || value === "" ? "-" : String(value);
}

function formatNumber(value) {
  if (value === null || value === undefined || value === "") return "-";
  const parsed = Number(value);
  if (Number.isNaN(parsed)) return String(value);
  return parsed.toFixed(4).replace(/\.?0+$/, "");
}

function formatDetailValue(key) {
  const value = current.value[key];
  const numericKeys = ["azimuth", "distance", "altitude", "speed", "confidence", "snr"];
  return numericKeys.includes(key) ? formatNumber(value) : displayValue(value);
}

function changeSource(nextSource) {
  source.value = nextSource;
  page.value = 1;
  keyword.value = "";
  current.value = {};
  load();
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
  if (!current.value.record_id && records.value[0]) {
    current.value = records.value[0];
  }
}

function show(row) {
  current.value = row;
}

onMounted(async () => {
  modalities.value = (await getModalities()).data || [];
  await load();
});
</script>

<style scoped>
.data-page {
  /* 页面位于应用主内容容器内，避免再次按视口计算高度造成底部裁切 */
  height: 100%;
  min-height: 0;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding-bottom: 8px;
}

/* 紧凑摘要条：仅占一行，不挤压主表 */
.data-summary-bar {
  flex: 0 0 48px;
  margin: 10px 0 12px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 0;
}

.summary-main,
.summary-right {
  display: flex;
  align-items: center;
  gap: 14px;
}

.summary-pill {
  display: flex;
  align-items: baseline;
  gap: 8px;
  white-space: nowrap;
}

.summary-pill span {
  color: #73849c;
  font-size: 12px;
}

.summary-pill strong {
  color: #173357;
  font-size: 15px;
  font-weight: 600;
}

.summary-role-pill strong {
  color: #2468d8;
}

.summary-divider {
  width: 1px;
  height: 19px;
  background: #dfe7f1;
}

.summary-tip {
  color: #73849c;
  font-size: 12px;
}

/* 主内容：上方工作台自动撑满，下方说明固定显示 */
.data-content {
  flex: 1;
  min-height: 0;
  display: grid;
  /* 底部分析卡增加可用高度，保证三步处理链路完整显示 */
  grid-template-rows: minmax(340px, 1fr) 218px;
  gap: 10px;
}

.data-workbench {
  min-height: 0;
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr) 320px;
  gap: 12px;
}

.data-workbench > .panel {
  height: 100%;
  min-height: 0;
  box-sizing: border-box;
  overflow: hidden;
  padding: 14px;
}

.data-analysis-grid > .panel {
  height: 100%;
  min-height: 0;
  box-sizing: border-box;
  overflow: hidden;
  padding: 12px 14px;
}

.section-title {
  flex: 0 0 auto;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.section-title h3 {
  margin: 0;
  color: #172b4d;
  font-size: 15px;
  font-weight: 600;
}

.section-title span {
  color: #7d8da4;
  font-size: 12px;
}

/* 左侧筛选栏 */
.filter-panel {
  display: flex;
  flex-direction: column;
}

.filter-panel :deep(.el-menu) {
  border-right: none;
  background: transparent;
}

.filter-panel :deep(.el-menu-item) {
  height: 42px;
  margin-bottom: 4px;
  padding: 0 10px !important;
  border-radius: 7px;
  color: #334867;
  font-size: 13px;
  line-height: 42px;
}

.filter-panel :deep(.el-menu-item.is-active) {
  background: #eaf3ff;
  color: #2468d8;
  font-weight: 600;
}

.muted {
  color: #8494aa;
  font-size: 12px;
}

.filter-info,
.filter-note {
  padding: 11px;
  border: 1px solid #e0e8f3;
  border-radius: 8px;
  background: #f8fbff;
}

.filter-info {
  margin-top: auto;
}

.filter-info.warning {
  border-color: #f0d1d1;
  background: #fff7f7;
}

.filter-info-head {
  margin-bottom: 7px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #71839a;
  font-size: 12px;
}

.filter-info p,
.filter-note p {
  margin: 0;
  color: #344a68;
  font-size: 12px;
  line-height: 1.55;
}

.filter-note {
  margin-top: 9px;
}

.filter-note span {
  display: block;
  margin-bottom: 5px;
  color: #71839a;
  font-size: 12px;
}

/* 中部表格主区 */
.table-panel {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.toolbar {
  flex: 0 0 auto;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar .el-input {
  width: min(360px, 38%);
}

.column-selector {
  display: grid;
  gap: 4px;
}

.table-shell {
  flex: 1;
  min-height: 0;
}

.table-fill {
  width: 100%;
}

.table-panel :deep(.el-table th.el-table__cell) {
  height: 38px;
  padding: 5px 0;
  background: #f4f7fb;
  color: #50637c;
  font-size: 13px;
  font-weight: 600;
}

.table-panel :deep(.el-table td.el-table__cell) {
  padding: 6px 0;
  color: #223650;
  font-size: 13px;
}

.table-panel :deep(.el-table .cell) {
  line-height: 21px;
}

.table-panel :deep(.el-table__row.current-row > td.el-table__cell) {
  background: #edf4ff;
}

.table-pagination {
  flex: 0 0 auto;
  margin-top: 10px;
  justify-content: flex-start;
}

/* 右侧详情 */
.detail-panel {
  display: flex;
  flex-direction: column;
}

.detail-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 3px;
}

.detail-block {
  margin-bottom: 13px;
}

.detail-block h4 {
  margin: 0 0 8px;
  color: #263d5d;
  font-size: 13px;
  font-weight: 600;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.field-card {
  min-width: 0;
  padding: 8px 9px;
  border: 1px solid #e2eaf4;
  border-radius: 7px;
  background: #f7faff;
}

.field-card span {
  display: block;
  margin-bottom: 4px;
  color: #7689a2;
  font-size: 12px;
}

.field-card strong {
  display: block;
  overflow: hidden;
  color: #182f50;
  font-size: 13px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.field-full {
  grid-column: 1 / -1;
}

.usage-list {
  display: grid;
  gap: 7px;
}

.usage-row {
  padding: 7px 8px;
  display: grid;
  grid-template-columns: 54px minmax(0, 1fr);
  align-items: center;
  gap: 7px;
  border-radius: 7px;
  background: #f5f8fc;
}

.usage-tag {
  display: inline-flex;
  justify-content: center;
  padding: 3px 4px;
  border-radius: 4px;
  background: #e7f1ff;
  color: #2468d8;
  font-size: 11px;
}

.usage-tag.evaluation {
  background: #fdecec;
  color: #d64545;
}

.usage-row p {
  margin: 0;
  color: #4f647e;
  font-size: 12px;
  line-height: 1.4;
}

.detail-empty {
  flex: 1;
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 底部三块说明区 */
.data-analysis-grid {
  min-height: 0;
  display: grid;
  grid-template-columns: 1.05fr 1fr 1.1fr;
  gap: 12px;
}

.analysis-panel {
  display: flex;
  flex-direction: column;
}

.analysis-panel .section-title {
  margin-bottom: 7px;
}

.guide-list {
  display: grid;
  gap: 6px;
}

.guide-item {
  padding: 7px 10px;
  border: 1px solid #e2eaf4;
  border-radius: 7px;
  background: #f8fbff;
}

.guide-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.guide-title strong {
  color: #1d3453;
  font-size: 13px;
}

.guide-item p {
  margin: 4px 0 0;
  color: #556a84;
  font-size: 12px;
  line-height: 1.4;
}

.modality-metrics {
  margin-bottom: 8px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 9px;
}

.metric-card {
  padding: 8px 11px;
  border: 1px solid #e1e9f3;
  border-radius: 7px;
  background: #f8fbff;
}

.metric-card span {
  display: block;
  margin-bottom: 4px;
  color: #7b8da5;
  font-size: 12px;
}

.metric-card strong {
  color: #173e86;
  font-size: 22px;
}

.modality-role {
  flex: 1;
  padding: 7px 10px;
  border: 1px solid #e1e9f3;
  border-radius: 7px;
  background: #f8fbff;
}

.modality-role span {
  color: #7b8da5;
  font-size: 12px;
}

.modality-role p {
  margin: 5px 0 0;
  color: #344a67;
  font-size: 12px;
  line-height: 1.5;
}

.pipeline-list {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-rows: repeat(3, minmax(0, 1fr));
  gap: 6px;
}

.pipeline-step {
  min-height: 0;
  padding: 6px 10px;
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr) auto;
  align-items: center;
  gap: 9px;
  border: 1px solid #e1e9f3;
  border-radius: 7px;
  background: #f8fbff;
}

.pipeline-step.evaluation {
  border-color: #f0d1d1;
  background: #fff7f7;
}

.step-index {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #e7f1ff;
  color: #2468d8;
  font-size: 12px;
  font-weight: 700;
}

.pipeline-step.evaluation .step-index {
  background: #fdecec;
  color: #d64545;
}

.step-text strong {
  display: block;
  color: #1d3453;
  font-size: 13px;
}

.step-text small {
  color: #677b93;
  font-size: 12px;
}

/* 若外层主内容未显式设定高度，请在布局容器上补充：
   .app-main { height: calc(100dvh - 48px); min-height: 0; overflow: hidden; }
   本页使用 height:100% 继承可用内容高度，避免被顶部栏重复挤压。 */

@media (max-height: 820px) and (min-width: 1201px) {
  .data-summary-bar {
    flex-basis: 44px;
    margin: 8px 0 10px;
  }

  .data-content {
    grid-template-rows: minmax(300px, 1fr) 206px;
    gap: 8px;
  }

  .data-analysis-grid > .panel {
    padding: 10px 12px;
  }

  .pipeline-step {
    padding: 5px 8px;
  }
}

/* 中小屏：允许纵向滚动，避免强行挤压 */
@media (max-width: 1440px) {
  .data-workbench {
    grid-template-columns: 205px minmax(0, 1fr) 300px;
  }

  .data-summary-bar {
    padding: 0 12px;
  }
}

@media (max-width: 1200px) {
  .data-page {
    height: auto;
    overflow: visible;
  }

  .data-summary-bar {
    height: auto;
    min-height: 52px;
    flex-wrap: wrap;
    gap: 10px;
  }

  .data-content {
    display: block;
  }

  .data-workbench {
    height: 560px;
    grid-template-columns: 190px minmax(0, 1fr) 280px;
  }

  .data-analysis-grid {
    margin-top: 12px;
    grid-template-columns: 1fr;
  }

  .data-analysis-grid > .panel {
    min-height: 190px;
    margin-bottom: 12px;
  }
}
</style>
