<template>
  <div class="page candidate-page">
    <PageHeader
      title="KG 融合候选分析工作台"
      subtitle="围绕候选池生成、排序、冲突解释和得分组成展开，突出知识图谱融合的核心算法输出。"
      eyebrow="KG Candidate Analysis"
    />

    <div class="kpi-row compact-kpis">
      <StatCard label="当前场景" :value="scenario" desc="可切换六类实验场景" />
      <StatCard label="候选总数" :value="rows.length" desc="进入 KG 候选池的目标数" />
      <StatCard label="冲突候选" :value="conflictCount" desc="存在语义或方位冲突" />
      <StatCard label="最高融合分数" :value="bestScore" desc="当前候选池最高 KG 分数" />
    </div>

    <div class="candidate-workbench">
      <!-- 左侧：场景切换与候选列表 -->
      <div class="panel candidate-list-panel">
        <div class="section-title">
          <h3>场景与候选池</h3>
          <span>Top-10：{{ displayRows.length }} / {{ rows.length }}</span>
        </div>

        <div class="toolbar">
          <el-select v-model="scenario" style="width: 100%" @change="load">
            <el-option
              v-for="scene in scenes"
              :key="scene"
              :label="scene"
              :value="scene"
            />
          </el-select>
          <el-button type="primary" style="width: 100%" @click="load">
            刷新候选
          </el-button>
        </div>

        <div class="candidate-table-shell">
          <el-table
            :data="displayRows"
            height="100%"
            highlight-current-row
            :row-class-name="rowClassName"
            @row-click="select"
          >
            <el-table-column fixed prop="candidate_id" label="候选" width="64" />
            <el-table-column prop="rank" label="#" width="42" />
            <el-table-column label="KG分数" width="76">
              <template #default="{ row }">
                {{ formatScore(row.kg_score) }}
              </template>
            </el-table-column>
            <el-table-column label="状态" min-width="78">
              <template #default="{ row }">
                <el-tag
                  :type="row.conflict_flag ? 'danger' : 'success'"
                  size="small"
                  effect="plain"
                >
                  {{ row.conflict_flag ? "冲突" : "一致" }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div v-if="scenario === '自然冲突'" class="pool-note">
          <strong>诊断重点</strong>
          <p>C02 为真实候选并进入 Top-K，但被 LLM reject；C01 为错误保留的竞争候选。</p>
        </div>
      </div>

      <!-- 中央：候选详情与评分拆解，不放流程图 -->
      <div class="panel candidate-detail-panel">
        <div class="section-title">
          <h3>候选详情与评分拆解</h3>
          <div class="title-tags" v-if="current.candidate_id">
            <el-tag :type="current.conflict_flag ? 'danger' : 'success'" size="small">
              {{ current.candidate_id }}
            </el-tag>
            <el-tag size="small" effect="plain">
              Rank #{{ current.rank ?? "-" }}
            </el-tag>
          </div>
        </div>

        <template v-if="current.candidate_id">
          <div class="detail-block">
            <div class="subsection-title">轨迹关联</div>
            <div class="detail-grid">
              <InfoItem label="候选来源" :value="current.candidate_source" />
              <InfoItem label="当前裁决" :value="current.decision_status" />
              <InfoItem label="雷达轨迹编号" :value="current.radar_track_id" />
              <InfoItem label="频谱轨迹编号" :value="current.spectrum_track_id" />
            </div>
          </div>

          <div class="detail-block">
            <div class="subsection-title">融合证据</div>
            <div class="detail-grid evidence-grid">
              <InfoItem label="时间重叠秒数" :value="current.time_overlap" />
              <InfoItem label="方位角差" :value="current.azimuth_diff" suffix="°" />
              <InfoItem label="知识图谱分数" :value="formatScore(current.kg_score)" />
              <InfoItem label="候选排序" :value="current.rank" />
            </div>
          </div>

          <div class="score-section">
            <div class="section-title score-title">
              <h3>KG 得分组成</h3>
              <span>时间、方位、语义、信号与运动特征</span>
            </div>
            <div ref="scoreChart" class="chart score-chart"></div>
          </div>
        </template>

        <div v-else class="empty-hint fill-empty">请选择左侧候选查看详情</div>
      </div>

      <!-- 右侧：排名图与候选解释 -->
      <div class="right-panels">
        <div class="panel rank-panel">
          <div class="section-title">
            <h3>候选排名分布</h3>
            <span>KG 融合分数</span>
          </div>
          <div ref="rankChart" class="chart rank-chart"></div>
        </div>

        <div class="panel explanation-panel">
          <div class="section-title">
            <h3>当前候选解释</h3>
            <span>融合分析摘要</span>
          </div>

          <div class="summary-status" v-if="current.candidate_id">
            <div class="summary-row">
              <span>候选编号</span>
              <strong>{{ current.candidate_id }}</strong>
            </div>
            <div class="summary-row">
              <span>KG 排名 / 分数</span>
              <strong>#{{ current.rank ?? "-" }} / {{ formatScore(current.kg_score) }}</strong>
            </div>
            <div class="summary-row">
              <span>冲突状态</span>
              <el-tag
                :type="current.conflict_flag ? 'danger' : 'success'"
                size="small"
                effect="light"
              >
                {{ current.conflict_flag ? "存在冲突" : "证据一致" }}
              </el-tag>
            </div>
          </div>

          <div class="explanation-text">
            {{ explanation.summary || defaultExplanation }}
          </div>

          <div v-if="scenario === '自然冲突'" class="diagnosis-note">
            <div class="note-title">自然冲突分析提示</div>
            <p>
              此视图用于检查 radar 与 spectrum 证据冲突下的候选排序与裁决结果。
              候选池优先呈现前 10 个候选，便于比较真实候选与竞争候选。
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  computed,
  defineComponent,
  h,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
} from "vue";
import * as echarts from "echarts";
import PageHeader from "../components/common/PageHeader.vue";
import StatCard from "../components/common/StatCard.vue";
import { getCandidate, getCandidates, getScoreBreakdown } from "../api/fusion";
import request from "../api/request";

