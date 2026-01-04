# LLM 集成指南

## 概述

PocketFlow 不内置任何 LLM SDK，而是让用户自行实现 LLM 调用。这种设计提供了最大的灵活性，可以轻松切换 LLM 供应商或使用本地模型。

## 为什么不内置 LLM？

1. **API 易变性**：LLM 供应商的 API 经常变化，硬编码会导致维护负担
2. **灵活性**：可以自由选择供应商、使用微调模型或本地部署
3. **优化空间**：可以自定义 prompt 缓存、批处理、流式输出等

## OpenAI 集成

### 基础调用

```python
from openai import OpenAI
import os

# 初始化客户端
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def call_llm(messages, model="gpt-4", **kwargs):
    """
    调用 OpenAI LLM

    Args:
        messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
        model: 模型名称
        **kwargs: 其他参数如 temperature, max_tokens 等

    Returns:
        str: 模型回复内容
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        **kwargs
    )
    return response.choices[0].message.content
```

### 在节点中使用

```python
from pocketflow import Node

class LLMNode(Node):
    def prep(self, shared):
        return shared["question"]

    def exec(self, question):
        messages = [
            {"role": "system", "content": "你是一个有用的助手。"},
            {"role": "user", "content": question}
        ]
        return call_llm(messages)

    def post(self, shared, prep_res, exec_res):
        shared["answer"] = exec_res
```

### 流式输出

```python
def stream_llm(messages, model="gpt-4"):
    """流式调用 LLM"""
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

class StreamingNode(Node):
    def exec(self, prompt):
        messages = [{"role": "user", "content": prompt}]
        full_response = ""

        for chunk in stream_llm(messages):
            print(chunk, end="", flush=True)
            full_response += chunk

        print()  # 换行
        return full_response
```

### 结构化输出

```python
import json

def call_llm_json(messages, model="gpt-4"):
    """调用 LLM 并返回 JSON"""
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

class StructuredOutputNode(Node):
    def exec(self, data):
        messages = [
            {"role": "system", "content": "请返回 JSON 格式的响应。"},
            {"role": "user", "content": f"从以下文本中提取信息：\n{data}"}
        ]
        return call_llm_json(messages)
```

## Claude (Anthropic) 集成

```python
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def call_claude(messages, model="claude-3-opus-20240229", **kwargs):
    """调用 Claude"""
    response = client.messages.create(
        model=model,
        max_tokens=kwargs.get("max_tokens", 1024),
        messages=messages
    )
    return response.content[0].text

class ClaudeNode(Node):
    def exec(self, prompt):
        messages = [{"role": "user", "content": prompt}]
        return call_claude(messages)
```

## 本地模型集成

### Ollama

```python
import requests

def call_ollama(prompt, model="llama2"):
    """调用 Ollama 本地模型"""
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]

class OllamaNode(Node):
    def exec(self, prompt):
        return call_ollama(prompt, model="llama2")
```

### LM Studio

```python
from openai import OpenAI

# LM Studio 兼容 OpenAI API
local_client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="not-needed"
)

def call_local_model(messages):
    response = local_client.chat.completions.create(
        model="local-model",
        messages=messages
    )
    return response.choices[0].message.content
```

### vLLM

```python
from openai import OpenAI

vllm_client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="token"
)

def call_vllm(messages, model="meta-llama/Llama-2-7b-chat-hf"):
    response = vllm_client.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content
```

## 嵌入模型集成

### OpenAI Embeddings

```python
def get_embedding(text, model="text-embedding-3-small"):
    """获取文本嵌入向量"""
    response = client.embeddings.create(
        model=model,
        input=text
    )
    return response.data[0].embedding

class EmbedNode(Node):
    def exec(self, text):
        return get_embedding(text)
```

### 本地嵌入模型（Sentence Transformers）

```python
from sentence_transformers import SentenceTransformer

# 加载模型（首次会下载）
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

def get_local_embedding(text):
    """使用本地模型获取嵌入"""
    return embed_model.encode(text).tolist()
```

## 异步 LLM 调用

### 异步 OpenAI

```python
from openai import AsyncOpenAI

async_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

async def async_call_llm(messages, model="gpt-4"):
    """异步调用 LLM"""
    response = await async_client.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content

class AsyncLLMNode(AsyncNode):
    async def exec_async(self, prompt):
        messages = [{"role": "user", "content": prompt}]
        return await async_call_llm(messages)
```

