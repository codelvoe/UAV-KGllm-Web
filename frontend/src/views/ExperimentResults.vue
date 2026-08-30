<template>
  <div class="page performance-page">
    <PageHeader
      title="性能评估与运行分析"
      subtitle="呈现多源融合策略在典型运行场景下的检测性能、虚警控制、稳定性和资源开销。"
      eyebrow="Performance Analytics"
    />

    <div class="kpi-row compact-kpis">
      <StatCard
        label="运行场景"
        :value="sceneCount"
        desc="完整、缺失、冲突、重复频谱"
      />
      <StatCard
        label="融合策略"
        :value="methodCount"
        desc="雷达、KG、启发式、大模型"
      />
      <StatCard label="最优 F1" :value="bestF1" desc="当前表格最大值" />
      <StatCard label="最高虚警率" :value="maxFar" desc="风险提示指标" />
      <StatCard label="风险场景" value="自然冲突" desc="KG+LLM 需要谨慎解释" />
      <StatCard
        label="关键事件数"
        :value="robustness.length"
        desc="模态缺失保持率"
      />
    </div>

    <div class="performance-layout">
      <div class="panel chart-panel">
        <div class="section-title">
          <h3>融合策略性能表现</h3>
          <span>F1 / 虚警率</span>
        </div>
        <div ref="compareChart" class="chart"></div>
      </div>

      <div class="panel conclusion-panel">
        <div class="section-title">
          <h3>关键结论</h3>
          <el-tag type="danger">自然冲突 = 风险场景</el-tag>
        </div>

        <div class="flow-list conclusion-list">
          <div class="analysis-step">
            <div class="step-index">1</div>
            <div>Radar-only 召回率高，但虚警率接近 1。</div>
            <el-tag type="warning">基线</el-tag>
          </div>
          <div class="analysis-step">
            <div class="step-index">2</div>
            <div>
              KG Fusion 显著压缩雷达候选池，但 loose 候选仍保留部分误报。
            </div>
            <el-tag>KG</el-tag>
          </div>
          <div class="analysis-step">
            <div class="step-index">3</div>
            <div>KG-Heuristic 在当前单目标数据上表现很强。</div>
            <el-tag type="success">规则</el-tag>
          </div>
          <div class="analysis-step">
            <div class="step-index">4</div>
            <div>自然冲突场景不能作为增益证据，应作为风险分析案例。</div>
            <el-tag type="danger">风险</el-tag>
          </div>
        </div>
      </div>

      <div class="panel detection-panel">
        <div class="section-title">
          <h3>检测性能明细</h3>
          <span>精确率 / 召回率 / F1 / 虚警率</span>
        </div>
        <div class="table-wrap">
          <el-table :data="detection" height="100%" :row-class-name="rowClassName">
            <el-table-column prop="场景" label="运行场景" min-width="110" />
            <el-table-column prop="方法" label="融合策略" min-width="130" />
            <el-table-column prop="Precision" label="精确率" min-width="100" />
            <el-table-column prop="Recall" label="召回率" min-width="100" />
            <el-table-column prop="F1" label="F1" min-width="100" />
            <el-table-column prop="FAR" label="虚警率" min-width="100" />
            <el-table-column label="分析标记" min-width="130">
              <template #default="{ row }">
                <el-tag v-if="isBest(row)" type="success">最优 F1</el-tag>
                <el-tag v-else-if="isConflictFailure(row)" type="danger">
                  风险场景
                </el-tag>
                <el-tag v-else>对照</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <div class="side-metrics">
        <div class="panel side-table-panel">
          <div class="section-title">
            <h3>资源开销</h3>
            <span>Token 成本 / 端到端延迟</span>
          </div>
          <div class="table-wrap">
            <el-table :data="efficiency" height="100%">
              <el-table-column prop="场景" label="运行场景" min-width="100" />
              <el-table-column prop="方法" label="融合策略" min-width="120" />
              <el-table-column prop="Token成本" label="Token" min-width="90" />
              <el-table-column prop="端到端延迟秒" label="延迟/s" min-width="90" />
            </el-table>
          </div>
        </div>

        <div class="panel side-table-panel">
          <div class="section-title">
            <h3>模态缺失稳定性</h3>
            <span>F1 保持率</span>
          </div>
          <div class="table-wrap">
            <el-table :data="robustness" height="100%">
              <el-table-column prop="缺失场景" label="缺失场景" min-width="100" />
              <el-table-column prop="KG Fusion F1" label="KG Fusion" min-width="105" />
              <el-table-column prop="KG-Heuristic F1" label="Heuristic" min-width="105" />
              <el-table-column prop="KG+LLM F1" label="KG+LLM" min-width="105" />
              <el-table-column prop="F1保持率" label="保持率" min-width="90" />
            </el-table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import * as echarts from "echarts";
import PageHeader from "../components/common/PageHeader.vue";
import StatCard from "../components/common/StatCard.vue";
import { getDetection, getEfficiency, getRobustness } from "../api/experiments";

const detection = ref([]);
const efficiency = ref([]);
const robustness = ref([]);
const compareChart = ref();
let chartInstance = null;

const sceneCount = computed(
  () => new Set(detection.value.map((row) => row["场景"])).size,
);
const methodCount = computed(
  () => new Set(detection.value.map((row) => row["方法"])).size,
);
const bestF1 = computed(() =>
  Math.max(...detection.value.map((row) => Number(row.F1 || 0)), 0).toFixed(4),
);
const maxFar = computed(() =>
  Math.max(...detection.value.map((row) => Number(row.FAR || 0)), 0).toFixed(4),
);

