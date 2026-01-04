# 设计模式：Agent 智能体

## 概述

**Agent（智能体）** 是一种能够自主决策的 LLM 应用模式。Agent 可以根据任务需求，自主选择使用工具、搜索信息或直接回答问题。

## 核心概念

### Agent 的特征

1. **自主决策**：根据当前状态选择下一步行动
2. **工具调用**：能够使用外部工具完成任务
3. **循环执行**：持续执行直到达成目标

### Agent 的基本结构

```
                ┌─────────────────────────────┐
                │                             │
                ▼                             │
         ┌──────────────┐                     │
         │   Decide     │  ──"use_tool"──┐    │
         │  (决策节点)   │                │    │
         └──────────────┘                ▼    │
                │               ┌──────────────┐
                │               │    Tool      │
           "answer"             │  (工具节点)   │
                │               └──────────────┘
                ▼                     │
         ┌──────────────┐             │
         │   Answer     │ ◀───────────┘
         │  (回答节点)   │
         └──────────────┘
```

## 基础 Agent 实现

### 决策节点

```python
from pocketflow import Node, Flow

class DecideNode(Node):
    """决策节点：决定使用工具还是直接回答"""

    def prep(self, shared):
        return {
            "question": shared["question"],
            "context": shared.get("context", ""),
            "history": shared.get("tool_history", [])
        }

    def exec(self, data):
        prompt = f"""
你是一个智能助手。根据问题和上下文，决定下一步行动。

问题: {data["question"]}
当前上下文: {data["context"]}
工具使用历史: {data["history"]}

可用工具:
- search: 搜索网络获取信息
- calculator: 进行数学计算
- none: 直接回答问题

请回复 JSON 格式:
{{"action": "工具名或none", "reason": "决策原因", "query": "工具查询内容(如需要)"}}
"""
        response = call_llm(prompt)
        return parse_json(response)

    def post(self, shared, prep_res, exec_res):
        shared["decision"] = exec_res

        if exec_res["action"] == "none":
            return "answer"
        else:
            return "use_tool"
```

### 工具节点

```python
class ToolNode(Node):
    """工具节点：执行工具调用"""

    TOOLS = {
        "search": web_search,
        "calculator": calculate
    }

    def prep(self, shared):
        return shared["decision"]

    def exec(self, decision):
        tool_name = decision["action"]
        query = decision.get("query", "")

        if tool_name in self.TOOLS:
            result = self.TOOLS[tool_name](query)
            return {"tool": tool_name, "result": result}
        return {"error": f"未知工具: {tool_name}"}

    def post(self, shared, prep_res, exec_res):
        # 记录工具使用历史
        if "tool_history" not in shared:
            shared["tool_history"] = []
        shared["tool_history"].append(exec_res)

        # 更新上下文
        shared["context"] = shared.get("context", "") + \
            f"\n工具 {exec_res['tool']} 返回: {exec_res['result']}"

        return "decide"  # 回到决策节点
```

### 回答节点

```python
class AnswerNode(Node):
    """回答节点：生成最终答案"""

    def prep(self, shared):
        return {
            "question": shared["question"],
            "context": shared.get("context", "")
        }

    def exec(self, data):
        prompt = f"""
根据以下信息回答问题：

问题: {data["question"]}
收集到的信息: {data["context"]}

请提供详细的回答：
"""
        return call_llm(prompt)

    def post(self, shared, prep_res, exec_res):
        shared["answer"] = exec_res
```

### 组装 Agent

```python
# 创建节点
decide = DecideNode()
tool = ToolNode()
answer = AnswerNode()

# 定义流程
decide - "use_tool" >> tool >> decide  # 工具循环
decide - "answer" >> answer             # 直接回答

# 创建 Agent Flow
agent = Flow(start=decide)

# 运行
shared = {"question": "2024年世界杯在哪里举办？"}
agent.run(shared)
print(shared["answer"])
```

## 带工具定义的 Agent

### 工具注册

```python
class Tool:
    """工具定义"""
    def __init__(self, name, description, func):
        self.name = name
        self.description = description
        self.func = func

    def to_prompt(self):
        return f"- {self.name}: {self.description}"

# 定义工具
tools = [
    Tool("search", "搜索网络获取最新信息", web_search),
    Tool("calculator", "执行数学计算", calculate),
    Tool("weather", "查询天气信息", get_weather),
]
```

### 动态工具选择

```python
class ToolSelectNode(Node):
    def __init__(self, tools):
        super().__init__()
        self.tools = {t.name: t for t in tools}

    def prep(self, shared):
        tools_desc = "\n".join(t.to_prompt() for t in self.tools.values())
        return {
            "question": shared["question"],
            "tools": tools_desc
        }

    def exec(self, data):
        prompt = f"""
问题: {data["question"]}

可用工具:
{data["tools"]}
- answer: 我已有足够信息，直接回答

选择一个工具并提供参数，返回 JSON:
{{"tool": "工具名", "params": {{...}}}}
"""
        return parse_json(call_llm(prompt))

    def post(self, shared, prep_res, exec_res):
        shared["tool_choice"] = exec_res
        return exec_res["tool"]

class DynamicToolNode(Node):
    def __init__(self, tools):
        super().__init__()
        self.tools = {t.name: t for t in tools}

    def prep(self, shared):
        return shared["tool_choice"]

    def exec(self, choice):
        tool = self.tools[choice["tool"]]
        return tool.func(**choice.get("params", {}))

    def post(self, shared, prep_res, exec_res):
        shared["tool_result"] = exec_res
        return "continue"
```

