import os
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables.graph import MermaidDrawMethod
from IPython.display import display, Image
from dotenv import load_dotenv
import os
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
if os.getenv("OPENAI_BASE_URL"):
    os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_BASE_URL")   
llm = ChatOpenAI(model="gpt-4o-mini")
class PlannerState(TypedDict):
    messages: Annotated[List[HumanMessage | AIMessage], "对话中的消息列表"] 
    city: str          # 城市
    interests: List[str]  # 兴趣点
    itinerary: str     # 最终生成的路线图

# 定义行程规划的提示词模板
itinerary_prompt = ChatPromptTemplate.from_messages([
    (
        "system", 
        "你是一个得力的旅游助手。请根据用户的兴趣：{interests}，为城市 {city} 制定一份一日游行程。请提供一份简明扼要的列表式行程指南。"
    ),
    (
        "human", 
        "请为我的一日游创建一个行程。"
    ),
])
"""def input_city(state: PlannerState) -> PlannerState:
    # 修改打印提示和输入提示
    print("请输入您计划一日游的城市名称：")
    user_message = input("您的输入: ")
    return {
        **state,
        "city": user_message,
        "messages": state['messages'] + [HumanMessage(content=user_message)],
    }

def input_interests(state: PlannerState) -> PlannerState:
    # 修改打印提示，使用了变量嵌入
    print(f"请输入您在 {state['city']} 旅游的兴趣爱好（请用逗号分隔）：")
    user_message = input("您的输入: ")
    return {
        **state,
        "interests": [interest.strip() for interest in user_message.split(',')],
        "messages": state['messages'] + [HumanMessage(content=user_message)],
    }"""
def input_city(state: PlannerState) -> PlannerState:
    # 如果 state 里已经有城市了（网页传过来的），就直接跳过 input
    if state.get('city'):
        return state
    
    # 只有在命令行运行、没有城市时才执行 input
    user_message = input("请输入您计划一日游的城市名称：")
    return {**state, "city": user_message}

def input_interests(state: PlannerState) -> PlannerState:
    # 如果已经有兴趣爱好列表了，直接跳过input
    if state.get('interests'):
        return state
        
    user_message = input(f"请输入您在 {state['city']} 旅游的兴趣爱好：")
    return {**state, "interests": [i.strip() for i in user_message.split(",")]}

def create_itinerary(state: PlannerState) -> PlannerState:
    # 修改处理过程中的提示语
    print(f"正在为您生成 {state['city']} 的行程，基于您的兴趣：{', '.join(state['interests'])}...")
    
    # 调用模型
    response = llm.invoke(itinerary_prompt.format_messages(city=state['city'], interests=", ".join(state['interests'])))
    
    print("\n最终行程安排：")
    print(response.content)
    
    return {
        **state,
        "messages": state['messages'] + [AIMessage(content=response.content)],
        "itinerary": response.content,
    }
workflow = StateGraph(PlannerState)

workflow.add_node("输入城市", input_city)
workflow.add_node("输入兴趣", input_interests)
workflow.add_node("生成行程", create_itinerary)

workflow.set_entry_point("输入城市")
workflow.add_edge("输入城市", "输入兴趣")
workflow.add_edge("输入兴趣", "生成行程")
workflow.add_edge("生成行程", END)

app = workflow.compile()


display(
    Image(
        app.get_graph().draw_mermaid_png(
            draw_method=MermaidDrawMethod.API,
        )
    )
)

def run_travel_planner(user_request: str):
    # 打印初始的请求信息
    print(f"初始请求: {user_request}\n")
    
    # 初始化“大脑状态”（State）
    # 这里的 key 必须和我们之前定义的 PlannerState 一一对应
    state = {
        "messages": [HumanMessage(content=user_request)], # 将用户的请求存入消息列表
        "city": "",      # 城市初始为空
        "interests": [], # 兴趣初始为空列表
        "itinerary": "", # 行程初始为空
    }
    
    # 开始流式运行工作流
    # app.stream(state) 会按照我们在 add_edge 里定义的顺序一个一个执行节点
    for output in app.stream(state):
        # 这里用 pass 是因为在 input_city 等函数里我们已经写了 print 了
        # 这里的循环只是为了驱动工作流一步步往下走
        pass
if __name__ == "__main__":
   run_travel_planner("我想去旅游")