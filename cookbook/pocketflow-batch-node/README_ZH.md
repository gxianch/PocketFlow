# PocketFlow BatchNode 示例

此示例通过实现一个 CSV 处理器来演示 PocketFlow 中的 BatchNode 概念，该处理器通过分块处理大文件。

## 本示例演示内容

- 如何使用 BatchNode 分块处理大输入
- BatchNode 的三个关键方法：
  1. `prep`：将输入拆分为块
  2. `exec`：独立处理每个块
  3. `post`：合并所有块的结果

## 项目结构

```
pocketflow-batch-node/
├── README.md
├── requirements.txt
├── data/
│   └── sales.csv      # 示例大 CSV 文件
├── main.py            # 入口点
├── flow.py            # 流程定义
└── nodes.py           # BatchNode 实现
```

## 工作原理

该示例处理包含销售数据的大 CSV 文件：

1. **分块（prep）**：读取 CSV 文件并拆分为 N 行的块
2. **处理（exec）**：处理每个块以计算：
   - 总销售额
   - 平均销售价值
   - 交易次数
3. **合并（post）**：将所有块的结果聚合为最终统计信息

## 安装

```bash
pip install -r requirements.txt
```

## 使用方式

```bash
python main.py
```

## 示例输出

```
Processing sales.csv in chunks...

Final Statistics:
- Total Sales: $1,234,567.89
- Average Sale: $123.45
- Total Transactions: 10,000
```

## 演示的关键概念

1. **基于块的处理**：展示 BatchNode 如何通过将大输入分解为可管理的块来处理它们
2. **独立处理**：演示每个块如何独立处理
3. **结果聚合**：展示如何将个别结果合并为最终输出
