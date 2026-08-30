<template>
  <div class="page track-page">
    <PageHeader
      title="轨迹证据管理工作台"
      subtitle="管理多源轨迹摘要、空间位置、运动特征、信号质量和候选关联，为目标融合与风险判断提供轨迹级证据。"
      eyebrow="Track Evidence Layer"
    />

    <div class="track-workbench">
      <div class="left-workspace">
        <div class="panel map-panel">
          <div class="section-title">
            <h3>局部相对坐标视图</h3>
            <span>x = distance * sin(azimuth)，y = distance * cos(azimuth)</span>
          </div>
          <div ref="trackMapChart" class="track-map"></div>
        </div>

        <div class="panel table-panel">
          <div class="section-title">
            <h3>轨迹摘要表</h3>
            <span>点击轨迹后，地图、证据摘要和右侧详情同步更新</span>
          </div>

          <div class="toolbar compact-toolbar">
            <el-select v-model="source" @change="load" style="width: 132px">
              <el-option label="全部模态" value="" />
              <el-option label="雷达" value="radar" />
              <el-option label="频谱" value="spectrum" />
              <el-option label="视觉识别" value="recognize" />
              <el-option label="隐藏标签" value="decrypt" />
            </el-select>

            <el-select v-model="targetType" @change="load" style="width: 132px">
              <el-option label="全部类型" value="" />
              <el-option label="无人机" value="drone" />
              <el-option label="鸟类" value="bird" />
              <el-option label="未知" value="unknown" />
            </el-select>

            <el-tag>{{ tracks.length }} 条轨迹</el-tag>
            <el-tag v-if="current.track_id" type="success">
              已选中：{{ shortTrackId(current.track_id) }}
            </el-tag>
          </div>

          <div class="table-body-grid">
            <div class="table-shell">
              <el-table
                :data="tracks"
                height="100%"
                highlight-current-row
                :row-class-name="rowClassName"
                @row-click="select"
              >
                <el-table-column
                  fixed
                  prop="track_id"
                  label="轨迹编号"
                  min-width="185"
                  show-overflow-tooltip
                />
                <el-table-column prop="source" label="来源" min-width="78" />
                <el-table-column prop="target_type" label="类别" min-width="76" />
                <el-table-column prop="model" label="型号" min-width="90" show-overflow-tooltip />
                <el-table-column prop="point_count" label="点数" min-width="66" />
                <el-table-column prop="azimuth_mean" label="方位" min-width="82" />
                <el-table-column prop="distance_mean" label="距离" min-width="86" />
                <el-table-column prop="altitude_mean" label="高度" min-width="86" />
                <el-table-column prop="speed_mean" label="速度" min-width="82" />
                <el-table-column prop="snr_mean" label="SNR" min-width="76" />
              </el-table>
            </div>

            <div class="evidence-side">
              <div class="evidence-head">
                <div>
                  <h4>选中轨迹证据摘要</h4>
                  <p>用于解释该轨迹如何进入候选生成与融合判断。</p>
                </div>
                <el-tag :type="candidateLink ? 'warning' : 'info'">
                  {{ candidateLink ? "候选关联" : "普通轨迹" }}
                </el-tag>
              </div>

              <div class="selected-track-card">
                <strong>{{ current.track_id || "未选择轨迹" }}</strong>
                <span>{{ current.source ? modalityName(current.source) : "-" }}</span>
              </div>

              <div class="evidence-metrics">
                <MetricBox label="点数" :value="current.point_count" />
                <MetricBox label="平均速度" :value="formatNum(current.speed_mean)" suffix=" m/s" />
                <MetricBox label="平均距离" :value="formatNum(current.distance_mean)" suffix=" m" />
                <MetricBox label="信噪比" :value="formatNum(current.snr_mean)" />
              </div>

              <div class="evidence-role">
                <h5>轨迹作用</h5>
                <p>{{ compactRoleText }}</p>
              </div>

              <div class="evidence-steps">
                <div class="evidence-step">
                  <span>1</span>
                  <div>
                    <strong>轨迹级摘要</strong>
                    <p>聚合方位、距离、高度、速度和信号质量。</p>
                  </div>
                </div>
                <div class="evidence-step">
                  <span>2</span>
                  <div>
                    <strong>空间匹配依据</strong>
                    <p>与频谱方位、视觉识别或隐藏标签建立候选关联。</p>
                  </div>
                </div>
                <div class="evidence-step">
                  <span>3</span>
                  <div>
                    <strong>融合候选输入</strong>
                    <p>作为 KG 候选池排序和冲突判断的轨迹证据。</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="right-detail">
        <div class="panel summary-panel">
          <div class="section-title">
            <h3>轨迹摘要卡</h3>
            <el-tag v-if="current.track_id" :type="candidateLink ? 'warning' : 'info'">
              {{ candidateLink ? "关联候选" : "普通轨迹" }}
            </el-tag>
          </div>

          <div class="summary-scroll">
            <div class="summary-card">
              <strong>{{ current.track_id || "未选择轨迹" }}</strong>
              <p>{{ trackRoleText }}</p>
            </div>

            <div class="summary-grid">
              <InfoItem label="来源模态" :value="modalityName(current.source)" />
              <InfoItem label="目标类别" :value="current.target_type" />
              <InfoItem label="轨迹点数" :value="current.point_count" />
              <InfoItem label="机型/型号" :value="current.model || '-'" />
              <InfoItem label="平均方位" :value="formatNum(current.azimuth_mean)" suffix="°" />
              <InfoItem label="平均距离" :value="formatNum(current.distance_mean)" suffix=" m" />
              <InfoItem label="平均高度" :value="formatNum(current.altitude_mean)" suffix=" m" />
              <InfoItem label="平均速度" :value="formatNum(current.speed_mean)" suffix=" m/s" />
              <InfoItem label="信号强度" :value="formatNum(current.signal_mean)" />
              <InfoItem label="置信度" :value="formatNum(current.confidence_mean)" />
              <InfoItem label="SNR" :value="formatNum(current.snr_mean)" />
              <InfoItem label="候选状态" :value="candidateLink ? '存在候选关联' : '暂无候选关联'" />
            </div>

            <div class="summary-note">
              <h4>证据说明</h4>
              <p>{{ compactRoleText }}</p>
            </div>
          </div>
        </div>

        <div class="panel feature-panel">
          <div class="section-title">
            <h3>轨迹特征概览图</h3>
            <span>空间 / 运动 / 信号</span>
          </div>
          <div ref="featureChart" class="feature-chart"></div>
        </div>

        <div class="panel quality-panel">
          <div class="section-title">
            <h3>轨迹质量解释</h3>
            <span>候选生成中的证据意义</span>
          </div>

          <div class="flow-list compact-flow">
            <div v-for="item in qualityItems" :key="item.label" class="analysis-step">
              <div class="step-index">{{ item.index }}</div>
              <div>
                <strong>{{ item.label }}</strong>
                <p>{{ item.text }}</p>
              </div>
              <el-tag :type="item.type">{{ item.level }}</el-tag>
            </div>
          </div>
        </div>

        <div class="panel timeline-panel">
          <div class="section-title">
            <h3>轨迹时间线</h3>
            <span>跨模态时间重叠</span>
          </div>

          <el-timeline>
            <el-timeline-item
              v-for="item in timeline"
              :key="item.event"
              :timestamp="item.time"
            >
              {{ eventLabel(item.event) }}
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import * as echarts from "echarts";
import { computed, defineComponent, h, nextTick, onMounted, onBeforeUnmount, ref } from "vue";
import PageHeader from "../components/common/PageHeader.vue";
import { getTrackFeatures, getTracks } from "../api/tracks";

