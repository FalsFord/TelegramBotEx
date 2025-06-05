from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
import bot.keyboards.keyboards as kb


from bot.states import OrderState
from aiogram.fsm.context import FSMContext
from database.models.requests import (
    create_order,
    get_orders,
)
from .schemas import OrderBase
from sqlalchemy.ext.asyncio import AsyncSession
from bot.config.config import get_config

commands_router = Router()
config = get_config()


@commands_router.message(CommandStart())
async def start(message: Message):
    await message.reply(
        """🌟 Приветствуем вас!
        
Этот бот — ваш удобный помощник для быстрого оформления заказов и отслеживания их статуса. 
Здесь вы можете легко выбрать товары, проверить ход выполнения заказа или перейти в административный раздел для управления.
Начните прямо сейчас — мы всегда рады помочь! 😊""",
        reply_markup=kb.main_menu,
    )


@commands_router.callback_query(F.data == "to_order")
async def to_order_frst(callback: CallbackQuery, state: FSMContext):
    sent_message = await callback.message.edit_text("Enter name your order")
    await state.update_data(
        last_message_id=sent_message.message_id
    )  # Сохранение ID сообщения
    await state.set_state(OrderState.order_name)


@commands_router.message(OrderState.order_name)
async def to_order_scnd(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(order_name=message.text)
    await message.delete()

    user_id = message.from_user.id
    order = await state.get_data()
    order_create = OrderBase(
        user_id=user_id, order_name=order["order_name"], status="Отправлен на проверку", id=None)

    await create_order(session, order_create)
    await state.clear()

    last_message_id = order.get("last_message_id")

    if last_message_id:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=last_message_id,
            text="Your order was sent.",
            reply_markup=kb.go_back,
        )


@commands_router.callback_query(F.data == "status")
async def user_orders(callback: CallbackQuery, session: AsyncSession):
    orders = await get_orders(session=session, user_id=callback.from_user.id)
    if not orders:
        await callback.message.edit_text(
            "У вас пока нет заказов", reply_markup=kb.go_back
        )
        return
    orders_text = "\n".join(
        f"{order.id} - {order.order_name} - {order.status}"
        for i, order in enumerate(orders)
    )
    await callback.message.edit_text(
        f"Ваши заказы:\n\n{orders_text}", reply_markup=kb.go_back
    )


@commands_router.callback_query(F.data == "back")
async def menu_1(callback: CallbackQuery):
    # await callback.answer()
    await callback.message.edit_text(
        """🌟 Приветствуем вас!
        
Этот бот — ваш удобный помощник для быстрого оформления заказов и отслеживания их статуса. 
Здесь вы можете легко выбрать товары, проверить ход выполнения заказа или перейти в административный раздел для управления.\
Начните прямо сейчас — мы всегда рады помочь! 😊""",
        reply_markup=kb.main_menu,
    )
