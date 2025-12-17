# 🏔️ 云雾山智慧导游系统 (Cloud Mist Mountain Smart Guide)

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Vue](https://img.shields.io/badge/Vue.js-3.x-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-teal.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.3+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

> **烟台大学 计245班数据结构课程设计作品**
>
> 一个基于 **图论算法** 与 **大语言模型 (LLM)** 的智能景区导览系统。它不仅能通过自然语言与游客交互，还能根据实时需求进行复杂的路径规划（最短路径、全图打卡、特色游览），实现了从“人工查询”到“AI 智能决策”的跨越。

---

## 📸 演示效果 (Demo)

<img width="100%" alt="系统主界面演示" src="https://github.com/user-attachments/assets/e933cda8-c4a5-4d9e-be26-1ad1d8a666b8" />
*(图示：左侧为 SVG 交互地图，支持路径动态高亮；右侧为 AI 智能导游对话窗口)*

---

## ✨ 主要功能 (Key Features)

* **🤖 智能自然语言交互**：基于 LangChain + 通义千问 (Qwen)，精准理解用户意图（如“我想去爬山”、“带老人怎么玩”），提供拟人化的导游解说。
* **📍 最短路径规划 (Dijkstra)**：针对用户指定的起终点，利用 **Dijkstra 算法 + 最小堆** 毫秒级计算最短路线，并在地图上实时绘制。
* **🏃 全景点“特种兵”打卡**：基于 **贪心策略 (Nearest Neighbor)** 解决 TSP (旅行商) 变体问题，自动生成一条覆盖全景区的游览环线。
* **🎨 个性化主题路线推荐**：内置“休闲康养”、“硬核探险”、“古刹祈福”等多条逻辑路线，根据用户画像自动推荐并解释原因。
* **🗺️ SVG 矢量交互地图**：前端采用 Vue + SVG 技术，支持点击景点自动填入指令，路径动态高亮动画展示。

---

## 🛠️ 技术栈 (Tech Stack)

| 模块 | 技术选型 | 说明 |
| :--- | :--- | :--- |
| **前端 (Frontend)** | Vue 3, Vite | 响应式界面，组件化开发 |
| **地图渲染** | SVG, CSS3 Animation | 矢量地图绘制与路径动画 |
| **后端 (Backend)** | FastAPI | 高性能异步 Web 框架 |
| **AI 编排** | LangChain, LangGraph | Agent 智能体构建与状态管理 |
| **工具协议** | FastMCP | 模型上下文协议 (Model Context Protocol) |
| **核心算法** | Python (Heapq, Set) | 图的邻接表存储、Dijkstra、贪心算法 |
| **大模型** | Aliyun Qwen (通义千问) | 底层对话与逻辑推理能力 |

---

## 🚀 快速开始 (Getting Started)

### 1. 环境依赖 (Prerequisites)

在开始之前，请确保您的开发环境满足以下要求：

* **Node.js**: v16.0 或更高版本 (用于运行前端)
* **Python**: v3.10 或更高版本 (用于运行后端)
* **API Key**: 阿里云 DashScope (通义千问) API 密钥

### 2. 安装步骤 (Installation)

**克隆项目**

```bash
git clone [https://github.com/abaiar/-AI-Agent-.git](https://github.com/abaiar/-AI-Agent-.git)
cd -AI-Agent-

```

**🔧 后端设置 (Backend Setup)**

```bash
# 1. 进入后端目录(假设在根目录)

# 2. 创建虚拟环境 (推荐)
python -m venv venv

# Windows 激活:
venv\Scripts\activate
# Mac/Linux 激活:
# source venv/bin/activate

# 3. 安装依赖
pip install fastapi uvicorn langchain langchain-community dashscope fastmcp

# 4. 设置 API KEY (Windows PowerShell 示例)
$env:DASHSCOPE_API_KEY="你的_sk_密钥"
# 或者在代码中设置 os.environ["DASHSCOPE_API_KEY"] = "..."

```

**💻 前端设置 (Frontend Setup)**

```bash
# 1. 进入前端目录 (如果 Vue 代码在 scenic-guide-web 文件夹下，请进入该文件夹)
cd scenic-guide-web

# 2. 安装 npm 依赖
npm install

```

---

## 🏃 运行指南 (Usage)

请分别在两个终端窗口中启动服务。

**启动后端 API**

```bash
# 确保在项目根目录且已激活虚拟环境
python main.py
# 服务将启动在 http://localhost:8000

```

**启动前端界面**

```bash
npm run dev
# 访问 http://localhost:5173 (具体端口看控制台输出)

```

---

## 💡 数据结构与算法亮点 (Course Highlights)

本项目在 `MCP_SERVER.py` 中深度应用了数据结构课程知识，是将理论应用于实践的典型案例：

* **图的存储 (Graph Storage)**
使用 **邻接表 (Adjacency List)** 存储稀疏图结构，有效降低了空间复杂度，适合景点多、路径相对固定的场景。
* **最短路径 (Shortest Path)**
实现 **Dijkstra 算法**，配合 **优先队列 (Min-Heap)** 优化查找最小权值节点的过程，将时间复杂度优化至 O(E \log V)。
* **全图遍历 (TSP Approximation)**
针对“游览所有景点”的需求（旅行商问题 TSP），采用 **贪心算法 (Greedy Strategy)** 中的最近邻策略 (Nearest Neighbor)，在保证响应速度（毫秒级）的同时提供较优的连通路径。

---

## 👥 作者 (Authors)

* **赵健硕** - *后端架构 & 算法实现*
* **季艺萍** - *前端交互 & 地图可视化*
* **班级**：烟台大学 计算机科学与技术 245 班
---

## ⚠️ 注意事项 (Notes)

* **网络问题**：如果在调用 AI 时出现 `SSLError`，通常是因为开启了 VPN 代理。建议在运行 Python 脚本时临时关闭代理，或配置环境变量以直连阿里云服务。
* **浏览器跨域**：后端已配置 `CORSMiddleware` 允许跨域请求，前端开发环境下可直接调用本地 API。

---

## 📄 License

This project is licensed under the MIT License.

```

```
