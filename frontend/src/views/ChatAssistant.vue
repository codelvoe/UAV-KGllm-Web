<template>
  <div class="page chat-page">
    <PageHeader
      title="大模型对话助手"
      subtitle="调用本地 Ollama 模型，支持项目问答、普通交流、概念解释、汇报表达组织和连续追问。"
      eyebrow="Ollama Copilot"
    >
      <template #extra>
        <el-tag :type="ollama.connected ? 'success' : 'danger'">
          Ollama：{{ ollama.connected ? "已连接" : "未连接" }}
        </el-tag>
        <el-tag v-if="ollama.models?.length"
          >模型：{{ ollama.models[0] }}</el-tag
        >
      </template>
    </PageHeader>

    <div class="chat-layout">
      <div class="panel side-panel">
        <div class="section-title">
          <div>
            <h3>会话列表</h3>
            <p>{{ sessions.length }} 个会话</p>
          </div>
        </div>

        <el-button type="primary" style="width: 100%" @click="newChat"
          >新建对话</el-button
        >

        <div class="session-list">
          <el-menu :default-active="session.session_id">
            <el-menu-item
              v-for="item in sessions"
              :key="item.session_id"
              :index="item.session_id"
              @click="selectSession(item)"
            >
              <span class="session-title">{{ item.title }}</span>
            </el-menu-item>
          </el-menu>
        </div>

        <div class="quick-section">
          <div class="section-title compact">
            <div>
              <h3>快捷问题</h3>
              <p>点击后直接发送</p>
            </div>
          </div>
          <QuestionTemplates @pick="send" />
        </div>
      </div>

      <div class="panel chat-main">
        <div class="chat-header">
          <div class="section-title compact">
            <div>
              <h3>主对话区</h3>
              <p>消息只在中间区域内部滚动，不撑开整个页面</p>
            </div>
            <el-tag effect="plain">{{ messages.length }} 条消息</el-tag>
          </div>
        </div>

        <div ref="messagesRef" class="messages">
          <ChatMessage
            v-for="(message, index) in messages"
            :key="index"
            :role="message.role"
            :content="message.content"
          />

          <div v-if="loading" class="analysis-step loading-step">
            <div class="step-index">...</div>
            <div>本地 Ollama 正在生成回答，请稍候。</div>
            <el-tag type="warning">生成中</el-tag>
          </div>

          <div v-if="messages.length === 0 && !loading" class="empty-chat">
            <div class="empty-icon">问</div>
            <h3>开始一次对话</h3>
            <p>
              可以询问系统功能、实验结果、KG
              Fusion、自然冲突失败原因，也可以正常交流、做简单计算、解释概念或帮你组织汇报语言。
            </p>
          </div>
        </div>

        <div class="chat-input-wrap">
          <ChatInput @send="send" />
        </div>
      </div>

      <div class="panel context-panel">
        <div class="section-title">
          <div>
            <h3>上下文与证据</h3>
            <p>项目相关问题会优先参考这些背景</p>
          </div>
        </div>

        <div class="context-scroll">
          <div class="detail-list">
            <div class="detail-item">
              <div class="detail-label">当前数据</div>
              <div class="detail-value">
                雷达 294 条轨迹，频谱 2 条轨迹，视觉 24 条轨迹。
              </div>
            </div>
            <div class="detail-item">
              <div class="detail-label">当前图谱</div>
              <div class="detail-value">53619 个节点 / 105420 条边。</div>
            </div>
            <div class="detail-item">
              <div class="detail-label">关注场景</div>
              <div class="detail-value status-risk">
                自然冲突、模态缺失、重复频谱。
              </div>
            </div>
            <div class="detail-item">
              <div class="detail-label">模型接口</div>
              <div class="detail-value">
                {{ ollama.url || "http://localhost:11434/api/tags" }}
              </div>
            </div>
          </div>

          <div class="right-section">
            <div class="section-title compact">
              <div>
                <h3>证据引用</h3>
                <p>项目问答可用的上下文标签</p>
              </div>
            </div>
            <div class="tag-line">
              <el-tag>KG Fusion</el-tag>
              <el-tag type="warning">自然冲突</el-tag>
              <el-tag>F1 值 / 虚警率</el-tag>
              <el-tag>轨迹级摘要</el-tag>
            </div>
          </div>

          <div class="right-section">
            <div class="section-title compact">
              <div>
                <h3>推荐追问</h3>
                <p>围绕当前系统继续提问</p>
              </div>
            </div>
            <div class="flow-list">
              <div
                v-for="question in followUps"
                :key="question"
                class="analysis-step follow-up"
                @click="send(question)"
              >
                <div class="step-index">?</div>
                <div>{{ question }}</div>
                <el-tag>提问</el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-bottom">
      <div class="panel info-card">
        <div class="section-title compact"><h3>对话能力</h3></div>
        <p>
          支持项目内问答、实验解释、失败诊断、报告语言组织，也支持普通沟通、简单计算和概念解释。
        </p>
      </div>
      <div class="panel info-card">
        <div class="section-title compact"><h3>模型使用边界</h3></div>
        <p>
          项目事实优先基于已有系统数据；没有依据的实时传感器输入、隐藏标签参与推理等内容会明确说明不确定。
        </p>
      </div>
      <div class="panel info-card">
        <div class="section-title compact"><h3>异常处理</h3></div>
        <p>
          Ollama
          未连接、模型未拉取或接口异常时，页面会返回具体调用失败原因，便于检查本地服务。
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref } from "vue";
import PageHeader from "../components/common/PageHeader.vue";
import ChatInput from "../components/chat/ChatInput.vue";
import ChatMessage from "../components/chat/ChatMessage.vue";
import QuestionTemplates from "../components/chat/QuestionTemplates.vue";
import {
  getOllamaStatus,
  getSessions,
  newSession,
  sendMessage,
} from "../api/chat";

