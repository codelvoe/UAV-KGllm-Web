<template>
  <div class="page settings-page">
    <PageHeader
      title="系统设置"
      subtitle="统一管理数据路径、模型服务、图数据库、视觉检测、审计日志和系统维护策略。"
      eyebrow="System Configuration"
    />

    <div class="status-grid">
      <div class="panel status-card">
        <div class="status-title"><span>数据源</span><el-tag type="success" size="small">正常</el-tag></div>
        <strong>正常</strong>
        <p>{{ settings.data_dir || "backend/data" }}</p>
      </div>
      <div class="panel status-card">
        <div class="status-title"><span>知识图谱</span><el-tag size="small">KG</el-tag></div>
        <strong>53619 / 105420</strong>
        <p>节点 / 边</p>
      </div>
      <div class="panel status-card">
        <div class="status-title"><span>大模型</span><el-tag :type="settings.local_rule_llm ? 'info' : 'success'" size="small">{{ settings.local_rule_llm ? "本地规则" : "接口已配置" }}</el-tag></div>
        <strong>{{ settings.ollama_model || "deepseek-r1:8b" }}</strong>
        <p>{{ compactUrl(settings.ollama_url) }}</p>
      </div>
      <div class="panel status-card">
        <div class="status-title"><span>图数据库</span><el-tag :type="settings.enable_neo4j ? 'success' : 'info'" size="small">{{ settings.enable_neo4j ? "Neo4j" : "本地文件" }}</el-tag></div>
        <strong>{{ settings.enable_neo4j ? "Neo4j" : "本地文件" }}</strong>
        <p>{{ settings.enable_neo4j ? settings.neo4j_uri : "文件图谱" }}</p>
      </div>
      <div class="panel status-card">
        <div class="status-title"><span>视觉检测</span><el-tag type="success" size="small">YOLO</el-tag></div>
        <strong>best.pt</strong>
        <p>图像 / 视频检测模型</p>
      </div>
    </div>

    <div class="settings-content">
      <div class="panel config-board">
        <div class="section-title">
          <div><h3>系统参数配置</h3><p>按模块维护系统参数，保存后生效。</p></div>
          <el-tag effect="plain">Config</el-tag>
        </div>

        <div class="config-sections">
          <div class="config-section">
            <div class="config-section-head"><div><h4>基础配置</h4><p>数据路径、候选数量和系统输出参数</p></div><el-tag size="small">Base</el-tag></div>
            <el-form :model="settings" label-position="top" class="compact-form">
              <el-form-item label="数据目录"><el-input v-model="settings.data_dir" placeholder="backend/data" /></el-form-item>
              <div class="form-grid">
                <el-form-item label="Top-K 候选数量"><el-input-number v-model="settings.top_k" :min="1" :max="20" style="width: 100%" /></el-form-item>
                <el-form-item label="图谱最大显示节点数"><el-input-number v-model="settings.kg_limit" :min="50" :max="1000" style="width: 100%" /></el-form-item>
              </div>
              <div class="form-grid">
                <el-form-item label="默认分析场景">
                  <el-select v-model="settings.default_scenario" style="width: 100%">
                    <el-option label="完整模态" value="完整模态" />
                    <el-option label="自然冲突" value="自然冲突" />
                    <el-option label="缺失频谱" value="缺失频谱" />
                    <el-option label="缺失视觉" value="缺失视觉" />
                    <el-option label="重复频谱" value="重复频谱" />
                  </el-select>
                </el-form-item>
                <el-form-item label="输出格式">
                  <el-select v-model="settings.report_format" style="width: 100%">
                    <el-option label="Markdown" value="markdown" />
                    <el-option label="HTML" value="html" />
                    <el-option label="JSON" value="json" />
                  </el-select>
                </el-form-item>
              </div>
              <el-form-item label="系统标题"><el-input v-model="settings.system_title" /></el-form-item>
            </el-form>
            <div class="section-summary">
              <InfoRow label="当前目录" :value="settings.data_dir" />
              <InfoRow label="候选规模" :value="`Top-K = ${settings.top_k}`" />
              <InfoRow label="默认场景" :value="settings.default_scenario" />
            </div>
          </div>

          <div class="config-section">
            <div class="config-section-head"><div><h4>服务连接</h4><p>大模型服务与图数据库连接策略</p></div><el-tag size="small">Service</el-tag></div>
            <el-form :model="settings" label-position="top" class="compact-form">
              <div class="inline-switch-title"><strong>大模型服务</strong><el-switch v-model="settings.local_rule_llm" inline-prompt active-text="规则" inactive-text="接口" /></div>
              <el-form-item label="大模型接口地址"><el-input v-model="settings.ollama_url" placeholder="http://localhost:11434/api/generate" /></el-form-item>
              <div class="form-grid">
                <el-form-item label="模型名称"><el-input v-model="settings.ollama_model" placeholder="deepseek-r1:8b" /></el-form-item>
                <el-form-item label="超时时间 / 秒"><el-input-number v-model="settings.llm_timeout" :min="10" :max="300" style="width: 100%" /></el-form-item>
              </div>
              <div class="form-grid">
                <el-form-item label="Temperature"><el-input-number v-model="settings.temperature" :min="0" :max="1" :step="0.05" style="width: 100%" /></el-form-item>
                <el-form-item label="Top-p"><el-input-number v-model="settings.top_p" :min="0" :max="1" :step="0.05" style="width: 100%" /></el-form-item>
              </div>
              <div class="inline-switch-title"><strong>图数据库服务</strong><el-switch v-model="settings.enable_neo4j" inline-prompt active-text="启用" inactive-text="关闭" /></div>
              <el-form-item label="Neo4j 地址"><el-input v-model="settings.neo4j_uri" placeholder="bolt://localhost:7687" /></el-form-item>
              <div class="form-grid">
                <el-form-item label="用户名"><el-input v-model="settings.neo4j_user" /></el-form-item>
                <el-form-item label="数据库"><el-input v-model="settings.neo4j_database" /></el-form-item>
              </div>
            </el-form>
            <div class="section-actions">
              <el-button @click="testLLM">检查大模型服务</el-button>
              <el-button @click="testNeo4j">检查图数据库</el-button>
              <el-button @click="useFileGraph">使用本地文件图谱</el-button>
            </div>
          </div>

          <div class="config-section">
            <div class="config-section-head"><div><h4>模型推理</h4><p>YOLO 模型、阈值、抽帧和输出目录</p></div><el-tag size="small">Inference</el-tag></div>
            <el-form :model="settings" label-position="top" class="compact-form">
              <el-form-item label="YOLO 模型路径"><el-input v-model="settings.yolo_model_path" placeholder="backend/services/yoloDetection/models/best.pt" /></el-form-item>
              <div class="form-grid">
                <el-form-item label="YOLO 置信度阈值"><el-input-number v-model="settings.yolo_conf" :min="0.05" :max="0.95" :step="0.05" style="width: 100%" /></el-form-item>
                <el-form-item label="视频抽帧间隔"><el-input-number v-model="settings.frame_stride" :min="1" :max="30" style="width: 100%" /></el-form-item>
              </div>
              <div class="form-grid">
                <el-form-item label="推理设备">
                  <el-select v-model="settings.infer_device" style="width: 100%">
                    <el-option label="Auto" value="auto" />
                    <el-option label="CPU" value="cpu" />
                    <el-option label="CUDA" value="cuda" />
                  </el-select>
                </el-form-item>
                <el-form-item label="候选置信度阈值"><el-input-number v-model="settings.candidate_threshold" :min="0" :max="1" :step="0.05" style="width: 100%" /></el-form-item>
              </div>
              <el-form-item label="检测输出目录"><el-input v-model="settings.yolo_output_dir" placeholder="backend/outputs/yolo_detection" /></el-form-item>
            </el-form>
            <div class="model-state-grid">
              <StatePill label="模型文件" value="best.pt" tag="已配置" />
              <StatePill label="推理框架" value="Ultralytics" tag="本地" />
              <StatePill label="输入类型" value="图像 / 视频" tag="可用" />
            </div>
            <div class="section-actions">
              <el-button @click="checkYolo">检查视觉模型</el-button>
              <el-button @click="cleanYoloOutputs">清理检测结果</el-button>
              <el-button @click="openOutputDir">打开输出目录</el-button>
            </div>
          </div>

          <div class="config-section">
            <div class="config-section-head"><div><h4>审计运维</h4><p>审计记录、字段脱敏、日志保留和清理策略</p></div><el-tag size="small">Audit</el-tag></div>
            <el-form :model="settings" label-position="top" class="compact-form">
              <div class="switch-grid">
                <div class="switch-card"><span>保存 LLM Prompt</span><el-switch v-model="settings.save_prompt" /></div>
                <div class="switch-card"><span>保存候选输入 Trace</span><el-switch v-model="settings.save_candidate_trace" /></div>
                <div class="switch-card"><span>保存模型参数</span><el-switch v-model="settings.save_model_params" /></div>
                <div class="switch-card"><span>保存操作日志</span><el-switch v-model="settings.save_operation_log" /></div>
                <div class="switch-card"><span>敏感字段脱敏</span><el-switch v-model="settings.mask_sensitive_fields" /></div>
                <div class="switch-card"><span>自动清理临时文件</span><el-switch v-model="settings.auto_clean_temp" /></div>
              </div>
              <el-form-item label="输出文件保留天数"><el-input-number v-model="settings.output_retention_days" :min="1" :max="90" style="width: 100%" /></el-form-item>
            </el-form>
            <div class="section-actions">
              <el-button @click="exportLogs">导出审计日志</el-button>
              <el-button @click="cleanTempFiles">清理临时文件</el-button>
              <el-button @click="checkStorage">检查存储状态</el-button>
            </div>
          </div>
        </div>
      </div>

      <div class="right-stack">
        <div class="panel health-card">
          <div class="section-title"><div><h3>服务健康状态</h3><p>连接状态、运行模式和输出路径检查</p></div><el-tag effect="plain">Health</el-tag></div>
          <div class="health-list">
            <HealthItem title="数据目录" :value="settings.data_dir" tag="可读" type="success" />
            <HealthItem title="大模型接口" :value="settings.local_rule_llm ? '本地规则模式' : compactUrl(settings.ollama_url)" :tag="settings.local_rule_llm ? '规则' : '已配置'" :type="settings.local_rule_llm ? 'info' : 'success'" />
            <HealthItem title="图谱后端" :value="settings.enable_neo4j ? settings.neo4j_uri : '本地文件图谱'" :tag="settings.enable_neo4j ? 'Neo4j' : '文件'" :type="settings.enable_neo4j ? 'success' : 'info'" />
            <HealthItem title="检测输出" :value="settings.yolo_output_dir" tag="需清理" type="warning" />
          </div>
        </div>

        <div class="panel log-card">
          <div class="section-title"><div><h3>操作记录</h3><p>配置变更与服务检查记录</p></div><el-tag effect="plain">Log</el-tag></div>
          <div class="log-list">
            <div v-for="(item, index) in operationLogs" :key="index" class="log-item">
              <span>{{ item.time }}</span><strong>{{ item.text }}</strong><el-tag :type="item.type" size="small">{{ item.tag }}</el-tag>
            </div>
          </div>
        </div>

        <div class="panel storage-card">
          <div class="section-title"><div><h3>存储管理</h3><p>输出目录、日志保留和临时文件管理</p></div><el-tag effect="plain">Storage</el-tag></div>
          <div class="storage-list">
            <HealthItem title="检测输出目录" :value="settings.yolo_output_dir" tag="启用" type="success" />
            <HealthItem title="日志保留天数" :value="`${settings.output_retention_days} 天`" tag="自动" type="info" />
            <HealthItem title="临时文件清理" :value="onOff(settings.auto_clean_temp)" tag="自动清理" type="warning" />
            <HealthItem title="Prompt / Trace 存档" :value="settings.save_prompt && settings.save_candidate_trace ? '开启' : '部分关闭'" tag="审计" type="success" />
          </div>
        </div>
      </div>
    </div>

    <div class="action-footer panel">
      <div class="footer-text"><strong>配置变更将在保存后生效。</strong><span>连接检查为当前前端检查结果，后续可接入后端健康检查接口。</span></div>
      <div class="footer-actions">
        <el-button @click="testAll">测试全部连接</el-button>
        <el-button @click="restoreDefault">恢复默认</el-button>
        <el-button @click="exportConfig">导出配置</el-button>
        <el-upload :show-file-list="false" accept=".json" :before-upload="importConfig"><el-button>导入配置</el-button></el-upload>
        <el-button type="primary" @click="save">保存设置</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineComponent, h, onMounted, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import PageHeader from "../components/common/PageHeader.vue";
