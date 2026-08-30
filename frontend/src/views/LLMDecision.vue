<template>
  <div class="page llm-page">
    <PageHeader
      title="大模型智能研判工作流"
      subtitle="呈现 KG Top-K 候选如何被组织为可见证据输入，并经过 LLM 裁决、Validator 校验和最终输出。"
      eyebrow="LLM Assisted Decision"
    />

    <div class="llm-layout">
      <div class="llm-workbench">
        <div class="panel queue-panel">
          <div class="section-title">
            <div>
              <h3>候选队列</h3>
              <p>选择 KG Top-K 研判对象</p>
            </div>
            <el-tag effect="plain">{{ filtered.length }} 条</el-tag>
          </div>

          <div class="queue-toolbar">
            <el-select v-model="scenario" style="width: 100%" @change="load">
              <el-option
                v-for="scene in scenes"
                :key="scene"
                :label="scene"
                :value="scene"
              />
            </el-select>
            <el-input
              v-model="kw"
              placeholder="搜索候选编号 / 轨迹编号"
              clearable
            />
          </div>

          <div class="queue-table-wrap">
            <el-table
              :data="filtered"
              height="100%"
              highlight-current-row
              :row-class-name="candidateRowClass"
              @row-click="select"
            >
              <el-table-column
                prop="candidate_id"
                label="候选"
                width="72"
                fixed
              />
              <el-table-column label="KG" width="68">
                <template #default="{ row }">{{
                  formatScore(row.kg_score)
                }}</template>
              </el-table-column>
              <el-table-column prop="rank" label="#" width="44" />
              <el-table-column label="冲突" width="64">
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
              <el-table-column label="LLM" min-width="76">
                <template #default="{ row }">
                  <el-tag
                    :type="llmTagType(llmStatus(row))"
                    size="small"
                    effect="light"
                  >
                    {{ llmStatus(row) }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>

        <div class="panel input-panel">
          <div class="section-title">
            <div>
              <h3>候选输入与约束摘要</h3>
              <p>仅使用可见模态证据，不使用 decrypt hidden label</p>
            </div>
            <el-tag v-if="current.candidate_id">{{
              current.candidate_id
            }}</el-tag>
          </div>

          <div class="input-scroll">
            <div class="flow-strip">
              <div class="flow-node active">
                <span>1</span>
                <strong>KG Top-K</strong>
                <small>候选输入</small>
              </div>
              <div class="flow-arrow">→</div>
              <div class="flow-node">
                <span>2</span>
                <strong>可见证据</strong>
                <small>模态摘要</small>
              </div>
              <div class="flow-arrow">→</div>
              <div class="flow-node warning">
                <span>3</span>
                <strong>LLM 裁决</strong>
                <small>三分类输出</small>
              </div>
              <div class="flow-arrow">→</div>
              <div class="flow-node validator">
                <span>4</span>
                <strong>Validator</strong>
                <small>校验回退</small>
              </div>
            </div>

            <div class="evidence-groups">
              <div class="evidence-group">
                <h4>基础信息</h4>
                <div class="group-grid">
                  <InfoItem label="候选编号" :value="current.candidate_id" />
                  <InfoItem
                    label="候选来源"
                    :value="current.candidate_source"
                  />
                  <InfoItem
                    label="KG 分数"
                    :value="formatScore(current.kg_score)"
                  />
                  <InfoItem label="候选排序" :value="current.rank" />
                </div>
              </div>

              <div class="evidence-group">
                <h4>轨迹证据</h4>
                <div class="group-grid">
                  <InfoItem label="雷达轨迹" :value="current.radar_track_id" />
                  <InfoItem
                    label="频谱轨迹"
                    :value="current.spectrum_track_id"
                  />
                  <InfoItem label="时间重叠" :value="current.time_overlap" />
                  <InfoItem
                    label="方位角差"
                    :value="current.azimuth_diff"
                    suffix="°"
                  />
                </div>
              </div>

              <div class="evidence-group">
                <h4>冲突与输入约束</h4>
                <div class="group-grid">
                  <InfoItem
                    label="冲突标记"
                    :value="formatValue(current.conflict_flag)"
                  />
                  <InfoItem label="可用模态" :value="availableModalitiesText" />
                  <InfoItem label="任务类型" :value="promptTask" />
                  <InfoItem
                    label="隐藏标签"
                    value="decrypt 不进入输入"
                    warning
                  />
                </div>
              </div>
            </div>

            <div class="prompt-card">
              <div class="prompt-card-title">
                <h3>LLM 输入约束摘要</h3>
                <el-tag size="small" effect="plain">Prompt Boundary</el-tag>
              </div>
              <div
                v-for="item in promptSummary"
                :key="item.label"
                class="prompt-row"
              >
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </div>

          <div class="action-bar">
            <el-button type="primary" :loading="loading" @click="judge"
              >生成研判</el-button
            >
            <el-button :loading="loading" @click="judge">重新研判</el-button>
          </div>
        </div>

        <div class="panel output-panel">
          <div class="section-title">
            <div>
              <h3>研判输出与校验</h3>
              <p>LLM 结果、Validator 和证据引用</p>
            </div>
            <el-tag :type="decisionType">{{
              decision.decision || "等待研判"
            }}</el-tag>
          </div>

          <div class="output-scroll">
            <div class="decision-card" :class="decision.decision || 'pending'">
              <div class="decision-head">
                <span>Decision</span>
                <strong>{{ decision.decision || "等待研判" }}</strong>
              </div>
              <p>{{ decision.reason || "选择候选后点击生成研判。" }}</p>
              <div class="decision-extra">
                <el-tag size="small"
                  >风险等级：{{ decision.risk_level || "-" }}</el-tag
                >
                <span>{{ decision.suggestion || "暂无建议" }}</span>
              </div>
            </div>

            <div class="verify-grid">
              <InfoItem
                label="Schema Valid"
                :value="formatValue(decision.schema_valid)"
                :status="decision.schema_valid === true ? 'ok' : ''"
              />
              <InfoItem
                label="Validator Result"
                :value="decision.validator_result || decision.validator || '-'"
              />
              <InfoItem
                label="Fallback Used"
                :value="formatValue(decision.fallback_used)"
                :status="decision.fallback_used ? 'danger' : ''"
              />
              <InfoItem
                label="Final Output"
                :value="decision.final_output || decision.decision || '-'"
              />
              <InfoItem
                label="Expand Mode"
                :value="decision.expand_mode || 'Python 展开'"
              />
              <InfoItem label="Token / Latency" :value="tokenLatencyText" />
            </div>

            <div class="evidence-table-section">
              <div class="subsection-line">
                <h3>证据引用</h3>
                <span>模型输出中的字段级依据</span>
              </div>
              <div class="evidence-table-wrap">
                <el-table
                  :data="decision.evidence || []"
                  height="100%"
                  size="small"
                >
                  <el-table-column prop="type" label="证据类型" width="92" />
                  <el-table-column prop="field" label="字段" min-width="90" />
                  <el-table-column
                    prop="value"
                    label="取值"
                    min-width="90"
                    show-overflow-tooltip
                  />
                </el-table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="llm-bottom">
        <div class="panel boundary-card">
          <h3>LLM 输入边界</h3>
          <p>
            输入对象限定为 KG Top-K 候选；输入证据限定为
            radar、spectrum、recognize、pho_status 等可见模态摘要。
          </p>
        </div>
        <div class="panel boundary-card">
          <h3>裁决输出约束</h3>
          <p>
            输出集合限定为 confirm / reject / uncertain，并要求满足预设 JSON
            schema，不能由 LLM 新增候选目标。
          </p>
        </div>
        <div class="panel boundary-card">
          <h3>Validator 与回退</h3>
          <p>
            当输出不合规、冲突过强或结果展开失败时，触发 validator /
            fallback，最终输出由后处理链路控制。
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, ref } from "vue";
import PageHeader from "../components/common/PageHeader.vue";
import { getCandidates } from "../api/fusion";
import { makeDecision } from "../api/llm";
import request from "../api/request";

