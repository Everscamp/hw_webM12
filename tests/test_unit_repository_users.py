import unittest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.getcwd())
sys.path.append(os.path.abspath('.\\src\\database'))

from sqlalchemy.orm import Session

from src.database.models import User, Contact
from src.schemas import UserModel, UserDb, UserResponse, TokenModel, RequestEmail
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_user_by_email_found(self):
        user = User()
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(email='test@test.com', db=self.session)
        self.assertEqual(result, user)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(email='test@test.com', db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        body = UserModel(username='test', email='test@test.com', password='password')
        result = await create_user(body=body, db=self.session)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_token(self):
        user = User()
        test_token = 'test'
        await update_token(user=user, token=test_token, db=self.session)
        self.assertEqual(user.refresh_token, test_token)

    async def test_confirmed_email(self):
        await confirmed_email(email='test@test.com', db=self.session)
        user = await get_user_by_email(email='test@test.com', db=self.session)
        self.assertEqual(user.confirmed, True)

    async def test_update_avatar(self):
        url = 'test_url'
        result = await update_avatar(email='test@test.com', url=url, db=self.session)
        self.assertEqual(result.avatar, url)


if __name__ == '__main__':
    unittest.main()