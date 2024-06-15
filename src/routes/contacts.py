from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.services.auth import auth_service
from src.database.models import User
from src.schemas import ContactBase, ContactResponse
from src.repository import contacts as repository_contacts


router = APIRouter(prefix='/contacts')


@router.get("/", response_model=List[ContactResponse], 
            summary="List of all contascts.",
            description="You can use limit if you need.")
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    return contacts

@router.get("/contact/{contact_id}", response_model=ContactResponse,
            summary="Get a contact by it's ID.")
async def read_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact

@router.get("/{path}/{value}", response_model=ContactResponse, 
            summary="Find a contact by it's name, surname or email.",
            description="Put name, surname or email to the path line. And then put the value itself to value line.")
async def read_contact(path:str, value: str, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact_by_name(path, value, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.get("/birthdays", response_model=List[ContactResponse], 
            summary="List of contacts with birthdays within 7 days.")
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_closest_birthdays(skip, limit, current_user, db)
    return contacts


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, summary="Add a new contact.")
async def create_contact(body: ContactBase, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    return await repository_contacts.create_contact(body, current_user, db)


@router.put("/{contact_id}", response_model=ContactResponse,
            summary="Update an existing contact by it's ID.",
            description="Put the contact ID in contact_id line. And then put the values itself to Request body.")
async def update_contact(body: ContactBase, contact_id: int, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse, summary="Delete an existing contact by it's ID.")
async def remove_contact(contact_id: int, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
