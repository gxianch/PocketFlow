# PocketFlow 通信示例

此示例演示了 PocketFlow 中的[通信](https://the-pocket.github.io/PocketFlow/communication.html)概念，特别关注共享存储模式。

## 概述

该示例实现了一个简单的单词计数器，展示节点如何使用共享存储进行通信。它演示了：

- 如何初始化和构建共享存储
- 节点如何从共享存储读取和写入
- 如何在多次节点执行之间维护状态
- 共享存储使用的最佳实践

## 项目结构

```
pocketflow-communication/
├── README.md
├── requirements.txt
├── main.py
├── flow.py
└── nodes.py
```

## 安装

```bash
pip install -r requirements.txt
```

## 使用方式

```bash
python main.py
```

当提示时输入文本。程序将：
1. 统计文本中的单词数
2. 将统计信息存储在共享存储中
3. 显示运行统计信息（总文本数、总单词数、平均值）

输入 'q' 退出。

## 工作原理

该示例使用三个节点：

1. `TextInput`：读取用户输入并初始化共享存储
2. `WordCounter`：统计单词数并在共享存储中更新统计信息
3. `ShowStats`：从共享存储显示统计信息

这展示了节点如何使用共享存储模式共享和维护状态。
