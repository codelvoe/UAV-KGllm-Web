<template>
  <div class="page kg-page">
    <PageHeader
      title="知识图谱可视化分析台"
      subtitle="左侧控制子图模式，中间浏览图谱结构，右侧解释节点属性、邻居关系和当前子图摘要。"
      eyebrow="Knowledge Graph Explorer"
    />

    <div class="kg-content">
      <div class="kg-workbench">
        <div class="panel control-panel">
          <div class="section-title">
            <h3>图谱控制</h3>
            <span>{{ modeLabel }}</span>
          </div>

          <el-form label-position="top">
            <el-form-item label="子图模式">
              <el-segmented
                v-model="mode"
                :options="modeOptions"
                @change="load"
              />
            </el-form-item>
            <el-form-item label="节点类型">
              <el-input
                v-model="nodeType"
                placeholder="如：轨迹、轨迹点、频谱特征"
                clearable
              />
            </el-form-item>
            <el-form-item label="来源模态">
              <el-input
                v-model="source"
                placeholder="如：radar、spectrum、recognize"
                clearable
              />
            </el-form-item>
            <el-form-item label="最大显示节点数">
              <el-input-number
                v-model="limit"
                :min="30"
                :max="500"
                style="width: 100%"
              />
            </el-form-item>
            <div class="control-switches">
              <el-checkbox v-model="onlyKeyNodes" @change="drawGraph"
                >仅显示关键节点</el-checkbox
              >
              <el-checkbox v-model="showChineseLabels" @change="drawGraph"
                >显示中文标签</el-checkbox
              >
            </div>
            <div class="toolbar dense-toolbar">
              <el-button type="primary" @click="load">加载子图</el-button>
              <el-button type="warning" @click="focusNaturalConflict"
                >聚焦自然冲突</el-button
              >
            </div>
          </el-form>

          <el-divider />
          <div class="section-title">
            <h3>节点图例</h3>
            <span>颜色代表业务类型</span>
          </div>
          <div class="legend-list">
            <div v-for="item in legend" :key="item.type" class="legend-item">
              <span
                class="legend-dot"
                :style="{ background: item.color }"
              ></span>
              <div>
                <strong>{{ item.name }}</strong>
                <p>{{ item.desc }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="panel graph-panel">
          <div class="section-title">
            <h3>图谱主画布</h3>
            <span>关键节点放大，高亮 Natural-conflict 子图</span>
          </div>
          <div ref="graphChart" class="kg-canvas"></div>
        </div>

        <div class="panel side-detail">
          <div class="section-title">
            <h3>节点详情与邻居</h3>
            <el-tag
              v-if="selected.id"
              :type="selected.important ? 'warning' : 'info'"
            >
              {{ selected.typeName || "节点" }}
            </el-tag>
          </div>

          <div v-if="selected.id" class="detail-list">
            <div class="detail-item">
              <div class="detail-label">节点原始名称</div>
              <div class="detail-value">
                {{ selected.rawName || selected.id }}
              </div>
            </div>
            <div class="detail-item">
              <div class="detail-label">中文名称</div>
              <div class="detail-value">{{ selected.zhName }}</div>
            </div>
            <div class="detail-item">
              <div class="detail-label">节点类型</div>
              <div class="detail-value">{{ selected.typeName }}</div>
            </div>
            <div class="detail-item">
              <div class="detail-label">来源模态</div>
              <div class="detail-value">{{ selected.sourceName }}</div>
            </div>
            <div class="detail-item">
              <div class="detail-label">业务含义</div>
              <div class="detail-value">{{ selected.meaning }}</div>
            </div>
            <div class="detail-item">
              <div class="detail-label">当前作用</div>
              <div class="detail-value">{{ selected.role }}</div>
            </div>
          </div>
          <div v-else class="empty-hint compact-empty">
            点击图谱节点查看中文解释与邻居关系
          </div>

          <el-divider />
          <div class="section-title">
            <h3>边关系列表</h3>
            <span>{{ selectedEdges.length }} 条</span>
          </div>
          <el-table :data="selectedEdges" height="170" size="small">
            <el-table-column
              prop="sourceName"
              label="起点"
              show-overflow-tooltip
            />
            <el-table-column prop="relationName" label="关系" width="120" />
            <el-table-column
              prop="targetName"
              label="终点"
              show-overflow-tooltip
            />
          </el-table>
        </div>
      </div>

      <div class="kg-analysis-grid">
        <div class="panel">
          <div class="section-title">
            <h3>图谱结构摘要</h3>
            <span>当前子图统计</span>
          </div>
          <div class="kg-summary-grid">
            <div class="metric-box">
              <span>节点数</span>
              <strong>{{ viewNodes.length }}</strong>
            </div>
            <div class="metric-box">
              <span>边数</span>
              <strong>{{ viewEdges.length }}</strong>
            </div>
            <div class="metric-box">
              <span>关键节点</span>
              <strong>{{ keyNodes.length }}</strong>
            </div>
          </div>
          <div class="type-bars">
            <div
              v-for="item in typeDistribution"
              :key="item.name"
              class="type-bar"
            >
              <div class="type-bar-head">
                <span>{{ item.name }}</span>
                <strong>{{ item.count }}</strong>
              </div>
              <el-progress
                :percentage="item.percent"
                :stroke-width="8"
                :show-text="false"
              />
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="section-title">
            <h3>关键节点说明</h3>
            <span>中文名称、类型含义与业务作用</span>
          </div>
          <div class="key-node-list">
            <div
              v-for="node in keyNodes"
              :key="node.id"
              :class="['key-node-card', { active: node.id === selected.id }]"
              @click="selectNode(node.id)"
            >
              <div class="key-node-title">
                <span
                  class="legend-dot"
                  :style="{ background: node.color }"
                ></span>
                <strong>{{ node.zhName }}</strong>
                <el-tag
                  size="small"
                  :type="node.important ? 'warning' : 'info'"
                  >{{ node.typeName }}</el-tag
                >
              </div>
              <p>{{ node.role }}</p>
              <small>{{ node.id }}</small>
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="section-title">
            <h3>关系链说明</h3>
            <span>当前子图路径解释</span>
          </div>
          <div class="relation-chain">
            <div
              v-for="(step, index) in relationNarrative"
              :key="step.title"
              class="chain-step"
            >
              <div class="step-index">{{ index + 1 }}</div>
              <div>
                <strong>{{ step.title }}</strong>
                <p>{{ step.desc }}</p>
              </div>
            </div>
          </div>
          <el-alert
            class="chain-alert"
            type="warning"
            :closable="false"
            title="Natural-conflict 子图用于解释候选竞争和证据冲突，不代表新增独立样本。"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import * as echarts from "echarts";
import { computed, nextTick, onMounted, ref } from "vue";
import PageHeader from "../components/common/PageHeader.vue";
import { getGraph } from "../api/kg";

const graphChart = ref();
let chart;

const mode = ref("natural");
const nodeType = ref("");
const source = ref("");
const limit = ref(180);
const onlyKeyNodes = ref(false);
const showChineseLabels = ref(true);
const rawGraph = ref({ nodes: [], edges: [] });
const selected = ref({});

const modeOptions = [
  { label: "全局概览", value: "overview" },
  { label: "候选子图", value: "candidate" },
  { label: "轨迹子图", value: "track" },
  { label: "自然冲突", value: "natural" },
];

const legend = [
  {
    type: "radar_track",
    name: "雷达轨迹",
    color: "#2f6fdd",
    desc: "空间、距离、高度、速度和 SNR 候选。",
  },
  {
    type: "spectrum_track",
    name: "频谱轨迹",
    color: "#16a085",
    desc: "无线电语义、机型、信号强度与置信度。",
  },
  {
    type: "visual_evidence",
    name: "视觉证据",
    color: "#8e63ce",
    desc: "光电视觉识别结果和辅助确认。",
  },
  {
    type: "candidate",
    name: "候选节点",
    color: "#f0a202",
    desc: "KG Fusion 生成的跨模态候选。",
  },
  {
    type: "attribute",
    name: "属性节点",
    color: "#7f8c8d",
    desc: "时间、方位、分数、语义、运动等属性。",
  },
  {
    type: "hidden_label",
    name: "评价节点",
    color: "#d64545",
    desc: "hidden label / decrypt，仅用于评价。",
  },
];

const modeLabel = computed(
  () => modeOptions.find((item) => item.value === mode.value)?.label || "子图",
);
const viewNodes = computed(() =>
  onlyKeyNodes.value
    ? rawGraph.value.nodes.filter((node) => node.important)
    : rawGraph.value.nodes,
);
const viewNodeIds = computed(
  () => new Set(viewNodes.value.map((node) => node.id)),
);
const viewEdges = computed(() =>
  rawGraph.value.edges.filter(
    (edge) =>
      viewNodeIds.value.has(edge.source) && viewNodeIds.value.has(edge.target),
  ),
);
const keyNodes = computed(() =>
  viewNodes.value.filter((node) => node.important).slice(0, 8),
);
const selectedEdges = computed(() => {
  if (!selected.value.id) return [];
  return viewEdges.value
    .filter(
      (edge) =>
        edge.source === selected.value.id || edge.target === selected.value.id,
    )
    .map((edge) => ({
      ...edge,
      sourceName: nodeById(edge.source)?.zhName || edge.source,
      targetName: nodeById(edge.target)?.zhName || edge.target,
      relationName: relationLabel(edge.relation),
    }));
});

const typeDistribution = computed(() => {
  const counts = {};
  for (const node of viewNodes.value) {
    counts[node.typeName] = (counts[node.typeName] || 0) + 1;
  }
  const max = Math.max(...Object.values(counts), 1);
  return Object.entries(counts).map(([name, count]) => ({
    name,
    count,
    percent: Math.round((count / max) * 100),
  }));
});

const relationNarrative = computed(() => {
  if (mode.value === "natural") {
    return [
      {
        title: "频谱语义锚点",
        desc: "trk_track_spectrum_79490 提供 DJI Air3 / drone 语义，是候选生成的主要语义锚点。",
      },
      {
        title: "候选竞争",
        desc: "C01 与 C02 共享同一频谱轨迹，但关联不同雷达轨迹，构成一对竞争候选。",
      },
      {
        title: "冲突解释",
        desc: "C02 对应真实候选，但雷达语义为 bird；C01 为 unknown，更容易被模型误保留。",
      },
    ];
  }
  return [
    {
      title: "单模态证据",
      desc: "雷达、频谱、视觉等节点先形成各自轨迹和属性证据。",
    },
    {
      title: "跨模态组织",
      desc: "KG Fusion 通过时间重叠、方位差和语义一致性生成候选连接。",
    },
    {
      title: "研判输出",
      desc: "候选节点再进入 LLM 或启发式规则，形成 confirm / reject / uncertain。",
    },
  ];
});

function typeColor(type) {
  return legend.find((item) => item.type === type)?.color || "#607d9c";
}

function nodeById(id) {
  return rawGraph.value.nodes.find((node) => node.id === id);
}

function relationLabel(relation = "") {
  const map = {
    same_spectrum_anchor: "共享频谱锚点",
    candidate_links_radar: "关联雷达轨迹",
    candidate_links_spectrum: "关联频谱轨迹",
    candidate_has_score: "具有融合分数",
    candidate_has_conflict: "存在证据冲突",
    evaluated_by: "由隐藏标签评价",
    visual_supports: "视觉辅助支持",
  };
  return map[relation] || relation || "关联";
}

function enrichApiNode(node, index) {
  const text =
    `${node.id} ${node.name} ${node.type} ${node.source}`.toLowerCase();
  let type = "attribute";
  if (text.includes("radar") || node.source === "radar") type = "radar_track";
  if (text.includes("spectrum") || node.source === "spectrum")
    type = "spectrum_track";
  if (text.includes("recognize") || node.source === "recognize")
    type = "visual_evidence";
  if (text.includes("decrypt") || node.source === "decrypt")
    type = "hidden_label";
  const isSpecial = Boolean(specialNodes[node.id]);
  const important =
    isSpecial ||
    type === "candidate" ||
    (mode.value !== "overview" && index < 8);
  return {
    ...node,
    rawName: node.name || node.id,
    zhName: chineseName(node.id, node.name),
    type,
    typeName: legend.find((item) => item.type === type)?.name || "属性节点",
    sourceName: node.source || "知识图谱",
    meaning: typeMeaning(type),
    role: important
      ? "当前子图中的高连接或轨迹类节点，用于解释证据组织方式。"
      : "普通属性或中间证据节点。",
    important,
    color: typeColor(type),
  };
}

function chineseName(id, name = "") {
  const special = specialNodes[id];
  if (special) return special.zhName;
  if (String(id).includes("radar"))
    return `雷达轨迹 ${String(id).split("_").pop()}`;
  if (String(id).includes("spectrum"))
    return `频谱轨迹 ${String(id).split("_").pop()}`;
  if (String(id).includes("recognize"))
    return `视觉证据 ${String(id).split("_").pop()}`;
  return name || id;
}

function typeMeaning(type) {
  return (
    legend.find((item) => item.type === type)?.desc ||
    "知识图谱中的属性或关系承载节点。"
  );
}

const specialNodes = {
  C01: {
    zhName: "C01 竞争误报候选",
    type: "candidate",
    meaning: "与真实候选共享同一频谱锚点，但关联 radar_343。",
    role: "用于解释 Natural-conflict 中误保留的竞争候选。",
  },
  C02: {
    zhName: "C02 真实候选",
    type: "candidate",
    meaning: "与频谱轨迹 79490 及 radar_278 形成真实候选链路。",
    role: "用于解释真实候选被 reject / uncertain 的失败链路。",
  },
  trk_track_radar_278: {
    zhName: "雷达轨迹 278",
    type: "radar_track",
    meaning: "真实候选对应的雷达轨迹，雷达语义可能为 bird。",
    role: "Natural-conflict 诊断中的真实雷达候选。",
  },
  trk_track_radar_343: {
    zhName: "雷达轨迹 343",
    type: "radar_track",
    meaning: "误保留候选关联的雷达轨迹，雷达语义为 unknown。",
    role: "作为 C01 的竞争雷达轨迹，用于对照 C02。",
  },
  trk_track_spectrum_79490: {
    zhName: "频谱轨迹 79490",
    type: "spectrum_track",
    meaning: "提供 DJI Air3 / drone 语义的强频谱证据。",
    role: "C01 与 C02 共同使用的语义锚点。",
  },
};

function naturalConflictGraph() {
  const nodes = [
    makeNode(
      "trk_track_spectrum_79490",
      "频谱轨迹 79490",
      "spectrum_track",
      true,
    ),
    makeNode("C01", "C01 竞争误报候选", "candidate", true),
    makeNode("C02", "C02 真实候选", "candidate", true),
    makeNode("trk_track_radar_343", "雷达轨迹 343", "radar_track", true),
    makeNode("trk_track_radar_278", "雷达轨迹 278", "radar_track", true),
    makeNode(
      "track_recognize_4",
      "视觉 drone 辅助证据",
      "visual_evidence",
      true,
    ),
    makeNode(
      "decrypt_F6N8C23C40037K1T",
      "隐藏评价标签 Air3",
      "hidden_label",
      true,
    ),
    makeNode("attr_model_DJI_Air3", "机型语义 DJI Air3", "attribute", false),
    makeNode("attr_type_drone", "频谱类别 drone", "attribute", false),
    makeNode("attr_radar_bird", "雷达类别 bird", "attribute", false),
    makeNode("attr_radar_unknown", "雷达类别 unknown", "attribute", false),
    makeNode("attr_azimuth_diff", "方位差证据", "attribute", false),
    makeNode("attr_time_overlap", "时间重叠证据", "attribute", false),
    makeNode("attr_kg_score", "KG 融合分数", "attribute", false),
  ];
  const edges = [
    edge("C01", "trk_track_spectrum_79490", "candidate_links_spectrum"),
    edge("C02", "trk_track_spectrum_79490", "candidate_links_spectrum"),
    edge("C01", "trk_track_radar_343", "candidate_links_radar"),
    edge("C02", "trk_track_radar_278", "candidate_links_radar"),
    edge("trk_track_spectrum_79490", "attr_model_DJI_Air3", "具有机型语义"),
    edge("trk_track_spectrum_79490", "attr_type_drone", "具有目标类别"),
    edge("trk_track_radar_278", "attr_radar_bird", "具有雷达类别"),
    edge("trk_track_radar_343", "attr_radar_unknown", "具有雷达类别"),
    edge("C01", "attr_azimuth_diff", "candidate_has_score"),
    edge("C02", "attr_azimuth_diff", "candidate_has_score"),
    edge("C01", "attr_time_overlap", "candidate_has_score"),
    edge("C02", "attr_time_overlap", "candidate_has_score"),
    edge("C02", "attr_radar_bird", "candidate_has_conflict"),
    edge("track_recognize_4", "C02", "visual_supports"),
    edge("decrypt_F6N8C23C40037K1T", "C02", "evaluated_by"),
    edge("C01", "attr_kg_score", "candidate_has_score"),
    edge("C02", "attr_kg_score", "candidate_has_score"),
  ];
  return { nodes, edges };
}

function makeNode(id, rawName, type, important) {
  const special = specialNodes[id] || {};
  return {
    id,
    name: rawName,
    rawName,
    zhName: special.zhName || rawName,
    type,
    typeName: legend.find((item) => item.type === type)?.name || "属性节点",
    sourceName: sourceNameByType(type),
    meaning: special.meaning || typeMeaning(type),
    role: special.role || "用于补充说明当前候选的证据链。",
    important,
    color: typeColor(type),
  };
}

function edge(source, target, relation) {
  return { source, target, relation };
}

function sourceNameByType(type) {
  return {
    radar_track: "radar",
    spectrum_track: "spectrum",
    visual_evidence: "recognize",
    candidate: "KG Fusion",
    attribute: "KG 属性",
    hidden_label: "decrypt / hidden label",
  }[type];
}

function convertApiGraph(graph) {
  const nodes = (graph.nodes || []).map((node, index) =>
    enrichApiNode(node, index),
  );
  const ids = new Set(nodes.map((node) => node.id));
  const edges = (graph.edges || [])
    .filter((item) => ids.has(item.source) && ids.has(item.target))
    .map((item) => ({
      source: item.source,
      target: item.target,
      relation: item.relation || "关联",
    }));
  return { nodes, edges };
}

async function load() {
  if (mode.value === "natural") {
    rawGraph.value = naturalConflictGraph();
  } else {
    const { data } = await getGraph({
      limit: limit.value,
      node_type: nodeType.value,
      source: source.value,
    });
    rawGraph.value = convertApiGraph(data);
    if (mode.value === "candidate")
      rawGraph.value = appendCandidateFocus(rawGraph.value);
    if (mode.value === "track")
      rawGraph.value.nodes = rawGraph.value.nodes.filter(
        (node) => node.important || node.type.includes("track"),
      );
  }
  selected.value = {};
  await nextTick();
  drawGraph();
}

function appendCandidateFocus(graph) {
  const natural = naturalConflictGraph();
  return {
    nodes: [
      ...natural.nodes,
      ...graph.nodes
        .filter((node) => !natural.nodes.some((item) => item.id === node.id))
        .slice(0, 40),
    ],
    edges: [...natural.edges, ...graph.edges.slice(0, 60)],
  };
}

function focusNaturalConflict() {
  mode.value = "natural";
  onlyKeyNodes.value = false;
  showChineseLabels.value = true;
  load();
}

function selectNode(id) {
  const node = nodeById(id);
  if (!node) return;
  selected.value = node;
  drawGraph();
}

function drawGraph() {
  if (!graphChart.value) return;
  if (!chart) chart = echarts.init(graphChart.value);
  const selectedId = selected.value.id;
  const categories = legend.map((item) => ({
    name: item.name,
    itemStyle: { color: item.color },
  }));
  const data = viewNodes.value.map((node) => ({
    ...node,
    name: showChineseLabels.value ? node.zhName : node.id,
    category: node.typeName,
    symbolSize: node.id === selectedId ? 46 : node.important ? 34 : 12,
    itemStyle: {
      color: node.color,
      opacity: node.important ? 1 : 0.42,
      borderColor:
        node.id === selectedId
          ? "#111827"
          : node.important
            ? "#ffffff"
            : "transparent",
      borderWidth: node.id === selectedId ? 4 : node.important ? 2 : 0,
      shadowBlur: node.important ? 10 : 0,
      shadowColor: node.color,
    },
    label: {
      show: showChineseLabels.value && node.important,
      fontWeight: node.important ? 700 : 400,
    },
  }));
  const links = viewEdges.value.map((edge) => ({
    ...edge,
    lineStyle: {
      opacity: mode.value === "natural" ? 0.55 : 0.1,
      width:
        edge.source === selectedId || edge.target === selectedId ? 2.5 : 0.8,
      color:
        edge.source === selectedId || edge.target === selectedId
          ? "#2468d8"
          : "#b8c6d8",
      curveness: 0.06,
    },
    label: {
      show: mode.value === "natural",
      formatter: relationLabel(edge.relation),
      color: "#60758f",
      fontSize: 10,
    },
  }));
  chart.setOption(
    {
      tooltip: {
        formatter: (params) => {
          if (params.dataType === "edge")
            return relationLabel(params.data.relation);
          return `${params.data.zhName}<br/>类型：${params.data.typeName}<br/>作用：${params.data.role}`;
        },
      },
      legend: {
        top: 0,
        data: categories.map((item) => item.name),
        type: "scroll",
      },
      series: [
        {
          type: "graph",
          layout: "force",
          roam: true,
          draggable: true,
          categories,
          data,
          links,
          label: {
            position: "right",
            formatter: "{b}",
            overflow: "truncate",
            width: 110,
            fontSize: 11,
          },
          edgeSymbol: ["none", "arrow"],
          edgeSymbolSize: 7,
          emphasis: {
            focus: "adjacency",
            label: { show: true, fontWeight: 700 },
            lineStyle: { width: 3, opacity: 0.9 },
          },
          force: {
            repulsion: mode.value === "natural" ? 520 : 220,
            edgeLength: mode.value === "natural" ? 140 : 95,
            gravity: mode.value === "natural" ? 0.04 : 0.08,
          },
        },
      ],
    },
    true,
  );
  chart.off("click");
  chart.on("click", (params) => {
    if (params.dataType === "node") selectNode(params.data.id);
  });
  setTimeout(() => chart?.resize(), 30);
}

onMounted(load);
</script>

<style scoped>
.kg-page {
  height: calc(100vh - 52px);
  padding-bottom: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.kg-content {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-rows: minmax(440px, 58%) minmax(220px, 42%);
  gap: 12px;
}

.kg-workbench {
  min-height: 0;
  display: grid;
  grid-template-columns: 250px minmax(0, 1fr) 300px;
  gap: 12px;
  align-items: stretch;
}

.control-panel,
.graph-panel,
.side-detail {
  height: 100%;
  min-height: 0;
  overflow: hidden;
  padding: 12px;
}

.graph-panel {
  display: flex;
  flex-direction: column;
}

.kg-canvas {
  flex: 1;
  height: auto;
  min-height: 0;
  border: 1px solid #dfe8f2;
  border-radius: 8px;
  background:
    radial-gradient(
      circle at 48% 45%,
      rgba(36, 104, 216, 0.07),
      transparent 38%
    ),
    linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
}

.control-panel {
  display: flex;
  flex-direction: column;
}

.control-switches {
  display: grid;
  gap: 8px;
  margin-bottom: 12px;
}

.dense-toolbar {
  align-items: stretch;
}

.dense-toolbar .el-button {
  flex: 1;
}

.legend-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: grid;
  gap: 6px;
}

.legend-item {
  display: grid;
  grid-template-columns: 16px 1fr;
  gap: 9px;
  align-items: start;
  padding: 8px;
  border: 1px solid #e4edf7;
  border-radius: 7px;
  background: #f8fbff;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-top: 3px;
  display: inline-block;
}

.legend-item strong {
  font-size: 13px;
  color: #1b2b42;
}

.legend-item p {
  margin: 2px 0 0;
  color: #69788c;
  font-size: 12px;
  line-height: 1.4;
}

.compact-empty {
  min-height: 68px;
  height: 68px;
}

.side-detail {
  display: flex;
  flex-direction: column;
}

.side-detail .detail-list {
  max-height: 185px;
  overflow-y: auto;
}

.kg-analysis-grid {
  min-height: 0;
  margin-top: 0;
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr) 430px;
  gap: 12px;
}

