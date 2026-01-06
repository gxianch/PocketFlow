# 带分析功能的网络搜索

使用 PocketFlow 构建的网络搜索工具，使用 SerpAPI 执行搜索并使用 LLM 分析结果。

## 功能特性

- 通过 SerpAPI 使用 Google 进行网络搜索
- 提取标题、摘要和链接
- 使用 GPT-4 分析搜索结果以提供：
  - 结果摘要
  - 关键点/事实
  - 建议的后续查询
- 清洁的命令行界面

## 安装

1. 克隆仓库
2. 安装依赖项：
   ```bash
   pip install -r requirements.txt
   ```
3. 设置必需的 API 密钥：
   ```bash
   export SERPAPI_API_KEY='your-serpapi-key'
   export OPENAI_API_KEY='your-openai-key'
   ```

## 使用方式

运行搜索工具：
```bash
python main.py
```

系统将提示您：
1. 输入您的搜索查询
2. 指定要获取的结果数（默认：5）

然后工具将：
1. 使用 SerpAPI 执行搜索
2. 使用 GPT-4 分析结果
3. 展示包含关键点和后续查询的摘要

## 项目结构

```
pocketflow-tool-search/
├── tools/
│   ├── search.py      # SerpAPI 搜索功能
│   └── parser.py      # 使用 LLM 进行结果分析
├── utils/
│   └── call_llm.py    # LLM API 封装器
├── nodes.py           # PocketFlow 节点
├── flow.py           # Flow 配置
├── main.py           # 主要脚本
└── requirements.txt   # 依赖项
```

## 局限性

- 需要 SerpAPI 订阅
- 受两个 API 速率限制
- 基本错误处理
- 仅文本结果

## 依赖项

- pocketflow：基于流程的处理
- google-search-results：SerpAPI 客户端
- openai：GPT-4 API 访问
- pyyaml：YAML 处理
