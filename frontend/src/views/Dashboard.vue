<template>
  <div class="page dashboard-page">
    <div class="dashboard-header">
      <PageHeader
        title="系统首页驾驶舱"
        subtitle="多设备感知、知识图谱融合与大模型辅助研判的系统能力入口。"
        eyebrow="SYSTEM DASHBOARD"
      >
        <template #extra>
          <el-tag type="success">系统数据在线</el-tag>
          <el-tag type="info">Neo4j 可选</el-tag>
          <el-button size="small" @click="reload">刷新</el-button>
        </template>
      </PageHeader>
    </div>

    <div class="hero-slot">
      <FusionHeroScene @navigate="go" />
    </div>

    <div class="overview-grid">
      <section class="cockpit-card status-card">
        <div class="card-accent"></div>
        <div class="card-head">
          <div>
            <h3>系统运行状态</h3>
            <p>健康状态、数据范围与核心图谱规模</p>
          </div>
          <span class="state-pill online">Online</span>
        </div>
        <div class="status-matrix">
          <div class="status-tile primary">
            <span>运行状态</span>
            <strong>{{ summary.system_status || "running" }}</strong>
            <small>服务可用</small>
          </div>
          <div class="status-tile">
            <span>数据时间范围</span>
            <strong class="time-value">{{ summary.time_range || "-" }}</strong>
            <small>当前序列</small>
          </div>
          <div class="status-tile">
            <span>知识图谱规模</span>
            <strong>{{ formatNumber(summary.kg_nodes) }} / {{ formatNumber(summary.kg_edges) }}</strong>
            <small>节点 / 边</small>
          </div>
          <div class="status-tile">
            <span>隐藏评价标签</span>
            <strong>{{ summary.decrypt_labels ?? "-" }}</strong>
            <small>评价锚点</small>
          </div>
        </div>
      </section>

      <section class="cockpit-card action-card">
        <div class="card-accent green"></div>
        <div class="card-head">
          <div>
            <h3>常用操作</h3>
            <p>进入数据、轨迹、图谱、候选与研判流程</p>
          </div>
          <span class="state-pill neutral">Workflow</span>
        </div>
        <div class="quick-actions">
          <button
            v-for="item in actionItems"
            :key="item.path"
            type="button"
            @click="go(item.path)"
          >
            <span class="action-icon">{{ item.icon }}</span>
            <span class="action-text">
              <strong>{{ item.title }}</strong>
              <small>{{ item.desc }}</small>
            </span>
          </button>
        </div>
      </section>

      <section class="cockpit-card event-card-wrap">
        <div class="card-accent orange"></div>
        <div class="card-head">
          <div>
            <h3>近期系统事件</h3>
            <p>关键记录与风险提示</p>
          </div>
          <span class="state-pill risk">Risk</span>
        </div>
        <div class="event-list">
          <article
            v-for="item in compactEvents"
            :key="item.time + item.title"
            :class="['event-item', item.level]"
          >
            <div class="event-time">{{ item.time }}</div>
            <div class="event-body">
              <strong>{{ normalizeTitle(item.title) }}</strong>
              <p>{{ eventText(item) }}</p>
            </div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import PageHeader from "../components/common/PageHeader.vue";
import FusionHeroScene from "../components/dashboard/FusionHeroScene.vue";
import request from "../api/request";

const router = useRouter();
const summary = ref({});
const charts = ref({ recent: [] });

const actionItems = [
  { title: "多模态数据管理", desc: "标准化记录", path: "/data", icon: "D" },
  { title: "轨迹证据管理", desc: "轨迹级摘要", path: "/tracks", icon: "T" },
  { title: "KG 融合候选分析", desc: "候选与冲突", path: "/fusion", icon: "K" },
  { title: "大模型智能研判", desc: "辅助裁决", path: "/llm-decision", icon: "L" },
  { title: "知识图谱可视化", desc: "节点与关系", path: "/kg", icon: "G" },
  { title: "运行分析归档", desc: "性能与记录", path: "/experiments", icon: "A" },
];

