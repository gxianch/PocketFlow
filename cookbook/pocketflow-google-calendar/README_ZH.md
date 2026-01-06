# Pocket Google Calendar

基于 Pocket Flow 框架的 Google Calendar 集成应用程序。

## 📋 描述

此项目使用 Pocket Flow 框架实现 Google Calendar 集成，允许通过简单直观的界面高效管理事件和约会。

## 🚀 功能特性

- Google Calendar API 集成
- 事件管理
- 约会查看
- 使用 Pocket Flow 的基于流程的界面

## 🛠️ 使用的技术

- Python
- Pocket Flow 框架
- Google Calendar API
- Pipenv 用于依赖项管理

## 📦 安装

1. 克隆仓库：
```bash
git clone [REPOSITORY_URL]
cd pocket-google-calendar
```

2. 使用 Pipenv 安装依赖项：
```bash
pipenv install
```

## 🔑 凭证设置

1. 转到 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 为您的项目启用 Google Calendar API
4. 创建凭证：
   - 转到"APIs & Services" > "Credentials"
   - 点击"Create Credentials" > "OAuth client ID"
   - 选择"Desktop application"作为应用程序类型
   - 下载凭证文件
   - 将其重命名为 `credentials.json`
   - 将其放在项目的根目录中

## 🌍 环境变量

在根目录中创建包含以下变量的 `.env` 文件：

```env
# Google Calendar API 配置
GOOGLE_CALENDAR_ID=your_calendar_id@group.calendar.google.com
GOOGLE_APPLICATION_CREDENTIALS=credentials.json

# 应用程序配置
TIMEZONE=America/Sao_Paulo  # 或您首选的时区
```

## 🔧 配置

1. 激活虚拟环境：
```bash
pipenv shell
```

2. 运行应用程序：
```bash
python main.py
```

## 预期输出

运行示例时，您将看到类似以下的输出：

```
=== Listing your calendars ===
- Primary Calendar
- Work
- Personal

=== Creating an example event ===
Event created successfully!
Event ID: abc123xyz
```

## 📁 项目结构

```
pocket-google-calendar/
├── main.py           # 应用程序入口点
├── nodes.py          # Pocket Flow 节点定义
├── utils/            # 实用函数和辅助函数
├── Pipfile           # Pipenv 配置
├── credentials.json  # Google Calendar API 凭证
├── .env             # 环境变量
└── token.pickle      # Google Calendar 认证令牌
```

## 🤝 贡献

1. Fork 项目
2. 创建您的功能分支（`git checkout -b feature/AmazingFeature`）
3. 提交您的更改（`git commit -m 'Add some AmazingFeature'`）
4. 推送到分支（`git push origin feature/AmazingFeature`）
5. 打开 Pull Request

## 📝 许可证

本项目基于 MIT 许可证。查看 [LICENSE](LICENSE) 文件了解更多详情。

## ✨ 致谢

- [Pocket Flow](https://github.com/the-pocket/PocketFlow) - 使用的框架
- [Google Calendar API](https://developers.google.com/calendar) - 集成 API
