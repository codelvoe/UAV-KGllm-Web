<template>
  <el-menu
    router
    :default-active="$route.path"
    class="side-menu"
    background-color="#0d1b2f"
    text-color="#d8e4f3"
    active-text-color="#7db2ff"
  >
    <div class="brand">
      <div class="brand-mark">KG</div>
      <div>
        <strong>UAV KG-LLM</strong>
        <span>融合分析系统</span>
      </div>
    </div>
    <el-menu-item index="/dashboard"><el-icon><DataBoard /></el-icon>系统首页</el-menu-item>
    <el-menu-item index="/data"><el-icon><Files /></el-icon>多模态数据管理</el-menu-item>
    <el-menu-item index="/tracks"><el-icon><Connection /></el-icon>轨迹证据管理</el-menu-item>
    <el-menu-item index="/kg"><el-icon><Share /></el-icon>知识图谱可视化</el-menu-item>
    <el-menu-item index="/fusion"><el-icon><Operation /></el-icon>KG融合候选分析</el-menu-item>
    <el-menu-item index="/llm-decision"><el-icon><Aim /></el-icon>大模型智能研判</el-menu-item>
    <el-menu-item index="/chat"><el-icon><ChatDotRound /></el-icon>大模型对话助手</el-menu-item>
    <el-menu-item index="/experiments"><el-icon><TrendCharts /></el-icon>性能评估与运行分析</el-menu-item>
    <el-menu-item index="/yolo-detection"><el-icon><VideoCamera /></el-icon>YOLO目标探测</el-menu-item>
    <el-menu-item index="/settings"><el-icon><Setting /></el-icon>系统设置</el-menu-item>
  </el-menu>
</template>

<style scoped>
.side-menu {
  height: 100vh;
  border-right: 0;
  overflow: hidden;
}

.brand {
  height: 58px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 16px;
  color: #fff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  box-sizing: border-box;
}

.brand-mark {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: #2468d8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
}

.brand strong,
.brand span {
  display: block;
}

.brand span {
  margin-top: 2px;
  color: #9fb3cc;
  font-size: 11px;
}
</style>