const InfoItem = defineComponent({
  props: {
    label: String,
    value: [String, Number],
    suffix: { type: String, default: "" },
  },
  setup(props) {
    return () =>
      h("div", { class: "mini-info" }, [
        h("span", props.label),
        h(
          "strong",
          { title: String(props.value ?? "-") },
          `${props.value ?? "-"}${
            props.value !== undefined && props.value !== null && props.value !== ""
              ? props.suffix
              : ""
          }`,
        ),
      ]);
  },
});

const MetricBox = defineComponent({
  props: {
    label: String,
    value: [String, Number],
    suffix: { type: String, default: "" },
  },
  setup(props) {
    return () =>
      h("div", { class: "metric-box" }, [
        h("span", props.label),
        h(
          "strong",
          { title: String(props.value ?? "-") },
          `${props.value ?? "-"}${
            props.value !== undefined && props.value !== null && props.value !== ""
              ? props.suffix
              : ""
          }`,
        ),
      ]);
  },
});

const tracks = ref([]);
const source = ref("");
const targetType = ref("");
const current = ref({});
const featureChart = ref();
const trackMapChart = ref();
const timeline = ref([]);
let mapChart;
let radarChart;

const candidateLinks = {
  trk_track_radar_278: {
    candidate_id: "C02",
    candidate_source: "radar-spectrum",
    kg_rank: "#2",
    kg_score: "0.880",
    conflict_type: "radar=bird 与 spectrum=drone 冲突",
    llm_decision: "reject",
    final_kept: false,
    note: "对应自然冲突场景中的真实候选。KG 排名靠前，但在冲突裁决中被拒绝，最终未保留。",
  },
  trk_track_radar_343: {
    candidate_id: "C01",
    candidate_source: "radar-spectrum",
    kg_rank: "#1",
    kg_score: "0.905",
    conflict_type: "radar=unknown 与 spectrum=drone 竞争",
    llm_decision: "confirm",
    final_kept: true,
    note: "对应自然冲突场景中的竞争候选。与真实候选共享频谱锚点，confirm 后被保留。",
  },
};