### 并行 LLM 调用

```python
from pocketflow import AsyncParallelBatchNode

class ParallelLLMNode(AsyncParallelBatchNode):
    async def prep_async(self, shared):
        return shared["prompts"]

    async def exec_async(self, prompt):
        messages = [{"role": "user", "content": prompt}]
        return await async_call_llm(messages)

    async def post_async(self, shared, prep_res, exec_res):
        shared["responses"] = exec_res
```

## LLM 封装器

创建一个统一的 LLM 封装器，方便切换供应商：

```python
class LLMWrapper:
    """统一的 LLM 封装器"""

    def __init__(self, provider="openai", model=None, **config):
        self.provider = provider
        self.model = model
        self.config = config
        self._init_client()

    def _init_client(self):
        if self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            self.model = self.model or "gpt-4"
        elif self.provider == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            self.model = self.model or "claude-3-opus-20240229"
        elif self.provider == "ollama":
            self.model = self.model or "llama2"

    def call(self, messages, **kwargs):
        merged_kwargs = {**self.config, **kwargs}

        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **merged_kwargs
            )
            return response.choices[0].message.content
        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                messages=messages,
                max_tokens=merged_kwargs.get("max_tokens", 1024)
            )
            return response.content[0].text
        elif self.provider == "ollama":
            import requests
            prompt = messages[-1]["content"]
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False}
            )
            return response.json()["response"]

# 使用
llm = LLMWrapper(provider="openai", model="gpt-4", temperature=0.7)
response = llm.call([{"role": "user", "content": "Hello!"}])

# 切换到 Claude
llm = LLMWrapper(provider="anthropic", model="claude-3-opus-20240229")
```

## 配置管理

### 环境变量

```python
import os

# .env 文件
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-...
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-4

class ConfigurableLLMNode(Node):
    def __init__(self):
        super().__init__()
        self.provider = os.environ.get("LLM_PROVIDER", "openai")
        self.model = os.environ.get("LLM_MODEL", "gpt-4")

    def exec(self, prompt):
        llm = LLMWrapper(provider=self.provider, model=self.model)
        return llm.call([{"role": "user", "content": prompt}])
```

### 通过 shared 配置

```python
class FlexibleLLMNode(Node):
    def prep(self, shared):
        return {
            "prompt": shared["prompt"],
            "llm_config": shared.get("llm_config", {})
        }

    def exec(self, data):
        config = data["llm_config"]
        llm = LLMWrapper(
            provider=config.get("provider", "openai"),
            model=config.get("model"),
            temperature=config.get("temperature", 0.7)
        )
        return llm.call([{"role": "user", "content": data["prompt"]}])

# 使用
shared = {
    "prompt": "Hello!",
    "llm_config": {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.9
    }
}
```

## 最佳实践

### 1. 重试和错误处理

```python
class RobustLLMNode(Node):
    def __init__(self):
        super().__init__(max_retries=3, wait=2)

    def exec(self, prompt):
        messages = [{"role": "user", "content": prompt}]
        return call_llm(messages)

    def exec_fallback(self, prep_res, exc):
        # 尝试使用备用模型
        try:
            return call_llm(
                [{"role": "user", "content": prep_res}],
                model="gpt-3.5-turbo"  # 降级到更便宜的模型
            )
        except:
            return "抱歉，服务暂时不可用。"
```

### 2. Token 计算

```python
import tiktoken

def count_tokens(text, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

class TokenAwareNode(Node):
    MAX_TOKENS = 4000

    def prep(self, shared):
        context = shared.get("context", "")
        if count_tokens(context) > self.MAX_TOKENS:
            # 截断上下文
            context = truncate_to_tokens(context, self.MAX_TOKENS)
        return context
```

### 3. 缓存

```python
import hashlib
import json

class CachedLLMNode(Node):
    cache = {}

    def exec(self, prompt):
        # 生成缓存键
        cache_key = hashlib.md5(prompt.encode()).hexdigest()

        if cache_key in self.cache:
            return self.cache[cache_key]

        result = call_llm([{"role": "user", "content": prompt}])
        self.cache[cache_key] = result
        return result
```

## 下一步

- [示例项目解析](./14_示例项目解析.md) - 查看 LLM 集成实例
- [API 参考](./15_API参考.md) - 异步节点 API
- [源码解读](./16_源码解读.md) - 理解框架原理