const InfoItem = defineComponent({
  props: {
    label: String,
    value: [String, Number, Boolean],
    suffix: { type: String, default: "" },
  },
  setup(props) {
    return () =>
      h("div", { class: "detail-item" }, [
        h("div", { class: "detail-label" }, props.label),
        h(
          "div",
          { class: "detail-value", title: String(props.value ?? "-") },
          `${props.value ?? "-"}${
            props.value !== undefined && props.value !== null ? props.suffix : ""
          }`,
        ),
      ]);
  },
});

const scenes = [
  "完整模态",
  "缺失频谱",
  "缺失视觉",
  "仅雷达",
  "自然冲突",
  "重复频谱",
];

/**
 * Natural-conflict 诊断实验已输出的 Top-10 候选。
 * 本页只在“自然冲突”场景使用该已完成诊断结果，保证左侧完整呈现 C01-C10；
 * 其他场景仍读取现有后端接口。
 */
const naturalConflictTop10 = [
  {
    candidate_id: "C01",
    candidate_source: "radar-spectrum",
    radar_track_id: "trk_track_radar_343",
    radar_semantic: "unknown",
    spectrum_track_id: "trk_track_spectrum_79490",
    spectrum_semantic: "drone",
    azimuth_diff: 4.3338,
    time_overlap: 1.0,
    kg_score: 0.8985,
    rank: 1,
    conflict_flag: true,
    decision_status: "confirm",
    final_kept: true,
    explanation_summary: "C01 为竞争误报候选：雷达语义为 unknown，频谱支持 drone，最终被 LLM 错误保留。"
  },
  {
    candidate_id: "C02",
    candidate_source: "radar-spectrum",
    radar_track_id: "trk_track_radar_278",
    radar_semantic: "bird",
    spectrum_track_id: "trk_track_spectrum_79490",
    spectrum_semantic: "drone",
    azimuth_diff: 3.3621,
    time_overlap: 1.0,
    kg_score: 0.8873,
    rank: 2,
    conflict_flag: true,
    decision_status: "reject",
    final_kept: false,
    explanation_summary: "C02 为真实候选：已进入 KG Top-K，但在 LLM 裁决阶段被 reject。"
  },
  {
    candidate_id: "C03",
    candidate_source: "radar-spectrum",
    radar_track_id: "trk_track_radar_348",
    radar_semantic: "unknown",
    spectrum_track_id: "trk_track_spectrum_79490",
    spectrum_semantic: "drone",
    azimuth_diff: 6.0655,
    time_overlap: 1.0,
    kg_score: 0.8590,
    rank: 3,
    conflict_flag: true,
    decision_status: "uncertain",
    final_kept: false,
    explanation_summary: "C03 为非真值竞争候选，LLM 裁决为 uncertain。"
  },
  {
    candidate_id: "C04",
    candidate_source: "radar-spectrum",
    radar_track_id: "trk_track_radar_243",
    radar_semantic: "bird",
    spectrum_track_id: "trk_track_spectrum_79490",
    spectrum_semantic: "drone",
    azimuth_diff: 10.9118,
    time_overlap: 1.0,
    kg_score: 0.8423,
    rank: 4,
    conflict_flag: true,
    decision_status: "reject",
    final_kept: false,
    explanation_summary: "C04 为非真值竞争候选，雷达 bird 与频谱 drone 存在语义冲突。"
  },
  {
    candidate_id: "C05",
    candidate_source: "radar-spectrum",
    radar_track_id: "trk_track_radar_337",
    radar_semantic: "unknown",
    spectrum_track_id: "trk_track_spectrum_79490",
    spectrum_semantic: "drone",
    azimuth_diff: 12.5681,
    time_overlap: 1.0,
    kg_score: 0.8334,
    rank: 5,
    conflict_flag: true,
    decision_status: "uncertain",
    final_kept: false,
    explanation_summary: "C05 为非真值竞争候选，LLM 裁决为 uncertain。"
  },
  {
    candidate_id: "C06",
    candidate_source: "radar-spectrum",
    radar_track_id: "trk_track_radar_313",
    radar_semantic: "bird",
    spectrum_track_id: "trk_track_spectrum_81397",
    spectrum_semantic: "drone",
    azimuth_diff: 1.0607,
    time_overlap: 1.0,
    kg_score: 0.8850,
    rank: 6,
    conflict_flag: true,
    decision_status: "reject",
    final_kept: false,
    explanation_summary: "C06 使用第二条频谱轨迹，为非真值竞争候选。"
  },
  {
    candidate_id: "C07",
    candidate_source: "radar-spectrum",
    radar_track_id: "trk_track_radar_318",
    radar_semantic: "bird",
    spectrum_track_id: "trk_track_spectrum_81397",
    spectrum_semantic: "drone",
    azimuth_diff: 2.1769,
    time_overlap: 1.0,
    kg_score: 0.8760,
    rank: 7,
    conflict_flag: true,
    decision_status: "reject",
    final_kept: false,
    explanation_summary: "C07 为非真值竞争候选，LLM 裁决为 reject。"
  },
  {
    candidate_id: "C08",
    candidate_source: "radar-spectrum",
    radar_track_id: "trk_track_radar_306",
    radar_semantic: "bird",
    spectrum_track_id: "trk_track_spectrum_81397",
    spectrum_semantic: "drone",
    azimuth_diff: 3.6698,
    time_overlap: 1.0,
    kg_score: 0.8647,
    rank: 8,
    conflict_flag: true,
    decision_status: "reject",
    final_kept: false,
    explanation_summary: "C08 为非真值竞争候选，LLM 裁决为 reject。"
  },
  {
    candidate_id: "C09",
    candidate_source: "radar-spectrum",
    radar_track_id: "trk_track_radar_352",
    radar_semantic: "unknown",
    spectrum_track_id: "trk_track_spectrum_81397",
    spectrum_semantic: "drone",
    azimuth_diff: 2.0655,
    time_overlap: 1.0,
    kg_score: 0.8603,
    rank: 9,
    conflict_flag: true,
    decision_status: "uncertain",
    final_kept: false,
    explanation_summary: "C09 为非真值竞争候选，LLM 裁决为 uncertain。"
  },
  {
    candidate_id: "C10",
    candidate_source: "radar-spectrum",
    radar_track_id: "trk_track_radar_119",
    radar_semantic: "bird",
    spectrum_track_id: "trk_track_spectrum_81397",
    spectrum_semantic: "drone",
    azimuth_diff: 4.9290,
    time_overlap: 1.0,
    kg_score: 0.8593,
    rank: 10,
    conflict_flag: true,
    decision_status: "reject",
    final_kept: false,
    explanation_summary: "C10 为非真值竞争候选，LLM 裁决为 reject。"
  }
];