const candidateLink = computed(() => candidateLinks[current.value.track_id]);

const compactRoleText = computed(() => {
  if (!current.value.track_id) return "请选择左侧表格或地图中的轨迹点。";
  if (candidateLink.value) return candidateLink.value.note;
  if (current.value.source === "radar") return "雷达轨迹提供空间位置、运动状态和信号质量，是候选生成的主要空间证据。";
  if (current.value.source === "spectrum") return "频谱轨迹提供语义锚点和信号置信度，用于跨模态候选关联。";
  if (current.value.source === "recognize") return "视觉轨迹提供目标类别和相似度，用于候选确认和冲突辅助判断。";
  if (current.value.source === "decrypt") return "隐藏标签仅用于评价，不直接参与融合裁决。";
  return "该轨迹用于支撑跨模态候选生成和证据解释。";
});

const trackRoleText = computed(() => compactRoleText.value);

const qualityItems = computed(() => {
  const snr = numeric(current.value.snr_mean);
  const speed = numeric(current.value.speed_mean);
  const altitude = numeric(current.value.altitude_mean);
  const pointCount = numeric(current.value.point_count);

  return [
    {
      index: 1,
      label: "连续性",
      text: pointCount >= 30 ? "轨迹点数较多，可支持稳定摘要。" : "轨迹点数偏少，候选关联需要谨慎。",
      level: pointCount >= 30 ? "较好" : "偏弱",
      type: pointCount >= 30 ? "success" : "warning",
    },
    {
      index: 2,
      label: "运动合理性",
      text:
        speed > 0 && speed <= 25 && altitude >= 0
          ? "速度和高度处于可解释范围。"
          : "速度或高度信息不足，需要其他模态补充。",
      level: speed > 0 && speed <= 25 ? "可用" : "待补充",
      type: speed > 0 && speed <= 25 ? "success" : "info",
    },
    {
      index: 3,
      label: "信号质量",
      text:
        snr > 0
          ? `平均 SNR 为 ${formatNum(snr)}，可作为雷达可靠性证据。`
          : "当前模态无 SNR 或信号字段。",
      level: snr >= 12 ? "较强" : snr > 0 ? "中等" : "无",
      type: snr >= 12 ? "success" : snr > 0 ? "warning" : "info",
    },
  ];
});

async function load() {
  tracks.value = (
    await getTracks({ source: source.value, target_type: targetType.value })
  ).data;

  if (tracks.value[0]) await select(tracks.value[0]);
  await nextTick();
  drawMap();
}

async function select(row) {
  current.value = row;
  const { data } = await getTrackFeatures(row.track_id);
  timeline.value = data.timeline || buildTimeline(row);

  await nextTick();
  drawFeature(data);
  drawMap();
}

function localPoint(track) {
  const distance = numeric(track.distance_mean || track.distance || track.range_mean);
  const azimuth = (numeric(track.azimuth_mean || track.azimuth) * Math.PI) / 180;
  const radius = distance || 80 + (Math.abs(hashCode(track.track_id || "")) % 1600);

  return {
    x: radius * Math.sin(azimuth),
    y: radius * Math.cos(azimuth),
    radius,
  };
}

