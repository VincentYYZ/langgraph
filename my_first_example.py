"""
LangGraph 入门示例 | LangGraph Getting Started Example
======================================================
这个例子展示了 LangGraph 的核心概念：
This example demonstrates LangGraph's core concepts:

1. StateGraph - 状态图 | State Graph
2. Node - 节点（处理函数）| Node (processing function)  
3. Edge - 边（连接）| Edge (connection)
4. Conditional Edge - 条件边 | Conditional Edge
"""

from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END


# ============================================================
# 第 1 步：定义状态 | Step 1: Define State
# ============================================================
# 状态就像一个"共享的笔记本"，所有节点都可以读写
# State is like a "shared notebook" that all nodes can read and write

class State(TypedDict):
    """Agent 的状态 | Agent's State"""
    # 用户的问题 | User's question
    question: str
    # 思考过程 | Thinking process
    thinking: str
    # 最终答案 | Final answer
    answer: str
    # 步骤计数 | Step counter
    step_count: int


# ============================================================
# 第 2 步：定义节点（处理函数）| Step 2: Define Nodes
# ============================================================
# 每个节点是一个函数，接收 state，返回更新后的 state
# Each node is a function that receives state and returns updated state

def think_node(state: State) -> dict:
    """
    思考节点 | Thinking Node
    模拟 AI 的思考过程 | Simulates AI's thinking process
    """
    question = state["question"]
    step = state.get("step_count", 0) + 1
    
    # 模拟思考过程 | Simulate thinking
    thinking = f"[第 {step} 步思考] 用户问的是: '{question}'，让我分析一下..."
    print(f"🧠 思考中: {thinking}")
    
    return {
        "thinking": thinking,
        "step_count": step
    }


def analyze_node(state: State) -> dict:
    """
    分析节点 | Analysis Node
    分析问题类型 | Analyze question type
    """
    question = state["question"].lower()
    step = state.get("step_count", 0) + 1
    
    # 简单的问题分类 | Simple question classification
    if "天气" in question or "weather" in question:
        analysis = "这是一个天气查询问题"
    elif "时间" in question or "time" in question:
        analysis = "这是一个时间查询问题"
    elif "计算" in question or "+" in question or "-" in question:
        analysis = "这是一个数学计算问题"
    else:
        analysis = "这是一个一般性问题"
    
    print(f"📊 分析结果: {analysis}")
    
    return {
        "thinking": state["thinking"] + f" -> {analysis}",
        "step_count": step
    }


def answer_node(state: State) -> dict:
    """
    回答节点 | Answer Node
    生成最终答案 | Generate final answer
    """
    question = state["question"]
    thinking = state["thinking"]
    step = state.get("step_count", 0) + 1
    
    # 根据问题生成模拟答案 | Generate mock answer based on question
    if "天气" in question.lower():
        answer = "🌤️ 今天天气晴朗，气温 25°C，适合外出！"
    elif "时间" in question.lower():
        from datetime import datetime
        answer = f"🕐 现在时间是: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    elif "+" in question:
        # 简单计算 | Simple calculation
        try:
            nums = question.replace(" ", "").split("+")
            result = sum(int(n) for n in nums if n.isdigit())
            answer = f"🔢 计算结果: {result}"
        except:
            answer = "抱歉，我无法计算这个表达式"
    else:
        answer = f"🤖 这是一个好问题！关于 '{question}'，我的回答是：这需要更多信息才能准确回答。"
    
    print(f"💬 生成答案: {answer}")
    
    return {
        "answer": answer,
        "step_count": step
    }


# ============================================================
# 第 3 步：定义条件函数 | Step 3: Define Condition Function
# ============================================================
# 条件函数决定下一步去哪个节点
# Condition function determines which node to go next