function isBest(row) {
  return Number(row.F1 || 0) === Number(bestF1.value);
}

function isConflictFailure(row) {
  return String(row["场景"]).includes("自然") && row["方法"] === "KG+LLM Agent";
}

function rowClassName({ row }) {
  return isConflictFailure(row) ? "danger-row" : "";
}

function draw() {
  if (!compareChart.value) return;
  if (!chartInstance) chartInstance = echarts.init(compareChart.value);

  const llmRows = detection.value.filter(
    (row) => row["方法"] === "KG+LLM Agent",
  );

  chartInstance.setOption(
    {
      tooltip: { trigger: "axis" },
      legend: { top: 0, data: ["F1", "虚警率"] },
      grid: { top: 38, left: 42, right: 24, bottom: 44 },
      xAxis: {
        type: "category",
        data: llmRows.map((row) => row["场景"]),
        axisLabel: {
          rotate: 0,
          interval: 0,
          fontSize: 11,
          overflow: "truncate",
          width: 72,
        },
      },
      yAxis: { type: "value", max: 1 },
      series: [
        {
          name: "F1",
          type: "bar",
          data: llmRows.map((row) => Number(row.F1 || 0)),
          itemStyle: { color: "#18a058" },
          barMaxWidth: 54,
        },
        {
          name: "虚警率",
          type: "line",
          data: llmRows.map((row) => Number(row.FAR || 0)),
          itemStyle: { color: "#d64545" },
          smooth: true,
          symbolSize: 6,
        },
      ],
    },
    true,
  );

  setTimeout(() => chartInstance?.resize(), 30);
}

function resizeChart() {
  chartInstance?.resize();
}

onMounted(async () => {
  detection.value = (await getDetection()).data;
  efficiency.value = (await getEfficiency()).data;
  robustness.value = (await getRobustness()).data;
  await nextTick();
  draw();
  window.addEventListener("resize", resizeChart);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", resizeChart);
  chartInstance?.dispose();
});
</script>

<style scoped>
.performance-page {
  height: 100%;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding-right: 10px;
  box-sizing: border-box;
}

.compact-kpis {
  flex: 0 0 96px;
  margin: 8px 0 12px;
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 10px;
  overflow: visible;
  align-items: stretch;
}

.compact-kpis :deep(.panel),
.compact-kpis :deep(.stat-card) {
  height: 88px;
  min-height: 88px;
  box-sizing: border-box;
  overflow: hidden;
}

.performance-layout {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 420px;
  grid-template-rows: 34% minmax(0, 66%);
  grid-template-areas:
    "chart conclusion"
    "detection side";
  gap: 12px;
  overflow: hidden;
}

.chart-panel {
  grid-area: chart;
}

.conclusion-panel {
  grid-area: conclusion;
}

.detection-panel {
  grid-area: detection;
}

.side-metrics {
  grid-area: side;
  min-height: 0;
  display: grid;
  grid-template-rows: minmax(0, 1fr) minmax(0, 1fr);
  gap: 12px;
  overflow: hidden;
}

.chart-panel,
.conclusion-panel,
.detection-panel,
.side-table-panel {
  min-height: 0;
  min-width: 0;
  overflow: hidden;
  padding: 12px;
  box-sizing: border-box;
}

.chart-panel,
.detection-panel,
.side-table-panel {
  display: flex;
  flex-direction: column;
}

.chart {
  flex: 1;
  min-height: 0;
  width: 100%;
}

.table-wrap {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.table-wrap :deep(.el-table) {
  width: 100% !important;
}

.conclusion-list {
  height: calc(100% - 42px);
  min-height: 0;
  overflow-y: auto;
  gap: 8px;
}

.conclusion-list .analysis-step {
  min-height: 42px;
  padding: 8px 10px;
}

:deep(.danger-row) {
  --el-table-tr-bg-color: #fff2f0;
}

:deep(.el-table .cell) {
  line-height: 1.35;
}

@media (max-width: 1500px) {
  .performance-layout {
    grid-template-columns: minmax(0, 1fr) 380px;
  }

  .compact-kpis {
    flex-basis: 92px;
  }

  .compact-kpis :deep(.panel),
  .compact-kpis :deep(.stat-card) {
    height: 84px;
    min-height: 84px;
  }
}

@media (max-height: 820px) {
  .compact-kpis {
    flex-basis: 88px;
    margin-bottom: 10px;
  }

  .compact-kpis :deep(.panel),
  .compact-kpis :deep(.stat-card) {
    height: 80px;
    min-height: 80px;
  }

  .performance-layout {
    grid-template-rows: 33% minmax(0, 67%);
    gap: 10px;
  }

  .chart-panel,
  .conclusion-panel,
  .detection-panel,
  .side-table-panel {
    padding: 10px;
  }

  .conclusion-list .analysis-step {
    min-height: 38px;
    padding: 7px 9px;
  }
}

@media (max-width: 1280px) {
  .performance-page {
    height: auto;
    overflow: visible;
  }

  .compact-kpis {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    height: auto;
    flex-basis: auto;
  }

  .performance-layout {
    display: block;
  }

  .chart-panel,
  .conclusion-panel,
  .detection-panel,
  .side-table-panel {
    margin-bottom: 12px;
    min-height: 260px;
  }

  .chart {
    height: 260px;
  }
}
</style>