function drawMap() {
  if (!trackMapChart.value) return;
  if (!mapChart) mapChart = echarts.init(trackMapChart.value);

  const points = tracks.value.map((track) => {
    const point = localPoint(track);
    const selected = track.track_id === current.value.track_id;
    const linked = Boolean(candidateLinks[track.track_id]);

    return {
      name: track.track_id,
      value: [point.x, point.y, point.radius],
      track,
      symbolSize: selected ? 20 : linked ? 16 : 9,
      itemStyle: {
        color: selected ? "#d64545" : linked ? "#f0a202" : colorBySource(track.source),
        borderColor: selected || linked ? "#111827" : "#ffffff",
        borderWidth: selected ? 3 : linked ? 2 : 1,
        opacity: selected || linked ? 1 : 0.62,
      },
      label: {
        show: selected,
        formatter: shortTrackId(track.track_id),
        position: "right",
        fontWeight: 700,
        color: "#142238",
      },
    };
  });

  const selectedPoint = current.value.track_id ? localPoint(current.value) : null;

  mapChart.setOption(
    {
      tooltip: {
        formatter: (params) => {
          if (params.seriesName === "设备中心") return "设备中心点<br/>局部相对坐标原点";
          const track = params.data.track;
          return `${track.track_id}<br/>模态：${modalityName(track.source)}<br/>方位：${formatNum(track.azimuth_mean)}°<br/>距离：${formatNum(track.distance_mean)} m`;
        },
      },
      legend: {
        top: 0,
        data: ["设备中心", "轨迹代表点", "运动方向"],
      },
      grid: { top: 38, left: 46, right: 24, bottom: 34 },
      xAxis: {
        type: "value",
        name: "x / m",
        splitLine: { lineStyle: { color: "#edf2f7" } },
      },
      yAxis: {
        type: "value",
        name: "y / m",
        splitLine: { lineStyle: { color: "#edf2f7" } },
        scale: true,
      },
      series: [
        {
          name: "设备中心",
          type: "scatter",
          data: [{ value: [0, 0], symbolSize: 18, itemStyle: { color: "#111827" } }],
          symbolSize: 18,
          label: { show: true, formatter: "设备中心", position: "right" },
        },
        {
          name: "轨迹代表点",
          type: "scatter",
          data: points,
          encode: { x: 0, y: 1 },
        },
        {
          name: "运动方向",
          type: "lines",
          coordinateSystem: "cartesian2d",
          symbol: ["none", "arrow"],
          symbolSize: 9,
          data: selectedPoint
            ? [{ coords: [[0, 0], [selectedPoint.x, selectedPoint.y]] }]
            : [],
          lineStyle: { color: "#d64545", width: 2, opacity: 0.85, curveness: 0 },
        },
      ],
    },
    true,
  );

  mapChart.off("click");
  mapChart.on("click", (params) => {
    if (params.seriesName === "轨迹代表点" && params.data?.track) {
      select(params.data.track);
    }
  });

  setTimeout(() => mapChart?.resize(), 30);
}

function drawFeature(data) {
  if (!featureChart.value) return;
  if (!radarChart) radarChart = echarts.init(featureChart.value);

  const fallback = [
    { name: "方位", value: numeric(current.value.azimuth_mean) },
    { name: "距离", value: numeric(current.value.distance_mean) / 20 },
    { name: "高度", value: numeric(current.value.altitude_mean) },
    { name: "速度", value: numeric(current.value.speed_mean) * 5 },
    { name: "信号", value: numeric(current.value.snr_mean || current.value.confidence_mean) },
  ];

  const radarItems = data?.radar?.length ? data.radar : fallback;
  const values = radarItems.map((item) => numeric(item.value));

  radarChart.setOption(
    {
      tooltip: {},
      radar: {
        radius: "64%",
        indicator: radarItems.map((item, index) => ({
          name: item.name,
          max: Math.max(100, values[index] * 1.2, 1),
        })),
      },
      series: [
        {
          type: "radar",
          areaStyle: { opacity: 0.16 },
          lineStyle: { color: "#2468d8" },
          itemStyle: { color: "#2468d8" },
          data: [{ value: values, name: "轨迹特征" }],
        },
      ],
    },
    true,
  );

  setTimeout(() => radarChart?.resize(), 30);
}

function resizeCharts() {
  mapChart?.resize();
  radarChart?.resize();
}