/* 默认进入自然冲突场景；该场景用于查看前 10 个冲突诊断候选 */
const scenario = ref("自然冲突");
const rows = ref([]);
const current = ref({});
const explanation = ref({});
const scoreChart = ref(null);
const rankChart = ref(null);

let scoreChartInstance = null;
let rankChartInstance = null;

const displayRows = computed(() =>
  [...rows.value]
    .sort((a, b) => Number(a.rank ?? 999) - Number(b.rank ?? 999))
    .slice(0, 10),
);

const conflictCount = computed(
  () => rows.value.filter((row) => row.conflict_flag).length,
);

const bestScore = computed(() =>
  Math.max(...rows.value.map((row) => Number(row.kg_score || 0)), 0).toFixed(3),
);

const defaultExplanation = computed(() => {
  if (!current.value.candidate_id) {
    return "选择候选后显示知识图谱融合证据解释。";
  }
  if (current.value.conflict_flag) {
    return "当前候选存在跨模态证据冲突，需结合时间重叠、方位一致性、语义支持与信号质量综合判断。";
  }
  return "当前候选的多模态证据整体一致，可结合 KG 融合得分和排序结果进一步分析。";
});

const scoreNameMap = {
  time_score: "时间一致",
  azimuth_score: "方位一致",
  semantic_score: "语义一致",
  signal_score: "信号质量",
  radar_score: "雷达可信",
  motion_score: "运动合理",
};

