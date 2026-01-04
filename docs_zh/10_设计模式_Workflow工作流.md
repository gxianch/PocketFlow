# 设计模式：Workflow 工作流

## 概述

**Workflow（工作流）** 是一种预定义的多步骤任务编排模式。与 Agent 不同，Workflow 的执行路径是确定的，适合结构化的任务处理。

## 核心特征

| 特征 | Workflow | Agent |
|------|----------|-------|
| 执行路径 | 预定义、确定 | 动态决策 |
| 复杂度 | 较低 | 较高 |
| 可预测性 | 高 | 低 |
| 适用场景 | 结构化任务 | 开放式问题 |

## 基本 Workflow

### 线性工作流

```python
from pocketflow import Node, Flow

class Step1(Node):
    """步骤1: 数据收集"""
    def exec(self, _):
        return collect_data()

    def post(self, shared, prep_res, exec_res):
        shared["raw_data"] = exec_res

class Step2(Node):
    """步骤2: 数据处理"""
    def prep(self, shared):
        return shared["raw_data"]

    def exec(self, data):
        return process_data(data)

    def post(self, shared, prep_res, exec_res):
        shared["processed_data"] = exec_res

class Step3(Node):
    """步骤3: 结果输出"""
    def prep(self, shared):
        return shared["processed_data"]

    def exec(self, data):
        return format_output(data)

    def post(self, shared, prep_res, exec_res):
        shared["final_result"] = exec_res

# 构建线性工作流
step1 = Step1()
step2 = Step2()
step3 = Step3()

step1 >> step2 >> step3

workflow = Flow(start=step1)
```

```
step1 ──▶ step2 ──▶ step3
收集       处理       输出
```

### 条件分支工作流

```python
class ValidateNode(Node):
    """验证节点"""
    def prep(self, shared):
        return shared["input"]

    def exec(self, data):
        return validate(data)

    def post(self, shared, prep_res, exec_res):
        shared["validation"] = exec_res
        if exec_res["is_valid"]:
            return "process"
        else:
            return "reject"

class ProcessNode(Node):
    """处理节点"""
    def exec(self, _):
        return "处理完成"

class RejectNode(Node):
    """拒绝节点"""
    def prep(self, shared):
        return shared["validation"]["errors"]

    def exec(self, errors):
        return f"验证失败: {errors}"

# 构建条件工作流
validate = ValidateNode()
process = ProcessNode()
reject = RejectNode()

validate - "process" >> process
validate - "reject" >> reject

workflow = Flow(start=validate)
```

```
           ┌──"process"──▶ ProcessNode
ValidateNode
           └──"reject"───▶ RejectNode
```

## 内容生成工作流

### 写作工作流

```python
class OutlineNode(Node):
    """生成大纲"""
    def prep(self, shared):
        return shared["topic"]

    def exec(self, topic):
        prompt = f"为以下主题生成文章大纲：\n{topic}"
        return call_llm(prompt)

    def post(self, shared, prep_res, exec_res):
        shared["outline"] = exec_res

class WriteNode(Node):
    """撰写内容"""
    def prep(self, shared):
        return {
            "topic": shared["topic"],
            "outline": shared["outline"]
        }

    def exec(self, data):
        prompt = f"""
主题: {data["topic"]}
大纲: {data["outline"]}

请根据大纲撰写完整文章：
"""
        return call_llm(prompt)

    def post(self, shared, prep_res, exec_res):
        shared["draft"] = exec_res

class ReviewNode(Node):
    """审核修改"""
    def prep(self, shared):
        return shared["draft"]

    def exec(self, draft):
        prompt = f"""
请审核并改进以下文章，修正错误并提升质量：

{draft}
"""
        return call_llm(prompt)

    def post(self, shared, prep_res, exec_res):
        shared["final_article"] = exec_res

# 构建写作工作流
outline = OutlineNode()
write = WriteNode()
review = ReviewNode()

outline >> write >> review

writing_flow = Flow(start=outline)

# 使用
shared = {"topic": "人工智能的未来发展"}
writing_flow.run(shared)
print(shared["final_article"])
```

