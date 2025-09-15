from typing import List
from backend.app.schemas.report import ReportData
from datetime import datetime, timedelta
import random

class ReportService:
    @staticmethod
    def get_sales_report() -> List[ReportData]:
        """获取销售报表数据"""
        categories = ["销售额", "订单数", "客户数", "利润率"]
        regions = ["大陆", "香港", "台湾"]
        
        data = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(20):
            category = random.choice(categories)
            region = random.choice(regions)
            
            base_value = random.uniform(1000, 50000)
            change = random.uniform(-0.2, 0.3) * base_value
            change_percent = (change / base_value) * 100
            
            data.append(ReportData(
                id=f"report_{i+1}",
                title=f"{region} {category}",
                value=round(base_value, 2),
                change=round(change, 2),
                change_percent=round(change_percent, 2),
                category=category,
                date=base_date + timedelta(days=i)
            ))
        
        return data
    
    @staticmethod
    def get_dashboard_summary() -> dict:
        """获取仪表板摘要数据"""
        return {
            "total_sales": 1250000.50,
            "total_orders": 3420,
            "total_customers": 1580,
            "growth_rate": 12.5,
            "top_region": "大陆",
            "top_category": "销售额"
        }