const compactEvents = computed(() => {
  const list = charts.value.recent?.length
    ? charts.value.recent
    : [
        { time: "12:52:33", title: "Natural-conflict 候选 C02 被拒绝", level: "risk" },
        { time: "12:53:32", title: "重复频谱候选完成去重分析", level: "normal" },
        { time: "13:04:15", title: "阶段性研判记录已生成", level: "normal" },
      ];
  return list.slice(0, 3);
});

function go(path) {
  router.push(path);
}

function formatNumber(value) {
  if (value === undefined || value === null || value === "") return "-";
  return Number(value).toLocaleString();
}

function normalizeTitle(title = "") {
  const text = String(title);
  if (text.includes("C02")) return "Natural-conflict 候选 C02 被拒绝";
  if (text.includes("重复") || text.includes("频谱")) return "重复频谱候选完成去重分析";
  if (text.includes("报告") || text.includes("研判")) return "研判记录已生成";
  return text;
}

function eventText(item) {
  return item.level === "risk"
    ? "建议进入候选分析或智能研判页面进一步核查。"
    : "记录已更新，可进入对应模块查看详情。";
}

async function reload() {
  const [summaryRes, chartRes] = await Promise.all([
    request.get("/dashboard/summary"),
    request.get("/dashboard/charts"),
  ]);
  summary.value = summaryRes.data || {};
  charts.value = chartRes.data || { recent: [] };
}

onMounted(reload);
</script>

<style scoped>
.dashboard-page {
  height: 100%;
  min-height: 0;
  overflow: hidden;
  display: grid;
  grid-template-rows: 70px minmax(250px, 1fr) 330px;
  gap: 12px;
  padding-bottom: 12px;
}

.dashboard-header,
.hero-slot {
  min-height: 0;
  overflow: hidden;
}

.overview-grid {
  min-height: 0;
  display: grid;
  grid-template-columns: minmax(0, 0.98fr) minmax(0, 1.12fr) minmax(320px, 0.72fr);
  gap: 12px;
  overflow: hidden;
}

.cockpit-card {
  position: relative;
  height: 100%;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  padding: 14px;
  border: 1px solid rgba(151, 174, 204, 0.42);
  border-radius: 14px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(246, 250, 255, 0.92)),
    radial-gradient(circle at 88% 8%, rgba(36, 104, 216, 0.12), transparent 34%);
  box-shadow: 0 16px 34px rgba(24, 45, 72, 0.1);
  box-sizing: border-box;
}

.cockpit-card::after {
  content: "";
  position: absolute;
  inset: auto 14px 0 14px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(36, 104, 216, 0.35), transparent);
}

.card-accent {
  position: absolute;
  left: 0;
  top: 14px;
  width: 4px;
  height: 46px;
  border-radius: 0 999px 999px 0;
  background: #2468d8;
  box-shadow: 0 0 20px rgba(36, 104, 216, 0.5);
}

.card-accent.green {
  background: #18a058;
  box-shadow: 0 0 20px rgba(24, 160, 88, 0.4);
}

.card-accent.orange {
  background: #d9822b;
  box-shadow: 0 0 20px rgba(217, 130, 43, 0.4);
}

.card-head {
  height: 38px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.card-head h3 {
  margin: 0;
  color: #102a43;
  font-size: 16px;
  line-height: 1.1;
  letter-spacing: 0;
}

.card-head p {
  margin: 5px 0 0;
  color: #60758f;
  font-size: 12px;
  line-height: 1.2;
}

.state-pill {
  flex: 0 0 auto;
  padding: 4px 9px;
  border-radius: 999px;
  border: 1px solid #d7e4f3;
  background: #f6faff;
  color: #60758f;
  font-size: 12px;
  font-weight: 700;
}

.state-pill.online {
  border-color: #bce7cb;
  background: #ecfff3;
  color: #16814a;
}

.state-pill.neutral {
  border-color: #cbdcf5;
  background: #edf5ff;
  color: #2468d8;
}

.state-pill.risk {
  border-color: #ffd8a8;
  background: #fff5e9;
  color: #b65d12;
}

.status-matrix {
  height: calc(100% - 48px);
  min-height: 0;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  grid-template-rows: repeat(2, minmax(0, 1fr));
  gap: 9px;
}

.status-tile {
  min-width: 0;
  min-height: 0;
  padding: 10px 12px;
  border: 1px solid rgba(203, 216, 233, 0.78);
  border-radius: 11px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(242, 247, 253, 0.92));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.85);
}

