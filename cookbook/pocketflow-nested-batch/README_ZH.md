# PocketFlow 嵌套 BatchFlow 示例

此示例使用简单的学校成绩计算器演示嵌套 BatchFlow。

## 本示例功能

计算以下各项的平均成绩：
1. 班级中每个学生的成绩
2. 学校中每个班级的成绩

## 结构

```
school/
├── class_a/
│   ├── student1.txt  (成绩: 7.5, 8.0, 9.0)
│   └── student2.txt  (成绩: 8.5, 7.0, 9.5)
└── class_b/
    ├── student3.txt  (成绩: 6.5, 8.5, 7.0)
    └── student4.txt  (成绩: 9.0, 9.5, 8.0)
```

## 工作原理

1. **外部 BatchFlow（SchoolBatchFlow）**
   - 处理每个班级文件夹
   - 返回参数，如：`{"class": "class_a"}`

2. **内部 BatchFlow（ClassBatchFlow）**
   - 处理班级中的每个学生文件
   - 返回参数，如：`{"student": "student1.txt"}`

3. **基础流程**
   - 加载学生成绩
   - 计算平均值
   - 保存结果

## 运行示例

```bash
pip install -r requirements.txt
python main.py
```

## 预期输出

```
Processing class_a...
- student1: Average = 8.2
- student2: Average = 8.3
Class A Average: 8.25

Processing class_b...
- student3: Average = 7.3
- student4: Average = 8.8
Class B Average: 8.05

School Average: 8.15
```

## 关键概念

1. **嵌套 BatchFlow**：一个 BatchFlow 内部包含另一个 BatchFlow
2. **参数继承**：内部流程从外部流程获取参数
3. **分层处理**：以树状结构处理数据
