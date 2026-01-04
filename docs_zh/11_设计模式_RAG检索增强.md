# 设计模式：RAG 检索增强

## 概述

**RAG（Retrieval-Augmented Generation，检索增强生成）** 是一种结合信息检索和文本生成的模式。通过检索相关文档为 LLM 提供上下文，提高回答的准确性和时效性。

## RAG 基本架构

```
┌─────────────────────────────────────────────────────────────┐
│                        RAG 系统                              │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   离线索引阶段                         │   │
│  │  文档 ──▶ 分块 ──▶ 向量化 ──▶ 存储到向量数据库          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   在线查询阶段                         │   │
│  │  查询 ──▶ 向量化 ──▶ 检索 ──▶ 构建 Prompt ──▶ 生成回答  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 离线索引阶段

### 文档加载节点

```python
from pocketflow import Node, BatchNode, Flow

class LoadDocumentsNode(Node):
    """加载文档"""
    def prep(self, shared):
        return shared["document_paths"]

    def exec(self, paths):
        documents = []
        for path in paths:
            with open(path, 'r') as f:
                documents.append({
                    "path": path,
                    "content": f.read()
                })
        return documents

    def post(self, shared, prep_res, exec_res):
        shared["documents"] = exec_res
```

### 文档分块节点

```python
class ChunkDocumentsNode(BatchNode):
    """文档分块"""
    def prep(self, shared):
        return shared["documents"]

    def exec(self, doc):
        chunks = []
        content = doc["content"]
        chunk_size = self.params.get("chunk_size", 500)
        overlap = self.params.get("overlap", 50)

        for i in range(0, len(content), chunk_size - overlap):
            chunk = content[i:i + chunk_size]
            chunks.append({
                "source": doc["path"],
                "content": chunk,
                "index": len(chunks)
            })
        return chunks

    def post(self, shared, prep_res, exec_res):
        # 展平嵌套列表
        all_chunks = []
        for doc_chunks in exec_res:
            all_chunks.extend(doc_chunks)
        shared["chunks"] = all_chunks
        print(f"共生成 {len(all_chunks)} 个文档块")
```

### 向量化节点

```python
class EmbedChunksNode(BatchNode):
    """生成向量嵌入"""
    def prep(self, shared):
        return shared["chunks"]

    def exec(self, chunk):
        # 调用嵌入模型
        embedding = get_embedding(chunk["content"])
        return {
            **chunk,
            "embedding": embedding
        }

    def post(self, shared, prep_res, exec_res):
        shared["embedded_chunks"] = exec_res
```

### 存储节点

```python
class StoreVectorsNode(Node):
    """存储到向量数据库"""
    def prep(self, shared):
        return shared["embedded_chunks"]

    def exec(self, chunks):
        # 存储到向量数据库（如 Chroma、Pinecone、FAISS）
        vector_store = get_vector_store()

        for chunk in chunks:
            vector_store.add(
                id=f"{chunk['source']}_{chunk['index']}",
                embedding=chunk["embedding"],
                metadata={
                    "source": chunk["source"],
                    "content": chunk["content"]
                }
            )

        return {"stored_count": len(chunks)}

    def post(self, shared, prep_res, exec_res):
        shared["index_result"] = exec_res
        print(f"索引完成，存储了 {exec_res['stored_count']} 个向量")
```

### 离线索引流程

```python
# 创建节点
load = LoadDocumentsNode()
chunk = ChunkDocumentsNode()
embed = EmbedChunksNode()
store = StoreVectorsNode()

# 连接流程
load >> chunk >> embed >> store

# 创建索引流程
index_flow = Flow(start=load)

# 配置分块参数
chunk.set_params({"chunk_size": 500, "overlap": 50})

# 执行索引
shared = {
    "document_paths": ["doc1.txt", "doc2.txt", "doc3.txt"]
}
index_flow.run(shared)
```

## 在线查询阶段

### 查询向量化节点

```python
class QueryEmbedNode(Node):
    """查询向量化"""
    def prep(self, shared):
        return shared["query"]

    def exec(self, query):
        return get_embedding(query)

    def post(self, shared, prep_res, exec_res):
        shared["query_embedding"] = exec_res
