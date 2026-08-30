<template>
  <div class="input">
    <el-input
      v-model="text"
      placeholder="输入问题"
      @keyup.enter="send"
    /><el-button type="primary" @click="send">发送</el-button>
  </div>
</template>
<script setup>
import { ref } from "vue";
const emit = defineEmits(["send"]);
const text = ref("");
const send = () => {
  if (text.value.trim()) {
    emit("send", text.value);
    text.value = "";
  }
};
</script>
<style scoped>
.input {
  display: flex;
  gap: 8px;
}
</style>
