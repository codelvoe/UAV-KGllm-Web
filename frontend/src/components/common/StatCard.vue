<template>
  <div class="kpi-card">
    <div class="kpi-label">{{ label }}</div>
    <div class="kpi-value">{{ value }}</div>
    <div class="kpi-desc">{{ desc }}</div>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  value: [String, Number],
  desc: String,
});
</script>
