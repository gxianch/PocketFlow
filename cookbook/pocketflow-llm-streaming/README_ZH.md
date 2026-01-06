# LLM 流式传输与中断

演示具有用户中断功能的实时 LLM 响应流式传输。

- 查看 [Substack 文章教程](https://zacharyhuang.substack.com/p/streaming-llm-responses-tutorial) 了解更多！

## 功能特性

- 实时显示 LLM 响应生成过程
- 用户可随时使用 ENTER 键中断

## 运行方式

```bash
pip install -r requirements.txt
python main.py
```

## 工作原理

StreamNode：
1. 创建中断监听器线程
2. 从 LLM 获取内容块
3. 实时显示内容块
4. 处理用户中断

## API 密钥

默认情况下，演示使用虚假流式响应。要使用真实的 OpenAI 流式传输：

1. 编辑 main.py，将 fake_stream_llm 替换为 stream_llm：
```python
# 修改这一行：
chunks = fake_stream_llm(prompt)
# 改为：
chunks = stream_llm(prompt)
```

2. 确保设置了您的 OpenAI API 密钥：
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## 文件说明

- `main.py`：StreamNode 实现
- `utils.py`：真实和虚假的 LLM 流式传输函数
