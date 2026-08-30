<template>
  <div class="login-page">
    <div class="login-card">
      <h1>基于知识图谱与大模型的无人机多源感知融合分析系统</h1>
      <p>多源感知 · 知识图谱 · 融合研判</p>
      <el-form :model="form" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-button type="primary" size="large" class="full" @click="login"
          >登录系统</el-button
        >
      </el-form>
      <div class="hint">默认账号：admin / 123456</div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from "vue";
import { useRouter } from "vue-router";
import request from "../api/request";

const router = useRouter();
const form = reactive({ username: "admin", password: "123456" });

const login = async () => {
  const { data } = await request.post("/auth/login", form);
  if (data.success) {
    localStorage.setItem("token", data.token);
    router.push("/dashboard");
  }
};
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #eef5ff, #f8fbff);
}

.login-card {
  width: 430px;
  padding: 36px;
  background: #fff;
  border: 1px solid #e5edf7;
  border-radius: 8px;
  box-shadow: 0 18px 50px rgba(20, 52, 86, 0.12);
}

h1 {
  font-size: 24px;
  line-height: 1.35;
  margin: 0 0 10px;
  color: #102a43;
}

p {
  color: #60758f;
  margin-bottom: 24px;
}

.full {
  width: 100%;
}

.hint {
  margin-top: 14px;
  color: #7b8ba3;
  font-size: 13px;
}
</style>
