<template>
  <div class="fusion-scene">
    <div class="scene-header">
      <div>
        <span class="scene-eyebrow">MULTI-SENSOR · KNOWLEDGE GRAPH · LLM</span>
        <h2>多设备感知 — 知识图谱融合 — 大模型智能研判</h2>
        <p>
          首页主视觉用于展示系统技术路线，不绑定具体业务数据。左侧为反无人机场景感知，
          中间为图谱关系组织，右侧为大模型推理与结构化输出。
        </p>
      </div>

      <div class="scene-actions">
        <button @click="$emit('navigate', '/data')">数据管理</button>
        <button @click="$emit('navigate', '/kg')">知识图谱</button>
        <button @click="$emit('navigate', '/llm-decision')">智能研判</button>
      </div>
    </div>

    <div class="scene-stage">
      <!-- 1. 多设备感知层 -->
      <section class="scene-card sensor-card">
        <div class="card-head">
          <strong>多设备感知层</strong>
          <span>Radar / RF / EO / YOLO</span>
        </div>

        <div class="sensor-canvas">
          <!-- 雷达 -->
          <div class="radar-station device-card">
            <div class="radar-icon">
              <div class="radar-base"></div>
              <div class="radar-dish"></div>
              <div class="radar-sweep"></div>
              <div class="radar-ring r1"></div>
              <div class="radar-ring r2"></div>
              <div class="radar-ring r3"></div>
            </div>
            <div>
              <strong>Radar</strong>
              <span>空间 / 运动</span>
            </div>
          </div>

          <!-- 频谱 -->
          <div class="rf-station device-card">
            <div class="antenna-icon">
              <div class="antenna-pole"></div>
              <div class="antenna-wave w1"></div>
              <div class="antenna-wave w2"></div>
              <div class="antenna-wave w3"></div>
            </div>
            <div>
              <strong>RF Spectrum</strong>
              <span>频率 / 信号</span>
            </div>
          </div>

          <!-- 光电相机 -->
          <div class="eo-station device-card">
            <div class="camera-icon">
              <div class="camera-body"></div>
              <div class="camera-lens"></div>
              <div class="camera-cone"></div>
            </div>
            <div>
              <strong>EO Camera</strong>
              <span>光电 / 视线</span>
            </div>
          </div>

          <!-- YOLO -->
          <div class="yolo-station device-card">
            <div class="detector-icon">
              <div class="detector-frame"></div>
              <div class="detector-dot"></div>
            </div>
            <div>
              <strong>YOLO</strong>
              <span>目标检测</span>
            </div>
          </div>

          <!-- 无人机 -->
          <div class="uav-object">
            <div class="uav-wing left"></div>
            <div class="uav-wing right"></div>
            <div class="uav-core"></div>
            <div class="uav-rotor rotor-a"></div>
            <div class="uav-rotor rotor-b"></div>
            <div class="uav-rotor rotor-c"></div>
            <div class="uav-rotor rotor-d"></div>
            <span>UAV Target</span>
          </div>

          <!-- 信号线 -->
          <svg class="sensor-lines" viewBox="0 0 560 380" preserveAspectRatio="none">
            <path class="line radar-line" d="M110,275 C210,210 300,170 410,135" />
            <path class="line rf-line" d="M130,90 C230,120 310,135 410,135" />
            <path class="line eo-line" d="M450,288 C450,225 430,170 410,135" />
            <path class="line yolo-line" d="M490,80 C470,105 440,122 410,135" />
          </svg>

          <div class="fusion-dot">
            <span>融合入口</span>
          </div>
        </div>
      </section>

      <!-- 2. 知识图谱融合层 -->
      <section class="scene-card kg-card">
        <div class="card-head">
          <strong>知识图谱融合层</strong>
          <span>Entity / Relation / Candidate</span>
        </div>

        <div class="kg-canvas">
          <svg class="kg-lines" viewBox="0 0 560 380" preserveAspectRatio="none">
            <path class="kg-edge main" d="M280,185 L150,90" />
            <path class="kg-edge main" d="M280,185 L410,88" />
            <path class="kg-edge main" d="M280,185 L130,280" />
            <path class="kg-edge main" d="M280,185 L430,280" />
            <path class="kg-edge soft" d="M150,90 L410,88" />
            <path class="kg-edge soft" d="M130,280 L430,280" />
            <path class="kg-edge soft" d="M150,90 L130,280" />
            <path class="kg-edge soft" d="M410,88 L430,280" />
            <path class="kg-edge pulse-line" d="M130,280 C210,250 340,250 430,280" />
          </svg>

          <div class="graph-node center-node">
            <strong>KG Fusion</strong>
            <span>候选关联</span>
          </div>

          <div class="graph-node node-track">
            <i></i>
            <strong>Track</strong>
            <span>轨迹</span>
          </div>

          <div class="graph-node node-sensor">
            <i></i>
            <strong>Sensor</strong>
            <span>设备</span>
          </div>

          <div class="graph-node node-signal">
            <i></i>
            <strong>Signal</strong>
            <span>信号</span>
          </div>

          <div class="graph-node node-risk">
            <i></i>
            <strong>Risk</strong>
            <span>风险</span>
          </div>

          <div class="graph-node node-event">
            <i></i>
            <strong>Event</strong>
            <span>事件</span>
          </div>

          <div class="kg-mini-panel">
            <div>
              <span>关系组织</span>
              <strong>节点 · 边 · 子图</strong>
            </div>
            <div>
              <span>融合目标</span>
              <strong>候选池 · 排序 · 冲突解释</strong>
            </div>
          </div>
        </div>
      </section>

      <!-- 3. 大模型研判层 -->
      <section class="scene-card llm-card">
        <div class="card-head">
          <strong>大模型研判层</strong>
          <span>Prompt / Reasoning / Validator</span>
        </div>

        <div class="llm-canvas">
          <div class="token-area left-token">
            <div
              v-for="n in 8"
              :key="'l' + n"
              class="token token-blue"
              :style="{ animationDelay: `${n * 0.12}s` }"
            ></div>
          </div>

          <div class="llm-chip">
            <div class="chip-pins pins-left"></div>
            <div class="chip-pins pins-right"></div>
            <div class="chip-core">
              <strong>LLM Core</strong>
              <span>Evidence Reasoning</span>
            </div>
          </div>

          <div class="token-area right-token">
            <div
              v-for="n in 6"
              :key="'r' + n"
              class="token token-green"
              :style="{ animationDelay: `${n * 0.16}s` }"
            ></div>
          </div>

          <div class="prompt-box">
            <span>Structured Prompt</span>
            <p>可见证据 · 任务约束 · 输出格式</p>
          </div>

          <div class="decision-stack">
            <div class="decision-item confirm">
              <span>Confirm</span>
              <strong>高风险</strong>
            </div>
            <div class="decision-item uncertain">
              <span>Uncertain</span>
              <strong>人工复核</strong>
            </div>
            <div class="decision-item reject">
              <span>Reject</span>
              <strong>低风险</strong>
            </div>
          </div>

          <div class="validator-box">
            <strong>Validator</strong>
            <span>边界校验 / 证据约束 / 报告输出</span>
          </div>
        </div>
      </section>
    </div>

    <div class="capability-row">
      <div class="capability">
        <strong>多设备反无人机场景</strong>
        <span>抽象展示雷达、频谱、光电、视觉检测等多源设备协同感知。</span>
      </div>
      <div class="capability">
        <strong>知识图谱关系组织</strong>
        <span>抽象展示目标、轨迹、设备、信号、风险和事件之间的关系网络。</span>
      </div>
      <div class="capability">
        <strong>大模型辅助研判</strong>
        <span>抽象展示 Prompt 输入、推理核心、结构化裁决与 Validator 校验。</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineEmits(["navigate"]);
