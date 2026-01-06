# 带内容分析的网络爬虫

使用 PocketFlow 构建的网络爬虫工具，可爬取网站并使用 LLM 分析内容。

## 功能特性

- 在遵守域边界的同时爬取网站
- 从页面提取文本内容和链接
- 使用 GPT-4 分析内容以生成：
  - 页面摘要
  - 主要主题/关键词
  - 内容类型分类
- 批量处理页面以提高效率
- 生成全面的分析报告

## 安装

1. 克隆仓库
2. 安装依赖项：
   ```bash
   pip install -r requirements.txt
   ```
3. 设置您的 OpenAI API 密钥：
   ```bash
   export OPENAI_API_KEY='your-api-key'
   ```

## 使用方式

运行爬虫：
```bash
python main.py
```

系统将提示您：
1. 输入要爬取的网站 URL
2. 指定要爬取的最大页面数（默认：10）

然后工具将：
1. 爬取指定的网站
2. 使用 GPT-4 提取和分析内容
3. 生成包含发现的报告

## 项目结构

```
pocketflow-tool-crawler/
├── tools/
│   ├── crawler.py     # 网络爬虫功能
│   └── parser.py      # 使用 LLM 进行内容分析
├── utils/
│   └── call_llm.py    # LLM API 封装器
├── nodes.py           # PocketFlow 节点
├── flow.py           # Flow 配置
├── main.py           # 主要脚本
└── requirements.txt   # 依赖项
```

## 局限性

- 仅在同一域内爬取
- 仅文本内容（无图像/媒体）
- 受 OpenAI API 速率限制
- 基本错误处理

## 依赖项

- pocketflow：基于流程的处理
- requests：HTTP 请求
- beautifulsoup4：HTML 解析
- openai：GPT-4 API 访问