function rowClassName({ row }) {
  if (row.track_id === current.value.track_id) return "selected-row";
  if (candidateLinks[row.track_id]) return "candidate-row";
  return "";
}

function numeric(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : 0;
}

function formatNum(value) {
  if (value === undefined || value === null || value === "") return "-";
  const number = Number(value);
  return Number.isFinite(number) ? number.toFixed(2) : value;
}

function colorBySource(src) {
  return (
    {
      radar: "#2f6fdd",
      spectrum: "#16a085",
      recognize: "#8e63ce",
      decrypt: "#d64545",
    }[src] || "#607d9c"
  );
}

function modalityName(src) {
  return (
    {
      radar: "雷达",
      spectrum: "频谱",
      recognize: "视觉识别",
      decrypt: "隐藏标签",
    }[src] || src || "-"
  );
}

function shortTrackId(id = "") {
  return String(id).replace("trk_track_", "");
}

function eventLabel(event) {
  return { start: "轨迹开始", end: "轨迹结束" }[event] || event;
}

function buildTimeline(row) {
  return [
    { event: "start", time: row.start_time || "-" },
    { event: "end", time: row.end_time || "-" },
  ];
}

function hashCode(text) {
  return String(text)
    .split("")
    .reduce((sum, char) => ((sum << 5) - sum + char.charCodeAt(0)) | 0, 0);
}

onMounted(() => {
  load();
  window.addEventListener("resize", resizeCharts);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", resizeCharts);
  mapChart?.dispose();
  radarChart?.dispose();
});
</script>

<style scoped>
.track-page {
  height: 100%;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding-right: 10px;
  box-sizing: border-box;
}

.track-workbench {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 390px;
  gap: 12px;
  overflow: hidden;
}

.left-workspace {
  min-height: 0;
  display: grid;
  grid-template-rows: 42% minmax(0, 58%);
  gap: 12px;
  overflow: hidden;
}

.map-panel,
.table-panel,
.right-detail > .panel {
  min-height: 0;
  overflow: hidden;
  padding: 12px;
  box-sizing: border-box;
}

.map-panel,
.table-panel {
  display: flex;
  flex-direction: column;
}

.track-map {
  flex: 1;
  min-height: 0;
  border: 1px solid #dfe8f2;
  border-radius: 8px;
  background:
    radial-gradient(circle at 50% 50%, rgba(36, 104, 216, 0.07), transparent 40%),
    linear-gradient(180deg, #ffffff, #f8fbff);
}

.compact-toolbar {
  flex: 0 0 auto;
  margin-bottom: 8px;
}

.table-body-grid {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: minmax(720px, 1fr) 360px;
  gap: 12px;
  overflow: hidden;
}

.table-shell {
  min-width: 0;
  min-height: 0;
  overflow: hidden;
}

.table-shell :deep(.el-table) {
  width: 100% !important;
}

.evidence-side {
  min-width: 0;
  min-height: 0;
  padding: 10px;
  border: 1px solid #dfe8f2;
  border-radius: 10px;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
  overflow-y: auto;
}

.evidence-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
}

.evidence-head h4 {
  margin: 0;
  color: #172f50;
  font-size: 14px;
}

.evidence-head p {
  margin: 2px 0 0;
  color: #7b8ea5;
  font-size: 12px;
  line-height: 1.35;
}

.selected-track-card {
  padding: 9px 10px;
  margin-bottom: 8px;
  border-radius: 8px;
  background: #eef5ff;
  border: 1px solid #d8e8ff;
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.selected-track-card strong {
  min-width: 0;
  overflow: hidden;
  color: #153f8f;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.selected-track-card span {
  color: #52677f;
  font-size: 12px;
  flex: 0 0 auto;
}

.evidence-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 7px;
  margin-bottom: 8px;
}

.metric-box {
  padding: 8px;
  border: 1px solid #e2eaf4;
  border-radius: 8px;
  background: #fff;
}

.metric-box span {
  display: block;
  color: #7b8ea5;
  font-size: 11px;
}

