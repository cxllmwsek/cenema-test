"""
Module: user.py
รับผิดชอบ: โมดูล M1 - User Management
ครอบคลุม: User (base class), Member, Admin
FR ที่เกี่ยวข้อง: FR-1.1 - FR-1.5
"""

from datetime import datetime
import hashlib


class User:
    """
    Base class สำหรับผู้ใช้งานทุกประเภทในระบบ
    เก็บข้อมูลพื้นฐาน: ชื่อ, อีเมล, รหัสผ่าน (แบบ hash)
    """

    def __init__(self, name: str, email: str, password: str):
        self.name = name
        self.email = email
        self.__password_hash = self._hash_password(password)  # private: encapsulation
        self.created_at = datetime.now()
        self.__is_logged_in = False

    @staticmethod
    def _hash_password(password: str) -> str:
        """แปลงรหัสผ่านเป็น hash ก่อนเก็บ ไม่เก็บ plain text"""
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password: str) -> bool:
        """ตรวจสอบว่ารหัสผ่านที่กรอกตรงกับที่เก็บไว้หรือไม่"""
        return self.__password_hash == self._hash_password(password)

    def login(self, password: str) -> bool:
        """
        เข้าสู่ระบบ (FR-1.2)
        คืนค่า True ถ้าสำเร็จ, False ถ้ารหัสผ่านผิด
        """
        if self.check_password(password):
            self.__is_logged_in = True
            print(f"[Login] {self.name} เข้าสู่ระบบสำเร็จ")
            return True
        print(f"[Login] รหัสผ่านไม่ถูกต้องสำหรับ {self.email}")
        return False

    def logout(self) -> None:
        """ออกจากระบบ (FR-1.2)"""
        self.__is_logged_in = False
        print(f"[Logout] {self.name} ออกจากระบบแล้ว")

    @property
    def is_logged_in(self) -> bool:
        return self.__is_logged_in

    def get_role(self) -> str:
        """
        Method ที่ subclass ควร override (polymorphism)
        base class คืนค่า role ทั่วไป
        """
        return "User"

    def __repr__(self) -> str:
        return f"<{self.get_role()}: {self.name} ({self.email})>"


class Member(User):
    """
    สมาชิกที่สามารถจองตั๋วและสะสมแต้มได้ (FR-1.3)
    สืบทอดจาก User (inheritance)
    """

    def __init__(self, name: str, email: str, password: str):
        super().__init__(name, email, password)
        self.__points = 0  # private: encapsulation
        self.booking_history = []

    @property
    def points(self) -> int:
        return self.__points

    def add_points(self, amount: int) -> None:
        """เพิ่มแต้มสะสมจากการจอง (FR-1.3)"""
        if amount < 0:
            raise ValueError("จำนวนแต้มต้องไม่ติดลบ")
        self.__points += amount

    def redeem_points(self, amount: int) -> bool:
        """ใช้แต้มแลกส่วนลด คืนค่า True ถ้าสำเร็จ"""
        if amount > self.__points:
            print("แต้มไม่พอสำหรับการแลก")
            return False
        self.__points -= amount
        return True

    def add_booking_record(self, booking) -> None:
        """เก็บประวัติการจอง (FR-3.5) - รับ Booking object จากโมดูล M3"""
        self.booking_history.append(booking)

    def get_role(self) -> str:
        """override method จาก base class (polymorphism)"""
        return "Member"


class Admin(User):
    """
    ผู้ดูแลระบบ มีสิทธิ์จัดการภาพยนตร์/รอบฉาย (FR-1.4)
    สืบทอดจาก User (inheritance)
    """

    def __init__(self, name: str, email: str, password: str, admin_level: int = 1):
        super().__init__(name, email, password)
        self.admin_level = admin_level

    def get_role(self) -> str:
        """override method จาก base class (polymorphism)"""
        return "Admin"

    def has_permission(self, action: str) -> bool:
        """
        ตรวจสอบสิทธิ์การทำ action ต่างๆ (FR-1.5)
        ขยายเพิ่มเติมได้ตามระดับ admin_level ในอนาคต
        """
        allowed_actions = {"add_movie", "edit_movie", "delete_movie",
                            "add_showtime", "edit_showtime", "view_report"}
        return action in allowed_actions


class AuthService:
    """
    บริการจัดการการสมัครสมาชิกและตรวจสอบสิทธิ์ส่วนกลาง
    ทำหน้าที่เป็นตัวกลางระหว่าง main.py กับ User/Member/Admin
    """

    def __init__(self):
        self.__users: dict[str, User] = {}  # key = email

    def register(self, name: str, email: str, password: str, role: str = "member") -> User:
        """
        สมัครสมาชิกใหม่ (FR-1.1)
        role: 'member' หรือ 'admin'
        """
        if email in self.__users:
            raise ValueError(f"อีเมล {email} ถูกใช้งานแล้ว")

        if role == "admin":
            user = Admin(name, email, password)
        else:
            user = Member(name, email, password)

        self.__users[email] = user
        print(f"[Register] สมัครสมาชิกสำเร็จ: {user}")
        return user

    def authenticate(self, email: str, password: str) -> User | None:
        """ตรวจสอบและเข้าสู่ระบบ คืนค่า User object ถ้าสำเร็จ"""
        user = self.__users.get(email)
        if user is None:
            print(f"[Auth] ไม่พบผู้ใช้งานอีเมล {email}")
            return None
        if user.login(password):
            return user
        return None

    def authorize(self, user: User, action: str) -> bool:
        """
        ตรวจสอบสิทธิ์ก่อนอนุญาตให้ทำ action (FR-1.5)
        ใช้ isinstance เพื่อเช็คว่าเป็น Admin หรือไม่ (ตัวอย่างการใช้ polymorphism ร่วมกับ type check)
        """
        if isinstance(user, Admin):
            return user.has_permission(action)
        return False
