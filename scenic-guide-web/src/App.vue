<template>
  <div class="app-container">
    <div class="left-panel">
      <div class="header">
        <h2>🏔️ 云雾山智慧导游</h2>
        <p>计245 数据结构课程设计</p>
      </div>
      <ScenicMap :active-path="currentPath" @spot-click="handleSpotClick" />
    </div>

    <div class="right-panel">
      <div class="chat-history" ref="chatContainer">
        <div 
          v-for="(msg, index) in messages" 
          :key="index" 
          class="message"
          :class="msg.role"
        >
          <div class="avatar">{{ msg.role === 'user' ? '🧑‍💻' : '🤖' }}</div>
          <div class="content">
            <div style="white-space: pre-wrap;">{{ msg.text }}</div>
          </div>
        </div>
        
        <div v-if="isLoading" class="message ai">
          <div class="avatar">🤖</div>
          <div class="content loading">正在思考...</div>
        </div>
      </div>

      <div class="input-area">
        <input 
          v-model="inputQuery" 
          @keyup.enter="sendMessage"
          placeholder="例如：从南大门怎么去摘星峰？" 
          :disabled="isLoading"
        />
        <button @click="sendMessage" :disabled="isLoading">发送</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue';
import axios from 'axios';
import ScenicMap from './components/ScenicMap.vue';

const inputQuery = ref("");
const messages = ref([
  { role: 'ai', text: '您好！我是云雾山智能导游。您可以问我景点介绍，或者让我为您规划路线。\n比如：“帮我规划从游客中心到飞龙瀑布的路线”' }
]);
const isLoading = ref(false);
const currentPath = ref([]);
const chatContainer = ref(null);

// 处理地图点击：将景点名填入输入框
const handleSpotClick = (spotName) => {
  if (!inputQuery.value) {
    inputQuery.value = `从 ${spotName} 去 `;
  } else {
    inputQuery.value += `${spotName}`;
  }
};

const sendMessage = async () => {
  if (!inputQuery.value.trim()) return;

  // 1. 添加用户消息
  const userText = inputQuery.value;
  messages.value.push({ role: 'user', text: userText });
  inputQuery.value = "";
  scrollToBottom();
  isLoading.value = true;
  
  // 清空旧路径
  currentPath.value = [];

  try {
    // 2. 请求 FastAPI
    const res = await axios.post('http://localhost:8000/chat', {
      query: userText
    });

    const fullResponse = res.data.response;
    
    // 3. 【核心逻辑】解析后端返回的 PATH_DATA
    // 约定格式：PATH_DATA: ['S01', 'S02', ...]
    let displayLogin = fullResponse;
    const pathRegex = /PATH_DATA:\s*(\[.*?\])/;
    const match = fullResponse.match(pathRegex);

    if (match) {
      try {
        // 提取数组字符串并转为 JS 数组 (处理 Python 单引号的问题)
        const jsonStr = match[1].replace(/'/g, '"');
        const pathCodes = JSON.parse(jsonStr);
        
        console.log("Parsed Path:", pathCodes);
        currentPath.value = pathCodes; // 触发地图高亮

        // 移除 PATH_DATA 标记，让展示给用户的文本更干净
        displayLogin = fullResponse.replace(pathRegex, "").trim();
      } catch (e) {
        console.error("Path parsing error:", e);
      }
    }

    // 4. 显示 AI 回复
    messages.value.push({ role: 'ai', text: displayLogin });

  } catch (error) {
    messages.value.push({ role: 'ai', text: "系统繁忙，请稍后再试。" });
    console.error(error);
  } finally {
    isLoading.value = false;
    scrollToBottom();
  }
};

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
    }
  });
};
</script>

<style>
/* 全局样式重置 */
body, html { margin: 0; padding: 0; height: 100%; font-family: 'Segoe UI', sans-serif; }
#app { height: 100vh; }
</style>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: #f0f2f5;
}

.left-panel {
  flex: 2;
  padding: 20px;
  display: flex;
  flex-direction: column; /* 垂直排列 */
  overflow: hidden;       /* 关键：防止内容溢出父容器 */
}

.header {
  margin-bottom: 10px;
  color: #333;
  flex-shrink: 0;         /* 关键：防止标题被压缩 */
}
.header h2 { margin: 0; }
.header p { margin: 5px 0 0; color: #666; font-size: 0.9em; }

.right-panel {
  flex: 1;
  background: white;
  display: flex;
  flex-direction: column;
  border-left: 1px solid #ddd;
  min-width: 350px;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #fff;
}

.message {
  display: flex;
  margin-bottom: 20px;
  align-items: flex-start;
}

.message.user { flex-direction: row-reverse; }

.avatar {
  width: 40px;
  height: 40px;
  background: #eee;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin: 0 10px;
}

.content {
  background: #f1f1f1;
  padding: 12px 16px;
  border-radius: 12px;
  max-width: 70%;
  line-height: 1.5;
  font-size: 14px;
}

.message.user .content {
  background: #4a90e2;
  color: white;
  border-bottom-right-radius: 2px;
}

.message.ai .content {
  background: #f5f7fa;
  border: 1px solid #eee;
  border-bottom-left-radius: 2px;
}

.input-area {
  padding: 20px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 10px;
}

input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  outline: none;
  font-size: 16px;
}

input:focus { border-color: #4a90e2; }

button {
  padding: 0 24px;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
}

button:disabled { background: #ccc; cursor: not-allowed; }
</style>