# PocketFlow 工具：PDF 视觉识别

演示使用 OpenAI 视觉 API 进行 OCR 和文本提取的 PDF 处理的 PocketFlow 示例项目。

## 功能特性

- 将 PDF 页面转换为图像，同时保持质量和大小限制
- 使用 GPT-4 视觉 API 从扫描文档中提取文本
- 支持自定义提取提示词
- 在提取的文本中保持页面顺序和格式
- 批量处理来自目录的多个 PDF

## 安装

1. 克隆仓库
2. 安装依赖项：
   ```bash
   pip install -r requirements.txt
   ```
3. 将您的 OpenAI API 密钥设置为环境变量：
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

## 使用方式

1. 将您的 PDF 文件放入 `pdfs` 目录
2. 运行示例：
   ```bash
   python main.py
   ```
   脚本将处理 `pdfs` 目录中的所有 PDF 文件，并输出每个文件的提取文本。

## 项目结构

```
pocketflow-tool-pdf-vision/
├── pdfs/           # 要处理的 PDF 文件目录
├── tools/
│   ├── pdf.py     # PDF 到图像的转换
│   └── vision.py  # 视觉 API 集成
├── utils/
│   └── call_llm.py # OpenAI 客户端配置
├── nodes.py       # PocketFlow 节点
├── flow.py        # Flow 配置
└── main.py        # 示例用法
```

## 流程描述

1. **LoadPDFNode**：加载 PDF 并将页面转换为图像
2. **ExtractTextNode**：使用视觉 API 处理图像
3. **CombineResultsNode**：合并所有页面的提取文本

## 自定义

您可以通过修改 `shared` 中的提示词来自定义提取：

```python
shared = {
    "pdf_path": "your_file.pdf",
    "extraction_prompt": "Your custom prompt here"
}
```

## 局限性

- 最大 PDF 页面大小：2000px（在 `tools/pdf.py` 中可配置）
- 视觉 API 令牌限制：每个响应 1000 个令牌
- 图像大小限制：每个图像 20MB（视觉 API）

## 许可证

MIT
