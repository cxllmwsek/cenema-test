"""
Unit tests สำหรับโมดูล Payment (M4)
รันด้วยคำสั่ง: pytest tests/test_payment.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from payment import CreditCardPayment, CashPayment, DiscountCalculator, Invoice
from booking import SeatMap, Booking
from movies import Movie, Theater, Showtime
from users import Member


class TestCreditCardPayment:
    def test_pay_success(self):
        payment = CreditCardPayment("1234567812345678")
        result = payment.pay(500)
        assert result is True
        assert payment.is_paid is True

    def test_pay_zero_amount_fails(self):
        payment = CreditCardPayment("1234567812345678")
        result = payment.pay(0)
        assert result is False
        assert payment.is_paid is False


class TestCashPayment:
    def test_pay_success(self):
        payment = CashPayment()
        result = payment.pay(300)
        assert result is True
        assert payment.is_paid is True


class TestPolymorphismPayment:
    def test_different_payment_types_share_interface(self):
        """ทดสอบว่า pay() ทำงานได้เหมือนกันแม้ object type ต่างกัน (polymorphism)"""
        payments = [CreditCardPayment("1111222233334444"), CashPayment()]
        results = [p.pay(100) for p in payments]
        assert all(results)


class TestDiscountCalculator:
    def test_member_discount(self):
        discount = DiscountCalculator.calculate_member_discount(1000)
        assert discount == 100  # 10%

    def test_points_discount(self):
        member = Member("Somchai", "somchai@test.com", "pass123")
        member.add_points(50)
        discount = DiscountCalculator.calculate_points_discount(member, 30)
        assert discount == 30

    def test_points_discount_insufficient_raises_error(self):
        member = Member("Somchai", "somchai@test.com", "pass123")
        member.add_points(10)
        with pytest.raises(ValueError):
            DiscountCalculator.calculate_points_discount(member, 50)


class TestInvoice:
    def _make_booking(self):
        movie = Movie("Test Movie", "Drama", 100)
        theater = Theater("Theater 1", rows=2, seats_per_row=5)
        showtime = Showtime(movie, theater, "2099-01-01", "18:30", 180)
        seat_map = SeatMap(rows=2, seats_per_row=5)
        seats = seat_map.book_seats(["A1", "A2"])
        member = Member("Somchai", "somchai@test.com", "pass123")
        return Booking(member, showtime, seats)

    def test_invoice_requires_paid_payment(self):
        booking = self._make_booking()
        payment = CashPayment()  # ยังไม่ได้ pay()
        with pytest.raises(ValueError):
            Invoice(booking, payment)

    def test_invoice_net_total_with_discount(self):
        booking = self._make_booking()
        payment = CashPayment()
        payment.pay(booking.calculate_total())
        invoice = Invoice(booking, payment, discount=50)
        assert invoice.subtotal == 360
        assert invoice.net_total == 310

    def test_invoice_generate_receipt_text_contains_key_info(self):
        booking = self._make_booking()
        payment = CashPayment()
        payment.pay(booking.calculate_total())
        invoice = Invoice(booking, payment)
        receipt = invoice.generate_receipt_text()
        assert "Test Movie" in receipt
        assert invoice.invoice_number in receipt
