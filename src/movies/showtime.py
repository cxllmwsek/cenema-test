"""
Module: showtime.py
รับผิดชอบ: โมดูล M2 - Movie & Showtime (ส่วนของ Theater/Showtime)
FR ที่เกี่ยวข้อง: FR-2.2, FR-2.4
"""

from datetime import datetime
from movies.movie import Movie


class Theater:
    """
    โรงภาพยนตร์ เก็บข้อมูลจำนวนที่นั่ง (แถว x คอลัมน์)
    """

    def __init__(self, name: str, rows: int = 7, seats_per_row: int = 10):
        if rows <= 0 or seats_per_row <= 0:
            raise ValueError("จำนวนแถวและที่นั่งต่อแถวต้องมากกว่า 0")
        self.name = name
        self.rows = rows
        self.seats_per_row = seats_per_row

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_per_row

    def __repr__(self) -> str:
        return f"<Theater: {self.name} ({self.capacity} seats)>"


class Showtime:
    """
    รอบฉายภาพยนตร์ - เป็น composition ของ Movie + Theater
    """

    def __init__(self, movie: Movie, theater: Theater, date: str,
                 time: str, price: float):
        if price <= 0:
            raise ValueError("ราคาตั๋วต้องมากกว่า 0")

        self.movie = movie          # composition: has-a Movie
        self.theater = theater      # composition: has-a Theater
        self.date = date            # เช่น "2026-07-20"
        self.time = time            # เช่น "18:30"
        self.price = price
        self.__booked_seat_count = 0  # private: encapsulation

    @property
    def booked_seat_count(self) -> int:
        return self.__booked_seat_count

    @property
    def available_seats_count(self) -> int:
        """ที่นั่งว่างที่เหลือ (FR-2.4)"""
        return self.theater.capacity - self.__booked_seat_count

    def is_available(self) -> bool:
        """เช็คว่ารอบฉายนี้ยังมีที่นั่งว่างไหม (FR-2.4)"""
        return self.available_seats_count > 0

    def reserve_seats(self, count: int) -> None:
        """เพิ่มจำนวนที่นั่งที่ถูกจองแล้ว (เรียกจากโมดูล M3 ตอนยืนยันการจอง)"""
        if count > self.available_seats_count:
            raise ValueError("ที่นั่งไม่พอสำหรับการจองนี้")
        self.__booked_seat_count += count

    def release_seats(self, count: int) -> None:
        """คืนที่นั่งกลับ (เช่น ยกเลิกการจอง หรือชำระเงินไม่สำเร็จ)"""
        self.__booked_seat_count = max(0, self.__booked_seat_count - count)

    def get_datetime(self) -> datetime:
        """แปลง date+time เป็น datetime object เพื่อใช้เปรียบเทียบเวลา (เช่น FR-3.4)"""
        return datetime.strptime(f"{self.date} {self.time}", "%Y-%m-%d %H:%M")

    def __repr__(self) -> str:
        return (f"<Showtime: {self.movie.title} @ {self.theater.name} "
                f"{self.date} {self.time} ({self.available_seats_count} seats left)>")


class ShowtimeCatalog:
    """
    ตัวกลางจัดการ Movie และ Showtime ทั้งหมดในระบบ (ใช้โดย main.py และ Admin)
    """

    def __init__(self):
        self.movies: list[Movie] = []
        self.showtimes: list[Showtime] = []

    def add_movie(self, movie: Movie) -> None:
        """Admin เพิ่มภาพยนตร์ใหม่ (FR-2.1)"""
        self.movies.append(movie)

    def add_showtime(self, showtime: Showtime) -> None:
        """Admin กำหนดรอบฉาย (FR-2.2)"""
        self.showtimes.append(showtime)

    def search_movies(self, keyword: str) -> list[Movie]:
        """ค้นหาภาพยนตร์ตามชื่อ/ประเภท (FR-2.3)"""
        return [m for m in self.movies if m.matches_search(keyword)]

    def get_available_showtimes(self, movie: Movie | None = None) -> list[Showtime]:
        """
        คืนเฉพาะรอบฉายที่ยังมีที่นั่งว่าง (FR-2.4)
        ถ้าระบุ movie จะกรองเฉพาะรอบของหนังเรื่องนั้น
        """
        result = [s for s in self.showtimes if s.is_available()]
        if movie is not None:
            result = [s for s in result if s.movie == movie]
        return result
