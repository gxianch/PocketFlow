# PocketFlow 可视化

此目录包含使用交互式 D3.js 可视化来可视化 PocketFlow 工作流程图的工具。

## 概述

可视化工具允许您：

1. 将 PocketFlow 节点和流程查看为交互式图
2. 查看不同流程如何相互连接
3. 理解流程内节点之间的关系

## 功能特性

- **交互式图**：节点可以拖动来重新组织布局
- **组可视化**：流程显示为带有虚线边框的组
- **组间链接**：流程之间的连接显示为连接组边界的虚线
- **操作标签**：边标签显示触发节点间转换的操作

## 要求

- Python 3.6 或更高版本
- 现代 Web 浏览器（Chrome、Firefox、Edge）用于查看可视化

## 使用方式

### 1. 基本可视化

要可视化 PocketFlow 图，您可以使用 `visualize.py` 中的 `visualize_flow` 函数：

```python
from visualize import visualize_flow
from your_flow_module import your_flow

# 生成可视化
visualize_flow(your_flow, "Your Flow Name")
```

这将：
1. 在控制台打印 Mermaid 图
2. 在 `./viz` 目录中生成 D3.js 可视化

### 2. 运行示例

包含的示例显示了一个包含支付、库存和运输流程的订单处理管道：

```bash
# 导航到目录
cd cookbook/pocketflow-minimal-flow2flow

# 运行可视化脚本
python visualize.py
```

这将在 `./viz` 目录中生成可视化文件。

### 3. 查看可视化

运行脚本后：

1. 使用以下命令托管
   ```
   cd ./viz/
   ```

2. 与可视化交互：
   - **拖动节点**来重新组织
   - **悬停在节点上**查看节点名称
   - **观察**节点和流程之间的连接

## 自定义可视化

### 调整布局参数

您可以在 `visualize.py` 中调整力模拟参数来更改节点和组的位置：

```javascript
// 创建力模拟
const simulation = d3.forceSimulation(data.nodes)
    // 控制连接节点之间的距离
    .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
    // 控制节点之间的排斥 - 较低的值使节点更接近
    .force("charge", d3.forceManyBody().strength(-30))
    // 将整个图居中在 SVG 中
    .force("center", d3.forceCenter(width / 2, height / 2))
    // 防止节点重叠 - 充当最小距离
    .force("collide", d3.forceCollide().radius(50));
```

### 样式

在 `create_d3_visualization` 函数内的 HTML 模板中调整 CSS 样式以更改颜色、形状和其他视觉属性。

## 工作原理

可视化过程包含三个主要步骤：

1. **流程到 JSON 转换**：`flow_to_json` 函数遍历 PocketFlow 图并将其转换为包含节点、链接和组信息的结构。

2. **D3.js 可视化**：JSON 数据用于创建交互式 D3.js 可视化，包含：
   - 节点表示为圆圈
   - 流程表示为包含节点的虚线矩形
   - 显示流程内和流程间连接的链接

3. **组边界连接**：可视化计算与组边界的交点，以确保组间链接在边界而不是中心连接。

## 扩展可视化

您可以通过以下方式扩展可视化工具：

1. 添加新的节点形状
2. 实现其他布局算法
3. 添加带有更详细信息的气泡提示
4. 为流程执行创建动画

## 故障排除

如果您遇到任何问题：

- 确保您的流程对象正确构建，节点连接正确
- 检查浏览器控制台是否有任何 JavaScript 错误
- 验证生成的 JSON 数据结构是否符合您的预期

## 示例输出

可视化显示：
- 支付处理流程节点
- 库存管理流程节点
- 运输流程节点
- 每个流程周围的组边界
- 流程之间的连接（支付 → 库存 → 运输）