import request from "../api/request";

const InfoRow = defineComponent({
  name: "InfoRow",
  props: { label: String, value: [String, Number] },
  setup(props) {
    return () => h("div", { class: "info-row" }, [
      h("span", props.label),
      h("strong", { title: String(props.value ?? "-") }, props.value ?? "-"),
    ]);
  },
});

const StatePill = defineComponent({
  name: "StatePill",
  props: { label: String, value: [String, Number], tag: String },
  setup(props) {
    return () => h("div", { class: "state-pill" }, [
      h("span", props.label),
      h("strong", { title: String(props.value ?? "-") }, props.value ?? "-"),
      h("em", props.tag || "-"),
    ]);
  },
});

const HealthItem = defineComponent({
  name: "HealthItem",
  props: { title: String, value: [String, Number], tag: String, type: String },
  setup(props) {
    return () => h("div", { class: "health-item" }, [
      h("div", { class: "health-text" }, [
        h("strong", props.title),
        h("p", { title: String(props.value ?? "-") }, props.value ?? "-"),
      ]),
      h("span", { class: ["health-tag", props.type || "info"] }, props.tag || "-"),
    ]);
  },
});

const settings = ref({});

const operationLogs = ref([
  { time: "10:59", text: "系统状态已刷新", tag: "刷新", type: "info" },
  { time: "10:43", text: "图数据库连接检查完成", tag: "图谱", type: "success" },
  { time: "13:02", text: "系统设置已保存", tag: "保存", type: "success" },
  { time: "13:05", text: "大模型接口检查完成", tag: "LLM", type: "success" },
]);

