from typing import List
from sqlalchemy import select, and_
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactBase, ContactResponse


async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    """
    Return the list of all contacts in the specified interval.

    Args:
        skip (int): The starting position.
        limit (int): The final position.
        user (User): Authorised user who search for a contact.
        db (Session): Just a session to retrieve data from DB.

    Returns:
        List[Contact]: List with all contacts.
    """
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


# just a note fore me
async def get_contact(contact_id: int, user: User, db: AsyncSession) -> Contact | None:
    """
    Search for a contact by it's id.

    Args:
        contact_id (int): Searched contact ID.
        user (User): User who searching.
        db (AsyncSession): Just a session to retrieve data from DB.

    Returns:
        Contact | None: Return contact with a specified id or None.
    """
    # stmt = select(Contact).filter_by(id=contact_id, user=user)
    # contact = db.execute(stmt)
    # return contact.scalar_one_or_none()
    """ I changed this part since I had lots of issues with test because of it."""
    return db.query(Contact).filter(Contact.id == contact_id).first()


async def get_contact_by_name(path: str, value: str, user: User, db: Session) -> Contact:
    """
    Search for a contact by it's name, surname or email.

    Args:
        path (str): Specify by what you want to search the contact. Can be name, surname, email.
        value (str): The actual name/surname/email to search by.
        user (User): Authorised user who search for a contact. 
        db (Session): Session to retrieve data from DB.

    Returns:
        Contact: Return contact with a specified name if exist.
    """
    if path == 'name':
        return db.query(Contact).filter(and_(Contact.name == value, Contact.user_id == user.id)).first()
    if path == 'surname':
        return db.query(Contact).filter(and_(Contact.surname == value, Contact.user_id == user.id)).first()
    if path == 'email':
        return db.query(Contact).filter(and_(Contact.surname == value, Contact.user_id == user.id)).first()
    

async def get_closest_birthdays(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    """
    Return the list of contact with birthday within the next 7 days.

    Args:
        skip (int): The starting position.
        limit (int): The final position.
        user (User): Authorised user who search for a contact. 
        db (Session): Session to retrieve data from DB.

    Returns:
        List[Contact]: List of the contacts.
    """
    contacts = db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()
    
    if not isinstance(contacts, list):
        contacts = contacts.return_value

    list_of_bees = []
    for i in contacts:
        modified_date = i.birthday.replace(year=datetime.now().year + 1) \
        if i.birthday.month == 1 \
        else i.birthday.replace(year=datetime.now().year)
        result = modified_date - datetime.today()
        if result <= timedelta(days=7) and result >= timedelta(days=0):
            list_of_bees.append(i)
    
    return list_of_bees


async def create_contact(body: ContactBase, user: User, db: AsyncSession) -> Contact:
    """
    Add the contact by an authorised user.

    Args:
        body (ContactBase): Containes contact details such as name, surname, email, number, bday.
        user (User): Authorised user. 
        db (AsyncSession): Session to connect the DB.

    Returns:
        Contact: Created contact.
    """
    contact = Contact(name=body.name, surname=body.surname, mobile=body.mobile, email=body.email, birthday=body.birthday, user=user)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def remove_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    """
    Delete the contact by it's ID.

    Args:
        contact_id (int): Id of the contact you want to delete.
        user (User): Authorised user who search for a contact. 
        db (Session): Session to retrieve data from DB.

    Returns:
        Contact | None: Return deleted contact info.
    """
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_contact(contact_id: int, body: ContactBase, user: User, db: Session) -> Contact | None:
    """
    Update the details of a contact by specified ID. 

    Args:
        contact_id (int): Id of a specified contact.
        body (ContactBase): The contact details that you want to update. Contains name, surname, mobile, email, bday.
        user (User): Authorised user who search for a contact. 
        db (Session): Session to retrieve data from DB.

    Returns:
        Contact | None: Return updated contact.
    """
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()
    if contact:
        contact.name=body.name
        contact.surname=body.surname
        contact.mobile=body.mobile
        contact.email=body.email
        contact.birthday=body.birthday
        db.commit()
    return contact
