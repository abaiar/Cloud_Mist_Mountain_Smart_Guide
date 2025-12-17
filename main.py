import os
import sys
from contextlib import asynccontextmanager
from typing import List
from langchain_community.chat_models.tongyi import ChatTongyi
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.agents import create_agent  # 核心改变：使用新版工厂函数
from langchain_mcp_adapters.client import MultiServerMCPClient
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage, AIMessage

# --- 配置部分 ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MCP_SERVER_PATH = os.path.join(CURRENT_DIR, "MCP_SERVER.py")

# 全局变量
agent = None  
mcp_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 生命周期：初始化 MCP 客户端和 Agent
    """
    global agent, mcp_client
    
    print(f"🔗 Connecting to MCP Server: {MCP_SERVER_PATH}")
    
    # 1. 初始化 MCP Client
    mcp_client = MultiServerMCPClient(
        {
            "campus_algorithm": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [MCP_SERVER_PATH],
            }
        }
    )
    
    # 2. 获取工具 (异步)
    tools = await mcp_client.get_tools()
    print(f"🛠️  Loaded Tools: {[t.name for t in tools]}")

    # 3. 初始化模型
    model = ChatTongyi(model="qwen-flash", temperature=0)

    # 4. 创建 Agent (核心改变)
    # create_agent 内部构建了 LangGraph 运行时
    system_prompt = (
        "你的名字叫阿白，你是一个云雾山景区智慧导游助手。你的核心能力是帮助访客规划路线和介绍景点。"
        "你有以下几个强大的路线规划工具，请根据用户意图灵活选择："
        "1. 如果用户问A到B怎么走，调用 'find_shortest_path'。"
        "2. 如果用户想“逛完所有景点”、“全图打卡”或“随机游览”，调用 'generate_all_spots_tour'。"
        "3. 如果用户想“推荐路线”、“适合老人的”、“刺激的”、“拜佛的”，调用 'recommend_themed_route'。"
        "\n"
        "重要输出规则：如果工具返回结果中包含 'path_codes' 列表，请你务必执行以下两步："
        "1. 用亲切、导游般的口吻向用户介绍这条路线（引用工具返回的 description 或 reason）。"
        "2. 在回复的【最后一行】，且必须是最后一行，输出路径数据，格式严格如下："
        "PATH_DATA: ['S01', 'S02', 'S05']"
        "(不要把这个列表融入到自然语言句子中，必须单独占一行，以便前端地图绘制)"
    )
    
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt
    )
    
    print("🤖 Agent initialized successfully (Graph-based).")
    
    yield
    


app = FastAPI(title="Campus Guide Agent API", lifespan=lifespan)

# 1. 配置跨域 (新增代码)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境建议改为 ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- API 定义 ---

class ChatRequest(BaseModel):
    query: str
    # 可选：如果你想在前端保留历史记录，可以传 messages 数组过来
    # history: List[dict] = [] 

class ChatResponse(BaseModel):
    response: str
    tool_used: bool = False # 标识是否使用了工具，便于前端做特殊渲染

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # 5. 调用 Agent
        # 新版 invoke 接收 {"messages": [...]}
        # 这里的 messages 会自动追加到 Agent 的状态中
        input_message = HumanMessage(content=request.query)
        
        result = await agent.ainvoke({
            "messages": [input_message]
        })
        
        # 6. 解析结果
        # result["messages"] 包含了完整的交互历史 (Human -> AI (tool_call) -> Tool -> AI)
        last_message = result["messages"][-1]
        
        # 简单判断是否使用了工具（检查历史消息中是否有 ToolMessage）
        # 也可以检查 last_message.content 是否包含特定的结构化数据
        has_tool_call = any(msg.type == "tool" for msg in result["messages"])

        return ChatResponse(
            response=last_message.content,
            tool_used=has_tool_call
        )

    except Exception as e:
        print(f"Error during agent invocation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)