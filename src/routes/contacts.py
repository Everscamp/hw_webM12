from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.services.auth import auth_service
from src.database.models import User
from src.schemas import ContactBase, ContactResponse
from src.repository import contacts as repository_contacts
from fastapi_limiter.depends import RateLimiter


router = APIRouter(prefix='/contacts')


@router.get("/", response_model=List[ContactResponse], 
            summary="List of all contascts.",
            description="No more than 10 requests per minute.", 
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    """
    Route to get the all contact list.

    Args:
        skip (int, optional): The starting position. Defaults to 0.
        limit (int, optional): The final position. Defaults to 100.
        db (Session, optional): Session to connect to DB. Defaults to Depends(get_db).
        current_user (User, optional): Authorised user who search for a contact. Defaults to Depends(auth_service.get_current_user).

    Returns:
        List[Contact]: List with all contacts.
    """
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    return contacts

@router.get("/contact/{contact_id}", response_model=ContactResponse,
            summary="Get a contact by it's ID.", 
            description="No more than 10 requests per minute.", 
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def read_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    """
    Route to get the contact by its ID.

    Args:
        contact_id (int, optional): Contact ID of a user you want to find. Defaults to Path(ge=1).
        db (AsyncSession, optional): Session to connect to DB. Defaults to Depends(get_db).
        current_user (User, optional): Authorised user who search for a contact. Defaults to Depends(auth_service.get_current_user).

    Raises:
        HTTPException: HTTP_404_NOT_FOUND if contact is not found.

    Returns:
        Contact | None: Return contact with a specified id or None.
    """
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact

@router.get("/{path}/{value}", response_model=ContactResponse, 
            summary="Find a contact by it's name, surname or email.",
            description="Put name, surname or email to the path line. And then put the value itself to value line.",
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def read_contact(path:str, value: str, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    """
    Route to get the contact buy its name/surname/emai.

    Args:
        path (str): Specify by what you want to search the contact. Can be name, surname, email.
        value (str): The actual name/surname/email to search by.
        db (Session, optional): Session to connect to DB. Defaults to Depends(get_db).
        current_user (User, optional): Authorised user who search for a contact. Defaults to Depends(auth_service.get_current_user).

    Raises:
        HTTPException: HTTP_404_NOT_FOUND if contact is not found.

    Returns:
        Contact: Return contact with a specified name if exist.
    """
    contact = await repository_contacts.get_contact_by_name(path, value, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.get("/birthdays", response_model=List[ContactResponse], 
            summary="List of contacts with birthdays within 7 days.", 
            description="No more than 10 requests per minute.", 
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    """
    Route to get the all contact with birthday within 7 days.

    Args:
        skip (int, optional): The starting position. Defaults to 0.
        limit (int, optional): The final position. Defaults to 100.
        db (Session, optional): Session to connect to DB. Defaults to Depends(get_db).
        current_user (User, optional): Authorised user who search for a contact. Defaults to Depends(auth_service.get_current_user).

    Returns:
        List[Contact]: List of the contacts.
    """
    contacts = await repository_contacts.get_closest_birthdays(skip, limit, current_user, db)
    return contacts


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, 
             summary="Add a new contact.",
             description="No more than 2 requests per minute.",
             dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def create_contact(body: ContactBase, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    """
    Route to add a new contact.

    Args:
        body (ContactBase): Containes contact details such as name, surname, email, number, bday.
        db (Session, optional): Session to connect to DB. Defaults to Depends(get_db).
        current_user (User, optional): Authorised user.. Defaults to Depends(auth_service.get_current_user).

    Returns:
        Contact: Created contact.
    """
    return await repository_contacts.create_contact(body, current_user, db)


@router.put("/{contact_id}", response_model=ContactResponse,
            summary="Update an existing contact by it's ID.",
            description="Put the contact ID in contact_id line. And then put the values itself to Request body.",
            dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def update_contact(body: ContactBase, contact_id: int, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    """
    Route to update the contact finded by its ID.

    Args:
        body (ContactBase): The contact details that you want to update.
        contact_id (int): Id of a specified contact you want to apdate.
        db (Session, optional): Session to connect to DB. Defaults to Depends(get_db).
        current_user (User, optional): Authorised user who search for a contact. Defaults to Depends(auth_service.get_current_user).

    Raises:
        HTTPException: HTTP_404_NOT_FOUND if contact not found.

    Returns:
        Contact | None: Return updated contact.
    """
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found!")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse, 
               summary="Delete an existing contact by it's ID.",
               description="No more than 5 requests per minute.",
             dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def remove_contact(contact_id: int, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    """
    Route to delete the contact finded by its ID.

    Args:
        contact_id (int): Id of the contact you want to delete.
        db (Session, optional): Session to connect to DB. Defaults to Depends(get_db).
        current_user (User, optional): Authorised user who search for a contact. Defaults to Depends(auth_service.get_current_user).

    Raises:
        HTTPException: HTTP_404_NOT_FOUND if contact not found.

    Returns:
        Contact | None: Return deleted contact info.
    """
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
