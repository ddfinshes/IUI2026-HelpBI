# HelpBI - 智能商业分析助手

HelpBI是一个基于大语言模型的智能商业分析系统，能够将自然语言查询转换为SQL查询，并提供数据分析和可视化功能。

## 项目结构

```
HelpBI/
├── db/                    # 数据库相关文件
│   ├── data/             # 数据文件
│   ├── connect.py        # 数据库连接
│   └── schema_information.txt
├── knowledge-base/        # 知识库
│   ├── business_info.txt
│   ├── sql_sample_kb.txt
│   └── extract.py
├── tools/                # 工具模块
│   ├── my_model.py       # 大模型封装
│   └── prompt.py         # 提示词模板
├── utils/                # 工具函数
│   ├── knownledge_retrival.py
│   └── utils.py
├── main.py              # 主程序入口
└── README.md
```

## 功能特性

- **自然语言转SQL**: 将用户的自然语言查询转换为SQL语句
- **智能分析**: 基于大语言模型的数据分析能力
- **知识库检索**: 利用RAG技术进行相关知识检索
- **多模型支持**: 支持多种大语言模型（DeepSeek、通义千问等）
- **数据可视化**: 提供图表生成和数据分析功能

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. 配置环境变量：
```bash
export OPENAI_API_KEY="your-api-key"
```

2. 运行主程序：
```bash
python main.py
```

## 技术栈

- Python 3.10+
- FastAPI
- SQLAlchemy
- OpenAI API
- 通义千问 API
- LightRAG
- Vue.js (前端)

## 许可证

MIT License