</script>

<style scoped>
.fusion-scene {
  overflow: hidden;
  border: 1px solid #d9e7f5;
  border-radius: 14px;
  background:
    radial-gradient(circle at 10% 15%, rgba(64, 158, 255, 0.16), transparent 28%),
    radial-gradient(circle at 86% 20%, rgba(103, 194, 58, 0.13), transparent 30%),
    linear-gradient(135deg, #f8fbff 0%, #edf5ff 50%, #ffffff 100%);
  box-shadow: 0 14px 36px rgba(23, 58, 96, 0.08);
}

.scene-header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  padding: 24px 26px 12px;
}

.scene-eyebrow {
  display: inline-flex;
  padding: 4px 10px;
  border-radius: 999px;
  background: #e8f2ff;
  color: #1d6fdc;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.04em;
}

.scene-header h2 {
  margin: 10px 0 6px;
  color: #0f2742;
  font-size: 26px;
  line-height: 1.3;
}

.scene-header p {
  margin: 0;
  max-width: 980px;
  color: #5f7287;
  line-height: 1.7;
}

.scene-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
  align-items: flex-start;
}

.scene-actions button {
  border: 1px solid #bfd9f5;
  background: #fff;
  color: #1d6fdc;
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
  font-weight: 700;
}

.scene-actions button:hover {
  background: #e8f2ff;
}

