# 核心概念：Node 节点

## 概述

**Node（节点）** 是 PocketFlow 的核心抽象单元，代表工作流中的一个处理步骤。每个 Node 负责完成一个特定的任务，如调用 LLM、处理数据、执行工具等。

## 类层次结构

```
BaseNode              ─── 最基础的节点抽象
    │
    ├── Node          ─── 带重试机制的节点（最常用）
    │   │
    │   └── BatchNode ─── 批处理节点
    │
    └── Flow          ─── 流程（也是节点，可嵌套）
```

## BaseNode 详解

`BaseNode` 是所有节点的基类，定义了节点的核心行为。

### 源码解析

```python
class BaseNode:
    def __init__(self):
        self.params = {}      # 节点参数
        self.successors = {}  # 后继节点映射 {action: node}

    def set_params(self, params):
        """设置节点参数"""
        self.params = params

    def next(self, node, action="default"):
        """定义后继节点"""
        if action in self.successors:
            warnings.warn(f"Overwriting successor for action '{action}'")
        self.successors[action] = node
        return node

    def prep(self, shared):
        """准备阶段：从 shared 读取数据"""
        pass

    def exec(self, prep_res):
        """执行阶段：核心处理逻辑"""
        pass

    def post(self, shared, prep_res, exec_res):
        """后处理阶段：写入 shared，返回 action"""
        pass

    def _exec(self, prep_res):
        """内部执行方法（可被子类覆写）"""
        return self.exec(prep_res)

    def _run(self, shared):
        """内部运行方法：执行三阶段"""
        p = self.prep(shared)
        e = self._exec(p)
        return self.post(shared, p, e)

    def run(self, shared):
        """公开的运行方法"""
        if self.successors:
            warnings.warn("Node won't run successors. Use Flow.")
        return self._run(shared)
```

### 属性说明

| 属性 | 类型 | 说明 |
|------|------|------|
| `params` | dict | 节点参数，可通过 `set_params` 设置 |
| `successors` | dict | 后继节点映射，格式为 `{action_string: node}` |

## 三阶段执行模型

Node 的执行遵循 **prep → exec → post** 三阶段模型：

```
┌─────────────────────────────────────────────────────────────┐
│                         shared                              │
│                    (全局共享存储)                            │
└─────────────────────────────────────────────────────────────┘
        │                                           ▲
        │ 读取                                      │ 写入
        ▼                                           │
   ┌─────────┐         ┌─────────┐         ┌─────────┐
   │  prep   │ ─────▶  │  exec   │ ─────▶  │  post   │
   │         │ prep_res│         │ exec_res│         │
   └─────────┘         └─────────┘         └─────────┘
                            │
                            │ 不能访问 shared
                            │ (关注点分离)
                            ▼
                       纯计算逻辑
```

### 1. prep（准备阶段）

**职责**：从 `shared` 读取所需数据

```python
def prep(self, shared):
    # 从共享存储获取输入数据
    question = shared["question"]
    context = shared.get("context", "")
    return {"question": question, "context": context}
```

**参数**：
- `shared`: 全局共享存储字典

**返回值**：
- 任意类型，将传递给 `exec` 阶段

### 2. exec（执行阶段）

**职责**：核心业务逻辑，如调用 LLM

```python
def exec(self, prep_res):
    # prep_res 是 prep 的返回值
    question = prep_res["question"]
    context = prep_res["context"]

    # 调用 LLM
    response = call_llm(f"Context: {context}\nQuestion: {question}")
    return response
```

**参数**：
- `prep_res`: `prep` 阶段的返回值

**返回值**：
- 任意类型，将传递给 `post` 阶段

**重要**：`exec` 不应直接访问 `shared`，这是关注点分离的设计。

### 3. post（后处理阶段）

**职责**：将结果写入 `shared`，返回 action 决定下一步

```python
def post(self, shared, prep_res, exec_res):
    # 存储结果
    shared["answer"] = exec_res

    # 返回 action 决定流程走向
    if "I don't know" in exec_res:
        return "need_search"  # 需要搜索更多信息
    else:
        return "done"  # 完成
```

**参数**：
- `shared`: 全局共享存储
- `prep_res`: `prep` 阶段的返回值
- `exec_res`: `exec` 阶段的返回值

**返回值**：
- 字符串（action），用于 Flow 决定下一个节点

## Node 类

