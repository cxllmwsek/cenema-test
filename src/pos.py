"""
Module: pos.py
หน้าจอ POS (Point of Sale) แบบ CLI ที่โต้ตอบกับผู้ใช้ได้จริง
เชื่อมทุกโมดูล M1-M5 เข้าด้วยกัน
 
รันด้วยคำสั่ง: python src/pos.py
"""
 
from users import AuthService, Admin, Member
from movies import Movie, Theater, Showtime, ShowtimeCatalog
from booking import SeatMap, Booking
from payment import CashPayment, CreditCardPayment, DiscountCalculator, Invoice
from data import DataStore, Report
 
 
class POSApp:
    """
    แอปพลิเคชัน POS หลัก ควบคุม flow การโต้ตอบกับผู้ใช้ทั้งหมด
    ทำหน้าที่เป็น "orchestrator" ที่เรียกใช้ทุกโมดูล ไม่ใส่ business logic เองตรงๆ
    """
 
    def __init__(self):
        self.auth = AuthService()
        self.catalog = ShowtimeCatalog()
        self.data_store = DataStore(file_path="data/cinema_data.json")
        self.seat_maps: dict[int, SeatMap] = {}
        self.invoices: list[Invoice] = []
        self.current_user = None
        self._seed_demo_data()
 
    # ---------- ข้อมูลตัวอย่าง ----------
    def _seed_demo_data(self):
        movie1 = Movie("Avengers: New Dawn", "Action", 140, "PG-13")
        movie2 = Movie("Whispers of the Forest", "Animation", 100, "G")
        self.catalog.add_movie(movie1)
        self.catalog.add_movie(movie2)
 
        theater1 = Theater("Theater 1", rows=5, seats_per_row=8)
        theater2 = Theater("Theater 2 (IMAX)", rows=6, seats_per_row=8)
 
        st1 = Showtime(movie1, theater1, "2026-08-01", "14:00", 150)
        st2 = Showtime(movie1, theater2, "2026-08-01", "18:30", 220)
        st3 = Showtime(movie2, theater1, "2026-08-01", "16:00", 130)
 
        for st in (st1, st2, st3):
            self.catalog.add_showtime(st)
            self.seat_maps[id(st)] = SeatMap(st.theater.rows, st.theater.seats_per_row)
 
        # แอดมินเริ่มต้นสำหรับทดสอบ
        self.auth.register("Admin User", "admin@cinema.com", "admin123", role="admin")
 
    # ---------- Helper รับ input ----------
    @staticmethod
    def _prompt(text: str) -> str:
        return input(text).strip()
 
    @staticmethod
    def _prompt_int(text: str, default: int | None = None) -> int:
        raw = input(text).strip()
        if raw == "" and default is not None:
            return default
        return int(raw)
 
    # ---------- หน้าจอ Login/Register ----------
    def screen_welcome(self):
        while True:
            print("\n=== ยินดีต้อนรับสู่ Cinema POS ===")
            print("1. เข้าสู่ระบบ")
            print("2. สมัครสมาชิกใหม่")
            print("0. ออกจากโปรแกรม")
            choice = self._prompt("เลือกเมนู: ")
 
            if choice == "1":
                if self._login():
                    return True
            elif choice == "2":
                self._register()
            elif choice == "0":
                return False
            else:
                print("!! กรุณาเลือกเมนูที่ถูกต้อง")
 
    def _login(self) -> bool:
        email = self._prompt("อีเมล: ")
        password = self._prompt("รหัสผ่าน: ")
        user = self.auth.authenticate(email, password)
        if user is None:
            return False
        self.current_user = user
        return True
 
    def _register(self):
        name = self._prompt("ชื่อ: ")
        email = self._prompt("อีเมล: ")
        password = self._prompt("รหัสผ่าน: ")
        try:
            self.auth.register(name, email, password, role="member")
        except ValueError as e:
            print(f"!! {e}")
 
    # ---------- เมนูหลัก ----------
    def screen_main_menu(self):
        while True:
            print(f"\n=== เมนูหลัก ({self.current_user.get_role()}: {self.current_user.name}) ===")
            if isinstance(self.current_user, Member):
                print("1. ดูรอบภาพยนตร์และจองตั๋ว")
            if isinstance(self.current_user, Admin):
                print("2. ดูรายงานยอดขาย (Admin)")
            print("9. ออกจากระบบ")
            print("0. ปิดโปรแกรม")
            choice = self._prompt("เลือกเมนู: ")
 
            if choice == "1" and isinstance(self.current_user, Member):
                self.screen_booking_flow()
            elif choice == "1":
                print("!! เฉพาะบัญชีสมาชิก (Member) เท่านั้นที่จองตั๋วได้")
            elif choice == "2" and isinstance(self.current_user, Admin):
                self.screen_admin_report()
            elif choice == "9":
                self.current_user.logout()
                self.current_user = None
                return True
            elif choice == "0":
                return False
            else:
                print("!! กรุณาเลือกเมนูที่ถูกต้อง")
 
    # ---------- Flow การจองตั๋ว ----------
    def screen_booking_flow(self):
        showtimes = self.catalog.get_available_showtimes()
        if not showtimes:
            print("ขณะนี้ไม่มีรอบฉายที่เปิดให้จอง")
            return
 
        print("\n--- รอบฉายที่เปิดให้จอง ---")
        for i, st in enumerate(showtimes, start=1):
            print(f"{i}. {st.movie.title} | {st.theater.name} | "
                  f"{st.date} {st.time} | ราคา {st.price:.0f} บาท | "
                  f"ว่าง {st.available_seats_count} ที่นั่ง")
 
        idx = self._prompt_int("เลือกรอบฉาย (ใส่หมายเลข, 0 = ยกเลิก): ", default=0)
        if idx == 0 or idx > len(showtimes):
            return
        showtime = showtimes[idx - 1]
        seat_map = self.seat_maps[id(showtime)]
 
        self._show_seat_map(seat_map)
        labels_raw = self._prompt("เลือกที่นั่ง (คั่นด้วยจุลภาค เช่น A1,A2): ")
        labels = [s.strip().upper() for s in labels_raw.split(",") if s.strip()]
 
        try:
            seats = seat_map.book_seats(labels)
        except ValueError as e:
            print(f"!! {e}")
            return
 
        booking = Booking(self.current_user, showtime, seats)
        subtotal = booking.calculate_total()
        print(f"\nยอดรวม: {subtotal:.2f} บาท")
 
        discount = self._screen_discount(subtotal)
        payment = self._screen_payment_method()
        amount_due = max(0.0, subtotal - discount)
 
        if not payment.pay(amount_due):
            print("!! การชำระเงินไม่สำเร็จ ปลดล็อกที่นั่งคืน")
            seat_map.release_seats(labels)
            return
 
        booking.confirm()
        invoice = Invoice(booking, payment, discount=discount)
        self.invoices.append(invoice)
 
        print("\n" + invoice.generate_receipt_text())
 
        self.data_store.add_record("bookings", {
            "booking_id": booking.booking_id,
            "member": self.current_user.email,
            "movie": showtime.movie.title,
            "seats": labels,
            "total": invoice.net_total,
        })
        self.data_store.save()
        print(f"[บันทึกข้อมูลแล้วที่ {self.data_store.file_path}]")
 
    def _show_seat_map(self, seat_map: SeatMap):
        print("\nผังที่นั่ง (X = จองแล้ว, O = ว่าง):")
        seats = seat_map.get_all_seats()
        rows = sorted(set(s.row for s in seats))
        seats_per_row = len(seats) // len(rows)
 
        for row in rows:
            line = f"{row}: "
            for num in range(1, seats_per_row + 1):
                seat = seat_map.get_seat(f"{row}{num}")
                line += "X " if not seat.is_available() else "O "
            print(line)
 
    def _screen_discount(self, subtotal: float) -> float:
        if not isinstance(self.current_user, Member):
            return 0.0
 
        print(f"\nแต้มสะสมของคุณ: {self.current_user.points}")
        use_points = self._prompt("ใช้แต้มแลกส่วนลดหรือไม่? (y/n): ").lower()
        if use_points == "y":
            points = self._prompt_int("จำนวนแต้มที่ต้องการใช้: ", default=0)
            try:
                discount = DiscountCalculator.calculate_points_discount(
                    self.current_user, points)
                self.current_user.redeem_points(points)
                return discount
            except ValueError as e:
                print(f"!! {e}")
                return 0.0
 
        member_discount = DiscountCalculator.calculate_member_discount(subtotal)
        print(f"ส่วนลดสมาชิก 10%: -{member_discount:.2f} บาท")
        return member_discount
 
    def _screen_payment_method(self):
        print("\nวิธีชำระเงิน:")
        print("1. เงินสด")
        print("2. บัตรเครดิต")
        choice = self._prompt("เลือกวิธีชำระเงิน: ")
        if choice == "2":
            card_number = self._prompt("หมายเลขบัตร (16 หลัก): ")
            return CreditCardPayment(card_number)
        return CashPayment()
 
    def screen_admin_report(self):
        report = Report(self.invoices)
        print("\n=== รายงานยอดขาย ===")
        print(f"รายได้รวม: {report.total_revenue():.2f} บาท")
        print(f"ตั๋วที่ขายได้: {report.total_tickets_sold()} ที่นั่ง")
        print("\nยอดขายแยกตามภาพยนตร์:")
        for title, total in report.sales_by_movie().items():
            print(f"  - {title}: {total:.2f} บาท")
 
    # ---------- จุดเริ่มโปรแกรม ----------
    def run(self):
        print("ยินดีต้อนรับสู่ Cinema Booking POS")
        print("(บัญชี Admin สำหรับทดสอบ: admin@cinema.com / admin123)")
        while True:
            if not self.screen_welcome():
                break
            if not self.screen_main_menu():
                break
        print("\nขอบคุณที่ใช้บริการ")
 
 
if __name__ == "__main__":
    POSApp().run()