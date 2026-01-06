# PocketFlow MCP 演示

此项目展示如何使用 PocketFlow 和模型上下文协议（MCP）构建执行加法运算的智能体。它比较了使用 MCP 和基本函数调用方法。

此实现基于教程：[MCP Simply Explained: Function Calling Rebranded or Genuine Breakthrough?](https://zacharyhuang.substack.com/p/mcp-simply-explained-function-calling)

## 功能特性

- 通过简单终端界面进行数学运算工具
- 与模型上下文协议（MCP）集成
- 比较 MCP 和直接函数调用
- **简单切换**在 MCP 和本地函数调用之间

## 如何运行

1. 设置您的 API 密钥：
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   或直接在 `utils.py` 中更新

2. 安装并运行：
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

## MCP 与函数调用

为了比较这两种方法，此演示提供了不需要 MCP 的本地函数替代方案：

- **使用简单标志切换：**在 `utils.py` 顶部设置 `MCP = True` 或 `MCP = False` 以在 MCP 和本地实现之间切换。
- 无需更改代码！应用程序自动使用以下任一方式：
  - `MCP = True` 时的 MCP 服务器工具
  - `MCP = False` 时的本地函数实现

这使您可以在保持相同工作流程的同时看到两种方法之间的差异。

### 函数调用
- 函数直接嵌入在应用程序代码中
- 每个新工具都需要修改应用程序
- 工具在应用程序本身内定义

### MCP 方法
- 工具位于单独的 MCP 服务器中
- 所有工具交互的标准协议
- 新工具可以在不更改智能体的情况下添加
- AI 可以通过一致的界面与工具交互

## 工作原理

```mermaid
flowchart LR
    tools[GetToolsNode] -->|decide| decide[DecideToolNode]
    decide -->|execute| execute[ExecuteToolNode]
```

智能体使用 PocketFlow 创建一个工作流程，其中：
1. 获取用户关于数字的输入
2. 连接到 MCP 服务器进行数学运算（或根据 `MCP` 标志使用本地函数）
3. 返回结果

## 文件说明

- [`main.py`](./main.py)：使用 PocketFlow 实现加法智能体
- [`utils.py`](./utils.py)：API 调用和 MCP 集成的辅助函数
- [`simple_server.py`](./simple_server.py)：提供加法工具的 MCP 服务器