.kg-analysis-grid > .panel {
  height: 100%;
  min-height: 0;
  overflow-y: auto;
  padding: 12px;
}

.kg-summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 12px;
}

.metric-box {
  padding: 12px;
  border-radius: 8px;
  background: #f8fbff;
  border: 1px solid #dfe8f2;
}

.metric-box span {
  display: block;
  color: #69788c;
  font-size: 12px;
  margin-bottom: 6px;
}

.metric-box strong {
  font-size: 24px;
  color: #153f8f;
}

.type-bars {
  display: grid;
  gap: 8px;
}

.type-bar-head {
  display: flex;
  justify-content: space-between;
  color: #465a70;
  font-size: 12px;
  margin-bottom: 4px;
}

.key-node-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.key-node-card {
  cursor: pointer;
  padding: 11px;
  border: 1px solid #dfe8f2;
  border-radius: 8px;
  background: #f8fbff;
  transition: 0.16s ease;
}

.key-node-card:hover,
.key-node-card.active {
  border-color: #7db2ff;
  box-shadow: 0 8px 20px rgba(36, 104, 216, 0.12);
  transform: translateY(-1px);
}

.key-node-title {
  display: flex;
  align-items: center;
  gap: 7px;
}

.key-node-card p {
  margin: 7px 0 5px;
  color: #465a70;
  line-height: 1.55;
}

.key-node-card small {
  color: #93a1b4;
}

.relation-chain {
  display: grid;
  gap: 10px;
}

.chain-step {
  display: grid;
  grid-template-columns: 34px 1fr;
  gap: 10px;
  padding: 11px;
  background: #f8fbff;
  border: 1px solid #dfe8f2;
  border-radius: 8px;
}

.chain-step p {
  margin: 5px 0 0;
  color: #60758f;
  line-height: 1.55;
}

.chain-alert {
  margin-top: 12px;
}

@media (max-width: 1280px) {
  .kg-workbench,
  .kg-analysis-grid {
    grid-template-columns: 1fr;
  }

  .control-panel,
  .side-detail,
  .graph-panel {
    min-height: auto;
  }
}
</style>
