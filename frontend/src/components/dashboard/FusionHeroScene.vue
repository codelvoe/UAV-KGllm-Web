<template>
  <div class="fusion-hero">
    <div class="scene-canvas">
      <div class="grid-bg"></div>
      <div class="glow glow-a"></div>
      <div class="glow glow-b"></div>

      <svg class="link-layer" viewBox="0 0 1400 520" preserveAspectRatio="none">
        <path class="sense-line radar-line" d="M95 410 C250 330 410 282 580 260" />
        <path class="sense-line rf-line" d="M105 120 C270 172 430 220 580 260" />
        <path class="sense-line eo-line" d="M170 282 C310 284 450 274 580 260" />
        <path class="sense-line yolo-line" d="M365 85 C445 130 525 190 580 260" />
        <path class="sense-line uav-line" d="M500 178 C525 215 552 238 580 260" />

        <path class="kg-line" d="M672 260 C755 210 835 172 918 144" />
        <path class="kg-line" d="M918 144 C960 182 992 220 1025 260" />
        <path class="kg-line" d="M918 144 C875 240 840 310 792 380" />
        <path class="kg-line" d="M918 144 C940 282 988 354 1050 410" />
        <path class="kg-line" d="M918 144 C988 152 1060 172 1135 206" />

        <path class="llm-line" d="M1035 260 C1115 260 1190 260 1272 260" />
      </svg>

      <div class="scene-label top-left">Multi-Sensor Perception</div>
      <div class="scene-label mid-label">Knowledge Graph Fusion</div>
      <div class="scene-label right-label">LLM Decision Flow</div>

      <div class="device radar-device">
        <div class="radar-visual">
          <span class="radar-sweep"></span>
          <span class="radar-ring ring-1"></span>
          <span class="radar-ring ring-2"></span>
          <span class="radar-ring ring-3"></span>
          <span class="radar-base"></span>
        </div>
        <div class="device-text">
          <strong>Radar</strong>
          <span>空间 / 运动</span>
        </div>
      </div>

      <div class="device rf-device">
        <div class="rf-icon">
          <i class="pole"></i>
          <i class="wave wave-1"></i>
          <i class="wave wave-2"></i>
          <i class="wave wave-3"></i>
        </div>
        <div class="device-text">
          <strong>RF Spectrum</strong>
          <span>频率 / 信号</span>
        </div>
      </div>

      <div class="device eo-device">
        <div class="camera-icon">
          <i class="camera-body"></i>
          <i class="camera-lens"></i>
          <i class="sight-cone"></i>
        </div>
        <div class="device-text">
          <strong>EO Camera</strong>
          <span>光电 / 视线</span>
        </div>
      </div>

      <div class="device yolo-device">
        <div class="yolo-icon">
          <i class="detect-box"></i>
          <i class="detect-dot"></i>
        </div>
        <div class="device-text">
          <strong>YOLO</strong>
          <span>目标检测</span>
        </div>
      </div>

      <div class="uav-target">
        <i class="rotor r1"></i>
        <i class="rotor r2"></i>
        <i class="rotor r3"></i>
        <i class="rotor r4"></i>
        <i class="arm arm-a"></i>
        <i class="arm arm-b"></i>
        <i class="uav-core"></i>
        <span>UAV Target</span>
      </div>

      <button class="fusion-center" @click="$emit('navigate', '/fusion')">
        <i class="fusion-pulse"></i>
        <strong>Fusion Center</strong>
        <span>多源证据汇聚</span>
      </button>

      <button class="kg-core" @click="$emit('navigate', '/kg')">
        <strong>KG</strong>
        <span>关系组织</span>
      </button>
      <div class="kg-node node-track">Track</div>
      <div class="kg-node node-signal">Signal</div>
      <div class="kg-node node-risk">Risk</div>
      <div class="kg-node node-event">Event</div>

      <button class="llm-core" @click="$emit('navigate', '/llm-decision')">
        <i class="chip-pin pin-left"></i>
        <i class="chip-pin pin-right"></i>
        <strong>LLM Core</strong>
        <span>结构化研判</span>
      </button>

      <div class="token-flow token-left">
        <i v-for="n in 8" :key="'left' + n" :style="{ animationDelay: `${n * 0.12}s` }"></i>
      </div>
      <div class="token-flow token-right">
        <i v-for="n in 7" :key="'right' + n" :style="{ animationDelay: `${n * 0.16}s` }"></i>
      </div>

      <div class="decision-stack">
        <div class="decision-item confirm">
          <span>Confirm</span>
          <strong>High</strong>
        </div>
        <div class="decision-item uncertain">
          <span>Uncertain</span>
          <strong>Review</strong>
        </div>
        <div class="decision-item reject">
          <span>Reject</span>
          <strong>Low</strong>
        </div>
      </div>

      <div class="legend-strip">
        <span><i class="dot radar"></i>雷达</span>
        <span><i class="dot rf"></i>频谱</span>
        <span><i class="dot eo"></i>光电</span>
        <span><i class="dot kg"></i>图谱关系</span>
        <span><i class="dot llm"></i>模型研判</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineEmits(["navigate"]);
