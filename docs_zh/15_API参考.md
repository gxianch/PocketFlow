# API 参考

## 概述

本文档提供 PocketFlow 所有类和方法的完整 API 参考。

---

## BaseNode

所有节点的基类。

### 构造函数

```python
BaseNode()
```

创建一个基础节点。

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `params` | `dict` | 节点参数字典 |
| `successors` | `dict` | 后继节点映射，格式为 `{action: node}` |

### 方法

#### set_params(params)

设置节点参数。

```python
def set_params(self, params: dict) -> None
```

**参数**：
- `params`: 要设置的参数字典

#### next(node, action="default")

添加后继节点。

```python
def next(self, node: BaseNode, action: str = "default") -> BaseNode
```

**参数**：
- `node`: 后继节点
- `action`: 触发此转换的 action 名称

**返回**：传入的后继节点（支持链式调用）

#### prep(shared)

准备阶段，从 shared 读取数据。

```python
def prep(self, shared: dict) -> Any
```

**参数**：
- `shared`: 全局共享存储

**返回**：传递给 `exec` 的数据

#### exec(prep_res)

执行阶段，核心业务逻辑。

```python
def exec(self, prep_res: Any) -> Any
```

**参数**：
- `prep_res`: `prep` 的返回值

**返回**：传递给 `post` 的结果

#### post(shared, prep_res, exec_res)

后处理阶段，写入 shared 并返回 action。

```python
def post(self, shared: dict, prep_res: Any, exec_res: Any) -> Optional[str]
```

**参数**：
- `shared`: 全局共享存储
- `prep_res`: `prep` 的返回值
- `exec_res`: `exec` 的返回值

**返回**：action 字符串，决定下一个节点

#### run(shared)

运行节点。

```python
def run(self, shared: dict) -> Any
```

**参数**：
- `shared`: 全局共享存储

**返回**：`post` 的返回值

### 运算符

#### >> (右移)

```python
node_a >> node_b  # 等同于 node_a.next(node_b, "default")
```

#### - (减法)

```python
node_a - "action" >> node_b  # 等同于 node_a.next(node_b, "action")
```

---

## Node

带重试机制的节点，继承自 `BaseNode`。

### 构造函数

```python
Node(max_retries: int = 1, wait: float = 0)
```

**参数**：
- `max_retries`: 最大重试次数（包括首次执行）
- `wait`: 重试间隔秒数

### 属性

继承 `BaseNode` 的所有属性，另有：

| 属性 | 类型 | 说明 |
|------|------|------|
| `max_retries` | `int` | 最大重试次数 |
| `wait` | `float` | 重试间隔 |
| `cur_retry` | `int` | 当前重试次数（运行时） |

### 方法

#### exec_fallback(prep_res, exc)

重试耗尽后的降级处理。

```python
def exec_fallback(self, prep_res: Any, exc: Exception) -> Any
```

**参数**：
- `prep_res`: `prep` 的返回值
- `exc`: 最后一次异常

**返回**：降级结果（默认重新抛出异常）

---

## BatchNode

批处理节点，继承自 `Node`。

### 说明

对 `prep` 返回的列表中的每个元素调用 `exec`。

### 执行逻辑

```python
def _exec(self, items):
    return [super()._exec(i) for i in (items or [])]
```

### 使用示例

```python
class MyBatchNode(BatchNode):
    def prep(self, shared):
        return shared["items"]  # 返回列表

    def exec(self, item):
        return process(item)  # 处理单个元素

    def post(self, shared, prep_res, exec_res):
        shared["results"] = exec_res  # exec_res 是结果列表
```

---

## Flow

流程编排器，继承自 `BaseNode`。

### 构造函数

```python
Flow(start: Optional[BaseNode] = None)
```

**参数**：
- `start`: 起始节点

### 属性

继承 `BaseNode` 的所有属性，另有：

| 属性 | 类型 | 说明 |
|------|------|------|
| `start_node` | `BaseNode` | 起始节点 |

### 方法

#### start(start)

设置起始节点。

```python
def start(self, start: BaseNode) -> BaseNode
```

**参数**：
- `start`: 起始节点

**返回**：起始节点

#### get_next_node(curr, action)

获取下一个节点。

```python
def get_next_node(self, curr: BaseNode, action: Optional[str]) -> Optional[BaseNode]
```

**参数**：
- `curr`: 当前节点
- `action`: 当前节点返回的 action

