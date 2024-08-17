import unittest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timedelta
import sys
import os


sys.path.append(os.path.abspath('.\\src\\database'))

from sqlalchemy.orm import Session

from src.database.models import User, Contact
from src.schemas import ContactBase, ContactResponse
from src.repository.contacts import (
    get_contacts,
    get_contact,
    get_contact_by_name,
    get_closest_birthdays,
    create_contact,
    remove_contact,
    update_contact,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        #contact = self.session.execute().scalar_one_or_none()
        #result = await get_contact(contact_id=1, user=self.user, db=self.session)
        #self.assertEqual(result, contact)

        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_by_name(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact_by_name(path='name', value='test', user=self.user, db=self.session)
        self.assertEqual(result, contact)
        result = await get_contact_by_name(path='surname', value='test', user=self.user, db=self.session)
        self.assertEqual(result, contact)
        result = await get_contact_by_name(path='email', value='test@test.com', user=self.user, db=self.session)
        self.assertEqual(result, contact)


    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactBase(name='test', surname='test', mobile='+155555555', email='test@test.com', birthday='2000-01-01')
        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.mobile, body.mobile)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.birthday, body.birthday)
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        body = ContactBase(name='test', surname='test', mobile='+155555555', email='test@test.com', birthday='2000-01-01', done=True)
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = ContactBase(name='test', surname='test', mobile='+155555555', email='test@test.com', birthday='2000-01-01', done=True)
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_get_closest_birthdays(self):
        body1 = ContactBase(name='test1', surname='test1', mobile='+155555555', email='test@test.com', birthday='2000-08-19')
        contact1 = await create_contact(body=body1, user=self.user, db=self.session)
        body2 = ContactBase(name='test2', surname='test2', mobile='+155555555', email='test@test.com', birthday='2000-08-20')
        contact2 = await create_contact(body=body2, user=self.user, db=self.session)
        body3 = ContactBase(name='test3', surname='test3', mobile='+155555555', email='test@test.com', birthday='2000-07-19')
        contact3 = await create_contact(body=body3, user=self.user, db=self.session)
        
        self.session.query().filter().offset().limit().all().return_value = [contact1, contact2, contact3]
        
        result = await get_closest_birthdays(skip=0, limit=100, user=self.user, db=self.session)
        print(result)
        self.assertEqual(len(result), 2)


if __name__ == '__main__':
    unittest.main()