/* 主舞台高度加大，不再遮挡 */
.scene-stage {
  height: 520px;
  margin: 0 20px 18px;
  display: grid;
  grid-template-columns: 1.05fr 1fr 1.05fr;
  gap: 16px;
}

.scene-card {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(201, 220, 239, 0.95);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.86);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.65);
}

.card-head {
  position: absolute;
  left: 18px;
  top: 16px;
  z-index: 10;
}

.card-head strong {
  display: block;
  color: #102a43;
  font-size: 15px;
}

.card-head span {
  display: block;
  color: #73869b;
  margin-top: 4px;
  font-size: 12px;
}

/* ========== 多设备感知层 ========== */
.sensor-canvas,
.kg-canvas,
.llm-canvas {
  position: absolute;
  inset: 0;
}

.device-card {
  position: absolute;
  z-index: 5;
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 138px;
  padding: 12px;
  border: 1px solid #d9e7f5;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 10px 22px rgba(26, 72, 116, 0.08);
}

.device-card strong {
  display: block;
  color: #102a43;
  font-size: 14px;
}

.device-card span {
  display: block;
  color: #71849a;
  margin-top: 2px;
  font-size: 12px;
}

.radar-station {
  left: 34px;
  bottom: 42px;
}

.rf-station {
  left: 34px;
  top: 94px;
}

.eo-station {
  right: 34px;
  bottom: 46px;
}

.yolo-station {
  right: 34px;
  top: 92px;
}

.radar-icon {
  position: relative;
  width: 56px;
  height: 56px;
}

.radar-base {
  position: absolute;
  left: 22px;
  bottom: 4px;
  width: 12px;
  height: 24px;
  background: #1d6fdc;
  border-radius: 4px;
}

