from openai import OpenAI
import os

def call_llm(messages):
    client = OpenAI(base_url="https://api.fe8.cn/v1",api_key=os.environ.get("OPENAI_API_KEY", "sk-y11UGaQfmvHCUw6IE88HuSAkwzMavYiQwtQSJZQZhZPU2ic6"))
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7
    )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    # Test the LLM call
    messages = [{"role": "user", "content": "In a few words, what's the meaning of life?"}]
    response = call_llm(messages)
    print(f"Prompt: {messages[0]['content']}")
    print(f"Response: {response}")
