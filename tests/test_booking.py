"""
Unit tests สำหรับโมดูล Seat & Booking (M3)
รันด้วยคำสั่ง: pytest tests/test_booking.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from datetime import datetime, timedelta
import pytest
from booking import Seat, SeatMap, Booking
from movies import Movie, Theater, Showtime
from users import Member


class TestSeat:
    def test_seat_starts_available(self):
        seat = Seat("A", 1)
        assert seat.is_available() is True

    def test_book_seat(self):
        seat = Seat("A", 1)
        seat.book()
        assert seat.is_available() is False

    def test_book_already_booked_seat_raises_error(self):
        seat = Seat("A", 1)
        seat.book()
        with pytest.raises(ValueError):
            seat.book()

    def test_release_seat(self):
        seat = Seat("A", 1)
        seat.book()
        seat.release()
        assert seat.is_available() is True

    def test_seat_label(self):
        seat = Seat("B", 5)
        assert seat.label == "B5"


class TestSeatMap:
    def test_seat_map_creates_correct_count(self):
        seat_map = SeatMap(rows=2, seats_per_row=5)
        assert len(seat_map.get_all_seats()) == 10

    def test_get_seat_by_label(self):
        seat_map = SeatMap(rows=2, seats_per_row=5)
        seat = seat_map.get_seat("A1")
        assert seat.label == "A1"

    def test_get_seat_invalid_label_raises_error(self):
        seat_map = SeatMap(rows=2, seats_per_row=5)
        with pytest.raises(ValueError):
            seat_map.get_seat("Z99")

    def test_book_multiple_seats(self):
        seat_map = SeatMap(rows=2, seats_per_row=5)
        booked = seat_map.book_seats(["A1", "A2"])
        assert len(booked) == 2
        assert seat_map.get_seat("A1").is_available() is False

    def test_book_seats_partial_conflict_raises_error_and_no_partial_booking(self):
        seat_map = SeatMap(rows=2, seats_per_row=5)
        seat_map.book_seats(["A1"])
        with pytest.raises(ValueError):
            seat_map.book_seats(["A1", "A2"])
        # A2 ต้องยังว่างอยู่ เพราะการจองต้อง all-or-nothing (FR-3.3)
        assert seat_map.get_seat("A2").is_available() is True

    def test_get_available_seats(self):
        seat_map = SeatMap(rows=1, seats_per_row=3)
        seat_map.book_seats(["A1"])
        available = seat_map.get_available_seats()
        assert len(available) == 2


class TestBooking:
    def _make_booking(self, num_seats=2):
        movie = Movie("Test Movie", "Drama", 100)
        theater = Theater("Theater 1", rows=2, seats_per_row=5)
        showtime = Showtime(movie, theater, "2099-01-01", "18:30", 180)
        seat_map = SeatMap(rows=2, seats_per_row=5)
        labels = ["A1", "A2"][:num_seats]
        seats = seat_map.book_seats(labels)
        member = Member("Somchai", "somchai@test.com", "pass123")
        booking = Booking(member, showtime, seats)
        return booking, showtime, member

    def test_booking_requires_at_least_one_seat(self):
        movie = Movie("Test Movie", "Drama", 100)
        theater = Theater("Theater 1")
        showtime = Showtime(movie, theater, "2099-01-01", "18:30", 180)
        member = Member("Somchai", "somchai@test.com", "pass123")
        with pytest.raises(ValueError):
            Booking(member, showtime, [])

    def test_calculate_total(self):
        booking, showtime, member = self._make_booking(num_seats=2)
        assert booking.calculate_total() == 360  # 2 * 180

    def test_confirm_booking_updates_showtime_and_member(self):
        booking, showtime, member = self._make_booking(num_seats=2)
        booking.confirm()
        assert showtime.booked_seat_count == 2
        assert booking in member.booking_history

    def test_cancel_booking_before_cutoff_releases_seats(self):
        booking, showtime, member = self._make_booking(num_seats=2)
        booking.confirm()
        booking.cancel()
        assert booking.seats[0].is_available() is True
        assert showtime.booked_seat_count == 0

    def test_cancel_booking_after_cutoff_raises_error(self):
        movie = Movie("Test Movie", "Drama", 100)
        theater = Theater("Theater 1", rows=2, seats_per_row=5)
        # showtime ที่ผ่านไปแล้ว เพื่อจำลองว่าเลยเวลายกเลิกได้แล้ว
        past_time = datetime.now() - timedelta(hours=1)
        showtime = Showtime(movie, theater, past_time.strftime("%Y-%m-%d"),
                             past_time.strftime("%H:%M"), 180)
        seat_map = SeatMap(rows=2, seats_per_row=5)
        seats = seat_map.book_seats(["A1"])
        member = Member("Somchai", "somchai@test.com", "pass123")
        booking = Booking(member, showtime, seats)

        with pytest.raises(ValueError):
            booking.cancel()
