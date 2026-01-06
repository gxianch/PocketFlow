# PocketFlow 异步基础示例

此示例使用简单的食谱查找器演示异步操作，该查找器：
1. 从 API 获取食谱（异步 HTTP）
2. 使用 LLM 处理它们（异步 LLM）
3. 等待用户确认（异步输入）

## 本示例功能

当您运行示例时：
1. 您输入一个配料（例如，"chicken"）
2. 它搜索食谱（异步 API 调用）
3. 它建议一个食谱（异步 LLM 调用）
4. 您批准或拒绝建议
5. 如果被拒绝，它会尝试不同的食谱

## 工作原理

1. **FetchRecipes（AsyncNode）**
   ```python
   async def prep_async(self, shared):
       ingredient = input("Enter ingredient: ")
       return ingredient

   async def exec_async(self, ingredient):
       # 异步 API 调用
       recipes = await fetch_recipes(ingredient)
       return recipes
   ```

2. **SuggestRecipe（AsyncNode）**
   ```python
   async def exec_async(self, recipes):
       # 异步 LLM 调用
       suggestion = await call_llm_async(
           f"Choose best recipe from: {recipes}"
       )
       return suggestion
   ```

3. **GetApproval（AsyncNode）**
   ```python
   async def post_async(self, shared, prep_res, suggestion):
       # 异步用户输入
       answer = await get_user_input(
           f"Accept {suggestion}? (y/n): "
       )
       return "accept" if answer == "y" else "retry"
   ```

## 运行示例

```bash
pip install -r requirements.txt
python main.py
```

## 示例交互

```
Enter ingredient: chicken
Fetching recipes...
Found 3 recipes.

Suggesting best recipe...
How about: Grilled Chicken with Herbs

Accept this recipe? (y/n): n
Suggesting another recipe...
How about: Chicken Stir Fry

Accept this recipe? (y/n): y
Great choice! Here's your recipe...
```

## 关键概念

1. **异步操作**：使用 `async/await` 进行：
   - API 调用（非阻塞 I/O）
   - LLM 调用（可能较慢）
   - 用户输入（等待响应）

2. **AsyncNode 方法**：
   - `prep_async`：设置和数据收集
   - `exec_async`：主要异步处理
   - `post_async`：后处理和决策

3. **流程控制**：
   - 操作（"accept"/"retry"）控制流程
   - 被拒绝建议的重试循环