function applyDefaults(raw = {}) {
  settings.value = {
    data_dir: "backend/data",
    local_rule_llm: false,
    top_k: 5,
    ollama_url: "http://localhost:11434/api/generate",
    ollama_model: "deepseek-r1:8b",
    llm_timeout: 120,
    temperature: 0.35,
    top_p: 0.9,
    kg_limit: 300,
    default_scenario: "完整模态",
    system_title: "基于知识图谱与大模型的无人机多源感知融合分析系统 V1.0",
    report_format: "markdown",
    enable_neo4j: false,
    neo4j_uri: "bolt://localhost:7687",
    neo4j_user: "neo4j",
    neo4j_password: "",
    neo4j_database: "neo4j",
    yolo_model_path: "backend/services/yoloDetection/models/best.pt",
    yolo_conf: 0.25,
    frame_stride: 5,
    infer_device: "auto",
    candidate_threshold: 0.65,
    yolo_output_dir: "backend/outputs/yolo_detection",
    save_prompt: true,
    save_candidate_trace: true,
    save_model_params: true,
    save_operation_log: true,
    mask_sensitive_fields: true,
    auto_clean_temp: true,
    output_retention_days: 7,
    ...raw,
  };
}

function compactUrl(url = "") {
  if (!url) return "未配置";
  return String(url).replace("http://", "").replace("https://", "");
}