async function load() {
  current.value = {};
  explanation.value = {};

  if (scenario.value === "自然冲突") {
    /* 使用已完成诊断的完整 Top-10 结果，不受当前接口仅返回 2 条的限制 */
    rows.value = naturalConflictTop10.map((item) => ({ ...item }));
  } else {
    const response = await getCandidates({ scenario: scenario.value });
    rows.value = Array.isArray(response.data) ? response.data : response.data?.items || [];
  }

  await nextTick();
  drawRanks();

  if (displayRows.value[0]) {
    await select(displayRows.value[0]);
  } else {
    clearScoreChart();
  }
}

async function select(row) {
  current.value = row;
  explanation.value = {
    summary: row.explanation_summary || ""
  };

  let breakdown = {};

  if (scenario.value !== "自然冲突") {
    try {
      const detailResponse = await getCandidate(row.candidate_id);
      current.value = detailResponse.data || row;
    } catch (_error) {
      current.value = row;
    }

    try {
      const explanationResponse = await request.get(`/fusion/explain/${row.candidate_id}`);
      explanation.value = explanationResponse.data || explanation.value;
    } catch (_error) {
      explanation.value = { summary: row.explanation_summary || "" };
    }
  }

  try {
    const breakdownResponse = await getScoreBreakdown(row.candidate_id);
    breakdown = breakdownResponse.data || {};
  } catch (_error) {
    /*
     * 若当前后端尚未存储 C01-C10 的分项得分，则保留空图提示；
     * 不根据总分伪造各评分维度。
     */
    breakdown = {};
  }

  await nextTick();
  drawScore(breakdown);
  drawRanks();
}

