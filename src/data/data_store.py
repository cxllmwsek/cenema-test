"""
Module: data_store.py
รับผิดชอบ: โมดูล M5 - Data & Reporting (ส่วนของ persistence)
FR ที่เกี่ยวข้อง: FR-5.1, FR-5.2, FR-5.4
"""

import json
import os


class DataStore:
    """
    จัดการบันทึกและโหลดข้อมูลแบบถาวรด้วยไฟล์ JSON
    ออกแบบให้แยกส่วน serialize/deserialize ไว้ที่นี่ ไม่ปนกับ business logic ของ class อื่น
    """

    def __init__(self, file_path: str = "data/cinema_data.json"):
        self.file_path = file_path
        self.__data = {"movies": [], "showtimes": [], "bookings": [], "users": []}
        self._ensure_directory_exists()

    def _ensure_directory_exists(self) -> None:
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def save(self) -> None:
        """บันทึกข้อมูลปัจจุบันลงไฟล์ (FR-5.1)"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.__data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            raise RuntimeError(f"บันทึกข้อมูลไม่สำเร็จ: {e}")

    def load(self) -> dict:
        """
        โหลดข้อมูลจากไฟล์ (FR-5.2)
        มี error handling กรณีไฟล์ไม่พบหรือเสียหาย (FR-5.4)
        """
        if not os.path.exists(self.file_path):
            print(f"[DataStore] ไม่พบไฟล์ {self.file_path} เริ่มต้นด้วยข้อมูลว่าง")
            return self.__data

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.__data = json.load(f)
        except json.JSONDecodeError:
            raise RuntimeError(f"ไฟล์ข้อมูล {self.file_path} เสียหาย ไม่สามารถอ่านได้")
        except OSError as e:
            raise RuntimeError(f"โหลดข้อมูลไม่สำเร็จ: {e}")

        return self.__data

    def add_record(self, category: str, record: dict) -> None:
        """
        เพิ่มข้อมูลลง category ที่กำหนด เช่น 'bookings', 'movies'
        """
        if category not in self.__data:
            raise ValueError(f"ไม่รู้จัก category: {category}")
        self.__data[category].append(record)

    def get_records(self, category: str) -> list:
        if category not in self.__data:
            raise ValueError(f"ไม่รู้จัก category: {category}")
        return self.__data[category]