const sessions = ref([]);
const session = ref({ session_id: "chat_001" });
const messages = ref([]);
const loading = ref(false);
const ollama = ref({ connected: false, models: [] });
const messagesRef = ref(null);

const followUps = [
  "KG Fusion 在自然冲突场景下表现如何？",
  "为什么重复频谱不能直接算多个目标？",
  "缺失频谱时 LLM 如何恢复目标？",
];

async function scrollToBottom() {
  await nextTick();
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight;
  }
}

async function load() {
  sessions.value = (await getSessions()).data;
  session.value = sessions.value[0] || { session_id: "chat_001" };
  messages.value = session.value.messages || [];
  ollama.value = (await getOllamaStatus()).data;
  await scrollToBottom();
}

async function selectSession(item) {
  session.value = item;
  messages.value = item.messages || [];
  await scrollToBottom();
}

async function newChat() {
  session.value = (await newSession()).data;
  messages.value = [];
  await load();
}

async function send(text) {
  if (!text || loading.value) return;
  messages.value.push({ role: "user", content: text });
  await scrollToBottom();

  loading.value = true;
  try {
    const { data } = await sendMessage({
      session_id: session.value.session_id,
      message: text,
      context_type: "chat",
    });
    messages.value.push({ role: "assistant", content: data.answer });
  } finally {
    loading.value = false;
    await scrollToBottom();
  }
}

onMounted(load);
</script>

<style scoped>
.chat-page {
  height: calc(100vh - 58px);
  min-height: 0;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding-bottom: 10px;
}

.chat-page :deep(.page-header) {
  flex: 0 0 78px;
  margin-bottom: 10px;
}

.chat-layout {
  flex: 1 1 auto;
  min-height: 0;
  display: grid;
  grid-template-columns: 250px minmax(0, 1fr) 330px;
  gap: 12px;
}

.chat-bottom {
  flex: 0 0 108px;
  min-height: 0;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 10px;
}

.panel {
  min-height: 0;
  box-sizing: border-box;
}