.metric-box strong {
  display: block;
  margin-top: 3px;
  overflow: hidden;
  color: #172f50;
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.evidence-role {
  padding: 8px;
  border-radius: 8px;
  border: 1px solid #e8edf5;
  background: #fff;
  margin-bottom: 8px;
}

.evidence-role h5 {
  margin: 0 0 4px;
  color: #172f50;
  font-size: 13px;
}

.evidence-role p {
  margin: 0;
  color: #60758f;
  font-size: 12px;
  line-height: 1.45;
}

.evidence-steps {
  display: grid;
  gap: 7px;
}

.evidence-step {
  display: grid;
  grid-template-columns: 24px minmax(0, 1fr);
  gap: 8px;
  padding: 7px 8px;
  border: 1px solid #e2eaf4;
  border-radius: 8px;
  background: #fff;
}

.evidence-step > span {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #e7f1ff;
  color: #2468d8;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 12px;
}

.evidence-step strong {
  display: block;
  color: #172f50;
  font-size: 12px;
}

.evidence-step p {
  margin: 2px 0 0;
  color: #72849b;
  font-size: 11px;
  line-height: 1.35;
}

.right-detail {
  min-height: 0;
  display: grid;
  grid-template-rows: 310px 200px 260px minmax(145px, 1fr);
  gap: 12px;
  overflow: hidden;
}

.summary-panel,
.feature-panel,
.quality-panel,
.timeline-panel {
  overflow: hidden;
}

.feature-chart {
  height: 156px;
}


.summary-scroll {
  height: calc(100% - 36px);
  min-height: 0;
  overflow-y: auto;
  padding-right: 4px;
}

.summary-note {
  margin-top: 8px;
  padding: 8px 10px;
  border: 1px solid #e4edf7;
  border-radius: 8px;
  background: #fff;
}

.summary-note h4 {
  margin: 0 0 5px;
  color: #172f50;
  font-size: 13px;
}

.summary-note p {
  margin: 0;
  color: #60758f;
  font-size: 12px;
  line-height: 1.45;
}

.summary-card {
  padding: 8px 10px;
  background: #f8fbff;
  border: 1px solid #dfe8f2;
  border-radius: 8px;
  margin-bottom: 7px;
}

.summary-card strong {
  display: block;
  color: #153f8f;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.summary-card p,
.candidate-note {
  margin: 0;
  color: #60758f;
  line-height: 1.42;
  font-size: 12px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 7px;
}

.mini-info {
  padding: 7px 8px;
  border: 1px solid #e4edf7;
  border-radius: 7px;
  background: #ffffff;
  min-width: 0;
}

.mini-info span {
  display: block;
  color: #69788c;
  font-size: 12px;
  margin-bottom: 3px;
}

.mini-info strong {
  display: block;
  color: #17233d;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.compact-flow {
  gap: 6px;
}

.compact-flow .analysis-step {
  grid-template-columns: 28px 1fr auto;
  padding: 7px 8px;
  min-height: 0;
}

.compact-flow p {
  margin: 2px 0 0;
  color: #69788c;
  font-size: 12px;
  line-height: 1.35;
}

.candidate-link-card {
  display: grid;
  gap: 8px;
}

.candidate-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.candidate-head strong {
  font-size: 18px;
  color: #153f8f;
}

.small-empty {
  min-height: 118px;
}

:deep(.selected-row) {
  --el-table-tr-bg-color: #fff7e6;
}

:deep(.candidate-row) {
  --el-table-tr-bg-color: #eef5ff;
}

:deep(.el-timeline) {
  padding-left: 4px;
}

:deep(.el-table .cell) {
  line-height: 1.35;
}

@media (max-width: 1500px) {
  .track-workbench {
    grid-template-columns: minmax(0, 1fr) 360px;
  }

  .table-body-grid {
    grid-template-columns: minmax(620px, 1fr) 320px;
  }

  .right-detail {
    grid-template-rows: 292px 184px 238px minmax(138px, 1fr);
  }
}

@media (max-width: 1280px) {
  .track-page {
    height: auto;
    overflow: visible;
  }

  .track-workbench,
  .table-body-grid {
    grid-template-columns: 1fr;
  }

  .left-workspace,
  .right-detail {
    grid-template-rows: auto;
  }

  .track-map {
    height: 360px;
  }

  .evidence-side {
    max-height: 360px;
  }
}

/* 删除 KG 候选关联面板后，右侧只保留摘要、特征、质量和时间线四块。 */
.summary-panel {
  overflow: hidden;
}

.summary-panel .summary-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}


.quality-panel {
  overflow-y: auto;
}

.quality-panel .flow-list {
  height: auto;
}

.timeline-panel {
  overflow-y: auto;
}

</style>
