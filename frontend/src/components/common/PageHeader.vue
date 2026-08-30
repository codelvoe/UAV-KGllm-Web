<template>
  <div class="page-header">
    <div>
      <div class="eyebrow">
        {{ eyebrow || "UAV KG-LLM Analysis Workbench" }}
      </div>
      <h1>{{ title }}</h1>
      <p>{{ subtitle }}</p>
    </div>
    <div v-if="$slots.extra" class="page-header-extra">
      <slot name="extra" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  subtitle: String,
  eyebrow: String,
});
</script>

<style scoped>
.page-header {
  height: 78px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 14px;
}

.eyebrow {
  color: #2468d8;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  margin-bottom: 5px;
}

h1 {
  margin: 0;
  color: #142238;
  font-size: 22px;
  line-height: 1.25;
}

p {
  margin: 6px 0 0;
  color: #69788c;
}

.page-header-extra {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
