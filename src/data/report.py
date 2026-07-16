"""
Module: report.py
รับผิดชอบ: โมดูล M5 - Data & Reporting (ส่วนของ Report)
FR ที่เกี่ยวข้อง: FR-5.3
"""

from collections import defaultdict


class Report:
    """
    สร้างรายงานสรุปยอดขายจากรายการ Booking/Invoice ที่มีอยู่
    ออกแบบให้รับ list ของ invoice เข้ามาโดยตรง (dependency injection)
    เพื่อไม่ผูกติดกับ DataStore หรือ Invoice class มากเกินไป
    """

    def __init__(self, invoices: list):
        self.invoices = invoices

    def daily_sales(self) -> dict:
        """สรุปยอดขายแยกตามวัน (FR-5.3)"""
        result = defaultdict(float)
        for inv in self.invoices:
            day = inv.issued_at.strftime("%Y-%m-%d")
            result[day] += inv.net_total
        return dict(result)

    def sales_by_movie(self) -> dict:
        """สรุปยอดขายแยกตามเรื่องภาพยนตร์ (FR-5.3)"""
        result = defaultdict(float)
        for inv in self.invoices:
            title = inv.booking.showtime.movie.title
            result[title] += inv.net_total
        return dict(result)

    def sales_by_showtime(self) -> dict:
        """สรุปยอดขายแยกตามรอบฉาย (FR-5.3)"""
        result = defaultdict(float)
        for inv in self.invoices:
            key = f"{inv.booking.showtime.movie.title} @ {inv.booking.showtime.date} {inv.booking.showtime.time}"
            result[key] += inv.net_total
        return dict(result)

    def total_revenue(self) -> float:
        return sum(inv.net_total for inv in self.invoices)

    def total_tickets_sold(self) -> int:
        return sum(len(inv.booking.seats) for inv in self.invoices)
