"""
Module: payment.py
รับผิดชอบ: โมดูล M4 - Payment
FR ที่เกี่ยวข้อง: FR-4.1, FR-4.2, FR-4.4
"""

from abc import ABC, abstractmethod


class Payment(ABC):
    """
    Abstract base class สำหรับวิธีชำระเงินทุกแบบ (abstraction)
    class ลูกทุกตัวต้อง implement pay() เอง
    """

    def __init__(self):
        self.__is_paid = False

    @abstractmethod
    def pay(self, amount: float) -> bool:
        """
        ดำเนินการชำระเงิน คืนค่า True ถ้าสำเร็จ
        class ลูกต้อง override method นี้
        """
        raise NotImplementedError

    def _mark_as_paid(self) -> None:
        """ให้ class ลูกเรียกใช้เมื่อชำระเงินสำเร็จ (protected-style method)"""
        self.__is_paid = True

    @property
    def is_paid(self) -> bool:
        return self.__is_paid


class CreditCardPayment(Payment):
    """ชำระผ่านบัตรเครดิต (polymorphism: override pay())"""

    def __init__(self, card_number: str):
        super().__init__()
        # เก็บเฉพาะ 4 ตัวท้าย เพื่อความปลอดภัย (encapsulation)
        self.__masked_card = f"****-****-****-{card_number[-4:]}"

    def pay(self, amount: float) -> bool:
        if amount <= 0:
            return False
        print(f"[Payment] เรียกเก็บเงิน {amount:.2f} บาท จากบัตร {self.__masked_card}")
        self._mark_as_paid()
        return True


class CashPayment(Payment):
    """ชำระด้วยเงินสด (polymorphism: override pay())"""

    def pay(self, amount: float) -> bool:
        if amount <= 0:
            return False
        print(f"[Payment] รับเงินสด {amount:.2f} บาท")
        self._mark_as_paid()
        return True


class DiscountCalculator:
    """
    คำนวณส่วนลดจากแต้มสะสมของ Member (FR-4.2)
    เชื่อมกับโมดูล M1 ผ่าน Member.points
    """

    POINTS_TO_BAHT_RATE = 1  # 1 แต้ม = 1 บาทส่วนลด (ปรับได้)
    MEMBER_DISCOUNT_RATE = 0.10  # ส่วนลดสมาชิกพื้นฐาน 10%

    @staticmethod
    def calculate_member_discount(subtotal: float) -> float:
        """ส่วนลดสมาชิกพื้นฐานแบบเปอร์เซ็นต์"""
        return round(subtotal * DiscountCalculator.MEMBER_DISCOUNT_RATE, 2)

    @staticmethod
    def calculate_points_discount(member, points_to_use: int) -> float:
        """
        คำนวณส่วนลดจากแต้มที่ต้องการใช้
        ไม่ได้หักแต้มจริงตรงนี้ - ต้องเรียก member.redeem_points() แยกตอนยืนยันชำระเงิน
        """
        if points_to_use > member.points:
            raise ValueError("แต้มไม่พอ")
        return points_to_use * DiscountCalculator.POINTS_TO_BAHT_RATE
