# 结构化输出演示

展示如何使用 PocketFlow 通过直接提示和 YAML 格式化从简历中提取结构化数据的最小演示应用程序。为什么使用 YAML？查看[文档](https://the-pocket.github.io/PocketFlow/design_pattern/structure.html)。

此实现基于：[Structured Output for Beginners: 3 Must-Know Prompting Tips](https://zacharyhuang.substack.com/p/structured-output-for-beginners-3)。

## 功能特性

- 使用提示工程提取结构化数据
- 在处理前验证输出结构

## 运行方式

1. 使用此简单命令安装所需的包：
    ```bash
    pip install -r requirements.txt
    ```

2. 确保设置了您的 OpenAI API 密钥：
    ```bash
    export OPENAI_API_KEY="your-api-key-here"
    ```
    或者，您可以编辑 [`utils.py`](./utils.py) 文件直接包含您的 API 密钥。

    让我们快速检查以确保您的 API 密钥正常工作：

    ```bash
    python utils.py
    ```

3. 编辑 [data.txt](./data.txt) 包含您想要解析的简历（已包含示例简历）

4. 运行应用程序：
    ```bash
    python main.py
    ```

## 工作原理

```mermaid
flowchart LR
    parser[ResumeParserNode]
```

简历解析器应用程序使用一个节点，该节点：
1. 从共享状态中获取简历文本（从 data.txt 加载）
2. 将简历发送到带有请求 YAML 格式化输出的提示词的 LLM
3. 提取并验证结构化 YAML 数据
4. 输出结构化结果

## 文件说明

- [`main.py`](./main.py)：ResumeParserNode 的实现
- [`utils.py`](./utils.py)：LLM 工具
- [`data.txt`](./data.txt)：示例简历文本文件

## 示例输出

```
=== Resume Parser - Structured Output with Indexes & Comments ===


=== STRUCTURED RESUME DATA (Comments & Skill Index List) ===

name: JOHN SMTIH
email: johnsmtih1983@gnail.com
experience:
- {title: SALES MANAGER, company: ABC Corportaion}
- {title: ASST. MANAGER, company: XYZ Industries}
- {title: CUSTOMER SERVICE REPRESENTATIVE, company: Fast Solutions Inc}
skill_indexes: [0, 1, 2, 3, 4]


============================================================

✅ Extracted resume information.

--- Found Target Skills (from Indexes) ---
- Team leadership & management (Index: 0)
- CRM software (Index: 1)
- Project management (Index: 2)
- Public speaking (Index: 3)
- Microsoft Office (Index: 4)
----------------------------------------
```