def should_continue(state: State) -> str:
    """
    决定是否继续或结束 | Decide whether to continue or end
    返回下一个节点的名称 | Return the name of the next node
    
    这个函数展示了条件边的核心思想：
    This function demonstrates the core idea of conditional edges:
    - 根据当前状态动态决定下一步 | Dynamically decide next step based on current state
    - 类似于 if-else 但是在图结构中 | Like if-else but in graph structure
    """
    question = state["question"].lower()
    
    # 简单问题直接回答，复杂问题需要分析
    # Simple questions: answer directly; Complex questions: need analysis
    simple_keywords = ["几点", "time", "1+", "2+", "3+", "你好", "hello"]
    
    is_simple = any(keyword in question for keyword in simple_keywords)
    
    if is_simple:
        print("   ⚡ 简单问题，跳过分析直接回答 | Simple question, skip to answer")
        return "answer"
    else:
        print("   🔄 复杂问题，需要分析 | Complex question, needs analysis")
        return "analyze"


# ============================================================
# 第 4 步：构建图 | Step 4: Build the Graph
# ============================================================

def build_graph():
    """
    构建状态图 | Build the state graph
    """
    # 创建图构建器 | Create graph builder
    graph = StateGraph(State)
    
    # 添加节点 | Add nodes
    graph.add_node("think", think_node)      # 思考节点
    graph.add_node("analyze", analyze_node)  # 分析节点
    graph.add_node("answer", answer_node)    # 回答节点
    
    # 添加边 | Add edges
    # START -> think: 从开始到思考
    graph.add_edge(START, "think")
    
    # think -> (条件判断): 根据条件决定下一步
    graph.add_conditional_edges(
        "think",           # 从哪个节点出发 | From which node
        should_continue,   # 条件函数 | Condition function
        {
            "analyze": "analyze",  # 如果返回 "analyze"，去 analyze 节点
            "answer": "answer"     # 如果返回 "answer"，去 answer 节点
        }
    )
    
    # analyze -> answer: 分析完后去回答
    graph.add_edge("analyze", "answer")
    
    # answer -> END: 回答完后结束
    graph.add_edge("answer", END)
    
    # 编译图 | Compile the graph
    compiled_graph = graph.compile()
    
    return compiled_graph


# ============================================================
# 第 5 步：运行示例 | Step 5: Run Example
# ============================================================

def main():
    print("=" * 60)
    print("🚀 LangGraph 入门示例 | LangGraph Getting Started Example")
    print("=" * 60)
    
    # 构建图 | Build graph
    agent = build_graph()
    
    # 可视化图结构 | Visualize graph structure
    print("\n📊 图结构 | Graph Structure:")
    print("-" * 40)
    try:
        # 打印图的节点信息 | Print graph node info
        print(agent.get_graph().draw_ascii())
    except Exception as e:
        print(f"(图形化显示需要额外依赖: {e})")
        print("节点: START -> think -> analyze/answer -> END")
    
    # 测试不同的问题 | Test different questions
    test_questions = [
        "今天北京的天气怎么样？",  # 复杂问题 → 需要分析
        "现在几点了？",            # 简单问题 → 跳过分析
        "1 + 2 + 3",              # 简单问题 → 跳过分析  
        "如何学习编程？",          # 复杂问题 → 需要分析
        "你好",                   # 简单问题 → 跳过分析
    ]
    
    for question in test_questions:
        print("\n" + "=" * 60)
        print(f"❓ 用户问题 | User Question: {question}")
        print("-" * 60)
        
        # 初始状态 | Initial state
        initial_state = {
            "question": question,
            "thinking": "",
            "answer": "",
            "step_count": 0
        }
        
        # 运行图 | Run the graph
        result = agent.invoke(initial_state)
        
        print("-" * 60)
        print(f"✅ 最终答案 | Final Answer: {result['answer']}")
        print(f"📝 总步骤数 | Total Steps: {result['step_count']}")
    
    print("\n" + "=" * 60)
    print("🎉 示例运行完成！| Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