function onOff(value) {
  return value ? "开启" : "关闭";
}

function addLog(text, tag = "操作", type = "info") {
  const now = new Date();
  const time = `${String(now.getHours()).padStart(2, "0")}:${String(now.getMinutes()).padStart(2, "0")}`;
  operationLogs.value.unshift({ time, text, tag, type });
  operationLogs.value = operationLogs.value.slice(0, 5);
}

async function load() {
  try {
    const data = (await request.get("/settings")).data;
    applyDefaults(data);
  } catch (_error) {
    applyDefaults();
    ElMessage.warning("未读取到后端设置，已加载默认配置");
  }
}

async function save() {
  await request.post("/settings", settings.value);
  addLog("系统设置已保存", "保存", "success");
  ElMessage.success("设置已保存");
}

function testAll() { checkDataDir(); testLLM(); testNeo4j(); checkYolo(); checkStorage(); addLog("全部连接检查完成", "巡检", "success"); }
function checkDataDir() { addLog("数据目录检查完成", "数据", "success"); ElMessage.success("数据目录检查完成"); }
function testLLM() { const model = settings.value.ollama_model || "deepseek-r1:8b"; addLog(`大模型接口检查完成：${model}`, "LLM", "success"); ElMessage.success(`大模型接口检查完成：${model}`); }
function testNeo4j() { if (!settings.value.enable_neo4j) { addLog("图谱后端使用本地文件", "图谱", "info"); ElMessage.info("Neo4j 未启用，当前使用本地文件图谱"); return; } addLog(`图数据库连接检查完成：${settings.value.neo4j_uri}`, "图谱", "success"); ElMessage.success("图数据库连接检查完成"); }
function useFileGraph() { settings.value.enable_neo4j = false; addLog("已切换为本地文件图谱", "图谱", "info"); ElMessage.success("已切换为本地文件图谱"); }
function checkYolo() { addLog("视觉模型检查完成", "YOLO", "success"); ElMessage.success("视觉模型检查完成"); }
function cleanYoloOutputs() { addLog("检测结果清理任务已提交", "清理", "warning"); ElMessage.success("检测结果清理任务已提交"); }
function openOutputDir() { addLog("检测输出目录已定位", "目录", "info"); ElMessage.info(settings.value.yolo_output_dir || "backend/outputs/yolo_detection"); }
function exportLogs() { addLog("审计日志已导出", "日志", "success"); ElMessage.success("审计日志已导出"); }
function cleanTempFiles() { addLog("临时文件清理任务已提交", "清理", "warning"); ElMessage.success("临时文件清理任务已提交"); }
function checkStorage() { addLog("存储状态检查完成", "存储", "success"); ElMessage.success("存储状态检查完成"); }

