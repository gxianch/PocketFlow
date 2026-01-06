# SQLite 数据库与 PocketFlow

此示例演示如何正确地将 SQLite 数据库操作与 PocketFlow 集成，重点关注：

1. 关注点分离的清洁代码组织：
   - 数据库操作的工具层（`tools/database.py`）
   - PocketFlow 集成的节点实现（`nodes.py`）
   - 流程配置（`flow.py`）
   - 使用参数绑定的安全 SQL 查询执行

2. 数据库操作的最佳实践：
   - 带适当关闭的连接管理
   - 使用参数化查询防止 SQL 注入
   - 错误处理和资源清理
   - 简单的架构管理

3. 示例任务管理系统：
   - 数据库初始化
   - 任务创建
   - 任务列表
   - 状态跟踪

## 项目结构

```
pocketflow-tool-database/
├── tools/
│   └── database.py    # SQLite 数据库操作
├── nodes.py          # PocketFlow 节点实现
├── flow.py          # Flow 配置
└── main.py          # 示例用法
```

## 环境配置

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Windows 系统：venv\Scripts\activate
```

2. 安装依赖项：
```bash
pip install -r requirements.txt
```

## 使用方式

运行示例：
```bash
python main.py
```

这将：
1. 使用任务表初始化 SQLite 数据库
2. 创建示例任务
3. 列出数据库中的所有任务
4. 显示结果

## 演示的关键概念

1. **数据库操作**
   - 安全的连接处理
   - 查询参数化
   - 架构管理

2. **代码组织**
   - 数据库操作和 PocketFlow 组件之间的清晰分离
   - 模块化项目结构
   - 类型提示和文档

3. **PocketFlow 集成**
   - 带有 prep->exec->post 生命周期的节点实现
   - Flow 配置
   - 用于数据传递的共享存储使用

## 示例输出

```
Database Status: Database initialized
Task Status: Task created successfully

All Tasks:
- ID: 1
  Title: Example Task
  Description: This is an example task created using PocketFlow
  Status: pending
  Created: 2024-03-02 12:34:56
```
