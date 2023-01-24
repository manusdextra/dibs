import unittest
from app.models import User


class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self) -> None:
        u = User(password="foo")
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self) -> None:
        u = User(password="foo")
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self) -> None:
        u = User(password="foo")
        self.assertTrue(u.verify_password("foo"))
        self.assertFalse(u.verify_password("bar"))

    def test_password_salts_are_random(self) -> None:
        u = User(password="foo")
        u2 = User(password="foo")
        self.assertTrue(u.password_hash != u2.password_hash)
