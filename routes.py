from typing import List

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

import schemas
from database import get_db
from sqlalchemy.orm import Session
from crud import (
    create_user, get_users, get_user, update_user, delete_user,
    create_item, get_items, get_item, update_item, delete_item
)

router_websocket = APIRouter()
router_users = APIRouter(prefix='/users', tags=['user'])
router_items = APIRouter(prefix='/items', tags=['item'])


# WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


async def notify_clients(message: str):
    for connection in manager.active_connections:
        await connection.send_text(message)


@router_websocket.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    await manager.broadcast(f"Client #{client_id} joined the chat")
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")



@router_users.post("/", response_model=schemas.User)
async def create_user_route(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = create_user(db, user_data)
    await notify_clients(f"User added: {user.name}")
    return user


@router_users.get("/", response_model=List[schemas.User])
async def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    return users


@router_users.get("/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    return user


@router_users.patch("/{user_id}", response_model=schemas.User)
async def update_user_route(user_id: int, user_data: schemas.UserUpdate, db: Session = Depends(get_db)):
    updated_user = update_user(db, user_id, user_data)
    if updated_user:
        await notify_clients(f"User updated: {updated_user.name}")
        return updated_user
    return {"message": "User not found"}


@router_users.delete("/{user_id}")
async def delete_user_route(user_id: int, db: Session = Depends(get_db)):
    deleted = delete_user(db, user_id)
    if deleted:
        await notify_clients(f"User deleted: ID {user_id}")
        return {"message": "User deleted"}
    return {"message": "User not found"}


# Товары
@router_items.post("/", response_model=schemas.Item)
async def create_item_route(schema: schemas.ItemCreate, db: Session = Depends(get_db)):
    item = create_item(db, schema)
    await notify_clients(f"Item added: {item.name}")
    return item


@router_items.get("/", response_model=List[schemas.Item])
async def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = get_items(db, skip=skip, limit=limit)
    return items


@router_items.get("/{item_id}", response_model=schemas.Item)
async def read_item(item_id: int, db: Session = Depends(get_db)):
    item = get_item(db, item_id)
    return item


@router_items.patch("/{item_id}")
async def update_item_route(item_id: int, schema: schemas.ItemUpdate, db: Session = Depends(get_db)):
    updated_item = update_item(db, item_id, schema)
    if updated_item:
        await notify_clients(f"Item updated: {updated_item.name}")
        return updated_item
    return {"message": "Item not found"}


@router_items.delete("/{item_id}")
async def delete_item_route(item_id: int, db: Session = Depends(get_db)):
    deleted = delete_item(db, item_id)
    if deleted:
        await notify_clients(f"Item deleted: ID {item_id}")
        return {"message": "Item deleted"}
    return {"message": "Item not found"}
