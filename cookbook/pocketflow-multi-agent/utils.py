import os
from openai import OpenAI

def call_llm(prompt):    
    client = OpenAI(base_url="https://api.fe8.cn/v1",api_key=os.environ.get("OPENAI_API_KEY", "sk-y11UGaQfmvHCUw6IE88HuSAkwzMavYiQwtQSJZQZhZPU2ic6"))
    r = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content

# Example usage
if __name__ == "__main__":
    print(call_llm("Tell me a short joke")) 