```

### 检索节点

```python
class RetrieveNode(Node):
    """检索相关文档"""
    def prep(self, shared):
        return shared["query_embedding"]

    def exec(self, query_embedding):
        vector_store = get_vector_store()

        # 检索最相似的文档
        results = vector_store.search(
            embedding=query_embedding,
            top_k=self.params.get("top_k", 5)
        )

        return results

    def post(self, shared, prep_res, exec_res):
        shared["retrieved_docs"] = exec_res
        print(f"检索到 {len(exec_res)} 个相关文档")
```

### 生成回答节点

```python
class GenerateAnswerNode(Node):
    """生成回答"""
    def prep(self, shared):
        return {
            "query": shared["query"],
            "docs": shared["retrieved_docs"]
        }

    def exec(self, data):
        # 构建上下文
        context = "\n\n".join([
            f"[来源: {doc['metadata']['source']}]\n{doc['metadata']['content']}"
            for doc in data["docs"]
        ])

        prompt = f"""
基于以下参考资料回答问题。如果资料中没有相关信息，请说明。

参考资料:
{context}

问题: {data["query"]}

回答:
"""
        return call_llm(prompt)

    def post(self, shared, prep_res, exec_res):
        shared["answer"] = exec_res
        shared["sources"] = [doc["metadata"]["source"] for doc in prep_res["docs"]]
```

### 在线查询流程

```python
# 创建节点
query_embed = QueryEmbedNode()
retrieve = RetrieveNode()
generate = GenerateAnswerNode()

# 连接流程
query_embed >> retrieve >> generate

# 创建查询流程
query_flow = Flow(start=query_embed)
retrieve.set_params({"top_k": 5})

# 执行查询
shared = {"query": "什么是 PocketFlow？"}
query_flow.run(shared)

print(f"回答: {shared['answer']}")
print(f"来源: {shared['sources']}")
```

## 高级 RAG 技术

### 查询重写

```python
class QueryRewriteNode(Node):
    """查询重写以提高检索效果"""
    def prep(self, shared):
        return shared["query"]

    def exec(self, query):
        prompt = f"""
将以下用户问题改写为更适合信息检索的形式。
生成 3 个不同角度的查询。

原始问题: {query}

返回 JSON 格式:
{{"queries": ["查询1", "查询2", "查询3"]}}
"""
        result = parse_json(call_llm(prompt))
        return result["queries"]

    def post(self, shared, prep_res, exec_res):
        shared["rewritten_queries"] = exec_res
```

### 多查询检索

```python
class MultiQueryRetrieveNode(Node):
    """使用多个查询进行检索"""
    def prep(self, shared):
        return shared["rewritten_queries"]

    def exec(self, queries):
        all_results = []
        seen_ids = set()

        for query in queries:
            embedding = get_embedding(query)
            results = vector_store.search(embedding, top_k=3)

            for result in results:
                if result["id"] not in seen_ids:
                    seen_ids.add(result["id"])
                    all_results.append(result)

        return all_results

    def post(self, shared, prep_res, exec_res):
        shared["retrieved_docs"] = exec_res
```

### 重排序

```python
class RerankNode(Node):
    """使用 LLM 重排序检索结果"""
    def prep(self, shared):
        return {
            "query": shared["query"],
            "docs": shared["retrieved_docs"]
        }

    def exec(self, data):
        prompt = f"""
根据与问题的相关性，对以下文档片段进行排序。
返回按相关性从高到低排列的文档索引列表。

问题: {data["query"]}

文档:
"""
        for i, doc in enumerate(data["docs"]):
            prompt += f"\n[{i}] {doc['metadata']['content'][:200]}..."

        prompt += "\n\n返回 JSON: {\"ranking\": [索引列表]}"

        result = parse_json(call_llm(prompt))
        ranking = result["ranking"]

        # 按排序重新组织文档
        return [data["docs"][i] for i in ranking]

    def post(self, shared, prep_res, exec_res):
        shared["reranked_docs"] = exec_res
```

### 假设性回答生成（HyDE）

```python
class HyDENode(Node):
    """生成假设性回答用于检索"""
    def prep(self, shared):
        return shared["query"]

    def exec(self, query):
        prompt = f"""
假设你已经知道以下问题的答案。
请写一个详细的假设性回答（即使你不确定是否正确）。

问题: {query}

假设性回答:
"""
        hypothetical_answer = call_llm(prompt)
        # 使用假设性回答进行检索
        return get_embedding(hypothetical_answer)

    def post(self, shared, prep_res, exec_res):
        shared["hyde_embedding"] = exec_res