const InfoItem = defineComponent({
  name: "InfoItem",
  props: {
    label: { type: String, default: "" },
    value: { type: [String, Number, Boolean], default: "-" },
    suffix: { type: String, default: "" },
    warning: { type: Boolean, default: false },
    status: { type: String, default: "" },
  },
  setup(props) {
    return () =>
      h(
        "div",
        { class: ["info-item", props.status, { warning: props.warning }] },
        [
          h("span", props.label),
          h(
            "strong",
            { title: String(props.value ?? "-") },
            `${props.value ?? "-"}${props.value !== undefined && props.value !== null && props.value !== "-" ? props.suffix : ""}`,
          ),
        ],
      );
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

const scenario = ref("完整模态");
const rows = ref([]);
const current = ref({});
const decision = ref({});
const promptPayload = ref({});
const kw = ref("");
const loading = ref(false);

const filtered = computed(() =>
  rows.value.filter((row) =>
    JSON.stringify(row).toLowerCase().includes(kw.value.toLowerCase()),
  ),
);

const decisionType = computed(() => {
  if (decision.value.decision === "confirm") return "success";
  if (decision.value.decision === "reject") return "danger";
  if (decision.value.decision === "uncertain") return "warning";
  return "info";
});

const promptSummary = computed(() => {
  const selected = promptPayload.value.selected_candidate || {};
  return [
    {
      label: "候选编号",
      value: selected.candidate_id || current.value.candidate_id || "-",
    },
    {
      label: "可用模态",
      value:
        (promptPayload.value.available_modalities || []).join("、") ||
        "radar、spectrum、recognize、pho_status",
    },
    {
      label: "任务类型",
      value: promptPayload.value.task || "基于 KG 候选的辅助研判",
    },
    { label: "输入约束", value: "不使用 decrypt 隐藏标签，只基于可见模态证据" },
  ];
});

const availableModalitiesText = computed(
  () =>
    (promptPayload.value.available_modalities || []).join("、") ||
    "radar、spectrum、recognize、pho_status",
);

const promptTask = computed(
  () => promptPayload.value.task || "候选目标辅助研判",
);

const tokenLatencyText = computed(() => {
  const token = decision.value.token_cost ?? decision.value.tokens;
  const latency = decision.value.latency_sec ?? decision.value.latency;
  if (!token && !latency) return "-";
  return `${token ?? "-"} / ${latency ?? "-"}s`;
});

function formatValue(value) {
  if (typeof value === "boolean") return value ? "是" : "否";
  if (value === null || value === undefined || value === "") return "-";
  return value;
}

function formatScore(value) {
  if (value === null || value === undefined || value === "") return "-";
  const number = Number(value);
  return Number.isNaN(number) ? value : number.toFixed(3);
}

function llmStatus(row) {
  if (
    row.candidate_id === current.value.candidate_id &&
    decision.value.decision
  ) {
    return decision.value.decision;
  }
  return row.llm_decision || row.decision_status || row.decision || "待研判";
}

function llmTagType(value) {
  if (value === "confirm") return "success";
  if (value === "reject") return "danger";
  if (value === "uncertain") return "warning";
  return "info";
}

function candidateRowClass({ row }) {
  if (row.candidate_id === current.value.candidate_id) return "selected-row";
  if (row.conflict_flag) return "conflict-row";
  return "";
}

async function load() {
  const response = await getCandidates({ scenario: scenario.value });
  const data = response.data;
  rows.value = Array.isArray(data) ? data : data?.items || [];
  decision.value = {};
  promptPayload.value = {};
  if (rows.value[0]) {
    await select(rows.value[0]);
  } else {
    current.value = {};
  }
}

async function select(row) {
  current.value = row;
  decision.value = {};
  try {
    promptPayload.value = (
      await request.get(`/llm/prompt/${row.candidate_id}`, {
        params: { scenario: scenario.value },
      })
    ).data;
  } catch (_error) {
    promptPayload.value = {};
  }
}

async function judge() {
  if (!current.value.candidate_id) return;
  loading.value = true;
  try {
    decision.value = (
      await makeDecision({
        candidate_id: current.value.candidate_id,
        scenario: scenario.value,
        local_rule_mode: false,
      })
    ).data;
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<style scoped>
.llm-page {
  height: 100%;
  min-height: 0;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding-bottom: 10px;
}

.llm-layout {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.llm-workbench {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr) 330px;
  gap: 12px;
}

.llm-bottom {
  flex: 0 0 120px;
  min-height: 0;
  margin-top: 12px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.panel {
  min-height: 0;
  box-sizing: border-box;
}

.queue-panel,
.input-panel,
.output-panel,
.boundary-card {
  padding: 14px;
  overflow: hidden;
}

.queue-panel,
.input-panel,
.output-panel {
  display: flex;
  flex-direction: column;
}

.section-title {
  flex: 0 0 auto;
  margin-bottom: 11px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.section-title h3 {
  margin: 0;
  color: #172f50;
  font-size: 15px;
  font-weight: 600;
}

.section-title p,
.subsection-line span {
  margin: 3px 0 0;
  color: #7b8ea5;
  font-size: 12px;
}

.queue-toolbar {
  flex: 0 0 auto;
  display: grid;
  gap: 8px;
  margin-bottom: 10px;
}

.queue-table-wrap {
  flex: 1;
  min-height: 0;
}

.queue-panel :deep(.el-table th.el-table__cell) {
  height: 35px;
  padding: 5px 0;
  background: #f4f7fb;
  color: #53677f;
  font-size: 12px;
}

.queue-panel :deep(.el-table td.el-table__cell) {
  padding: 6px 0;
  color: #253b5a;
  font-size: 12px;
}

.queue-panel :deep(.selected-row td.el-table__cell) {
  background: #edf4ff !important;
}

.queue-panel :deep(.conflict-row td.el-table__cell) {
  background: #fff9f5;
}

.input-scroll,
.output-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 2px;
}

.flow-strip {
  display: grid;
  grid-template-columns: 1fr 24px 1fr 24px 1fr 24px 1fr;
  align-items: center;
  gap: 4px;
  margin-bottom: 12px;
}

.flow-node {
  min-width: 0;
  padding: 9px 8px;
  border: 1px solid #e1eaf4;
  border-radius: 8px;
  background: #f8fbff;
  text-align: center;
}

.flow-node span {
  display: inline-flex;
  width: 22px;
  height: 22px;
  margin-bottom: 4px;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #e7f1ff;
  color: #2468d8;
  font-size: 12px;
  font-weight: 700;
}

.flow-node strong {
  display: block;
  color: #203858;
  font-size: 13px;
}

.flow-node small {
  color: #71839b;
  font-size: 11px;
}

.flow-node.warning span {
  background: #fff0d8;
  color: #c97916;
}

.flow-node.validator span {
  background: #eaf7ef;
  color: #158255;
}

.flow-arrow {
  color: #9aa9ba;
  text-align: center;
}

.evidence-groups {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

.evidence-group {
  padding: 10px;
  border: 1px solid #e2eaf4;
  border-radius: 8px;
  background: #fbfdff;
}

.evidence-group h4 {
  margin: 0 0 8px;
  color: #253b5a;
  font-size: 13px;
}

.group-grid,
.verify-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.info-item {
  min-width: 0;
  padding: 8px 9px;
  border-radius: 7px;
  background: #f6f9fd;
  border: 1px solid #e4edf7;
}

.info-item span {
  display: block;
  margin-bottom: 4px;
  color: #7689a2;
  font-size: 12px;
}

.info-item strong {
  display: block;
  overflow: hidden;
  color: #172f50;
  font-size: 13px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.info-item.warning strong {
  color: #b96b22;
}

.info-item.ok strong {
  color: #158255;
}

.info-item.danger strong {
  color: #d74747;
}

.prompt-card {
  margin-top: 12px;
  border: 1px solid #dfe8f2;
  border-radius: 8px;
  background: #f8fbff;
  overflow: hidden;
}

.prompt-card-title {
  padding: 10px 12px;
  border-bottom: 1px solid #e8eef6;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.prompt-card-title h3 {
  margin: 0;
  color: #253b5a;
  font-size: 13px;
}

.prompt-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 9px 12px;
  border-bottom: 1px solid #e8eef6;
}

.prompt-row:last-child {
  border-bottom: 0;
}

.prompt-row span {
  color: #65758b;
  font-size: 12px;
}

.prompt-row strong {
  color: #17233d;
  text-align: right;
  font-size: 12px;
}

.action-bar {
  flex: 0 0 auto;
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.decision-card {
  padding: 13px;
  border: 1px solid #e2eaf4;
  border-radius: 8px;
  background: #f8fbff;
  margin-bottom: 12px;
}

.decision-card.confirm {
  border-color: #cfe5da;
  background: #f4fbf7;
}

.decision-card.reject {
  border-color: #f0d1d1;
  background: #fff7f7;
}

.decision-card.uncertain {
  border-color: #f1dfc7;
  background: #fffaf3;
}

.decision-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.decision-head span {
  color: #7689a2;
  font-size: 12px;
}

.decision-head strong {
  color: #172f50;
  font-size: 20px;
}

.decision-card p {
  margin: 8px 0;
  color: #41566f;
  font-size: 13px;
  line-height: 1.55;
}

.decision-extra {
  display: grid;
  gap: 6px;
  color: #5d7088;
  font-size: 12px;
}

.verify-grid {
  margin-bottom: 12px;
}

.evidence-table-section {
  min-height: 210px;
  display: flex;
  flex-direction: column;
}

.subsection-line {
  flex: 0 0 auto;
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.subsection-line h3 {
  margin: 0;
  color: #253b5a;
  font-size: 13px;
}

.evidence-table-wrap {
  flex: 1;
  min-height: 0;
}

.boundary-card h3 {
  margin: 0 0 8px;
  color: #172f50;
  font-size: 14px;
}

.boundary-card p {
  margin: 0;
  color: #4f647e;
  font-size: 12px;
  line-height: 1.55;
}

@media (max-height: 820px) and (min-width: 1200px) {
  .llm-bottom {
    flex-basis: 104px;
  }

  .flow-strip {
    margin-bottom: 9px;
  }

  .flow-node {
    padding: 7px 6px;
  }

  .evidence-group {
    padding: 8px;
  }
}

@media (max-width: 1180px) {
  .llm-page {
    height: auto;
    overflow: visible;
  }

  .llm-workbench,
  .llm-bottom {
    display: block;
  }

  .queue-panel,
  .input-panel,
  .output-panel,
  .boundary-card {
    min-height: 320px;
    margin-bottom: 12px;
  }
}
</style>