.status-tile.primary {
  background:
    linear-gradient(135deg, rgba(36, 104, 216, 0.1), rgba(255, 255, 255, 0.92));
  border-color: rgba(36, 104, 216, 0.22);
}

.status-tile span,
.status-tile small {
  display: block;
  color: #70839b;
  font-size: 11px;
  line-height: 1.1;
}

.status-tile strong {
  display: block;
  margin: 6px 0 5px;
  overflow: hidden;
  color: #0d3b70;
  font-size: 17px;
  line-height: 1.08;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-tile .time-value {
  font-size: 12px;
  line-height: 1.25;
}

.quick-actions {
  height: calc(100% - 48px);
  min-height: 0;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  grid-template-rows: repeat(2, minmax(0, 1fr));
  gap: 9px;
}

.quick-actions button {
  min-width: 0;
  min-height: 0;
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr);
  gap: 9px;
  align-items: center;
  padding: 9px 10px;
  border: 1px solid rgba(203, 216, 233, 0.86);
  border-radius: 11px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.95), rgba(246, 250, 255, 0.95));
  text-align: left;
  cursor: pointer;
  transition: 0.18s ease;
}

.quick-actions button:hover {
  border-color: rgba(36, 104, 216, 0.48);
  background: linear-gradient(180deg, #ffffff, #eef6ff);
  box-shadow: 0 10px 22px rgba(36, 104, 216, 0.13);
  transform: translateY(-1px);
}

.action-icon {
  width: 28px;
  height: 28px;
  border-radius: 9px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #2468d8, #53a5ff);
  color: #ffffff;
  font-size: 13px;
  font-weight: 800;
  box-shadow: 0 8px 18px rgba(36, 104, 216, 0.22);
}

.action-text {
  min-width: 0;
}

.action-text strong,
.action-text small {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.action-text strong {
  color: #102a43;
  font-size: 12px;
  line-height: 1.25;
}

.action-text small {
  margin-top: 3px;
  color: #71849a;
  font-size: 11px;
}

.event-list {
  height: calc(100% - 48px);
  min-height: 0;
  display: grid;
  grid-template-rows: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.event-item {
  min-height: 0;
  display: grid;
  grid-template-columns: 58px minmax(0, 1fr);
  gap: 9px;
  align-items: center;
  padding: 8px 10px;
  border: 1px solid rgba(203, 216, 233, 0.86);
  border-radius: 11px;
  background: linear-gradient(180deg, #ffffff, #f8fbff);
}

.event-item.risk {
  border-color: rgba(217, 130, 43, 0.36);
  background:
    linear-gradient(180deg, #fffaf4, #fff7ed),
    radial-gradient(circle at 100% 0, rgba(217, 130, 43, 0.12), transparent 40%);
}

.event-time {
  width: 58px;
  padding: 5px 0;
  border-radius: 8px;
  background: #edf5ff;
  color: #1d6fdc;
  font-size: 11px;
  font-weight: 800;
  text-align: center;
}

.event-item.risk .event-time {
  background: #fff0dd;
  color: #b65d12;
}

.event-body {
  min-width: 0;
}

.event-body strong,
.event-body p {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-body strong {
  color: #102a43;
  font-size: 12px;
  line-height: 1.2;
}

.event-body p {
  margin: 4px 0 0;
  color: #71849a;
  font-size: 11px;
}

@media (max-height: 820px) {
  .dashboard-page {
    grid-template-rows: 62px minmax(210px, 1fr) 292px;
    gap: 10px;
  }

  .cockpit-card {
    padding: 12px;
  }

  .card-head {
    height: 28px;
    margin-bottom: 8px;
  }

  .card-head p {
    display: none;
  }

  .status-matrix,
  .quick-actions,
  .event-list {
    height: calc(100% - 36px);
  }
}
</style>
