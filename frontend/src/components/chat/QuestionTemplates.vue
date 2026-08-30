<template>
  <div class="templates">
    <el-tag v-for="q in questions" :key="q" @click="$emit('pick', q)">{{
      q
    }}</el-tag>
  </div>
</template>

<script setup>
const questions = [
  "当前数据概况",
  "图谱规模分析",
  "KG Fusion 是什么？",
  "KG-Heuristic 是什么？",
  "自然冲突为什么失败？",
  "重复频谱是什么意思？",
  "缺失频谱场景结果如何？",
  "请生成阶段性总结",
];
</script>

<style scoped>
.templates {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.el-tag {
  cursor: pointer;
}
</style>
