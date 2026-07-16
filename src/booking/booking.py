"""
Module: booking.py
รับผิดชอบ: โมดูล M3 - Seat & Booking (ส่วนของ Booking)
FR ที่เกี่ยวข้อง: FR-3.2, FR-3.4, FR-3.5
"""

from datetime import datetime, timedelta
from enum import Enum
import uuid


class BookingStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Booking:
    """
    การจองหนึ่งครั้ง - composition ของ Member + Showtime + Seat[]
    """

    CANCELLATION_CUTOFF_MINUTES = 30  # ต้องยกเลิกก่อนฉายอย่างน้อย 30 นาที (FR-3.4)

    def __init__(self, member, showtime, seats: list):
        """
        member: Member object จากโมดูล M1
        showtime: Showtime object จากโมดูล M2
        seats: list ของ Seat object จากโมดูล M3 ที่จองไว้แล้ว (book_seats() เรียกก่อนหน้านี้)
        """
        if not seats:
            raise ValueError("ต้องเลือกอย่างน้อย 1 ที่นั่ง")

        self.booking_id = str(uuid.uuid4())[:8]
        self.member = member
        self.showtime = showtime
        self.seats = seats
        self.status = BookingStatus.PENDING
        self.created_at = datetime.now()

    def calculate_total(self) -> float:
        """คำนวณราคารวมจากจำนวนที่นั่ง x ราคาต่อที่นั่ง"""
        return len(self.seats) * self.showtime.price

    def confirm(self) -> None:
        """ยืนยันการจองหลังชำระเงินสำเร็จ"""
        self.status = BookingStatus.CONFIRMED
        self.showtime.reserve_seats(len(self.seats))
        self.member.add_booking_record(self)  # เชื่อมกับโมดูล M1

    def cancel(self) -> None:
        """
        ยกเลิกการจอง (FR-3.4)
        ต้องยกเลิกก่อนเวลาฉายอย่างน้อย CANCELLATION_CUTOFF_MINUTES นาที
        """
        showtime_start = self.showtime.get_datetime()
        cutoff = showtime_start - timedelta(minutes=self.CANCELLATION_CUTOFF_MINUTES)

        if datetime.now() > cutoff:
            raise ValueError(
                f"ไม่สามารถยกเลิกได้ ต้องยกเลิกก่อนฉายอย่างน้อย "
                f"{self.CANCELLATION_CUTOFF_MINUTES} นาที"
            )

        for seat in self.seats:
            seat.release()

        if self.status == BookingStatus.CONFIRMED:
            self.showtime.release_seats(len(self.seats))

        self.status = BookingStatus.CANCELLED

    def __repr__(self) -> str:
        seat_labels = ", ".join(s.label for s in self.seats)
        return (f"<Booking {self.booking_id}: {self.member.name} - "
                f"{self.showtime.movie.title} [{seat_labels}] ({self.status.value})>")
