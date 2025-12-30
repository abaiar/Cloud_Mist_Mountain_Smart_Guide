import os 
import sys  
from contextlib import asynccontextmanager  
from typing import List  
from langchain_community.chat_models.tongyi import ChatTongyi  
from fastapi import FastAPI, HTTPException 
from pydantic import BaseModel  
from langchain.agents import create_agent 
from langchain_mcp_adapters.client import MultiServerMCPClient 
from fastapi.middleware.cors import CORSMiddleware  
from langchain_core.messages import HumanMessage, AIMessage 

# --- 配置部分 ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MCP_SERVER_PATH = os.path.join(CURRENT_DIR, "MCP_SERVER.py")
agent = None  
mcp_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 生命周期：初始化 MCP 客户端和 Agent
    """
    global agent, mcp_client
    
    print(f"🔗 Connecting to MCP Server: {MCP_SERVER_PATH}")
    
    mcp_client = MultiServerMCPClient(
        {
            "campus_algorithm": {
                "transport": "stdio",  # 使用标准输入输出 (stdio) 进行通信，简单可靠
                "command": sys.executable,  # 指明使用当前的 Python 解释器来运行命令
                "args": [MCP_SERVER_PATH],  # 指明要运行的具体脚本文件
            }
        }
    )

    tools = await mcp_client.get_tools()
    print(f"🛠️  Loaded Tools: {[t.name for t in tools]}")

    model = ChatTongyi(model="qwen-flash", temperature=0)

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

# 1. 配置跨域 (CORS) - 非常重要！
# 添加中间件，允许前端网页访问这个后端接口
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源的请求（比如 localhost:5173），* 代表不限制
    allow_credentials=True,  # 允许携带 Cookie 等凭证
    allow_methods=["*"],  # 允许所有的 HTTP 方法（GET, POST 等）
    allow_headers=["*"],  # 允许所有的 HTTP 请求头
)

# --- API 定义部分 ---
class ChatRequest(BaseModel):
    query: str  # 前端请求

class ChatResponse(BaseModel):
    response: str  # 后端回复
    tool_used: bool = False 

# response_model=ChatResponse 告诉 FastAPI 自动把返回值转换成我们定义的格式
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # 检查 agent 是否初始化成功。如果服务器启动失败，这里会拦截请求
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    # 开始处理请求，使用 try-except 捕获可能发生的错误
    try:

        input_message = HumanMessage(content=request.query)
        

        result = await agent.ainvoke({
            "messages": [input_message]
        })
        
        last_message = result["messages"][-1]
        
        has_tool_call = any(msg.type == "tool" for msg in result["messages"])

        return ChatResponse(
            response=last_message.content,  # AI 的回复文本
            tool_used=has_tool_call         # 是否使用了工具的标记
        )

    except Exception as e:
        print(f"Error during agent invocation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
