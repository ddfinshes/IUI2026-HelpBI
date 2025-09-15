# IUI2026-HelpBI

## 架构
- 后端：FastAPI（backend/app），提供 REST API；保留 legacy 数据与脚本（backend/legacy）。
- 前端：Vue 3 + Vite（frontend），包含数据看板演示。

## 运行后端
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./scripts/dev.sh
```

API 接口：
- GET /health -> {"status": "ok"}
- GET /api/v1/ping -> {"message": "pong"}
- GET /api/v1/reports/sales -> 销售报表数据
- GET /api/v1/reports/dashboard -> 仪表板摘要

## 运行前端
```bash
cd frontend
# 如果有 npm
npm install
npm run dev

# 或直接打开
open frontend/index.html
```

前端功能：
- API 连接测试（Ping/Health）
- 仪表板摘要数据展示
- 销售报表数据表格展示
- 自动代理到后端 API（localhost:8000）

## 项目结构
```
├── backend/
│   ├── app/                 # FastAPI 应用
│   │   ├── api/v1/         # API 路由
│   │   ├── core/           # 配置
│   │   ├── schemas/        # 数据模型
│   │   └── services/       # 业务逻辑
│   ├── legacy/             # 原 Ex-ChatBI 代码与数据
│   └── requirements.txt
├── frontend/               # Vue 3 前端
│   ├── index.html         # 主页面
│   ├── package.json       # 依赖配置
│   └── vite.config.js     # Vite 配置（代理到后端）
└── README.md
```
