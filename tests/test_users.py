"""
Unit tests สำหรับโมดูล User Management (M1)
รันด้วยคำสั่ง: pytest tests/test_users.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from users import User, Member, Admin, AuthService


class TestUser:
    def test_password_is_hashed_not_plaintext(self):
        user = Member("Somchai", "somchai@test.com", "mypassword123")
        # password ไม่ควรถูกเก็บเป็น plain text (encapsulation test)
        assert "mypassword123" not in user.__dict__.values()

    def test_login_success(self):
        user = Member("Somchai", "somchai@test.com", "mypassword123")
        assert user.login("mypassword123") is True
        assert user.is_logged_in is True

    def test_login_wrong_password(self):
        user = Member("Somchai", "somchai@test.com", "mypassword123")
        assert user.login("wrongpassword") is False
        assert user.is_logged_in is False

    def test_logout(self):
        user = Member("Somchai", "somchai@test.com", "mypassword123")
        user.login("mypassword123")
        user.logout()
        assert user.is_logged_in is False


class TestMember:
    def test_add_points(self):
        member = Member("Somchai", "somchai@test.com", "pass123")
        member.add_points(50)
        assert member.points == 50

    def test_add_negative_points_raises_error(self):
        member = Member("Somchai", "somchai@test.com", "pass123")
        with pytest.raises(ValueError):
            member.add_points(-10)

    def test_redeem_points_success(self):
        member = Member("Somchai", "somchai@test.com", "pass123")
        member.add_points(100)
        assert member.redeem_points(30) is True
        assert member.points == 70

    def test_redeem_points_insufficient(self):
        member = Member("Somchai", "somchai@test.com", "pass123")
        member.add_points(10)
        assert member.redeem_points(50) is False
        assert member.points == 10

    def test_get_role_returns_member(self):
        member = Member("Somchai", "somchai@test.com", "pass123")
        assert member.get_role() == "Member"


class TestAdmin:
    def test_get_role_returns_admin(self):
        admin = Admin("Wanna", "wanna@test.com", "adminpass")
        assert admin.get_role() == "Admin"

    def test_has_permission_allowed_action(self):
        admin = Admin("Wanna", "wanna@test.com", "adminpass")
        assert admin.has_permission("add_movie") is True

    def test_has_permission_disallowed_action(self):
        admin = Admin("Wanna", "wanna@test.com", "adminpass")
        assert admin.has_permission("delete_all_data") is False


class TestPolymorphism:
    def test_get_role_polymorphic_behavior(self):
        """ทดสอบว่า get_role() ให้ผลต่างกันตาม object type แม้เรียกด้วย syntax เดียวกัน"""
        users = [
            Member("Somchai", "m@test.com", "pass"),
            Admin("Wanna", "a@test.com", "pass"),
        ]
        roles = [u.get_role() for u in users]
        assert roles == ["Member", "Admin"]


class TestAuthService:
    def test_register_member(self):
        auth = AuthService()
        user = auth.register("Somchai", "somchai@test.com", "pass123", role="member")
        assert isinstance(user, Member)

    def test_register_admin(self):
        auth = AuthService()
        user = auth.register("Wanna", "wanna@test.com", "pass123", role="admin")
        assert isinstance(user, Admin)

    def test_register_duplicate_email_raises_error(self):
        auth = AuthService()
        auth.register("Somchai", "somchai@test.com", "pass123")
        with pytest.raises(ValueError):
            auth.register("Somchai2", "somchai@test.com", "pass456")

    def test_authenticate_success(self):
        auth = AuthService()
        auth.register("Somchai", "somchai@test.com", "pass123")
        user = auth.authenticate("somchai@test.com", "pass123")
        assert user is not None
        assert user.is_logged_in is True

    def test_authenticate_wrong_password(self):
        auth = AuthService()
        auth.register("Somchai", "somchai@test.com", "pass123")
        user = auth.authenticate("somchai@test.com", "wrongpass")
        assert user is None

    def test_authorize_admin_action(self):
        auth = AuthService()
        admin = auth.register("Wanna", "wanna@test.com", "pass123", role="admin")
        assert auth.authorize(admin, "add_movie") is True

    def test_authorize_member_has_no_admin_permission(self):
        auth = AuthService()
        member = auth.register("Somchai", "somchai@test.com", "pass123", role="member")
        assert auth.authorize(member, "add_movie") is False