function drawScore(breakdown) {
  if (!scoreChart.value) return;
  if (!scoreChartInstance) {
    scoreChartInstance = echarts.init(scoreChart.value);
  }

  const keys = Object.keys(breakdown || {}).filter(
    (key) => key !== "kg_score" && scoreNameMap[key],
  );
  const fallbackKeys = Object.keys(scoreNameMap);
  const usedKeys = keys.length ? keys : fallbackKeys;
  const values = usedKeys.map((key) => Number(breakdown?.[key] || 0));

  scoreChartInstance.setOption(
    {
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
      grid: { top: 8, left: 90, right: 45, bottom: 20 },
      xAxis: {
        type: "value",
        max: 1,
        axisLabel: { fontSize: 11, color: "#73849b" },
        splitLine: { lineStyle: { color: "#edf2f8" } },
      },
      yAxis: {
        type: "category",
        inverse: true,
        data: usedKeys.map((key) => scoreNameMap[key]),
        axisTick: { show: false },
        axisLine: { show: false },
        axisLabel: { fontSize: 12, color: "#485e79" },
      },
      series: [
        {
          type: "bar",
          barWidth: 15,
          data: values,
          itemStyle: {
            color: "#3477dc",
            borderRadius: [0, 4, 4, 0],
          },
          label: {
            show: true,
            position: "right",
            color: "#4c617c",
            fontSize: 11,
            formatter: ({ value }) => Number(value).toFixed(3),
          },
        },
      ],
    },
    true,
  );
}

function drawRanks() {
  if (!rankChart.value) return;
  if (!rankChartInstance) {
    rankChartInstance = echarts.init(rankChart.value);
  }

  const data = displayRows.value;
  rankChartInstance.setOption(
    {
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
      grid: { top: 8, left: 42, right: 42, bottom: 22, containLabel: true },
      xAxis: {
        type: "value",
        max: 1,
        axisLabel: { fontSize: 10, color: "#72859d" },
        splitLine: { lineStyle: { color: "#edf2f8" } },
      },
      yAxis: {
        type: "category",
        inverse: true,
        data: data.map((row) => row.candidate_id),
        axisTick: { show: false },
        axisLine: { show: false },
        axisLabel: { color: "#485e79", fontSize: 11 },
      },
      series: [
        {
          type: "bar",
          barWidth: data.length > 6 ? 12 : 17,
          data: data.map((row) => ({
            value: Number(row.kg_score || 0),
            itemStyle: {
              color:
                row.candidate_id === current.value.candidate_id
                  ? "#2468d8"
                  : row.conflict_flag
                    ? "#e88a50"
                    : "#85a7df",
              borderRadius: [0, 4, 4, 0],
            },
          })),
          label: {
            show: true,
            position: "right",
            fontSize: 10,
            color: "#4f657e",
            formatter: ({ value }) => Number(value).toFixed(3),
          },
        },
      ],
    },
    true,
  );
}

function clearScoreChart() {
  scoreChartInstance?.clear();
}

function rowClassName({ row }) {
  if (row.candidate_id === current.value.candidate_id) return "selected-row";
  return row.conflict_flag ? "conflict-row" : "";
}

function formatScore(value) {
  if (value === null || value === undefined || value === "") return "-";
  const number = Number(value);
  return Number.isNaN(number) ? String(value) : number.toFixed(3);
}

function resizeCharts() {
  scoreChartInstance?.resize();
  rankChartInstance?.resize();
}

onMounted(async () => {
  window.addEventListener("resize", resizeCharts);
  await load();
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", resizeCharts);
  scoreChartInstance?.dispose();
  rankChartInstance?.dispose();
});
</script>

<style scoped>
.candidate-page {
  height: 100%;
  min-height: 0;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding-bottom: 10px;
}

.compact-kpis {
  flex: 0 0 76px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 250px));
  gap: 12px;
  margin: 10px 0 12px;
}

.candidate-workbench {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr) 330px;
  gap: 12px;
}

.panel {
  min-height: 0;
  box-sizing: border-box;
}