.side-panel,
.chat-main,
.context-panel,
.info-card {
  padding: 12px;
  overflow: hidden;
}

.side-panel,
.chat-main,
.context-panel {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.section-title {
  flex: 0 0 auto;
  margin-bottom: 8px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}

.section-title.compact {
  margin-bottom: 6px;
}

.section-title h3 {
  margin: 0;
  color: #172f50;
  font-size: 15px;
  font-weight: 600;
}

.section-title p {
  margin: 3px 0 0;
  color: #7b8ea5;
  font-size: 12px;
}

.session-list {
  flex: 0 0 150px;
  min-height: 0;
  margin: 10px 0;
  overflow-y: auto;
  border-top: 1px solid #e5edf5;
  border-bottom: 1px solid #e5edf5;
  padding: 6px 0;
}

.session-list :deep(.el-menu) {
  border-right: none;
  background: transparent;
}

.session-list :deep(.el-menu-item) {
  height: 36px;
  border-radius: 7px;
  padding-left: 10px !important;
  color: #334867;
  font-size: 13px;
}

.session-list :deep(.el-menu-item.is-active) {
  background: #eaf3ff;
  color: #2468d8;
}

.session-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.quick-section {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.chat-main {
  min-height: 0;
}

.chat-header {
  flex: 0 0 auto;
}

.messages {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 10px 8px 10px 0;
  scroll-behavior: smooth;
  border-top: 1px solid #eef3f8;
  border-bottom: 1px solid #eef3f8;
  overscroll-behavior: contain;
}

.messages :deep(.msg) {
  max-width: 100%;
}

.messages :deep(.bubble) {
  max-width: min(78%, 900px);
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
  line-height: 1.65;
}

.chat-input-wrap {
  flex: 0 0 auto;
  padding-top: 8px;
}

.loading-step {
  margin-top: 8px;
}

.empty-chat {
  height: 100%;
  min-height: 220px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 7px;
  color: #6d7f96;
  text-align: center;
}

.empty-chat h3 {
  margin: 0;
  color: #213957;
  font-size: 16px;
}

.empty-chat p {
  max-width: 520px;
  margin: 0;
  color: #71839b;
  font-size: 13px;
  line-height: 1.6;
}

.empty-icon {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: #eaf3ff;
  color: #2468d8;
  font-weight: 800;
  font-size: 18px;
}

.context-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 2px;
}

.right-section {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid #e6edf5;
}

.detail-list {
  display: grid;
  gap: 8px;
}

.detail-item {
  padding: 9px 10px;
  border: 1px solid #e2eaf4;
  border-radius: 8px;
  background: #f8fbff;
}

.detail-label {
  margin-bottom: 4px;
  color: #7689a2;
  font-size: 12px;
}

.detail-value {
  color: #1b3454;
  font-size: 13px;
  font-weight: 600;
  line-height: 1.45;
  word-break: break-word;
}

.status-risk {
  color: #c56a22;
}

.tag-line {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.flow-list {
  display: grid;
  gap: 8px;
}

.follow-up {
  cursor: pointer;
  transition: all 0.16s ease;
}

.follow-up:hover {
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(34, 75, 130, 0.08);
}

.info-card h3 {
  margin: 0;
}

.info-card p {
  margin: 0;
  color: #4f647e;
  font-size: 12px;
  line-height: 1.55;
}

@media (max-height: 820px) and (min-width: 1180px) {
  .chat-bottom {
    flex-basis: 86px;
  }

  .side-panel,
  .chat-main,
  .context-panel,
  .info-card {
    padding: 10px;
  }

  .session-list {
    flex-basis: 120px;
  }
}

@media (max-width: 1180px) {
  .chat-page {
    height: auto;
    overflow: visible;
  }

  .chat-layout,
  .chat-bottom {
    display: block;
  }

  .side-panel,
  .chat-main,
  .context-panel,
  .info-card {
    min-height: 320px;
    margin-bottom: 12px;
  }

  .chat-main {
    height: 620px;
  }
}
</style>
