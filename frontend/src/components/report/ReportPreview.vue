<template>
  <div class="preview">
    <h2>{{ draft.title || "无人机多源融合研判报告" }}</h2>
    <div v-if="!(draft.items || []).length" class="empty-hint">
      暂无报告条目
    </div>
    <section v-for="(item, index) in draft.items || []" :key="index">
      <h3>{{ index + 1 }}. {{ item.title }}</h3>
      <p>{{ item.content }}</p>
    </section>
  </div>
</template>

<script setup>
defineProps({ draft: Object });
</script>

<style scoped>
.preview {
  background: #fff;
  padding: 24px;
  border: 1px solid #dfe8f2;
  border-radius: 8px;
  min-height: 640px;
  line-height: 1.8;
}

h2 {
  margin-top: 0;
  color: #142238;
}

section {
  border-top: 1px solid #edf2f7;
  padding-top: 12px;
}
</style>