**返回**：下一个节点或 `None`

---

## BatchFlow

批量执行流程，继承自 `Flow`。

### 说明

`prep` 返回参数字典列表，对每个参数字典执行一次完整流程。

### 执行逻辑

```python
def _run(self, shared):
    pr = self.prep(shared) or []
    for bp in pr:
        self._orch(shared, {**self.params, **bp})
    return self.post(shared, pr, None)
```

### 使用示例

```python
class MyBatchFlow(BatchFlow):
    def prep(self, shared):
        return [{"item": x} for x in shared["items"]]
```

---

## AsyncNode

异步节点，继承自 `Node`。

### 异步方法

| 方法 | 说明 |
|------|------|
| `prep_async(shared)` | 异步准备阶段 |
| `exec_async(prep_res)` | 异步执行阶段 |
| `exec_fallback_async(prep_res, exc)` | 异步降级处理 |
| `post_async(shared, prep_res, exec_res)` | 异步后处理阶段 |
| `run_async(shared)` | 异步运行入口 |

### 使用示例

```python
class MyAsyncNode(AsyncNode):
    async def prep_async(self, shared):
        return shared["data"]

    async def exec_async(self, data):
        return await async_operation(data)

    async def post_async(self, shared, prep_res, exec_res):
        shared["result"] = exec_res

# 运行
await node.run_async(shared)
```

### 注意

同步 `_run` 方法会抛出 `RuntimeError("Use run_async.")`

---

## AsyncBatchNode

异步顺序批处理节点，继承自 `AsyncNode` 和 `BatchNode`。

### 执行逻辑

```python
async def _exec(self, items):
    return [await super()._exec(i) for i in items]
```

顺序执行每个元素。

---

## AsyncParallelBatchNode

异步并行批处理节点，继承自 `AsyncNode` 和 `BatchNode`。

### 执行逻辑

```python
async def _exec(self, items):
    return await asyncio.gather(
        *(super()._exec(i) for i in items)
    )
```

并行执行所有元素。

---

## AsyncFlow

异步流程，继承自 `Flow` 和 `AsyncNode`。

### 方法

#### run_async(shared)

异步运行流程。

```python
async def run_async(self, shared: dict) -> Any
```

### 混合节点支持

`AsyncFlow` 可同时包含同步和异步节点：

```python
async def _orch_async(self, shared, params=None):
    while curr:
        if isinstance(curr, AsyncNode):
            last_action = await curr._run_async(shared)
        else:
            last_action = curr._run(shared)  # 同步节点
        curr = self.get_next_node(curr, last_action)
```

---

## AsyncBatchFlow

异步顺序批量流程，继承自 `AsyncFlow` 和 `BatchFlow`。

### 执行逻辑

```python
async def _run_async(self, shared):
    pr = await self.prep_async(shared) or []
    for bp in pr:
        await self._orch_async(shared, {**self.params, **bp})
    return await self.post_async(shared, pr, None)
```

---

## AsyncParallelBatchFlow

异步并行批量流程，继承自 `AsyncFlow` 和 `BatchFlow`。

### 执行逻辑

```python
async def _run_async(self, shared):
    pr = await self.prep_async(shared) or []
    await asyncio.gather(
        *(self._orch_async(shared, {**self.params, **bp}) for bp in pr)
    )
    return await self.post_async(shared, pr, None)
```

---

## _ConditionalTransition

内部辅助类，用于实现 `-` 运算符。

```python
class _ConditionalTransition:
    def __init__(self, src, action):
        self.src = src
        self.action = action

    def __rshift__(self, tgt):
        return self.src.next(tgt, self.action)
```

---

## 类层次结构图

```
BaseNode
├── Node
│   └── BatchNode
├── Flow
│   └── BatchFlow
├── AsyncNode
│   ├── AsyncBatchNode
│   └── AsyncParallelBatchNode
├── AsyncFlow
│   ├── AsyncBatchFlow
│   └── AsyncParallelBatchFlow
└── _ConditionalTransition (辅助类)
```

---

## 导入

```python
from pocketflow import (
    BaseNode,
    Node,
    BatchNode,
    Flow,
    BatchFlow,
    AsyncNode,
    AsyncBatchNode,
    AsyncParallelBatchNode,
    AsyncFlow,
    AsyncBatchFlow,
    AsyncParallelBatchFlow
)
```

## 下一步

- [源码解读](./16_源码解读.md) - 逐行解析 100 行代码
