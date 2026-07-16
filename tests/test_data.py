"""
Unit tests สำหรับโมดูล Data & Reporting (M5)
รันด้วยคำสั่ง: pytest tests/test_data.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import shutil
import pytest
from data import DataStore, Report
from payment import CashPayment, Invoice
from booking import SeatMap, Booking
from movies import Movie, Theater, Showtime
from users import Member


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "_test_data_tmp")


@pytest.fixture
def temp_store():
    file_path = os.path.join(TEST_DATA_DIR, "test_data.json")
    store = DataStore(file_path=file_path)
    yield store
    if os.path.exists(TEST_DATA_DIR):
        shutil.rmtree(TEST_DATA_DIR)


class TestDataStore:
    def test_save_and_load_roundtrip(self, temp_store):
        temp_store.add_record("movies", {"title": "Test Movie", "genre": "Drama"})
        temp_store.save()

        new_store = DataStore(file_path=temp_store.file_path)
        loaded = new_store.load()
        assert len(loaded["movies"]) == 1
        assert loaded["movies"][0]["title"] == "Test Movie"

    def test_load_missing_file_returns_empty_structure(self, temp_store):
        data = temp_store.load()
        assert data["movies"] == []
        assert data["bookings"] == []

    def test_add_record_invalid_category_raises_error(self, temp_store):
        with pytest.raises(ValueError):
            temp_store.add_record("unknown_category", {})

    def test_get_records_invalid_category_raises_error(self, temp_store):
        with pytest.raises(ValueError):
            temp_store.get_records("unknown_category")

    def test_load_corrupted_file_raises_runtime_error(self, temp_store):
        os.makedirs(os.path.dirname(temp_store.file_path), exist_ok=True)
        with open(temp_store.file_path, "w") as f:
            f.write("{ this is not valid json")

        with pytest.raises(RuntimeError):
            temp_store.load()


class TestReport:
    def _make_invoice(self, price=180, num_seats=2):
        movie = Movie("Test Movie", "Drama", 100)
        theater = Theater("Theater 1", rows=2, seats_per_row=5)
        showtime = Showtime(movie, theater, "2099-01-01", "18:30", price)
        seat_map = SeatMap(rows=2, seats_per_row=5)
        labels = ["A1", "A2"][:num_seats]
        seats = seat_map.book_seats(labels)
        member = Member("Somchai", "somchai@test.com", "pass123")
        booking = Booking(member, showtime, seats)
        payment = CashPayment()
        payment.pay(booking.calculate_total())
        return Invoice(booking, payment)

    def test_total_revenue(self):
        invoices = [self._make_invoice(), self._make_invoice()]
        report = Report(invoices)
        assert report.total_revenue() == 720  # (2*180) * 2 invoices

    def test_total_tickets_sold(self):
        invoices = [self._make_invoice(num_seats=2), self._make_invoice(num_seats=1)]
        report = Report(invoices)
        assert report.total_tickets_sold() == 3

    def test_sales_by_movie(self):
        invoices = [self._make_invoice()]
        report = Report(invoices)
        result = report.sales_by_movie()
        assert result["Test Movie"] == 360

    def test_daily_sales_groups_by_date(self):
        invoices = [self._make_invoice()]
        report = Report(invoices)
        result = report.daily_sales()
        assert len(result) == 1
