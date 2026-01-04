# 核心概念：Flow 流程

## 概述

**Flow（流程）** 是 PocketFlow 的流程编排器，负责按照定义的规则连接和执行多个 Node。Flow 本身也是一个 Node，因此可以嵌套组合。

## 核心设计

Flow 实现了**状态机模式**：
- 每个 Node 是一个状态
- Node 的 `post()` 返回值（action）是状态转换的触发器
- `successors` 字典定义了状态转换规则

```
          ┌──────────────────────────────────────┐
          │              Flow                     │
          │                                       │
          │   ┌───────┐  action_a  ┌───────┐     │
     ────▶│   │ Start │──────────▶│ Node A│     │
          │   └───────┘            └───────┘     │
          │        │                    │        │
          │        │action_b            │action_c│
          │        ▼                    ▼        │
          │   ┌───────┐            ┌───────┐     │
          │   │ Node B│            │ Node C│─────│────▶
          │   └───────┘            └───────┘     │
          │                                       │
          └──────────────────────────────────────┘
```

## Flow 类详解

### 源码解析

```python
class Flow(BaseNode):
    def __init__(self, start=None):
        super().__init__()
        self.start_node = start  # 起始节点

    def start(self, start):
        """设置起始节点"""
        self.start_node = start
        return start

    def get_next_node(self, curr, action):
        """获取下一个节点"""
        nxt = curr.successors.get(action or "default")
        if not nxt and curr.successors:
            warnings.warn(f"Flow ends: '{action}' not found in {list(curr.successors)}")
        return nxt

    def _orch(self, shared, params=None):
        """编排执行：遍历节点图"""
        curr = copy.copy(self.start_node)
        p = params or {**self.params}
        last_action = None

        while curr:
            curr.set_params(p)
            last_action = curr._run(shared)
            curr = copy.copy(self.get_next_node(curr, last_action))

        return last_action

    def _run(self, shared):
        """运行流程"""
        p = self.prep(shared)
        o = self._orch(shared)
        return self.post(shared, p, o)

    def post(self, shared, prep_res, exec_res):
        """默认 post：返回最后一个节点的 action"""
        return exec_res
```

### 关键机制

#### 1. 节点复制（copy.copy）

```python
curr = copy.copy(self.start_node)
```

每次执行时复制节点，避免节点状态污染：
- 多次运行同一 Flow 不会相互影响
- 节点的 `params`、`cur_retry` 等状态独立

#### 2. 编排循环

```python
while curr:
    curr.set_params(p)              # 传递参数
    last_action = curr._run(shared)  # 执行节点
    curr = copy.copy(self.get_next_node(curr, last_action))  # 获取下一个节点
```

循环直到没有后继节点（`get_next_node` 返回 `None`）。

## 创建 Flow 的方式

### 方式一：构造函数

```python
flow = Flow(start=node_a)
```

### 方式二：start 方法

```python
flow = Flow()
flow.start(node_a)
```

### 方式三：链式定义

```python
# 先定义节点关系
node_a >> node_b >> node_c

# 再创建 Flow
flow = Flow(start=node_a)
```

## 节点连接语法

### 顺序连接（>>）

```python
# 线性流程
node_a >> node_b >> node_c

# 等同于
node_a.next(node_b, "default")
node_b.next(node_c, "default")
```

执行流程：
```
node_a (post 返回 "default") → node_b → node_c
```

### 条件分支（-）

```python
# 条件分支
decide_node - "option_a" >> node_a
decide_node - "option_b" >> node_b
decide_node - "option_c" >> node_c
```

执行流程：
```
decide_node.post() 返回 "option_a" → node_a
decide_node.post() 返回 "option_b" → node_b
decide_node.post() 返回 "option_c" → node_c
```

### 循环（自引用）

```python
# 自循环
process_node - "continue" >> process_node
process_node - "done" >> end_node
```

执行流程：
```
process_node ──"continue"──┐
     ▲                     │
     └─────────────────────┘

process_node ──"done"──▶ end_node
```

### 复杂流程示例

```python
# 研究型 Agent 流程
decide = DecideNode()
search = SearchNode()
summarize = SummarizeNode()
answer = AnswerNode()

# 定义关系
decide - "search" >> search >> summarize >> decide
decide - "answer" >> answer

# 创建 Flow
flow = Flow(start=decide)
```

流程图：
```
          ┌────────────────────────────┐
          │                            │
          ▼                            │
     ┌─────────┐   search    ┌──────────┐
     │ Decide  │────────────▶│  Search  │
     └─────────┘             └──────────┘
          │                       │
          │answer                 │default
          ▼                       ▼
     ┌─────────┐            ┌──────────┐
     │ Answer  │            │Summarize │
     └─────────┘            └──────────┘
                                  │
                                  │default
                                  └────────▶ (回到 Decide)
```

