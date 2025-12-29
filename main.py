import os  # 导入操作系统模块，用于处理文件路径等系统级操作
import sys  # 导入系统模块，主要用于获取当前 Python 解释器的路径
from contextlib import asynccontextmanager  # 导入异步上下文管理器，用于管理 FastAPI 的生命周期（启动和关闭）
from typing import List  # 导入类型提示工具，虽然代码里暂时没用到 List，但保留是个好习惯
from langchain_community.chat_models.tongyi import ChatTongyi  # 导入通义千问模型，这是我们的 AI "大脑"
from fastapi import FastAPI, HTTPException  # 导入 FastAPI 框架和 HTTP 异常处理类
from pydantic import BaseModel  # 导入 Pydantic，用于定义数据模型，验证请求和响应的数据格式
from langchain.agents import create_agent  # 导入 LangChain 的 Agent 工厂函数，用于创建智能体
from langchain_mcp_adapters.client import MultiServerMCPClient  # 导入 MCP 客户端，用于连接我们的工具服务器
from fastapi.middleware.cors import CORSMiddleware  # 导入 CORS 中间件，解决跨域访问问题
from langchain_core.messages import HumanMessage, AIMessage  # 导入消息类，用于构建 AI 对话的标准消息格式

# --- 配置部分 ---
# 获取当前文件（main.py）所在的目录的绝对路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 拼接路径，找到我们要连接的 MCP 工具服务器脚本（MCP_SERVER.py）的位置
MCP_SERVER_PATH = os.path.join(CURRENT_DIR, "MCP_SERVER.py")

# --- 全局变量定义 ---
# 定义全局变量 agent，初始化为 None。它稍后会存储构建好的智能体对象
agent = None  
# 定义全局变量 mcp_client，初始化为 None。它稍后会存储 MCP 连接客户端
mcp_client = None

# 定义 FastAPI 的生命周期管理器
# 这个函数会在服务器启动前和关闭后自动执行
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 生命周期：初始化 MCP 客户端和 Agent
    """
    # 声明我们要修改外部定义的全局变量 agent 和 mcp_client
    global agent, mcp_client
    
    # 打印日志，告诉开发者正在尝试连接 MCP 服务器
    print(f"🔗 Connecting to MCP Server: {MCP_SERVER_PATH}")
    
    # 1. 初始化 MCP Client (多服务器 MCP 客户端)
    # 这是一个桥梁，让我们的主程序能跟工具程序说话
    mcp_client = MultiServerMCPClient(
        {
            # 给连接起个名字叫 "campus_algorithm"
            "campus_algorithm": {
                "transport": "stdio",  # 使用标准输入输出 (stdio) 进行通信，简单可靠
                "command": sys.executable,  # 指明使用当前的 Python 解释器来运行命令
                "args": [MCP_SERVER_PATH],  # 指明要运行的具体脚本文件
            }
        }
    )
    
    # 2. 获取工具 (异步操作)
    # 客户端连接成功后，询问 MCP 服务器：“你都有哪些工具可以用？”
    tools = await mcp_client.get_tools()
    # 打印日志，显示加载了哪些工具，方便调试
    print(f"🛠️  Loaded Tools: {[t.name for t in tools]}")

    # 3. 初始化模型
    # 创建通义千问模型实例，使用 "qwen-flash" 版本，temperature=0 表示回答要严谨、不随机
    model = ChatTongyi(model="qwen-flash", temperature=0)

    # 4. 创建 Agent (核心步骤)
    # 定义 System Prompt (系统提示词)，这是给 AI 的“人设”和“操作手册”
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
    
    # 使用 create_agent 函数，把 模型(Brain) + 工具(Hands) + 提示词(Instructions) 组装在一起
    # 内部会自动构建一个基于 LangGraph 的状态图
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt
    )
    
    # 打印日志，表示智能体已经准备好接客了
    print("🤖 Agent initialized successfully (Graph-based).")
    
    # yield 是一个分隔符。程序运行到这里会暂停，FastAPI 服务器正式启动接收请求。
    # 当服务器关闭时，程序会继续执行 yield 后面的代码（这里没有写后续代码，通常用于清理资源）
    yield
    

# 创建 FastAPI 应用实例，title 是文档标题，lifespan 传入刚才定义的生命周期函数
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

# 定义请求数据的格式（Schema）
class ChatRequest(BaseModel):
    query: str  # 规定前端发过来的 JSON 必须包含 'query' 字段，且必须是字符串
    # 下面这行注释掉的是预留功能：如果以后想让前端传历史记录，可以打开
    # history: List[dict] = [] 

# 定义响应数据的格式（Schema）
class ChatResponse(BaseModel):
    response: str  # 返回给前端的主要文本内容
    tool_used: bool = False # 一个布尔标记，告诉前端这次对话有没有调用工具（比如有没有查路线）

# 定义核心聊天接口：POST 方法，路径是 /chat
# response_model=ChatResponse 告诉 FastAPI 自动把返回值转换成我们定义的格式
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # 检查 agent 是否初始化成功。如果服务器启动失败，这里会拦截请求
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    # 开始处理请求，使用 try-except 捕获可能发生的错误
    try:
        # 5. 调用 Agent
        # 将用户的输入 (request.query) 包装成 LangChain 的 HumanMessage 对象
        input_message = HumanMessage(content=request.query)
        
        # 使用 agent.ainvoke 异步调用智能体
        # 传入的字典 {"messages": [...]} 是 LangGraph 的标准输入格式
        # Agent 会思考、调用工具、再思考，最后生成结果
        result = await agent.ainvoke({
            "messages": [input_message]
        })
        
        # 6. 解析结果
        # result["messages"] 是一个列表，包含了这次对话所有的步骤（用户发了啥，AI想了啥，工具回了啥，AI最后说了啥）
        # 我们取列表的最后一个元素 ([-1])，这就是 AI 给用户的最终回复
        last_message = result["messages"][-1]
        
        # 判断是否使用了工具：遍历消息列表，看里面有没有类型为 "tool" 的消息
        # 如果有，说明 AI 调用了外部函数（比如查了路径）
        has_tool_call = any(msg.type == "tool" for msg in result["messages"])

        # 返回符合 ChatResponse 模型的数据
        return ChatResponse(
            response=last_message.content,  # AI 的回复文本
            tool_used=has_tool_call         # 是否使用了工具的标记
        )

    # 如果处理过程中出错（比如断网、API 欠费等）
    except Exception as e:
        # 在后台打印错误详情，方便排查
        print(f"Error during agent invocation: {e}")
        # 向前端返回 500 服务器内部错误，并带上错误信息
        raise HTTPException(status_code=500, detail=str(e))

# 程序入口：如果直接运行这个文件（而不是被导入）
if __name__ == "__main__":
    import uvicorn  # 导入 uvicorn 服务器
    # 启动服务器：加载 "main" 文件里的 "app" 对象
    # host="0.0.0.0" 允许局域网访问，port=8000 是端口号，reload=True 表示代码修改后自动重启
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