`Node` 继承自 `BaseNode`，增加了**重试机制**。

### 源码解析

```python
class Node(BaseNode):
    def __init__(self, max_retries=1, wait=0):
        super().__init__()
        self.max_retries = max_retries  # 最大重试次数
        self.wait = wait                # 重试间隔（秒）

    def exec_fallback(self, prep_res, exc):
        """降级处理：当重试耗尽时调用"""
        raise exc  # 默认行为：抛出异常

    def _exec(self, prep_res):
        for self.cur_retry in range(self.max_retries):
            try:
                return self.exec(prep_res)
            except Exception as e:
                if self.cur_retry == self.max_retries - 1:
                    return self.exec_fallback(prep_res, e)
                if self.wait > 0:
                    time.sleep(self.wait)
```

### 重试机制使用

```python
class LLMNode(Node):
    def __init__(self):
        # 最多重试3次，每次间隔2秒
        super().__init__(max_retries=3, wait=2)

    def exec(self, prompt):
        # 可能因网络问题失败，会自动重试
        return call_llm(prompt)

    def exec_fallback(self, prep_res, exc):
        # 重试耗尽后的降级处理
        return "抱歉，服务暂时不可用"
```

### 重试属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `max_retries` | int | 1 | 最大重试次数 |
| `wait` | float | 0 | 重试间隔秒数 |
| `cur_retry` | int | - | 当前重试次数（运行时） |

## 运算符重载（DSL）

PocketFlow 通过运算符重载提供了优雅的 DSL 语法：

### >> 操作符（默认转换）

```python
def __rshift__(self, other):
    return self.next(other)

# 使用
node_a >> node_b
# 等同于
node_a.next(node_b, action="default")
```

### - 操作符（条件转换）

```python
def __sub__(self, action):
    if isinstance(action, str):
        return _ConditionalTransition(self, action)
    raise TypeError("Action must be a string")

# 辅助类
class _ConditionalTransition:
    def __init__(self, src, action):
        self.src = src
        self.action = action

    def __rshift__(self, tgt):
        return self.src.next(tgt, self.action)

# 使用
node_a - "search" >> node_b
# 等同于
node_a.next(node_b, action="search")
```

### DSL 示例

```python
# 创建节点
decide = DecideNode()
search = SearchNode()
answer = AnswerNode()

# 定义流程（使用 DSL）
decide - "search" >> search >> decide  # 搜索后回到决策
decide - "answer" >> answer             # 直接回答

# 等同于（使用方法）
decide.next(search, action="search")
search.next(decide, action="default")
decide.next(answer, action="answer")
```

## 节点参数

通过 `params` 可以向节点传递参数：

```python
class GreetNode(Node):
    def exec(self, _):
        name = self.params.get("name", "Guest")
        lang = self.params.get("lang", "en")

        if lang == "zh":
            return f"你好，{name}！"
        else:
            return f"Hello, {name}!"

# 使用
node = GreetNode()
node.set_params({"name": "Alice", "lang": "zh"})
node.run({})  # 输出: 你好，Alice！
```

## 最佳实践

### 1. 保持 exec 纯净

```python
# ❌ 不推荐：exec 中直接访问 shared
def exec(self, prep_res):
    self.shared["temp"] = "..."  # 不应该这样做

# ✅ 推荐：通过 prep 和 post 处理 shared
def prep(self, shared):
    return shared["input"]

def exec(self, prep_res):
    return process(prep_res)

def post(self, shared, prep_res, exec_res):
    shared["output"] = exec_res
```

### 2. action 命名清晰

```python
# ✅ 语义明确的 action
return "need_more_info"
return "answer_ready"
return "error_occurred"

# ❌ 模糊的 action
return "next"
return "1"
return "a"
```

### 3. 错误处理

```python
class SafeNode(Node):
    def __init__(self):
        super().__init__(max_retries=3, wait=1)

    def exec_fallback(self, prep_res, exc):
        # 记录错误
        logging.error(f"执行失败: {exc}")
        # 返回默认值而非抛出异常
        return {"error": str(exc), "data": None}
```

## 下一步

- [Flow 流程](./04_核心概念_Flow流程.md) - 了解如何编排多个节点
- [共享存储](./05_核心概念_共享存储.md) - 深入理解数据通信
- [重试与容错](./08_高级特性_重试与容错.md) - 更多错误处理技巧
