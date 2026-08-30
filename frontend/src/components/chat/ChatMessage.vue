<template>
  <div :class="['msg', role]">
    <div class="bubble">{{ content }}</div>
  </div>
</template>
<script setup>
defineProps({ role: String, content: String });
</script>
<style scoped>
.msg {
  display: flex;
  margin: 10px 0;
}
.msg.user {
  justify-content: flex-end;
}
.bubble {
  max-width: 70%;
  padding: 10px 12px;
  border-radius: 8px;
  background: #eef3fb;
}
.user .bubble {
  background: #1d75d0;
  color: #fff;
}
</style>
