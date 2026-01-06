# 并行图像处理器

演示 AsyncParallelBatchFlow 如何使用多个滤镜并行处理多个图像，比顺序处理快 >8 倍。

## 功能特性

  ```mermaid
  graph TD
      subgraph AsyncParallelBatchFlow[Image Processing Flow]
          subgraph AsyncFlow[Per Image-Filter Flow]
              A[Load Image] --> B[Apply Filter]
              B --> C[Save Image]
          end
      end
  ```

- 使用多个滤镜并行处理图像
- 应用三种不同的滤镜（灰度、模糊、怀旧）
- 展示相对于顺序处理的显著速度提升
- 使用信号量管理系统资源

## 运行方式

```bash
pip install -r requirements.txt
python main.py
```

## 输出

```=== Processing Images in Parallel ===
Parallel Image Processor
------------------------------
Found 3 images:
- images/bird.jpg
- images/cat.jpg
- images/dog.jpg

Running sequential batch flow...
Processing 3 images with 3 filters...
Total combinations: 9
Loading image: images/bird.jpg
Applying grayscale filter...
Saved: output/bird_grayscale.jpg
...etc

Timing Results:
Sequential batch processing: 13.76 seconds
Parallel batch processing: 1.71 seconds
Speedup: 8.04x

Processing complete! Check the output/ directory for results.
```

## 关键要点

- **顺序处理**：总时间 = 所有项目时间之和
  - 适用于：限速 API、保持顺序

- **并行处理**：总时间 ≈ 最长单个项目时间
  - 适用于：I/O 密集型任务、独立操作
