# PocketFlow FastAPI 后台任务与实时进度

一个 Web 应用程序，演示作为 FastAPI 后台任务运行的 PocketFlow 工作流程，并通过服务器发送事件（SSE）进行实时进度更新。

<p align="center">
  <img
    src="./assets/banner.png" width="800"
  />
</p>

## 功能特性

- **现代 Web UI**：带有实时进度可视化的清洁界面
- **后台处理**：使用 FastAPI BackgroundTasks 进行非阻塞文章生成
- **服务器发送事件**：无需轮询的实时进度流式传输
- **精细进度**：内容生成过程中逐节更新
- **PocketFlow 集成**：三节点工作流程（大纲 → 内容 → 样式）

## 如何运行

1. 安装依赖项：
   ```bash
   pip install -r requirements.txt
   ```

2. 设置您的 OpenAI API 密钥：
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

3. 运行 FastAPI 服务器：
   ```bash
   python main.py
   ```

4. 访问 Web UI：
   打开浏览器并导航到 `http://localhost:8000`。

5. 使用应用程序：
   - 输入文章主题或点击建议的主题
   - 点击"生成文章"开始后台处理
   - 观看带有步骤指示器的实时进度更新
   - 完成后复制最终文章

## 工作原理

应用程序使用 PocketFlow 定义三步文章生成工作流程。FastAPI 处理 Web 请求并管理用于进度更新的实时 SSE 通信。

**PocketFlow 工作流程：**

```mermaid
flowchart LR
    A[Generate Outline] --> B[Write Content]
    B --> C[Apply Style]
```

1. **`GenerateOutline`**：创建最多包含 3 个部分的结构化大纲
2. **`WriteContent` (BatchNode)**：单独为每个部分写入内容，发送进度更新
3. **`ApplyStyle`**：用对话语气润色文章

**FastAPI 和 SSE 集成：**

- `/start-job` 端点创建唯一作业，初始化 SSE 队列，并使用 `BackgroundTasks` 调度工作流程
- 节点在执行期间将进度更新发送到作业特定的 `sse_queue`
- `/progress/{job_id}` 端点通过服务器发送事件将实时更新流式传输到客户端
- Web UI 显示进度，带有动画条、步骤指示器和详细状态消息

**进度更新：**
- 33%：大纲生成完成
- 33-66%：内容编写（各部分更新）
- 66-100%：样式应用
- 100%：文章就绪

## 文件说明

- [`main.py`](./main.py)：带有后台任务和 SSE 端点的 FastAPI 应用程序
- [`flow.py`](./flow.py)：连接三个节点的 PocketFlow 工作流程定义
- [`nodes.py`](./nodes.py)：工作流程节点（GenerateOutline、WriteContent BatchNode、ApplyStyle）
- [`utils/call_llm.py`](./utils/call_llm.py)：OpenAI LLM 工具函数
- [`static/index.html`](./static/index.html)：带有主题建议的现代作业提交表单
- [`static/progress.html`](./static/progress.html)：带有动画的实时进度监控