```

## 带反馈的 RAG

```python
class RetrieveWithFeedbackNode(Node):
    """带用户反馈的检索"""
    MAX_ITERATIONS = 3

    def prep(self, shared):
        return {
            "query": shared["query"],
            "feedback": shared.get("feedback", None),
            "previous_docs": shared.get("retrieved_docs", [])
        }

    def exec(self, data):
        if data["feedback"]:
            # 根据反馈调整查询
            adjusted_query = adjust_query(data["query"], data["feedback"])
            embedding = get_embedding(adjusted_query)
        else:
            embedding = get_embedding(data["query"])

        # 排除之前已检索的文档
        exclude_ids = [doc["id"] for doc in data["previous_docs"]]
        return vector_store.search(embedding, top_k=5, exclude=exclude_ids)

    def post(self, shared, prep_res, exec_res):
        shared["retrieved_docs"].extend(exec_res)
        shared["iterations"] = shared.get("iterations", 0) + 1

class EvaluateAnswerNode(Node):
    """评估回答质量"""
    def prep(self, shared):
        return {
            "query": shared["query"],
            "answer": shared["answer"]
        }

    def exec(self, data):
        # 让用户或 LLM 评估
        prompt = f"""
评估以下回答是否完整回答了问题。

问题: {data["query"]}
回答: {data["answer"]}

如果回答完整，返回 {{"satisfied": true}}
如果需要更多信息，返回 {{"satisfied": false, "feedback": "需要的信息"}}
"""
        return parse_json(call_llm(prompt))

    def post(self, shared, prep_res, exec_res):
        if exec_res["satisfied"] or shared["iterations"] >= 3:
            return "complete"
        shared["feedback"] = exec_res["feedback"]
        return "retrieve_more"

# 反馈循环流程
retrieve >> generate >> evaluate
evaluate - "retrieve_more" >> retrieve
evaluate - "complete" >> output
```

## 完整 RAG 系统

```python
class RAGSystem:
    def __init__(self):
        # 索引流程
        self.index_flow = self._build_index_flow()
        # 查询流程
        self.query_flow = self._build_query_flow()

    def _build_index_flow(self):
        load = LoadDocumentsNode()
        chunk = ChunkDocumentsNode()
        embed = EmbedChunksNode()
        store = StoreVectorsNode()

        load >> chunk >> embed >> store
        return Flow(start=load)

    def _build_query_flow(self):
        embed = QueryEmbedNode()
        retrieve = RetrieveNode()
        generate = GenerateAnswerNode()

        embed >> retrieve >> generate
        return Flow(start=embed)

    def index(self, document_paths):
        shared = {"document_paths": document_paths}
        self.index_flow.run(shared)
        return shared["index_result"]

    def query(self, question):
        shared = {"query": question}
        self.query_flow.run(shared)
        return {
            "answer": shared["answer"],
            "sources": shared.get("sources", [])
        }

# 使用
rag = RAGSystem()

# 索引文档
rag.index(["knowledge_base/*.txt"])

# 查询
result = rag.query("如何使用 PocketFlow 构建 RAG？")
print(result["answer"])
```

## 最佳实践

### 1. 分块策略

```python
# 按语义分块（推荐）
def semantic_chunk(text, max_size=500):
    sentences = split_sentences(text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_size:
            current_chunk += sentence
        else:
            chunks.append(current_chunk)
            current_chunk = sentence

    return chunks
```

### 2. 检索数量调优

```python
# 根据上下文窗口动态调整
def get_optimal_top_k(query_complexity):
    if query_complexity == "simple":
        return 3
    elif query_complexity == "medium":
        return 5
    else:
        return 10
```

### 3. 上下文压缩

```python
class CompressContextNode(Node):
    """压缩上下文，保留最相关信息"""
    def exec(self, data):
        prompt = f"""
从以下文档中提取与问题最相关的信息。
只保留关键信息，去除冗余。

问题: {data["query"]}
文档: {data["context"]}

压缩后的上下文:
"""
        return call_llm(prompt)
```

## 下一步

- [多智能体](./12_设计模式_多智能体.md) - RAG 与多 Agent 结合
- [LLM 集成指南](./13_LLM集成指南.md) - 嵌入模型集成
- [示例项目解析](./14_示例项目解析.md) - RAG 实战案例
