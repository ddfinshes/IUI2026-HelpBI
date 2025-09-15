# IUI2026-HelpBI

## 架构
- 后端：FastAPI（backend/app），提供 REST API；保留 legacy 数据与脚本（backend/legacy）。
- 前端：ex-chatbi（Vite + Vue）。

## 运行后端
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./scripts/dev.sh
```

接口示例：
- GET /health -> {"status": "ok"}
- GET /api/v1/ping -> {"message": "pong"}

## 运行前端
```bash
cd ex-chatbi
npm install
npm run dev
```
