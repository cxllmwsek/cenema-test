"""
Module: seat.py
รับผิดชอบ: โมดูล M3 - Seat & Booking (ส่วนของ Seat/SeatMap)
FR ที่เกี่ยวข้อง: FR-3.1, FR-3.3
"""

from enum import Enum


class SeatStatus(Enum):
    AVAILABLE = "available"
    BOOKED = "booked"


class Seat:
    """
    ที่นั่งหนึ่งตำแหน่งในโรงภาพยนตร์
    """

    def __init__(self, row: str, number: int, seat_type: str = "normal"):
        self.row = row
        self.number = number
        self.seat_type = seat_type  # เช่น normal, vip
        self.__status = SeatStatus.AVAILABLE  # private: encapsulation

    @property
    def status(self) -> SeatStatus:
        return self.__status

    @property
    def label(self) -> str:
        return f"{self.row}{self.number}"

    def is_available(self) -> bool:
        return self.__status == SeatStatus.AVAILABLE

    def book(self) -> None:
        """จองที่นั่ง (FR-3.3) - ป้องกันการจองซ้ำ"""
        if not self.is_available():
            raise ValueError(f"ที่นั่ง {self.label} ถูกจองไปแล้ว")
        self.__status = SeatStatus.BOOKED

    def release(self) -> None:
        """ปลดล็อกที่นั่งกลับเป็นว่าง (เช่น ยกเลิกจอง หรือชำระเงินไม่สำเร็จ)"""
        self.__status = SeatStatus.AVAILABLE

    def __repr__(self) -> str:
        return f"<Seat {self.label} ({self.status.value})>"


class SeatMap:
    """
    ผังที่นั่งทั้งหมดของ Showtime หนึ่งรอบ (FR-3.1)
    """

    def __init__(self, rows: int, seats_per_row: int):
        self.__seats: dict[str, Seat] = {}
        row_labels = [chr(ord('A') + i) for i in range(rows)]
        for row in row_labels:
            for num in range(1, seats_per_row + 1):
                seat = Seat(row, num)
                self.__seats[seat.label] = seat

    def get_seat(self, label: str) -> Seat:
        """ค้นหาที่นั่งจาก label เช่น 'A1'"""
        seat = self.__seats.get(label)
        if seat is None:
            raise ValueError(f"ไม่พบที่นั่ง {label}")
        return seat

    def get_available_seats(self) -> list[Seat]:
        return [s for s in self.__seats.values() if s.is_available()]

    def get_all_seats(self) -> list[Seat]:
        return list(self.__seats.values())

    def book_seats(self, labels: list[str]) -> list[Seat]:
        """
        จองหลายที่นั่งพร้อมกัน (FR-3.2)
        ตรวจสอบทุกที่นั่งว่างก่อน แล้วค่อยจองจริง (ป้องกันจองครึ่งเดียว)
        """
        seats = [self.get_seat(label) for label in labels]
        unavailable = [s.label for s in seats if not s.is_available()]
        if unavailable:
            raise ValueError(f"ที่นั่งไม่ว่าง: {', '.join(unavailable)}")

        for seat in seats:
            seat.book()
        return seats

    def release_seats(self, labels: list[str]) -> None:
        """ปลดล็อกหลายที่นั่งพร้อมกัน"""
        for label in labels:
            self.get_seat(label).release()
