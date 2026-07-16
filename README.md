# Cinema Booking System

ระบบจองตั๋วโรงภาพยนตร์ พัฒนาด้วย Python เน้นหลักการ Object-Oriented Programming (OOP) ครบ 4 เสาหลัก: Encapsulation, Inheritance, Polymorphism, Abstraction

โปรเจ็คนี้พัฒนาโดยทีม 5 คน แบ่งงานเป็น 5 โมดูลตามเอกสาร [SRS](docs/SRS_Cinema_Booking_System.md)

## โครงสร้างโปรเจ็ค

```
cinema-booking-system/
├── src/
│   ├── main.py           # จุดเริ่มโปรแกรม
│   ├── users/             # M1: User, Member, Admin, AuthService
│   ├── movies/             # M2: Movie, Theater, Showtime, ShowtimeCatalog
│   ├── booking/            # M3: Seat, SeatMap, Booking
│   ├── payment/            # M4: Payment, CreditCardPayment, CashPayment, Invoice
│   └── data/                # M5: DataStore, Report
├── tests/                  # unit tests (pytest) แยกตามโมดูล
└── docs/                   # SRS และเอกสารประกอบ
```

## การติดตั้ง

```bash
pip install -r requirements.txt
```

## วิธีรันโปรแกรม

```bash
python src/main.py
```

โปรแกรมจะจำลอง flow การใช้งานแบบ end-to-end: สมัครสมาชิก → ดูรอบฉาย → จองที่นั่ง → ชำระเงิน → ออกใบเสร็จ → บันทึกข้อมูล → สรุปรายงานยอดขาย

## วิธีรัน test

```bash
pytest tests/ -v
```

## สมาชิกทีมและหน้าที่รับผิดชอบ

| โมดูล | ผู้รับผิดชอบ | ไฟล์ |
|---|---|---|
| M1: User Management | คนที่ 1 | `src/users/` |
| M2: Movie & Showtime | คนที่ 2 | `src/movies/` |
| M3: Seat & Booking | คนที่ 3 | `src/booking/` |
| M4: Payment | คนที่ 4 | `src/payment/` |
| M5: Data & Reporting | คนที่ 5 | `src/data/` |

## OOP Concepts ที่ใช้

- **Encapsulation**: `User.__password_hash`, `Seat.__status`, `Showtime.__booked_seat_count`
- **Inheritance**: `Member`/`Admin` สืบทอดจาก `User`, `CreditCardPayment`/`CashPayment` สืบทอดจาก `Payment`
- **Polymorphism**: `get_role()` และ `pay()` ให้ผลต่างกันตาม object type
- **Abstraction**: `Payment` เป็น abstract class (ใช้ `abc` module)
- **Composition**: `Booking` ประกอบจาก `Member` + `Showtime` + `Seat[]`, `Invoice` ประกอบจาก `Booking` + `Payment`
