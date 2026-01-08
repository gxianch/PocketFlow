import os
from openai import OpenAI

def call_llm1(prompt):    
    client = OpenAI(base_url="https://api.fe8.cn/v1",api_key=os.environ.get("OPENAI_API_KEY", "sk-y11UGaQfmvHCUw6IE88HuSAkwzMavYiQwtQSJZQZhZPU2ic6"))
    r = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content

def call_llm(prompt):
    """测试dify2openai"""
    client = OpenAI(base_url="http://127.0.0.1:5000/v1",api_key=os.environ.get("OPENAI_API_KEY", "sk-abc123"))
    
    response = client.chat.completions.create(
        model="deepseek-v3-0324",
        messages=[{"role": "user", "content": prompt}],
       
    )
    
    return response.choices[0].message.content


if __name__ == "__main__":
    print(call_llm("Tell me a short joke")) 