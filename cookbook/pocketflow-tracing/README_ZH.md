# PocketFlow 追踪（Langfuse 集成）

此 cookbook 演示如何使用 [Langfuse](https://langfuse.com/) 作为追踪后端为 PocketFlow 工作流程提供全面的可观测性。只需进行最少的代码更改（仅需添加一个装饰器），即可自动追踪 PocketFlow 工作流程中的所有节点执行、输入、输出和错误。

## 🎯 功能特性

- **自动追踪**：使用单个装饰器追踪整个流程
- **节点级可观测性**：自动追踪每个节点的 `prep`、`exec` 和 `post` 阶段
- **输入/输出追踪**：捕获工作流程中流动的所有数据
- **错误追踪**：自动捕获和追踪异常
- **异步支持**：全面支持 AsyncFlow 和 AsyncNode
- **最小代码更改**：只需在 Flow 类上添加 `@trace_flow()`
- **Langfuse 集成**：利用 Langfuse 强大的可观测性平台

## 🚀 快速开始

### 1. 安装依赖项

```bash
pip install -r requirements.txt
```

### 2. 环境设置

复制示例环境文件并配置您的 Langfuse 凭据：

```bash
cp .env.example .env
```

然后编辑 `.env` 文件，使用您实际的 Langfuse 配置：

```env
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
LANGFUSE_PUBLIC_KEY=your-langfuse-public-key
LANGFUSE_HOST=your-langfuse-host-url
POCKETFLOW_TRACING_DEBUG=true
```

**注意**：将占位符值替换为您实际的 Langfuse 凭据和主机 URL。

### 3. 基本用法

```python
from pocketflow import Node, Flow
from tracing import trace_flow

class MyNode(Node):
    def prep(self, shared):
        return shared["input"]

    def exec(self, data):
        return f"Processed: {data}"

    def post(self, shared, prep_res, exec_res):
        shared["output"] = exec_res
        return "default"

@trace_flow()  # 🎉 就这样！您的流程现在被追踪了
class MyFlow(Flow):
    def __init__(self):
        super().__init__(start=MyNode())

# 运行您的流程 - 追踪自动发生
flow = MyFlow()
shared = {"input": "Hello World"}
flow.run(shared)
```

## 📊 追踪内容

当您应用 `@trace_flow()` 装饰器时，系统会自动追踪：

### 流程级别
- **流程开始/结束**：总体执行时间和状态
- **输入数据**：流程开始时的初始共享状态
- **输出数据**：流程完成时的最终共享状态
- **错误**：流程执行期间发生的任何异常

### 节点级别
对于流程中的每个节点，系统追踪：

- **prep() 阶段**：
  - 输入：`shared` 数据
  - 输出：`prep` 方法返回的 `prep_res`
  - 执行时间和任何错误

- **exec() 阶段**：
  - 输入：prep 阶段的 `prep_res`
  - 输出：`exec` 方法返回的 `exec_res`
  - 执行时间和任何错误
  - 重试次数（如果已配置）

- **post() 阶段**：
  - 输入：`shared`、`prep_res`、`exec_res`
  - 输出：返回的操作字符串
  - 执行时间和任何错误

## 🔧 配置选项

### 基本配置

```python
from tracing import trace_flow, TracingConfig

# 使用环境变量（默认）
@trace_flow()
class MyFlow(Flow):
    pass

# 自定义流程名称
@trace_flow(flow_name="CustomFlowName")
class MyFlow(Flow):
    pass

# 自定义会话和用户 ID
@trace_flow(session_id="session-123", user_id="user-456")
class MyFlow(Flow):
    pass
```

### 高级配置

```python
from tracing import TracingConfig

# 创建自定义配置
config = TracingConfig(
    langfuse_secret_key="your-secret-key",
    langfuse_public_key="your-public-key",
    langfuse_host="https://your-langfuse-instance.com",
    debug=True,
    trace_inputs=True,
    trace_outputs=True,
    trace_errors=True
)

@trace_flow(config=config)
class MyFlow(Flow):
    pass
```

## 📁 示例

### 基本同步流程
有关追踪简单同步流程的完整示例，请参阅 `examples/basic_example.py`。

```bash
cd examples
python basic_example.py
```

### 异步流程
有关追踪 AsyncFlow 和 AsyncNode 的示例，请参阅 `examples/async_example.py`。

```bash
cd examples
python async_example.py
```

## 🔍 查看追踪结果

运行您的追踪流程后，访问您的 Langfuse 仪表板查看追踪：

**仪表板 URL**：使用您在 `LANGFUSE_HOST` 环境变量中配置的 URL

在仪表板中您将看到：
- **追踪**：每个流程执行一个追踪
- **跨度**：单个节点阶段（prep、exec、post）
- **输入/输出数据**：工作流程中流动的所有数据
- **性能指标**：每个阶段的执行时间
- **错误详情**：堆栈跟踪和错误消息

示例中的追踪。
![alt text](screenshots/chrome_2025-06-27_12-05-28.png)

节点的详细追踪。
![langfuse](screenshots/chrome_2025-06-27_12-07-56.png)

## 🛠️ 高级用法

### 自定义追踪器配置

```python
from tracing import TracingConfig, LangfuseTracer

# 创建自定义配置
config = TracingConfig.from_env()
config.debug = True

# 直接使用追踪器（适用于高级用例）
tracer = LangfuseTracer(config)
```

### 环境变量

您可以使用这些环境变量自定义追踪行为：

```env
# 必需的 Langfuse 配置
LANGFUSE_SECRET_KEY=your-secret-key
LANGFUSE_PUBLIC_KEY=your-public-key
LANGFUSE_HOST=your-langfuse-host

# 可选的追踪配置
POCKETFLOW_TRACING_DEBUG=true
POCKETFLOW_TRACE_INPUTS=true
POCKETFLOW_TRACE_OUTPUTS=true
POCKETFLOW_TRACE_PREP=true
POCKETFLOW_TRACE_EXEC=true
POCKETFLOW_TRACE_POST=true
POCKETFLOW_TRACE_ERRORS=true

# 可选的会话/用户追踪
POCKETFLOW_SESSION_ID=your-session-id
POCKETFLOW_USER_ID=your-user-id
```

## 🐛 故障排除

### 常见问题

1. **"langfuse package not installed"**
   ```bash
   pip install langfuse
   ```

2. **"Langfuse client initialization failed"**
   - 检查您的 `.env` 文件配置
   - 验证 Langfuse 服务器在指定主机上运行
   - 检查网络连接

3. **"No traces appearing in dashboard"**
   - 确保 `POCKETFLOW_TRACING_DEBUG=true` 以查看调试输出
   - 检查您的流程是否实际被执行
   - 验证 Langfuse 凭据是否正确

### 调试模式

启用调试模式以查看详细的追踪信息：

```env
POCKETFLOW_TRACING_DEBUG=true
```

这将打印有关以下内容的详细信息：
- Langfuse 客户端初始化
- 追踪和跨度创建
- 数据序列化
- 错误消息

## 📚 API 参考

### `@trace_flow()`

为 PocketFlow 流程添加 Langfuse 追踪的装饰器。

**参数：**
- `config`（TracingConfig，可选）：自定义配置。如果为 None，则从环境加载。
- `flow_name`（str，可选）：流程的自定义名称。如果为 None，则使用类名。
- `session_id`（str，可选）：用于分组相关追踪的会话 ID。
- `user_id`（str，可选）：追踪的用户 ID。

### `TracingConfig`

追踪设置的配置类。

**方法：**
- `TracingConfig.from_env()`：从环境变量创建配置
- `validate()`：检查配置是否有效
- `to_langfuse_kwargs()`：转换为 Langfuse 客户端 kwargs

### `LangfuseTracer`

Langfuse 集成的核心追踪器类。

**方法：**
- `start_trace()`：开始新的追踪
- `end_trace()`：结束当前追踪
- `start_node_span()`：开始节点执行的跨度
- `end_node_span()`：结束节点执行跨度
- `flush()`：将待处理的追踪刷新到 Langfuse

## 🤝 贡献

此 cookbook 旨在作为 PocketFlow 可观测性的起点。随意根据您的特定需求进行扩展和自定义！

## 📄 许可证

此 cookbook 遵循与 PocketFlow 相同的许可证。
