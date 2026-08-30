<template>
  <el-container class="layout-root">
    <el-aside width="238px" class="layout-aside">
      <SideMenu />
    </el-aside>
    <el-container class="layout-main">
      <el-header class="topbar">
        <div class="topbar-title">
          <strong>基于知识图谱与大模型的无人机多源感知融合分析系统 V1.0</strong>
          <span>低空多源感知 · 知识图谱 · LLM 辅助研判</span>
        </div>
        <div class="topbar-actions">
          <el-tag type="success">系统数据在线</el-tag>
          <el-tag>Neo4j 可选</el-tag>
          <el-button @click="logout">退出</el-button>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRouter } from "vue-router";
import SideMenu from "./SideMenu.vue";

const router = useRouter();
const logout = () => {
  localStorage.removeItem("token");
  router.push("/login");
};
</script>

<style scoped>
.layout-root {
  height: 100vh;
  min-height: 0;
  overflow: hidden;
}

.layout-aside,
.layout-main {
  min-height: 0;
  overflow: hidden;
}

.topbar {
  height: 58px;
  background: #ffffff;
  border-bottom: 1px solid #dfe8f2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  box-sizing: border-box;
}

.topbar-title {
  display: flex;
  align-items: baseline;
  gap: 14px;
  min-width: 0;
}

.topbar-title strong {
  color: #142238;
  white-space: nowrap;
}

.topbar-title span {
  color: #69788c;
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.topbar-actions {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  gap: 8px;
}

.main-content {
  height: calc(100vh - 58px);
  min-height: 0;
  overflow: hidden;
  padding: 0;
  background: #eef3f8;
  box-sizing: border-box;
}
</style>
