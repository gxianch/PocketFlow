# PocketFlow 文本摘要

演示如何使用 PocketFlow 构建具有错误处理和重试机制的强大文本摘要工具的实际示例。此示例在实际应用中展示了核心 PocketFlow 概念。

## 功能特性

- 使用 LLM（大语言模型）进行文本摘要
- API 失败时自动重试机制（最多 3 次尝试）
- 具有回退响应的优雅错误处理
- 使用 PocketFlow 的 Node 架构实现清晰的关注点分离

## 项目结构

```
.
├── docs/          # 文档文件
├── utils/         # 实用函数（LLM API 封装器）
├── flow.py        # 带摘要节点的 PocketFlow 实现
├── main.py        # 主要应用程序入口点
└── README.md      # 项目文档
```

## 实现细节

该示例实现了一个简单但强大的文本摘要工作流程：

1. **摘要节点** (`flow.py`)：
   - `prep()`：从共享存储中检索文本
   - `exec()`：调用 LLM 将文本摘要为 10 个单词
   - `exec_fallback()`：提供优雅的错误处理
   - `post()`：将摘要存储回共享存储

2. **流程结构**：
   - 用于演示的单节点流程
   - 配置 3 次重试以提高可靠性
   - 使用共享存储传递数据

## 环境配置

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Windows 系统：venv\Scripts\activate
```

2. 安装依赖项：
```bash
pip install -r requirements.txt
```

3. 配置您的环境：
   - 设置您的 LLM API 密钥（检查 utils/call_llm.py 以获取配置）

4. 运行示例：
```bash
python main.py
```

## 示例用法

该示例带有关于 PocketFlow 的示例文本，但您可以修改 `main.py` 来摘要您自己的文本：

```python
shared = {"data": "Your text to summarize here..."}
flow.run(shared)
print("Summary:", shared["summary"])
```

## 您将学到什么

此示例演示了几个关键的 PocketFlow 概念：

- **节点架构**：如何使用 prep/exec/post 模式构建 LLM 任务
- **错误处理**：实现重试机制和回退
- **共享存储**：使用共享存储在步骤之间传递数据
- **流程创建**：设置基本的 PocketFlow 工作流程

## 更多资源

- [PocketFlow 文档](https://the-pocket.github.io/PocketFlow/)
- [节点概念指南](https://the-pocket.github.io/PocketFlow/node.html)
- [流程设计模式](https://the-pocket.github.io/PocketFlow/flow.html)
