"""
Module: main.py
จุดเริ่มโปรแกรม CLI ระบบจองตั๋วโรงภาพยนตร์
เชื่อมทุกโมดูล (M1-M5) เข้าด้วยกัน

รันด้วยคำสั่ง: python src/main.py
"""

from users import AuthService, Admin
from movies import Movie, Theater, Showtime, ShowtimeCatalog
from booking import SeatMap, Booking
from payment import CashPayment, CreditCardPayment, DiscountCalculator, Invoice
from data import DataStore, Report


def seed_demo_data(catalog: ShowtimeCatalog) -> dict[int, SeatMap]:
    """สร้างข้อมูลตัวอย่างไว้ทดสอบระบบ (หนัง 1 เรื่อง, 2 รอบฉาย)"""
    movie = Movie("Avengers: New Dawn", "Action", 140, "PG-13")
    catalog.add_movie(movie)

    theater1 = Theater("Theater 1", rows=5, seats_per_row=8)
    theater2 = Theater("Theater 2 (IMAX)", rows=7, seats_per_row=10)

    showtime1 = Showtime(movie, theater1, "2026-08-01", "14:00", 150)
    showtime2 = Showtime(movie, theater2, "2026-08-01", "18:30", 220)

    catalog.add_showtime(showtime1)
    catalog.add_showtime(showtime2)

    seat_maps = {
        id(showtime1): SeatMap(theater1.rows, theater1.seats_per_row),
        id(showtime2): SeatMap(theater2.rows, theater2.seats_per_row),
    }
    return seat_maps


def main():
    print("=== ระบบจองตั๋วโรงภาพยนตร์ (Cinema Booking System) ===\n")

    auth = AuthService()
    catalog = ShowtimeCatalog()
    data_store = DataStore(file_path="data/cinema_data.json")
    seat_maps = seed_demo_data(catalog)
    invoices = []

    # --- Demo flow: จำลองการทำงานแบบ end-to-end ---
    member = auth.register("Somchai", "somchai@example.com", "pass123", role="member")
    admin = auth.register("Wanna", "admin@example.com", "adminpass", role="admin")

    print(f"\nสิทธิ์ของ {admin.name}: จัดการหนังได้ = {auth.authorize(admin, 'add_movie')}")
    print(f"สิทธิ์ของ {member.name}: จัดการหนังได้ = {auth.authorize(member, 'add_movie')}\n")

    print("รอบฉายที่มีที่นั่งว่าง:")
    for st in catalog.get_available_showtimes():
        print(f"  - {st}")

    # เลือกรอบฉายแรก จองที่นั่ง A1, A2
    showtime = catalog.get_available_showtimes()[0]
    seat_map = seat_maps[id(showtime)]
    seats = seat_map.book_seats(["A1", "A2"])

    booking = Booking(member, showtime, seats)
    print(f"\nสร้างการจอง: {booking}")
    print(f"ยอดรวม: {booking.calculate_total():.2f} บาท")

    # ชำระเงิน + คำนวณส่วนลด
    discount = DiscountCalculator.calculate_member_discount(booking.calculate_total())
    payment = CashPayment()
    payment.pay(booking.calculate_total() - discount)
    booking.confirm()

    invoice = Invoice(booking, payment, discount=discount)
    invoices.append(invoice)
    print("\n" + invoice.generate_receipt_text())

    # บันทึกข้อมูล
    data_store.add_record("bookings", {
        "booking_id": booking.booking_id,
        "member": member.email,
        "movie": showtime.movie.title,
        "seats": [s.label for s in seats],
        "total": invoice.net_total,
    })
    data_store.save()
    print(f"\n[บันทึกข้อมูลแล้วที่ {data_store.file_path}]")

    # รายงานยอดขาย (สำหรับ Admin)
    report = Report(invoices)
    print(f"\nรายงานยอดขาย: รวม {report.total_revenue():.2f} บาท, "
          f"ขายได้ {report.total_tickets_sold()} ที่นั่ง")


if __name__ == "__main__":
    main()
