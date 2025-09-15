from fastapi import APIRouter
from backend.app.services.report_service import ReportService
from backend.app.schemas.report import ReportResponse

api_router = APIRouter()

@api_router.get("/ping")
async def ping():
    return {"message": "pong"}

@api_router.get("/reports/sales", response_model=ReportResponse)
async def get_sales_report():
    """获取销售报表数据"""
    data = ReportService.get_sales_report()
    return ReportResponse(
        success=True,
        data=data,
        total=len(data)
    )

@api_router.get("/reports/dashboard")
async def get_dashboard_summary():
    """获取仪表板摘要数据"""
    return ReportService.get_dashboard_summary()
