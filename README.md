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

[系统主界面演示]
<img width="1915" height="1077" alt="image" src="https://github.com/user-attachments/assets/e933cda8-c4a5-4d9e-be26-1ad1d8a666b8" />
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
git clone https://github.com/abaiar/-AI-Agent-.git
cd -AI-Agent-
