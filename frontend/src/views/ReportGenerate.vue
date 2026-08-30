<template>
  <div class="page">
    <PageHeader
      title="研判报告生成工作台"
      subtitle="左侧配置报告内容，中间管理章节结构，右侧实时预览，形成从候选研判到报告输出的闭环。"
      eyebrow="Report Workspace"
    />

    <div class="workbench three-col">
      <div class="panel">
        <div class="section-title">
          <h3>报告配置</h3>
          <span>选择生成范围</span>
        </div>
        <el-form label-position="top">
          <el-form-item label="报告类型">
            <el-select v-model="type" style="width: 100%">
              <el-option label="阶段性研判报告" value="阶段性研判报告" />
              <el-option label="候选目标处置报告" value="候选目标处置报告" />
            </el-select>
          </el-form-item>
          <el-form-item label="候选目标">
            <el-select v-model="candidate" style="width: 100%">
              <el-option label="候选 C01" value="C01" />
              <el-option label="候选 C02" value="C02" />
              <el-option label="候选 C03" value="C03" />
            </el-select>
          </el-form-item>
          <el-checkbox v-model="includeDecision">加入大模型研判</el-checkbox>
          <el-checkbox v-model="includeExperiment">加入实验结果</el-checkbox>
          <el-checkbox v-model="includeRisk">加入风险与局限性</el-checkbox>
          <div class="toolbar" style="margin-top: 14px">
            <el-button type="primary" @click="compose">生成预览</el-button>
            <el-button @click="clear">清空草稿</el-button>
            <el-button @click="gen">导出报告</el-button>
          </div>
          <el-alert
            v-if="path"
            type="success"
            :closable="false"
            :title="`导出路径：${path}`"
          />
        </el-form>
      </div>

      <div class="panel">
        <div class="section-title">
          <h3>章节结构</h3>
          <span>报告骨架</span>
        </div>
        <div class="flow-list">
          <div
            v-for="(section, index) in sections"
            :key="section"
            class="analysis-step"
          >
            <div class="step-index">{{ index + 1 }}</div>
            <div>{{ section }}</div>
            <el-tag>{{ enabledSection(section) ? "启用" : "可选" }}</el-tag>
          </div>
        </div>
        <el-divider />
        <div class="detail-item">
          <div class="detail-label">生成策略</div>
          <div class="detail-value">
            先组织数据集和知识图谱概况，再追加候选研判、实验结果、风险等级和处置建议。
          </div>
        </div>
      </div>

      <div class="panel split-detail">
        <div class="section-title">
          <h3>报告预览</h3>
          <el-tag>{{ draft.items?.length || 0 }} 条内容</el-tag>
        </div>
        <div class="scroll-area">
          <div v-if="!draft.items?.length" class="report-skeleton">
            <h2>{{ type }}</h2>
            <p>
              一、数据集概况：汇总
              radar、spectrum、recognize、pho_status、decrypt 的数据规模。
            </p>
            <p>二、知识图谱信息：汇总节点、边、轨迹和模态证据组织方式。</p>
            <p>
              三、融合候选研判：汇总候选 {{ candidate }} 的 KG
              分数和大模型裁决。
            </p>
            <p>四、性能结果：汇总 F1 值、虚警率、Token 成本和端到端延迟。</p>
            <p>五、风险与处置建议：标记自然冲突等短板场景，并给出处置建议。</p>
          </div>
          <ReportPreview v-else :draft="draft" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import PageHeader from "../components/common/PageHeader.vue";
import ReportPreview from "../components/report/ReportPreview.vue";
import {
  addReportItem,
  clearReport,
  generateReport,
  getDraft,
} from "../api/report";

const type = ref("阶段性研判报告");
const candidate = ref("C01");
const includeDecision = ref(true);
const includeExperiment = ref(true);
const includeRisk = ref(true);
const draft = ref({ items: [] });
const path = ref("");
const sections = [
  "数据集概况",
  "知识图谱信息",
  "KG 融合候选",
  "大模型研判结果",
  "实验指标",
  "风险等级",
  "处置建议",
  "当前不足",
];

function enabledSection(section) {
  if (section.includes("大模型")) return includeDecision.value;
  if (section.includes("实验")) return includeExperiment.value;
  if (section.includes("风险")) return includeRisk.value;
  return true;
}

async function refresh() {
  draft.value = (await getDraft()).data;
}

async function compose() {
  await clearReport();
  await addReportItem({
    type: "overview",
    title: "数据集概况",
    content:
      "当前系统包含 radar、spectrum、recognize、pho_status、decrypt 等多模态数据，支持轨迹级 evidence summary。",
  });
  await addReportItem({
    type: "kg",
    title: "知识图谱信息",
    content:
      "知识图谱包含设备、观测帧、轨迹、轨迹点、空间位置、运动特征、频谱特征和视觉特征等节点。",
  });
  if (includeDecision.value) {
    await addReportItem({
      type: "decision",
      title: `候选 ${candidate.value} 大模型研判`,
      content:
        "候选证据链已整理，建议结合 KG 分数、冲突标记和人工复核结果综合判断。",
    });
  }
  if (includeExperiment.value) {
    await addReportItem({
      type: "experiment",
      title: "实验结果摘要",
      content:
        "KG Fusion 能降低虚警，KG+LLM 在部分模态缺失场景可改变 positive 集合，自然冲突仍为短板场景。",
    });
  }
  if (includeRisk.value) {
    await addReportItem({
      type: "risk",
      title: "风险与局限性",
      content:
        "当前系统未接入实时传感器闭环，LLM 研判应作为受控辅助裁决模块使用。",
    });
  }
  refresh();
}

async function clear() {
  await clearReport();
  refresh();
}

async function gen() {
  path.value = (await generateReport()).data.report_path;
}

onMounted(refresh);
</script>

<style scoped>
.report-skeleton {
  min-height: 640px;
  background: #ffffff;
  border: 1px solid #dfe8f2;
  border-radius: 8px;
  padding: 24px;
  line-height: 1.9;
}
</style>