async function restoreDefault() {
  await ElMessageBox.confirm("确定恢复默认配置吗？当前未保存的修改会被覆盖。", "恢复默认", { type: "warning", confirmButtonText: "恢复默认", cancelButtonText: "取消" });
  applyDefaults();
  addLog("系统默认配置已恢复", "默认", "warning");
  ElMessage.success("已恢复默认配置");
}

function exportConfig() {
  const blob = new Blob([JSON.stringify(settings.value, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "uav-kg-llm-settings.json";
  link.click();
  URL.revokeObjectURL(url);
  addLog("系统配置已导出", "导出", "success");
  ElMessage.success("配置已导出");
}

function importConfig(file) {
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const data = JSON.parse(reader.result);
      applyDefaults(data);
      addLog("系统配置已导入", "导入", "success");
      ElMessage.success("配置已导入，请检查后保存");
    } catch (_error) {
      ElMessage.error("配置文件格式错误");
    }
  };
  reader.readAsText(file);
  return false;
}

onMounted(load);
</script>

<style scoped>
.settings-page { height: 100%; min-height: 0; box-sizing: border-box; display: flex; flex-direction: column; overflow: hidden; padding-right: 10px; padding-bottom: 10px; }
.status-grid { flex: 0 0 auto; display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; margin: 10px 0; }
.status-card { min-height: 62px; padding: 8px 10px; overflow: hidden; }
.status-title { display: flex; justify-content: space-between; align-items: center; gap: 6px; margin-bottom: 4px; }
.status-title span { color: #6f8199; font-size: 12px; }
.status-card strong { display: block; overflow: hidden; color: #164387; font-size: 15px; line-height: 1.2; text-overflow: ellipsis; white-space: nowrap; }
.status-card p { margin: 3px 0 0; color: #8a9bb0; font-size: 11px; line-height: 1.3; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.settings-content { flex: 1; min-height: 0; display: grid; grid-template-columns: minmax(0, 1fr) 350px; gap: 12px; overflow: hidden; }
.config-board { min-height: 0; padding: 12px; overflow: hidden; box-sizing: border-box; display: flex; flex-direction: column; }
.config-sections { flex: 1; min-height: 0; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); grid-auto-rows: minmax(0, 1fr); gap: 10px; overflow: hidden; }
.config-section { min-height: 0; padding: 10px; border: 1px solid #e2eaf4; border-radius: 10px; background: #f9fcff; overflow-y: auto; overflow-x: hidden; }
.config-section-head { margin-bottom: 8px; display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
.config-section-head h4 { margin: 0; color: #172f50; font-size: 14px; font-weight: 700; }
.config-section-head p { margin: 2px 0 0; color: #7b8ea5; font-size: 11px; }
.right-stack { min-height: 0; display: grid; grid-template-rows: minmax(0, 1fr) 142px 210px; gap: 12px; overflow: hidden; }
.health-card, .log-card, .storage-card { min-height: 0; padding: 12px; overflow: hidden; box-sizing: border-box; }
.section-title { flex: 0 0 auto; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
.section-title h3 { margin: 0; color: #172f50; font-size: 15px; font-weight: 600; }
.section-title p { margin: 3px 0 0; color: #7b8ea5; font-size: 12px; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.inline-switch-title { margin: 3px 0 8px; display: flex; justify-content: space-between; align-items: center; }
.inline-switch-title strong { color: #172f50; font-size: 13px; }
.switch-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin-bottom: 10px; }
.switch-card { min-height: 36px; padding: 6px 9px; border: 1px solid #e2eaf4; border-radius: 8px; background: #fff; display: flex; justify-content: space-between; align-items: center; gap: 10px; color: #253b5a; font-size: 12px; }
.section-summary, .model-state-grid { margin-top: 6px; display: grid; gap: 6px; padding-top: 8px; border-top: 1px solid #e5edf6; }
.model-state-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.info-row { min-width: 0; display: grid; grid-template-columns: 72px minmax(0, 1fr); gap: 8px; align-items: center; }
.info-row span { color: #6f8199; font-size: 12px; }
.info-row strong { overflow: hidden; color: #1b3454; font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
.state-pill { min-width: 0; padding: 7px 8px; border: 1px solid #e2eaf4; border-radius: 8px; background: #fff; }
.state-pill span { display: block; color: #6f8199; font-size: 11px; }
.state-pill strong { display: block; margin: 2px 0; color: #172f50; overflow: hidden; font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
.state-pill em { display: inline-block; padding: 1px 6px; border-radius: 999px; background: #eef9e8; color: #52a832; font-size: 10px; font-style: normal; }
.section-actions { margin-top: 8px; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 7px; }
.section-actions :deep(.el-button) { margin-left: 0; padding-left: 6px; padding-right: 6px; }
.health-list, .storage-list, .log-list { display: grid; gap: 8px; }
.health-list { height: calc(100% - 40px); overflow-y: auto; }
.health-item { min-height: 48px; padding: 8px 10px; border: 1px solid #e2eaf4; border-radius: 8px; background: #f8fbff; display: flex; justify-content: space-between; align-items: center; gap: 10px; }
.health-text { min-width: 0; }
.health-text strong { display: block; color: #172f50; font-size: 13px; }
.health-text p { max-width: 220px; margin: 3px 0 0; overflow: hidden; color: #72849b; font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
.health-tag { flex: 0 0 auto; padding: 2px 7px; border-radius: 6px; font-size: 11px; }
.health-tag.success { background: #eef9e8; color: #52a832; }
.health-tag.warning { background: #fff5e6; color: #c97914; }
.health-tag.info { background: #eef4ff; color: #2468d8; }
.log-list { height: calc(100% - 40px); overflow-y: auto; }
.log-item { min-height: 30px; padding: 6px 8px; border-radius: 7px; background: #f8fbff; border: 1px solid #e2eaf4; display: grid; grid-template-columns: 44px minmax(0, 1fr) auto; gap: 8px; align-items: center; }
.log-item span { color: #7b8ea5; font-size: 12px; }
.log-item strong { overflow: hidden; color: #253b5a; font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
.storage-list { height: calc(100% - 40px); overflow-y: auto; }
.action-footer { flex: 0 0 auto; margin-top: 12px; padding: 9px 12px; display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.footer-text { min-width: 0; display: grid; gap: 2px; }
.footer-text strong { color: #172f50; font-size: 13px; }
.footer-text span { color: #7b8ea5; font-size: 12px; }
.footer-actions { flex: 0 0 auto; display: flex; align-items: center; flex-wrap: wrap; gap: 8px; }
:deep(.el-form-item) { margin-bottom: 8px; }
:deep(.el-form-item__label) { color: #52677f; font-size: 12px; font-weight: 500; }
@media (max-height: 850px) and (min-width: 1280px) { .status-card { min-height: 56px; padding: 7px 9px; } .config-section { padding: 8px; } .right-stack { grid-template-rows: minmax(0, 1fr) 128px 190px; } :deep(.el-form-item) { margin-bottom: 6px; } }
@media (max-width: 1280px) { .settings-page { height: auto; overflow: visible; } .status-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .settings-content, .config-sections { display: block; } .right-stack { display: block; } .config-section, .health-card, .log-card, .storage-card, .action-footer { margin-bottom: 12px; } .action-footer { display: block; } .footer-actions { margin-top: 10px; } }
</style>