</script>

<style scoped>
.fusion-hero {
  height: 100%;
  min-height: 0;
  overflow: hidden;
  border: 1px solid #dbe8f5;
  border-radius: 16px;
  background:
    radial-gradient(circle at 16% 24%, rgba(64, 158, 255, 0.18), transparent 34%),
    radial-gradient(circle at 82% 30%, rgba(103, 194, 58, 0.13), transparent 33%),
    linear-gradient(135deg, #f8fbff 0%, #edf5ff 52%, #ffffff 100%);
  box-shadow: 0 16px 36px rgba(30, 63, 103, 0.08);
}

.scene-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

.grid-bg {
  position: absolute;
  inset: 0;
  opacity: 0.45;
  background-image:
    linear-gradient(rgba(36, 104, 216, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(36, 104, 216, 0.08) 1px, transparent 1px);
  background-size: 36px 36px;
  mask-image: radial-gradient(circle at 52% 48%, black 0%, transparent 82%);
}

.glow {
  position: absolute;
  width: 320px;
  height: 320px;
  border-radius: 50%;
  filter: blur(20px);
  opacity: 0.2;
}

.glow-a {
  left: 36%;
  top: 30%;
  background: #409eff;
}

.glow-b {
  right: 7%;
  top: 23%;
  background: #67c23a;
}

.scene-label {
  position: absolute;
  z-index: 16;
  padding: 5px 10px;
  border: 1px solid #d7e7f8;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.78);
  color: #2468d8;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.04em;
}

.top-left {
  left: 22px;
  top: 18px;
}

.mid-label {
  left: 58%;
  top: 18px;
  transform: translateX(-50%);
}

.right-label {
  right: 22px;
  top: 18px;
}

.link-layer {
  position: absolute;
  inset: 0;
  z-index: 3;
  pointer-events: none;
}

.sense-line,
.kg-line,
.llm-line {
  fill: none;
  stroke-width: 2.5;
  stroke-dasharray: 8 10;
  animation: dashMove 3.2s linear infinite;
}

.radar-line {
  stroke: rgba(64, 158, 255, 0.64);
}

.rf-line {
  stroke: rgba(103, 194, 58, 0.65);
}

.eo-line {
  stroke: rgba(230, 162, 60, 0.66);
}

.yolo-line {
  stroke: rgba(245, 108, 108, 0.62);
}

.uav-line {
  stroke: rgba(217, 72, 15, 0.6);
}

.kg-line {
  stroke: rgba(64, 158, 255, 0.48);
}

.llm-line {
  stroke: rgba(16, 42, 67, 0.54);
}

.device {
  position: absolute;
  z-index: 12;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border: 1px solid #dbe8f5;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.84);
  box-shadow: 0 10px 22px rgba(30, 63, 103, 0.08);
}

.device strong {
  display: block;
  color: #102a43;
  font-size: 13px;
  line-height: 1.1;
}

.device span {
  color: #667b91;
  font-size: 11px;
}

.radar-device {
  left: 42px;
  bottom: 58px;
}

.rf-device {
  left: 48px;
  top: 86px;
}

.eo-device {
  left: 72px;
  top: 49%;
}

.yolo-device {
  left: 300px;
  top: 64px;
}

.radar-visual {
  position: relative;
  width: 58px;
  height: 58px;
}

.radar-sweep {
  position: absolute;
  left: -40px;
  top: -40px;
  width: 136px;
  height: 136px;
  border-radius: 50%;
  background: conic-gradient(from 0deg, rgba(64, 158, 255, 0.42), rgba(64, 158, 255, 0.07), transparent 42%);
  animation: sweep 4s linear infinite;
}

.radar-ring {
  position: absolute;
  inset: 50%;
  border: 1px solid rgba(64, 158, 255, 0.32);
  border-radius: 50%;
  transform: translate(-50%, -50%);
}

.ring-1 {
  width: 30px;
  height: 30px;
}

.ring-2 {
  width: 48px;
  height: 48px;
}

.ring-3 {
  width: 66px;
  height: 66px;
}

.radar-base {
  position: absolute;
  left: 25px;
  bottom: 8px;
  width: 8px;
  height: 22px;
  border-radius: 5px;
  background: #409eff;
}

.rf-icon,
.camera-icon,
.yolo-icon {
  position: relative;
  width: 46px;
  height: 46px;
}

.pole {
  position: absolute;
  left: 21px;
  top: 10px;
  width: 6px;
  height: 28px;
  border-radius: 4px;
  background: #67c23a;
}

.wave {
  position: absolute;
  left: 23px;
  top: 24px;
  border: 2px solid rgba(103, 194, 58, 0.48);
  border-left: 0;
  border-bottom: 0;
  border-radius: 0 44px 0 0;
  transform: translateY(-50%) rotate(-45deg);
  animation: wave 2.2s ease-out infinite;
}

.wave-1 {
  width: 16px;
  height: 16px;
}

.wave-2 {
  width: 28px;
  height: 28px;
  animation-delay: 0.32s;
}

.wave-3 {
  width: 40px;
  height: 40px;
  animation-delay: 0.64s;
}

.camera-body {
  position: absolute;
  left: 4px;
  top: 13px;
  width: 28px;
  height: 20px;
  border-radius: 7px;
  background: #e6a23c;
}

.camera-lens {
  position: absolute;
  right: 4px;
  top: 17px;
  width: 17px;
  height: 12px;
  border-radius: 4px;
  background: #b26a00;
}

.sight-cone {
  position: absolute;
  right: -42px;
  top: 5px;
  width: 72px;
  height: 36px;
  background: linear-gradient(90deg, rgba(230, 162, 60, 0.28), transparent);
  clip-path: polygon(0 50%, 100% 0, 100% 100%);
}

.detect-box {
  position: absolute;
  inset: 9px;
  border: 3px solid #f56c6c;
  border-radius: 8px;
}

.detect-dot {
  position: absolute;
  left: 20px;
  top: 20px;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #f56c6c;
  animation: blink 1.2s infinite;
}

.uav-target {
  position: absolute;
  left: 36%;
  top: 32%;
  z-index: 15;
  width: 128px;
  height: 88px;
  transform: translate(-50%, -50%);
  animation: uavFloat 3.4s ease-in-out infinite;
}

.uav-core {
  position: absolute;
  left: 46px;
  top: 32px;
  width: 36px;
  height: 22px;
  border-radius: 16px;
  background: linear-gradient(135deg, #ff922b, #d9480f);
  box-shadow: 0 10px 24px rgba(217, 72, 15, 0.28);
}

.arm {
  position: absolute;
  left: 18px;
  top: 42px;
  width: 92px;
  height: 5px;
  border-radius: 4px;
  background: #d9480f;
}

.arm-b {
  transform: rotate(90deg);
}

.rotor {
  position: absolute;
  width: 27px;
  height: 27px;
  border: 2px solid rgba(217, 72, 15, 0.55);
  border-radius: 50%;
  animation: rotor 0.8s linear infinite;
}

.r1 {
  left: 0;
  top: 12px;
}

.r2 {
  right: 0;
  top: 12px;
}

.r3 {
  left: 0;
  bottom: 7px;
}

.r4 {
  right: 0;
  bottom: 7px;
}

.uav-target span {
  position: absolute;
  left: 0;
  right: 0;
  bottom: -6px;
  color: #d9480f;
  font-size: 12px;
  font-weight: 800;
  text-align: center;
}

.fusion-center,
.kg-core,
.llm-core {
  position: absolute;
  z-index: 18;
  border: 0;
  cursor: pointer;
  font-family: inherit;
}

.fusion-center {
  left: 43.5%;
  top: 50%;
  width: 160px;
  height: 86px;
  transform: translate(-50%, -50%);
  display: grid;
  place-items: center;
  border-radius: 21px;
  background: linear-gradient(135deg, #1d6fdc, #409eff);
  color: #fff;
  box-shadow: 0 18px 36px rgba(64, 158, 255, 0.3);
}

.fusion-center strong {
  display: block;
  font-size: 16px;
}

.fusion-center span,
.kg-core span,
.llm-core span {
  display: block;
  font-size: 12px;
  opacity: 0.86;
}

.fusion-pulse {
  position: absolute;
  inset: -16px;
  border: 1px solid rgba(64, 158, 255, 0.48);
  border-radius: 28px;
  animation: pulse 2s ease-out infinite;
}

.kg-core {
  left: 66%;
  top: 28%;
  width: 108px;
  padding: 13px;
  border: 1px solid #d9e7f5;
  border-radius: 15px;
  background: #fff;
  color: #102a43;
  box-shadow: 0 10px 22px rgba(26, 72, 116, 0.08);
  text-align: center;
}

.kg-core strong {
  display: block;
  color: #1d6fdc;
  font-size: 22px;
}

.kg-node {
  position: absolute;
  z-index: 16;
  padding: 7px 10px;
  border: 1px solid #d9e7f5;
  border-radius: 999px;
  background: #fff;
  box-shadow: 0 10px 22px rgba(26, 72, 116, 0.08);
  font-size: 12px;
  font-weight: 800;
}

.node-track {
  left: 59%;
  top: 15%;
  color: #1d6fdc;
}

.node-signal {
  left: 58%;
  bottom: 25%;
  color: #b26a00;
}

.node-risk {
  left: 75%;
  bottom: 26%;
  color: #cf1322;
}

.node-event {
  left: 69%;
  bottom: 13%;
  color: #722ed1;
}

.llm-core {
  right: 72px;
  top: 47%;
  width: 150px;
  height: 96px;
  display: grid;
  place-items: center;
  border-radius: 20px;
  background: #102a43;
  color: #fff;
  box-shadow: 0 20px 40px rgba(16, 42, 67, 0.28);
  text-align: center;
}

.llm-core strong {
  font-size: 17px;
}

.chip-pin {
  position: absolute;
  top: 14px;
  bottom: 14px;
  width: 8px;
  background: repeating-linear-gradient(to bottom, #6aaeea 0 8px, transparent 8px 15px);
}

.pin-left {
  left: -8px;
}

.pin-right {
  right: -8px;
}

.token-flow {
  position: absolute;
  z-index: 14;
  display: flex;
  gap: 6px;
}

.token-left {
  left: 57%;
  top: 11%;
}

.token-right {
  right: 34px;
  top: 19%;
}

.token-flow i {
  width: 24px;
  height: 13px;
  border-radius: 6px;
  opacity: 0;
  background: linear-gradient(90deg, #d7ecff, #409eff);
  animation: tokenFlow 2.2s linear infinite;
}

.token-right i {
  background: linear-gradient(90deg, #e1f5d8, #67c23a);
}

.decision-stack {
  position: absolute;
  right: 38px;
  bottom: 34px;
  z-index: 17;
  width: 176px;
  display: grid;
  gap: 7px;
}

.decision-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 10px;
  border: 1px solid #d9e7f5;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.9);
}

.decision-item span {
  color: #72859a;
  font-size: 12px;
}

.decision-item strong {
  font-size: 12px;
}

.confirm strong {
  color: #18a058;
}

.uncertain strong {
  color: #d88a00;
}

.reject strong {
  color: #d64545;
}

.legend-strip {
  position: absolute;
  left: 20px;
  bottom: 16px;
  z-index: 20;
  display: flex;
  gap: 12px;
  padding: 8px 10px;
  border: 1px solid #dbe8f5;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.76);
  color: #5f7287;
  font-size: 11px;
  font-weight: 700;
}

.legend-strip span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot.radar {
  background: #409eff;
}

.dot.rf {
  background: #67c23a;
}

.dot.eo {
  background: #e6a23c;
}

.dot.kg {
  background: #1d6fdc;
}

.dot.llm {
  background: #102a43;
}

@keyframes sweep {
  to {
    transform: rotate(360deg);
  }
}

@keyframes wave {
  0% {
    transform: translateY(-50%) rotate(-45deg) scale(0.6);
    opacity: 0.85;
  }
  100% {
    transform: translateY(-50%) rotate(-45deg) scale(1.35);
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

@keyframes pulse {
  0% {
    transform: scale(0.92);
    opacity: 0.75;
  }
  100% {
    transform: scale(1.16);
    opacity: 0;
  }
}

@keyframes uavFloat {
  0%,
  100% {
    transform: translate(-50%, -50%);
  }
  50% {
    transform: translate(calc(-50% - 10px), calc(-50% + 8px));
  }
}

@keyframes tokenFlow {
  0% {
    transform: translateX(-24px);
    opacity: 0;
  }
  20%,
  80% {
    opacity: 0.86;
  }
  100% {
    transform: translateX(70px);
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

@media (max-height: 820px) {
  .scene-label {
    top: 12px;
  }

  .radar-device {
    bottom: 46px;
  }

  .decision-stack {
    bottom: 24px;
  }

  .legend-strip {
    bottom: 12px;
  }
}
</style>
