# 并行批处理翻译流程

此项目演示使用 PocketFlow 的异步和并行功能（`AsyncFlow`、`AsyncParallelBatchNode`）并发地将文档翻译成多种语言。

- 查看[Substack 文章教程](https://pocketflow.substack.com/p/parallel-llm-calls-from-scratch-tutorial)了解更多！

## 目标

并行地将 `../../README.md` 翻译成多种语言（中文、西班牙语等），将每个保存到 `translations/` 目录中的文件。主要目标是与顺序流程比较执行时间。

## 快速开始

1. 安装依赖项：
```bash
pip install -r requirements.txt
```

2. 设置 API 密钥：
   为您的 Anthropic API 密钥设置环境变量。
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```
   *（将 `"your-api-key-here"` 替换为您的实际密钥）*
   *（或者，将 `ANTHROPIC_API_KEY=your-api-key-here` 放在 `.env` 文件中）*

3. 验证 API 密钥（可选）：
   使用实用脚本运行快速检查。
   ```bash
   python utils.py
   ```
   *（注意：这需要设置有效的 API 密钥。）*

4. 运行翻译流程：
   ```bash
   python main.py
   ```

## 工作原理

实现使用一个 `AsyncParallelBatchNode` 来并发处理翻译请求。`TranslateTextNodeParallel`：

1. 准备批处理，将源文本与每种目标语言配对。

2. 使用 `async` 操作并发地向 LLM 执行所有语言的翻译调用。

3. 将翻译后的内容保存到单独的文件（`translations/README_LANGUAGE.md`）。

这种方法利用 `asyncio` 和并行执行来加速像多个 API 调用这样的 I/O 密集型任务。

## 示例输出和比较

运行这个并行版本与顺序方法相比显著减少了总时间：

```
# --- 顺序运行输出（来自 pocketflow-batch）---
Starting sequential translation into 8 languages...
Translated Chinese text
...
Translated Korean text
Saved translation to translations/README_CHINESE.md
...
Saved translation to translations/README_KOREAN.md

Total sequential translation time: ~1136 seconds

=== Translation Complete ===
Translations saved to: translations
============================


# --- 并行运行输出（此示例）---
Starting parallel translation into 8 languages...
Translated French text
Translated Portuguese text
... # 消息可能会交错出现
Translated Spanish text
Saved translation to translations/README_CHINESE.md
...
Saved translation to translations/README_KOREAN.md

Total parallel translation time: ~209 seconds

=== Translation Complete ===
Translations saved to: translations
============================
```
*（实际时间会根据 API 响应速度和系统而变化。）*

## 文件说明

- [`main.py`](./main.py)：实现并行批处理翻译节点和流程。
- [`utils.py`](./utils.py)：调用 Anthropic 模型的异步封装器。
- [`requirements.txt`](./requirements.txt)：项目依赖项（包含 `aiofiles`）。
- [`translations/`](./translations/)：输出目录（自动创建）。
