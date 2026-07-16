"""
Module: invoice.py
รับผิดชอบ: โมดูล M4 - Payment (ส่วนของ Invoice)
FR ที่เกี่ยวข้อง: FR-4.3
"""

from datetime import datetime
import uuid
from payment.payment import Payment


class Invoice:
    """
    ใบเสร็จ - composition ของ Booking + Payment
    """

    def __init__(self, booking, payment: Payment, discount: float = 0.0):
        if not payment.is_paid:
            raise ValueError("ไม่สามารถออกใบเสร็จได้ เนื่องจากยังไม่ได้ชำระเงิน")

        self.invoice_number = f"INV-{str(uuid.uuid4())[:8].upper()}"
        self.booking = booking
        self.payment = payment
        self.discount = discount
        self.issued_at = datetime.now()

    @property
    def subtotal(self) -> float:
        return self.booking.calculate_total()

    @property
    def net_total(self) -> float:
        """ยอดสุทธิหลังหักส่วนลด (FR-4.3)"""
        return max(0.0, self.subtotal - self.discount)

    def generate_receipt_text(self) -> str:
        """สร้างข้อความใบเสร็จสำหรับพิมพ์ออกทาง CLI"""
        seat_labels = ", ".join(s.label for s in self.booking.seats)
        lines = [
            "=" * 40,
            f"ใบเสร็จเลขที่: {self.invoice_number}",
            f"วันที่: {self.issued_at.strftime('%Y-%m-%d %H:%M')}",
            "-" * 40,
            f"ภาพยนตร์: {self.booking.showtime.movie.title}",
            f"รอบฉาย: {self.booking.showtime.date} {self.booking.showtime.time}",
            f"ที่นั่ง: {seat_labels}",
            "-" * 40,
            f"ยอดก่อนหักส่วนลด: {self.subtotal:.2f} บาท",
            f"ส่วนลด: {self.discount:.2f} บาท",
            f"ยอดสุทธิ: {self.net_total:.2f} บาท",
            "=" * 40,
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"<Invoice {self.invoice_number}: {self.net_total:.2f} บาท>"