.radar-dish {
  position: absolute;
  left: 7px;
  top: 8px;
  width: 42px;
  height: 26px;
  border-radius: 42px 42px 10px 10px;
  background: linear-gradient(135deg, #409eff, #1d6fdc);
  transform: rotate(-15deg);
}

.radar-sweep {
  position: absolute;
  left: -92px;
  top: -92px;
  width: 240px;
  height: 240px;
  border-radius: 50%;
  background: conic-gradient(from 0deg, rgba(64, 158, 255, 0.35), rgba(64, 158, 255, 0.04), transparent 42%);
  animation: sweep 4s linear infinite;
  z-index: -1;
}

.radar-ring {
  position: absolute;
  left: 28px;
  top: 28px;
  border: 1px dashed rgba(64, 158, 255, 0.35);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  z-index: -1;
}

.r1 {
  width: 96px;
  height: 96px;
}

.r2 {
  width: 160px;
  height: 160px;
}

.r3 {
  width: 230px;
  height: 230px;
}

.antenna-icon {
  position: relative;
  width: 52px;
  height: 52px;
}

.antenna-pole {
  position: absolute;
  left: 23px;
  top: 10px;
  width: 6px;
  height: 34px;
  border-radius: 4px;
  background: #67c23a;
}

.antenna-wave {
  position: absolute;
  left: 26px;
  top: 25px;
  border: 2px solid rgba(103, 194, 58, 0.46);
  border-left: none;
  border-bottom: none;
  border-radius: 0 48px 0 0;
  transform: translateY(-50%) rotate(-45deg);
  animation: wave 2.2s ease-out infinite;
}

.w1 {
  width: 20px;
  height: 20px;
}

.w2 {
  width: 34px;
  height: 34px;
  animation-delay: 0.35s;
}

.w3 {
  width: 48px;
  height: 48px;
  animation-delay: 0.7s;
}

.camera-icon {
  position: relative;
  width: 56px;
  height: 44px;
}

.camera-body {
  position: absolute;
  left: 6px;
  top: 12px;
  width: 34px;
  height: 22px;
  border-radius: 7px;
  background: #e6a23c;
}

.camera-lens {
  position: absolute;
  right: 6px;
  top: 16px;
  width: 20px;
  height: 14px;
  border-radius: 4px;
  background: #b26a00;
}

.camera-cone {
  position: absolute;
  right: -38px;
  top: 0;
  width: 74px;
  height: 44px;
  background: linear-gradient(90deg, rgba(230, 162, 60, 0.28), transparent);
  clip-path: polygon(0 50%, 100% 0, 100% 100%);
}

.detector-icon {
  position: relative;
  width: 52px;
  height: 52px;
}

.detector-frame {
  position: absolute;
  inset: 8px;
  border: 3px solid #f56c6c;
  border-radius: 8px;
}

.detector-frame::before,
.detector-frame::after {
  content: "";
  position: absolute;
  background: #f56c6c;
}

.detector-frame::before {
  left: 8px;
  right: 8px;
  top: 50%;
  height: 2px;
}

.detector-frame::after {
  top: 8px;
  bottom: 8px;
  left: 50%;
  width: 2px;
}

.detector-dot {
  position: absolute;
  left: 23px;
  top: 23px;
  width: 6px;
  height: 6px;
  background: #f56c6c;
  border-radius: 50%;
  animation: blink 1.4s infinite;
}

.uav-object {
  position: absolute;
  left: 50%;
  top: 38%;
  z-index: 8;
  width: 126px;
  height: 86px;
  transform: translate(-50%, -50%);
  animation: uavFloat 3.6s ease-in-out infinite;
}

.uav-core {
  position: absolute;
  left: 44px;
  top: 31px;
  width: 38px;
  height: 24px;
  border-radius: 16px;
  background: linear-gradient(135deg, #ff922b, #d9480f);
  box-shadow: 0 10px 24px rgba(217, 72, 15, 0.28);
}

.uav-wing {
  position: absolute;
  top: 38px;
  width: 42px;
  height: 6px;
  border-radius: 6px;
  background: #d9480f;
}

.uav-wing.left {
  left: 4px;
}

.uav-wing.right {
  right: 4px;
}

.uav-rotor {
  position: absolute;
  width: 26px;
  height: 26px;
  border: 2px solid rgba(217, 72, 15, 0.55);
  border-radius: 50%;
  animation: rotor 0.8s linear infinite;
}

.rotor-a {
  left: 0;
  top: 14px;
}

.rotor-b {
  right: 0;
  top: 14px;
}

.rotor-c {
  left: 0;
  bottom: 8px;
}

.rotor-d {
  right: 0;
  bottom: 8px;
}

.uav-object span {
  position: absolute;
  left: 20px;
  right: 20px;
  bottom: -10px;
  text-align: center;
  color: #d9480f;
  font-size: 12px;
  font-weight: 800;
}

.sensor-lines {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.line {
  fill: none;
  stroke-width: 2.4;
  stroke-dasharray: 8 10;
  animation: dashMove 2.8s linear infinite;
}

.radar-line {
  stroke: rgba(64, 158, 255, 0.62);
}

.rf-line {
  stroke: rgba(103, 194, 58, 0.62);
}

.eo-line {
  stroke: rgba(230, 162, 60, 0.62);
}

.yolo-line {
  stroke: rgba(245, 108, 108, 0.62);
}

.fusion-dot {
  position: absolute;
  left: 72%;
  top: 35%;
  z-index: 7;
  width: 70px;
  height: 70px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: #e8f2ff;
  border: 2px solid #409eff;
  color: #1d6fdc;
  font-size: 12px;
  font-weight: 800;
  box-shadow: 0 12px 26px rgba(64, 158, 255, 0.18);
}

/* ========== KG 层 ========== */
.kg-lines {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.kg-edge {
  fill: none;
  stroke-width: 2;
  stroke-dasharray: 8 9;
  animation: dashMove 3s linear infinite;
}

.kg-edge.main {
  stroke: rgba(64, 158, 255, 0.56);
}

.kg-edge.soft {
  stroke: rgba(103, 194, 58, 0.34);
}

.pulse-line {
  stroke: rgba(230, 162, 60, 0.65);
  stroke-width: 3;
}

.graph-node {
  position: absolute;
  z-index: 5;
  min-width: 96px;
  padding: 10px;
  border: 1px solid #d9e7f5;
  border-radius: 14px;
  background: #fff;
  text-align: center;
  box-shadow: 0 10px 22px rgba(26, 72, 116, 0.08);
  animation: nodeFloat 3.4s ease-in-out infinite;
}

.graph-node i {
  display: block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin: 0 auto 5px;
}

.graph-node strong {
  display: block;
  color: #102a43;
  font-size: 14px;
}

.graph-node span {
  color: #71849a;
  font-size: 12px;
}

.center-node {
  left: 50%;
  top: 49%;
  width: 156px;
  padding: 18px 10px;
  transform: translate(-50%, -50%);
  color: #fff;
  background: linear-gradient(135deg, #1d6fdc, #409eff);
  border: none;
  box-shadow: 0 20px 38px rgba(64, 158, 255, 0.32);
}

.center-node strong,
.center-node span {
  color: #fff;
}

.node-track {
  left: 16%;
  top: 16%;
}

.node-track i {
  background: #409eff;
}

.node-sensor {
  right: 14%;
  top: 15%;
}

.node-sensor i {
  background: #67c23a;
}

.node-signal {
  left: 12%;
  bottom: 18%;
}

.node-signal i {
  background: #e6a23c;
}

.node-risk {
  right: 13%;
  bottom: 18%;
}

.node-risk i {
  background: #f56c6c;
}

.node-event {
  left: 50%;
  bottom: 8%;
  transform: translateX(-50%);
}

.node-event i {
  background: #722ed1;
}

.kg-mini-panel {
  position: absolute;
  left: 24px;
  right: 24px;
  bottom: 24px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.kg-mini-panel div {
  padding: 11px;
  border-radius: 10px;
  background: #f8fbff;
  border: 1px solid #dbe8f5;
}

.kg-mini-panel span {
  display: block;
  color: #73869b;
  font-size: 12px;
}

.kg-mini-panel strong {
  display: block;
  margin-top: 4px;
  color: #102a43;
}

/* ========== LLM 层 ========== */
.token-area {
  position: absolute;
  display: flex;
  gap: 8px;
}

.left-token {
  left: 36px;
  top: 94px;
}

.right-token {
  right: 36px;
  top: 94px;
}

.token {
  width: 30px;
  height: 18px;
  border-radius: 6px;
  opacity: 0;
  animation: tokenFlow 2.2s linear infinite;
}

.token-blue {
  background: linear-gradient(90deg, #d7ecff, #409eff);
}

.token-green {
  background: linear-gradient(90deg, #e1f5d8, #67c23a);
}

.llm-chip {
  position: absolute;
  left: 50%;
  top: 42%;
  width: 188px;
  height: 138px;
  transform: translate(-50%, -50%);
  border-radius: 22px;
  background: #102a43;
  box-shadow: 0 22px 44px rgba(16, 42, 67, 0.26);
}

.chip-core {
  position: absolute;
  inset: 18px;
  border-radius: 16px;
  background: linear-gradient(135deg, #173b5f, #244f7a);
  display: grid;
  place-items: center;
  text-align: center;
  color: #fff;
}

.chip-core strong {
  display: block;
  font-size: 20px;
}

.chip-core span {
  font-size: 12px;
  opacity: 0.85;
}

.chip-pins {
  position: absolute;
  top: 16px;
  bottom: 16px;
  width: 10px;
  background: repeating-linear-gradient(
    to bottom,
    #6aaeea 0 8px,
    transparent 8px 16px
  );
}

.pins-left {
  left: -10px;
}

.pins-right {
  right: -10px;
}

.prompt-box {
  position: absolute;
  left: 34px;
  bottom: 150px;
  width: 178px;
  padding: 12px;
  border: 1px solid #d9e7f5;
  border-radius: 12px;
  background: #fff;
}

.prompt-box span {
  color: #1d6fdc;
  font-weight: 800;
  font-size: 12px;
}

.prompt-box p {
  margin: 5px 0 0;
  color: #63768a;
  font-size: 13px;
}

.decision-stack {
  position: absolute;
  right: 34px;
  bottom: 118px;
  width: 180px;
  display: grid;
  gap: 8px;
}

.decision-item {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid #d9e7f5;
  background: #fff;
}

.decision-item span {
  color: #71849a;
  font-size: 12px;
}

.decision-item strong {
  color: #102a43;
}

.confirm {
  background: #ecf5ff;
}

.uncertain {
  background: #fff7ed;
}

.reject {
  background: #f6ffed;
}

.validator-box {
  position: absolute;
  left: 34px;
  right: 34px;
  bottom: 32px;
  padding: 14px;
  border-radius: 12px;
  border: 1px solid #d9e7f5;
  background: #f8fbff;
}

.validator-box strong {
  display: block;
  color: #1d6fdc;
  font-size: 14px;
}

.validator-box span {
  display: block;
  margin-top: 5px;
  color: #63768a;
}

.capability-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  padding: 0 20px 20px;
}

.capability {
  padding: 14px;
  border: 1px solid #dbe8f5;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.86);
}

.capability strong {
  display: block;
  color: #102a43;
  margin-bottom: 6px;
}

.capability span {
  color: #63768a;
  line-height: 1.6;
  font-size: 13px;
}

/* 动画 */
@keyframes sweep {
  to {
    transform: rotate(360deg);
  }
}

@keyframes wave {
  0% {
    transform: translateY(-50%) rotate(-45deg) scale(0.6);
    opacity: 0.8;
  }
  100% {
    transform: translateY(-50%) rotate(-45deg) scale(1.3);
    opacity: 0;
  }
}

@keyframes rotor {
  to {
    transform: rotate(360deg);
  }
}

@keyframes dashMove {
  to {
    stroke-dashoffset: -90;
  }
}

@keyframes uavFloat {
  0%,
  100% {
    transform: translate(-50%, -50%);
  }
  50% {
    transform: translate(calc(-50% - 12px), calc(-50% + 10px));
  }
}

@keyframes nodeFloat {
  0%,
  100% {
    margin-top: 0;
  }
  50% {
    margin-top: -8px;
  }
}

@keyframes tokenFlow {
  0% {
    transform: translateX(-30px);
    opacity: 0;
  }
  20% {
    opacity: 0.85;
  }
  75% {
    opacity: 0.85;
  }
  100% {
    transform: translateX(90px);
    opacity: 0;
  }
}

@keyframes blink {
  0%,
  100% {
    opacity: 0.35;
  }
  50% {
    opacity: 1;
  }
}

@media (max-width: 1500px) {
  .scene-stage {
    height: auto;
    grid-template-columns: 1fr;
  }

  .scene-card {
    height: 500px;
  }

  .scene-header {
    flex-direction: column;
  }

  .capability-row {
    grid-template-columns: 1fr;
  }
}
</style>