.section-title {
  flex: 0 0 auto;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.section-title h3 {
  margin: 0;
  color: #162e4e;
  font-size: 15px;
  font-weight: 600;
}

.section-title span {
  color: #7b8ea5;
  font-size: 12px;
}

.title-tags {
  display: flex;
  gap: 6px;
}

.candidate-list-panel {
  height: 100%;
  padding: 14px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.toolbar {
  flex: 0 0 auto;
  display: grid;
  gap: 8px;
  margin-bottom: 10px;
}

.candidate-table-shell {
  flex: 1;
  min-height: 0;
}

.candidate-list-panel :deep(.el-table th.el-table__cell) {
  height: 36px;
  padding: 5px 0;
  background: #f4f7fb;
  color: #50647d;
  font-size: 12px;
}

.candidate-list-panel :deep(.el-table td.el-table__cell) {
  padding: 6px 0;
  color: #253b5a;
  font-size: 12px;
}

.candidate-list-panel :deep(.el-table .selected-row td.el-table__cell) {
  background: #edf4ff !important;
}

.candidate-list-panel :deep(.el-table .conflict-row td.el-table__cell) {
  background: #fff9f5;
}

.pool-note {
  flex: 0 0 auto;
  margin-top: 10px;
  padding: 10px;
  border: 1px solid #f0d7c8;
  border-radius: 7px;
  background: #fff8f4;
}

.pool-note strong {
  color: #ba6538;
  font-size: 12px;
}

.pool-note p {
  margin: 5px 0 0;
  color: #53687f;
  font-size: 12px;
  line-height: 1.5;
}

.candidate-detail-panel {
  height: 100%;
  padding: 14px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.detail-block {
  flex: 0 0 auto;
  margin-bottom: 12px;
}

.subsection-title {
  margin-bottom: 8px;
  color: #253b59;
  font-size: 13px;
  font-weight: 600;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 9px;
}

.detail-item {
  min-width: 0;
  padding: 10px 12px;
  border: 1px solid #e1eaf4;
  border-radius: 7px;
  background: #f8fbff;
}

.detail-label {
  margin-bottom: 5px;
  color: #7588a1;
  font-size: 12px;
}

.detail-value {
  overflow: hidden;
  color: #172f51;
  font-size: 13px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.score-section {
  flex: 1;
  min-height: 0;
  margin-top: 3px;
  padding-top: 12px;
  border-top: 1px solid #e6edf5;
  display: flex;
  flex-direction: column;
}

.score-title {
  margin-bottom: 5px;
}

.score-chart {
  flex: 1;
  min-height: 220px;
}

.fill-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.right-panels {
  height: 100%;
  min-height: 0;
  display: grid;
  grid-template-rows: minmax(260px, 1.05fr) minmax(230px, 0.95fr);
  gap: 12px;
}

.rank-panel,
.explanation-panel {
  padding: 14px;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.rank-chart {
  flex: 1;
  min-height: 0;
}

.summary-status {
  flex: 0 0 auto;
  display: grid;
  gap: 7px;
  margin-bottom: 10px;
}

.summary-row {
  min-height: 36px;
  padding: 7px 9px;
  border-radius: 6px;
  background: #f6f9fd;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 7px;
}

.summary-row span {
  color: #7487a0;
  font-size: 12px;
}

.summary-row strong {
  color: #1b3454;
  font-size: 12px;
}

.explanation-text {
  padding: 10px;
  border: 1px solid #e1eaf4;
  border-radius: 7px;
  background: #f8fbff;
  color: #405670;
  font-size: 12px;
  line-height: 1.6;
}

.diagnosis-note {
  margin-top: 10px;
  padding: 10px;
  border: 1px solid #f0d7c8;
  border-radius: 7px;
  background: #fff8f4;
}

.note-title {
  margin-bottom: 5px;
  color: #bd6739;
  font-size: 12px;
  font-weight: 600;
}

.diagnosis-note p {
  margin: 0;
  color: #546980;
  font-size: 12px;
  line-height: 1.55;
}

@media (max-width: 1400px) {
  .candidate-workbench {
    grid-template-columns: 278px minmax(0, 1fr) 305px;
  }
}

@media (max-width: 1100px) {
  .candidate-page {
    height: auto;
    overflow: visible;
  }

  .compact-kpis {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .candidate-workbench {
    display: block;
  }

  .candidate-list-panel,
  .candidate-detail-panel,
  .right-panels {
    min-height: 470px;
    margin-bottom: 12px;
  }
}
</style>
