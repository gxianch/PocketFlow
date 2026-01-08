import os
from openai import AsyncOpenAI

async def stream_llm1(messages):
    client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
    
    stream = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True,
        temperature=0.7
    )
    
    async for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content


async def stream_llm(messages):
    """测试dify2openai"""
    client = AsyncOpenAI(base_url="http://127.0.0.1:5000/v1",api_key=os.environ.get("OPENAI_API_KEY", "sk-abc123"))
    stream = await client.chat.completions.create(
        model="deepseek-v3-0324",
        messages=messages,
        stream=True,
        temperature=0.7
    )
    
    async for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content




if __name__ == "__main__":
    import asyncio
    
    async def test():
        messages = [{"role": "user", "content": "Hello!"}]
        async for chunk in stream_llm(messages):
            print(chunk, end="", flush=True)
        print()
    
    asyncio.run(test()) 