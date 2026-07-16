"""
Module: movie.py
รับผิดชอบ: โมดูล M2 - Movie & Showtime (ส่วนของ Movie)
FR ที่เกี่ยวข้อง: FR-2.1, FR-2.3
"""


class Movie:
    """
    เก็บข้อมูลภาพยนตร์แต่ละเรื่อง
    """

    VALID_RATINGS = {"G", "PG", "PG-13", "R", "NC-17"}

    def __init__(self, title: str, genre: str, duration_minutes: int,
                 rating: str = "PG", description: str = ""):
        if duration_minutes <= 0:
            raise ValueError("ความยาวภาพยนตร์ต้องมากกว่า 0 นาที")
        if rating not in self.VALID_RATINGS:
            raise ValueError(f"เรตอายุไม่ถูกต้อง ต้องเป็นหนึ่งใน {self.VALID_RATINGS}")

        self.title = title
        self.genre = genre
        self.duration_minutes = duration_minutes
        self.rating = rating
        self.description = description

    def matches_search(self, keyword: str) -> bool:
        """
        ค้นหาว่าคำค้นตรงกับชื่อหรือประเภทหนังไหม (FR-2.3)
        ไม่สนตัวพิมพ์เล็ก/ใหญ่
        """
        keyword = keyword.lower()
        return keyword in self.title.lower() or keyword in self.genre.lower()

    def __repr__(self) -> str:
        return f"<Movie: {self.title} ({self.genre}, {self.duration_minutes} min, {self.rating})>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Movie):
            return False
        return self.title == other.title and self.genre == other.genre