### 代码生成工作流

```python
class AnalyzeRequirements(Node):
    """分析需求"""
    def prep(self, shared):
        return shared["requirements"]

    def exec(self, requirements):
        prompt = f"""
分析以下需求，输出技术方案：
{requirements}

返回 JSON:
{{"language": "编程语言", "modules": ["模块列表"], "architecture": "架构说明"}}
"""
        return parse_json(call_llm(prompt))

    def post(self, shared, prep_res, exec_res):
        shared["tech_spec"] = exec_res

class GenerateCode(Node):
    """生成代码"""
    def prep(self, shared):
        return {
            "requirements": shared["requirements"],
            "spec": shared["tech_spec"]
        }

    def exec(self, data):
        prompt = f"""
根据以下规格生成代码：
需求: {data["requirements"]}
技术规格: {data["spec"]}
"""
        return call_llm(prompt)

    def post(self, shared, prep_res, exec_res):
        shared["code"] = exec_res

class GenerateTests(Node):
    """生成测试"""
    def prep(self, shared):
        return shared["code"]

    def exec(self, code):
        prompt = f"为以下代码生成单元测试：\n{code}"
        return call_llm(prompt)

    def post(self, shared, prep_res, exec_res):
        shared["tests"] = exec_res

# 构建代码生成工作流
analyze = AnalyzeRequirements()
generate = GenerateCode()
test = GenerateTests()

analyze >> generate >> test
```

## 数据处理工作流

### ETL 工作流

```python
class ExtractNode(Node):
    """抽取数据"""
    def prep(self, shared):
        return shared["source"]

    def exec(self, source):
        return extract_from_source(source)

    def post(self, shared, prep_res, exec_res):
        shared["raw_data"] = exec_res

class TransformNode(Node):
    """转换数据"""
    def prep(self, shared):
        return shared["raw_data"]

    def exec(self, data):
        # 清洗、转换、标准化
        cleaned = clean_data(data)
        transformed = transform_data(cleaned)
        return transformed

    def post(self, shared, prep_res, exec_res):
        shared["transformed_data"] = exec_res

class LoadNode(Node):
    """加载数据"""
    def prep(self, shared):
        return {
            "data": shared["transformed_data"],
            "target": shared["target"]
        }

    def exec(self, params):
        load_to_target(params["data"], params["target"])
        return {"status": "success", "count": len(params["data"])}

    def post(self, shared, prep_res, exec_res):
        shared["load_result"] = exec_res

# ETL 工作流
extract = ExtractNode()
transform = TransformNode()
load = LoadNode()

extract >> transform >> load

etl_flow = Flow(start=extract)
```

## 审批工作流

```python
class SubmitNode(Node):
    """提交申请"""
    def post(self, shared, prep_res, exec_res):
        shared["status"] = "pending"
        return "review"

class ReviewNode(Node):
    """初审"""
    def prep(self, shared):
        return shared["application"]

    def exec(self, application):
        # 自动初审逻辑
        score = evaluate(application)
        return {"score": score, "pass": score >= 60}

    def post(self, shared, prep_res, exec_res):
        shared["review_result"] = exec_res
        if exec_res["pass"]:
            return "approve"
        elif exec_res["score"] >= 40:
            return "manual_review"
        else:
            return "reject"

class ManualReviewNode(Node):
    """人工审核"""
    def exec(self, _):
        # 等待人工审核
        return get_manual_review_result()

    def post(self, shared, prep_res, exec_res):
        if exec_res["approved"]:
            return "approve"
        return "reject"

class ApproveNode(Node):
    """批准"""
    def post(self, shared, prep_res, exec_res):
        shared["status"] = "approved"
        notify_applicant(shared, "approved")

class RejectNode(Node):
    """拒绝"""
    def post(self, shared, prep_res, exec_res):
        shared["status"] = "rejected"
        notify_applicant(shared, "rejected")

# 审批工作流
submit = SubmitNode()
review = ReviewNode()
manual = ManualReviewNode()
approve = ApproveNode()
reject = RejectNode()

submit >> review
review - "approve" >> approve
review - "manual_review" >> manual
review - "reject" >> reject
manual - "approve" >> approve
manual - "reject" >> reject
```

