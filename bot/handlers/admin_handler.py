from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import bot.keyboards.keyboards as kb
from bot.keyboards.keyboards import orders_page, order_status
from bot.handlers.schemas import OrderBase
from bot.states import AdminState, ChangeStatus
from aiogram.fsm.context import FSMContext
from database.models.requests import (
    get_orders_paginated,
    change_status_order,
    get_order,
)
from sqlalchemy.ext.asyncio import AsyncSession
from bot.config.config import get_config

admin_router = Router()
config = get_config()

async def is_admin(admin_in: dict)-> bool:
    admin_name = config.admin
    admin_password = config.password
    if admin_in["name"] == admin_name and admin_in["password"] == admin_password:
        return True
    else:
        return False



@admin_router.callback_query(F.data == "admin")
async def join_admin_frst(callback: CallbackQuery, state: FSMContext):
    sent_message = await callback.message.edit_text("Enter name:")
    await state.update_data(last_message_id=sent_message.message_id)
    await state.set_state(AdminState.name)


@admin_router.message(AdminState.name)
async def join_admin_scnd(message: Message, state: FSMContext):
    await state.update_data(name=message.text)

    # Получаем ID последнего сообщения бота
    data = await state.get_data()
    last_message_id = data.get("last_message_id")
    await message.delete()
    if last_message_id:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=last_message_id,
            text="Введите пароль:"
        )
    await state.set_state(AdminState.password)



@admin_router.message(AdminState.password)
async def join_admin_thrd(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    admin_in = await state.get_data()
    await message.delete()
    last_message_id = admin_in.get("last_message_id")
    if last_message_id:
        if await is_admin(admin_in):
            # Создаём искусственный CallbackQuery
            fake_callback = CallbackQuery(
                id="0",
                from_user=message.from_user,
                chat_instance="fake_instance",
                message=message,
                data="admin_panel",
                message_id=last_message_id,
            )

            await admin_router.callback_query.trigger(fake_callback)

        else:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=last_message_id,
                text="Неверное имя или пароль!",
                reply_markup=kb.go_back
            )

    await state.clear()



@admin_router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery):
    bot = callback.message.bot
    try:
        await bot.edit_message_text(
            chat_id=callback.message.chat.id,message_id=callback.message_id, text="Welcome, admin!", reply_markup=kb.admin_panel)
    except:
        await callback.message.edit_text(text="Welcome, admin!", reply_markup=kb.admin_panel)


@admin_router.callback_query(F.data.startswith("admin_check_orders_page_"))
async def admin_orders_page(callback: CallbackQuery, session: AsyncSession):
    data_parts = callback.data.split("_")
    if len(data_parts) < 4 or not data_parts[-1].isdigit():
        page = 1
    else:
        page = int(data_parts[-1])

    orders = await get_orders_paginated(session=session, page=page)
    keyboard = await orders_page(page)
    if not orders:
        await callback.message.edit_text(f"На странице {page} нет заказов.", reply_markup=keyboard)
        return

    orders_text = "\n".join(
        f"{order.id} -   {order.order_name} - {order.status} (User ID: {order.user_id})"
        for order in orders
    )
    await callback.message.edit_text(f"Страница {page}:\n\n{orders_text}", reply_markup=keyboard)


@admin_router.callback_query(F.data == "change_status")
async def change_status_frst(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ChangeStatus.order_id)
    sent_message = await callback.message.edit_text("Enter order id please to change status:")
    await state.update_data(last_message_id=sent_message.message_id)


@admin_router.message(ChangeStatus.order_id)
async def change_status_scnd(message: Message, session: AsyncSession, state: FSMContext):
    await state.update_data(order_id=message.text)
    await message.delete()

    data = await state.get_data()
    last_message_id = data.get("last_message_id")
    order_id = int(data.get("order_id"))
    order = await get_order(session=session,order_id=order_id)
    print(f"{order.id}, {order.status}")
    if last_message_id:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=last_message_id,
            text=f"Задайте статус данному заказу:\n\n {order.id}. {order.order_name} - {order.status}.",
            reply_markup=await order_status()
        )
    await state.set_state(ChangeStatus.status)


@admin_router.callback_query(ChangeStatus.status)
async def change_status_thrd(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    order_id = int(data.get("order_id"))
    old_order = await get_order(session=session,order_id=order_id)
    new_order = OrderBase(id=old_order.id, user_id=old_order.user_id, order_name=old_order.order_name, status=callback.data)
    await change_status_order(session=session, order=new_order)
    await callback.message.edit_text(f"Заказ №{new_order.id} {new_order.order_name} имеет обновленный статус: {new_order.status}", reply_markup=kb.go_admin)
    await state.clear()
    await callback.bot.send_message(new_order.user_id, text=f"Обновился статус заказа:\n Заказ №{new_order.id} {new_order.order_name}  имеет статус:\n{new_order.status}")