## ReAct 模式

ReAct (Reasoning + Acting) 是一种流行的 Agent 模式，让 LLM 交替进行推理和行动。

```python
class ReActNode(Node):
    """ReAct 节点：思考-行动-观察循环"""

    def prep(self, shared):
        return {
            "question": shared["question"],
            "scratchpad": shared.get("scratchpad", "")
        }

    def exec(self, data):
        prompt = f"""
问题: {data["question"]}

之前的思考和观察:
{data["scratchpad"]}

请按以下格式回复:
Thought: 你的思考过程
Action: 选择的行动 (search/calculate/finish)
Action Input: 行动的输入
"""
        return parse_react_response(call_llm(prompt))

    def post(self, shared, prep_res, exec_res):
        # 更新 scratchpad
        shared["scratchpad"] = shared.get("scratchpad", "") + \
            f"\nThought: {exec_res['thought']}\n" + \
            f"Action: {exec_res['action']}\n" + \
            f"Action Input: {exec_res['action_input']}\n"

        if exec_res["action"] == "finish":
            shared["answer"] = exec_res["action_input"]
            return "done"

        return exec_res["action"]

class ObservationNode(Node):
    """观察节点：执行行动并获取结果"""

    def prep(self, shared):
        # 从 scratchpad 获取最后一个 action
        return extract_last_action(shared["scratchpad"])

    def exec(self, action_info):
        result = execute_action(action_info)
        return result

    def post(self, shared, prep_res, exec_res):
        shared["scratchpad"] += f"Observation: {exec_res}\n"
        return "think"  # 继续思考

# 构建 ReAct Agent
react = ReActNode()
observe = ObservationNode()

react - "search" >> observe - "think" >> react
react - "calculate" >> observe
react - "done" >> final_node
```

## 多轮对话 Agent

```python
class ConversationAgent(Node):
    """支持多轮对话的 Agent"""

    def prep(self, shared):
        if "messages" not in shared:
            shared["messages"] = []
        return shared["messages"]

    def exec(self, messages):
        # 添加系统提示
        full_messages = [
            {"role": "system", "content": "你是一个有用的助手。"}
        ] + messages

        return call_llm(full_messages)

    def post(self, shared, prep_res, exec_res):
        # 更新对话历史
        shared["messages"].append({
            "role": "assistant",
            "content": exec_res
        })
        shared["last_response"] = exec_res
        return "wait_input"

class UserInputNode(Node):
    def exec(self, _):
        return input("You: ")

    def post(self, shared, prep_res, exec_res):
        if exec_res.lower() in ["quit", "exit", "bye"]:
            return "end"

        shared["messages"].append({
            "role": "user",
            "content": exec_res
        })
        return "respond"

# 构建对话 Agent
agent = ConversationAgent()
user_input = UserInputNode()

user_input - "respond" >> agent - "wait_input" >> user_input
user_input - "end" >> end_node
```

## 安全限制

### 迭代次数限制

```python
class SafeDecideNode(DecideNode):
    MAX_ITERATIONS = 10

    def post(self, shared, prep_res, exec_res):
        iterations = shared.get("iterations", 0) + 1
        shared["iterations"] = iterations

        if iterations >= self.MAX_ITERATIONS:
            shared["answer"] = "达到最大迭代次数，无法完成任务"
            return "force_answer"

        return super().post(shared, prep_res, exec_res)
```

### 工具调用限制

```python
class LimitedToolNode(ToolNode):
    def prep(self, shared):
        tool_calls = shared.get("tool_call_count", {})
        decision = shared["decision"]
        tool_name = decision["action"]

        # 检查工具调用次数
        if tool_calls.get(tool_name, 0) >= 3:
            return {"skip": True, "reason": f"{tool_name} 调用次数过多"}

        return decision

    def exec(self, data):
        if data.get("skip"):
            return {"error": data["reason"]}
        return super().exec(data)

    def post(self, shared, prep_res, exec_res):
        # 记录调用次数
        if "tool_call_count" not in shared:
            shared["tool_call_count"] = {}
        tool_name = shared["decision"]["action"]
        shared["tool_call_count"][tool_name] = \
            shared["tool_call_count"].get(tool_name, 0) + 1

        return super().post(shared, prep_res, exec_res)
```

## 最佳实践

### 1. 清晰的决策提示

```python
# ✅ 结构化的决策提示
prompt = """
任务: {task}
当前状态: {state}
可用行动: {actions}

请选择最合适的行动，返回 JSON 格式。
"""
```

### 2. 工具结果验证

```python
def exec(self, decision):
    result = self.tools[decision["action"]](decision["query"])

    # 验证结果
    if not result or len(result) < 10:
        return {"error": "工具返回结果无效", "raw": result}

    return result
```

### 3. 上下文管理

```python
class ContextManager:
    MAX_CONTEXT_LENGTH = 4000

    @staticmethod
    def add_to_context(shared, new_info):
        context = shared.get("context", "")
        context += f"\n{new_info}"

        # 保持上下文在限制内
        if len(context) > ContextManager.MAX_CONTEXT_LENGTH:
            context = context[-ContextManager.MAX_CONTEXT_LENGTH:]

        shared["context"] = context
```

## 下一步

- [Workflow 工作流](./10_设计模式_Workflow工作流.md) - 固定流程的编排
- [多智能体](./12_设计模式_多智能体.md) - 多个 Agent 协作
- [示例项目解析](./14_示例项目解析.md) - Agent 实战案例
