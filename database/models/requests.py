from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from .orders_model import Order
from bot.handlers.schemas import OrderBase

async def get_orders_paginated(session: AsyncSession, page: int, limit: int = 10):
    offset = (page - 1) * limit
    stmt = select(Order).order_by(Order.id).limit(limit).offset(offset)
    result = await session.execute(stmt)
    orders = result.scalars().all()
    print(f"Загружено {len(orders)} заказов на странице {page}")  # Проверка
    return list(orders)


async def get_orders(session: AsyncSession, user_id: int) -> List[Order]:
    """
    Получает все заказы пользователя по его user_id.
    Args:
        session: Асинхронная сессия SQLAlchemy.
        user_id: ID пользователя, чьи заказы нужно найти.
    Returns:
        Список объектов Order или пустой список, если заказов нет.
    """
    stmt = select(Order).where(Order.user_id == user_id)
    result = await session.execute(stmt)
    orders = result.scalars().all()
    return list(orders)


async def create_order(session: AsyncSession, order: OrderBase) -> Order:
    db_order = Order(**order.model_dump())
    session.add(db_order)
    await session.commit()
    await session.refresh(db_order)
    return db_order


async def change_status_order(session: AsyncSession, order: OrderBase)-> Order:
    stmt = select(Order).where(Order.id == order.id)
    result = await session.execute(stmt)
    db_order = result.scalars().first()
    if db_order is None:
        raise ValueError(f"Закаказ с номером {order.id} не найден")
    db_order.status = order.status
    await session.commit()
    await session.refresh(db_order)
    return db_order


async def get_order(session: AsyncSession, order_id: int) -> Order:
    stmt = select(Order).where(Order.id == order_id)
    result = await session.execute(stmt)
    order = result.scalars().first()
    return order