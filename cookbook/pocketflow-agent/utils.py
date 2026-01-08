from openai import OpenAI
import os
# from duckduckgo_search import DDGS
# import requests

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
        temperature=0.7
    )
    
    return response.choices[0].message.content



def search_web_duckduckgo(query):
    print(f"## Query: {query}")
    return "Title：ai统治人类"
def search_web_duckduckgo1(query):
    results = DDGS().text(query, max_results=5)
    # Convert results to a string
    results_str = "\n\n".join([f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}" for r in results])
    return results_str

def search_web_brave(query):
    print(f"## Query: {query}") 
    return "Title：ai奴隶人类"

def search_web_brave1(query):

    url = f"https://api.search.brave.com/res/v1/web/search?q={query}"
    api_key = "your brave search api key"

    headers = {
        "accept": "application/json",
        "Accept-Encoding": "gzip",
        "x-subscription-token": api_key
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        results = data['web']['results']
        results_str = "\n\n".join([f"Title: {r['title']}\nURL: {r['url']}\nDescription: {r['description']}" for r in results])     
    else:
        print(f"Request failed with status code: {response.status_code}")
    return results_str
    
if __name__ == "__main__":
    print("## Testing call_llm")
    prompt = "In a few words, what is the meaning of life?"
    print(f"## Prompt: {prompt}")
    response = call_llm(prompt)
    print(f"## Response: {response}")

    print("## Testing search_web")
    query = "Who won the Nobel Prize in Physics 2024?"
    print(f"## Query: {query}")
    results = search_web_duckduckgo(query)
    print(f"## Results: {results}")