## 循环工作流

### 迭代优化

```python
class GenerateNode(Node):
    """生成初稿"""
    def exec(self, _):
        return generate_initial()

    def post(self, shared, prep_res, exec_res):
        shared["content"] = exec_res
        shared["iteration"] = 0

class EvaluateNode(Node):
    """评估质量"""
    def prep(self, shared):
        return shared["content"]

    def exec(self, content):
        score = evaluate_quality(content)
        return {"score": score, "feedback": get_feedback(content)}

    def post(self, shared, prep_res, exec_res):
        shared["evaluation"] = exec_res
        shared["iteration"] += 1

        if exec_res["score"] >= 90:
            return "complete"
        elif shared["iteration"] >= 5:
            return "max_iterations"
        else:
            return "improve"

class ImproveNode(Node):
    """改进"""
    def prep(self, shared):
        return {
            "content": shared["content"],
            "feedback": shared["evaluation"]["feedback"]
        }

    def exec(self, data):
        return improve_content(data["content"], data["feedback"])

    def post(self, shared, prep_res, exec_res):
        shared["content"] = exec_res
        return "evaluate"

# 迭代优化工作流
generate = GenerateNode()
evaluate = EvaluateNode()
improve = ImproveNode()
complete = CompleteNode()

generate >> evaluate
evaluate - "improve" >> improve >> evaluate
evaluate - "complete" >> complete
evaluate - "max_iterations" >> complete
```

## 嵌套工作流

```python
# 子工作流：数据验证
validate_flow = Flow(start=check_format)
check_format >> check_content >> check_rules

# 子工作流：数据处理
process_flow = Flow(start=clean_data)
clean_data >> transform_data >> enrich_data

# 主工作流
main_flow = Flow(start=input_node)
input_node >> validate_flow >> process_flow >> output_node
```

## 错误处理

```python
class SafeWorkflowNode(Node):
    def _run(self, shared):
        try:
            return super()._run(shared)
        except Exception as e:
            shared["error"] = str(e)
            return "error"

class ErrorHandlerNode(Node):
    def prep(self, shared):
        return shared["error"]

    def exec(self, error):
        log_error(error)
        return {"handled": True, "message": error}

# 添加错误处理
step1 - "error" >> error_handler
step2 - "error" >> error_handler
step3 - "error" >> error_handler
```

## 最佳实践

### 1. 单一职责

```python
# ✅ 每个节点做一件事
class ParseNode(Node): pass      # 只负责解析
class ValidateNode(Node): pass   # 只负责验证
class TransformNode(Node): pass  # 只负责转换

# ❌ 避免节点职责过重
class DoEverythingNode(Node):    # 不推荐
    def exec(self, data):
        parsed = parse(data)
        validated = validate(parsed)
        return transform(validated)
```

### 2. 明确的数据契约

```python
class DocumentedNode(Node):
    """
    输入 shared:
        - input_data: 原始数据
        - config: 配置参数

    输出 shared:
        - result: 处理结果
        - metadata: 元信息
    """
    pass
```

### 3. 可重用的节点

```python
class GenericTransformNode(Node):
    """通用转换节点，通过 params 配置行为"""
    def exec(self, data):
        transform_type = self.params.get("transform_type")
        if transform_type == "uppercase":
            return data.upper()
        elif transform_type == "lowercase":
            return data.lower()
        return data

# 复用
upper_node = GenericTransformNode()
upper_node.set_params({"transform_type": "uppercase"})

lower_node = GenericTransformNode()
lower_node.set_params({"transform_type": "lowercase"})
```

## 下一步

- [RAG 检索增强](./11_设计模式_RAG检索增强.md) - 结合检索的工作流
- [多智能体](./12_设计模式_多智能体.md) - 工作流与 Agent 结合
- [示例项目解析](./14_示例项目解析.md) - Workflow 实战案例