## Flow 嵌套

Flow 本身是 BaseNode 的子类，因此可以作为另一个 Flow 的节点：

```python
# 子流程1：数据预处理
preprocess_flow = Flow(start=clean_node)
clean_node >> validate_node >> transform_node

# 子流程2：数据处理
process_flow = Flow(start=compute_node)
compute_node >> aggregate_node

# 主流程
main_flow = Flow(start=preprocess_flow)
preprocess_flow >> process_flow >> save_node
```

层次结构：
```
main_flow
├── preprocess_flow
│   ├── clean_node
│   ├── validate_node
│   └── transform_node
├── process_flow
│   ├── compute_node
│   └── aggregate_node
└── save_node
```

## Flow 的 prep/post

Flow 也可以覆写 `prep` 和 `post`：

```python
class MyFlow(Flow):
    def prep(self, shared):
        """流程开始前的准备"""
        print(f"流程开始，共享数据: {shared}")
        return shared.get("flow_config", {})

    def post(self, shared, prep_res, exec_res):
        """流程结束后的处理"""
        print(f"流程结束，最后 action: {exec_res}")
        shared["flow_completed"] = True
        return exec_res  # 或返回自定义 action
```

## 参数传递

Flow 可以通过 `params` 向所有节点传递参数：

```python
class TranslateNode(Node):
    def exec(self, text):
        target_lang = self.params.get("target_lang", "en")
        return translate(text, target_lang)

# 创建流程
flow = Flow(start=translate_node)

# 设置参数（所有节点都能访问）
flow.set_params({"target_lang": "zh"})

# 运行
flow.run(shared)
```

## 运行 Flow

### 基本运行

```python
shared = {"input": "Hello World"}
result = flow.run(shared)
print(result)  # 最后一个节点的 action
```

### 结果获取

Flow 的 `run()` 返回最后一个节点的 `post()` 返回值（action）。
实际结果通常存储在 `shared` 中：

```python
shared = {"question": "What is AI?"}
flow.run(shared)

# 从 shared 获取结果
answer = shared["answer"]
sources = shared.get("sources", [])
```

## BatchFlow

`BatchFlow` 用于批量执行流程：

```python
class BatchFlow(Flow):
    def _run(self, shared):
        pr = self.prep(shared) or []
        for bp in pr:
            self._orch(shared, {**self.params, **bp})
        return self.post(shared, pr, None)
```

使用示例：

```python
class TranslateBatchFlow(BatchFlow):
    def prep(self, shared):
        # 返回批处理参数列表
        return [
            {"text": doc, "target_lang": "zh"}
            for doc in shared["documents"]
        ]

# 每个文档都会执行一次完整流程
batch_flow = TranslateBatchFlow(start=translate_node)
batch_flow.run({"documents": ["Hello", "World", "PocketFlow"]})
```

## 调试技巧

### 1. 打印执行路径

```python
class DebugNode(Node):
    def _run(self, shared):
        print(f">>> 执行节点: {self.__class__.__name__}")
        result = super()._run(shared)
        print(f"<<< 节点返回: {result}")
        return result
```

### 2. 可视化流程

```python
def visualize_flow(flow, indent=0):
    """简单的流程可视化"""
    prefix = "  " * indent
    node = flow.start_node
    visited = set()

    def visit(n, level):
        if n is None or id(n) in visited:
            return
        visited.add(id(n))

        print(f"{'  ' * level}{n.__class__.__name__}")
        for action, successor in n.successors.items():
            print(f"{'  ' * level}  --{action}-->")
            visit(successor, level + 1)

    visit(node, indent)
```

## 最佳实践

### 1. 明确的起始和结束

```python
# ✅ 推荐：清晰的流程结构
start_node >> process_node >> end_node

# 结束节点不定义后继
class EndNode(Node):
    def post(self, shared, prep_res, exec_res):
        shared["completed"] = True
        # 不返回 action，流程自然结束
```

### 2. 处理未知 action

```python
# 添加默认处理
decide_node - "option_a" >> node_a
decide_node - "option_b" >> node_b
decide_node >> default_node  # 默认路径
```

### 3. 避免死循环

```python
# ✅ 有退出条件的循环
class LoopNode(Node):
    def post(self, shared, prep_res, exec_res):
        shared["iterations"] = shared.get("iterations", 0) + 1
        if shared["iterations"] >= 10:  # 最大迭代次数
            return "done"
        return "continue"
```

## 下一步

- [共享存储](./05_核心概念_共享存储.md) - 理解节点间通信
- [批处理](./06_高级特性_批处理.md) - 学习 BatchFlow
- [异步支持](./07_高级特性_异步支持.md) - 了解 AsyncFlow
